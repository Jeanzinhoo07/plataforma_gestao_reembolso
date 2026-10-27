from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from ..database import get_db
from ..models import Solicitacao, HistoricoAnalise, Usuario
from ..schemas import SolicitacaoCreate, SolicitacaoUpdate, SolicitacaoOut, DecisaoInput, PagamentoInput
from ..security import usuario_atual, exigir_perfis

router = APIRouter(prefix="/reembolsos", tags=["Reembolsos"])
ENCERRADAS = {"paga", "recusada"}

def buscar_solicitacao(db: Session, solicitacao_id: int) -> Solicitacao:
    item = db.query(Solicitacao).options(selectinload(Solicitacao.historico)).filter(Solicitacao.id == solicitacao_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada.")
    return item

def pode_ver(item: Solicitacao, usuario: Usuario):
    if usuario.perfil == "colaborador" and item.solicitante_id != usuario.id:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada.")
    if usuario.perfil == "gestor":
        # Busca de departamento é feita no endpoint com acesso ao banco.
        pass

def registrar_historico(db, item, usuario, etapa, decisao, observacao=None):
    db.add(HistoricoAnalise(solicitacao_id=item.id, responsavel_id=usuario.id, etapa=etapa,
                            decisao=decisao, observacao=observacao))

@router.post("/", response_model=SolicitacaoOut, status_code=201)
def criar(dados: SolicitacaoCreate, db: Session = Depends(get_db), usuario: Usuario = Depends(exigir_perfis("colaborador"))):
    if dados.data_despesa > date.today():
        raise HTTPException(status_code=422, detail="A data da despesa não pode ser futura.")
    item = Solicitacao(solicitante_id=usuario.id, categoria=dados.categoria.strip(), valor=dados.valor,
                       data_despesa=dados.data_despesa, justificativa=dados.justificativa.strip(),
                       referencia_comprovante=dados.referencia_comprovante.strip(), situacao="rascunho")
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe uma solicitação sua com esta referência de comprovante.")
    db.refresh(item)
    return item

@router.get("/", response_model=list[SolicitacaoOut])
def listar(db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual),
           situacao: str | None = Query(default=None), categoria: str | None = Query(default=None),
           departamento_id: int | None = Query(default=None)):
    q = db.query(Solicitacao).options(selectinload(Solicitacao.historico)).join(Usuario, Solicitacao.solicitante_id == Usuario.id)
    if usuario.perfil == "colaborador":
        q = q.filter(Solicitacao.solicitante_id == usuario.id)
    elif usuario.perfil == "gestor":
        q = q.filter(Usuario.departamento_id == usuario.departamento_id)
    if situacao:
        q = q.filter(Solicitacao.situacao == situacao)
    if categoria:
        q = q.filter(Solicitacao.categoria == categoria)
    if departamento_id is not None:
        if usuario.perfil != "financeiro" and departamento_id != usuario.departamento_id:
            raise HTTPException(status_code=403, detail="Você não pode consultar este departamento.")
        q = q.filter(Usuario.departamento_id == departamento_id)
    return q.order_by(Solicitacao.criada_em.desc()).all()

@router.get("/{solicitacao_id}", response_model=SolicitacaoOut)
def consultar(solicitacao_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual)):
    item = buscar_solicitacao(db, solicitacao_id)
    pode_ver(item, usuario)
    solicitante = db.get(Usuario, item.solicitante_id)
    if usuario.perfil == "gestor" and solicitante.departamento_id != usuario.departamento_id:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada.")
    return item

@router.put("/{solicitacao_id}", response_model=SolicitacaoOut)
def atualizar(solicitacao_id: int, dados: SolicitacaoUpdate, db: Session = Depends(get_db),
              usuario: Usuario = Depends(exigir_perfis("colaborador"))):
    item = buscar_solicitacao(db, solicitacao_id)
    if item.solicitante_id != usuario.id:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada.")
    if item.situacao != "rascunho":
        raise HTTPException(status_code=409, detail="Só é possível alterar solicitações em rascunho.")
    alteracoes = dados.model_dump(exclude_unset=True, exclude_none=True)
    if "data_despesa" in alteracoes and alteracoes["data_despesa"] > date.today():
        raise HTTPException(status_code=422, detail="A data da despesa não pode ser futura.")
    for campo, valor in alteracoes.items():
        setattr(item, campo, valor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Referência de comprovante já utilizada por você.")
    db.refresh(item)
    return item

@router.delete("/{solicitacao_id}", status_code=204)
def excluir(solicitacao_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(exigir_perfis("colaborador"))):
    item = buscar_solicitacao(db, solicitacao_id)
    if item.solicitante_id != usuario.id:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada.")
    if item.situacao != "rascunho":
        raise HTTPException(status_code=409, detail="Só é possível excluir solicitações em rascunho.")
    db.delete(item); db.commit()
    return None

@router.post("/{solicitacao_id}/enviar", response_model=SolicitacaoOut)
def enviar(solicitacao_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(exigir_perfis("colaborador"))):
    item = buscar_solicitacao(db, solicitacao_id)
    if item.solicitante_id != usuario.id:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada.")
    if item.situacao != "rascunho":
        raise HTTPException(status_code=409, detail="A solicitação não está em rascunho.")
    item.situacao = "aguardando_gestor"
    registrar_historico(db, item, usuario, "envio", "enviada", "Solicitação encaminhada ao gestor.")
    db.commit(); db.refresh(item)
    return item

@router.post("/{solicitacao_id}/decisao-gestor", response_model=SolicitacaoOut)
def decisao_gestor(solicitacao_id: int, dados: DecisaoInput, db: Session = Depends(get_db),
                   usuario: Usuario = Depends(exigir_perfis("gestor"))):
    item = buscar_solicitacao(db, solicitacao_id)
    solicitante = db.get(Usuario, item.solicitante_id)
    if solicitante.departamento_id != usuario.departamento_id:
        raise HTTPException(status_code=403, detail="Solicitação fora do seu departamento.")
    if item.solicitante_id == usuario.id:
        raise HTTPException(status_code=403, detail="Não é permitido aprovar solicitação de sua própria autoria.")
    if item.situacao != "aguardando_gestor":
        raise HTTPException(status_code=409, detail="A solicitação não aguarda decisão do gestor.")
    if dados.decisao == "recusar" and not (dados.observacao or "").strip():
        raise HTTPException(status_code=422, detail="A recusa exige justificativa.")
    item.situacao = "aguardando_financeiro" if dados.decisao == "aprovar" else "recusada"
    registrar_historico(db, item, usuario, "gestor", dados.decisao, dados.observacao)
    db.commit(); db.refresh(item)
    return item

@router.post("/{solicitacao_id}/decisao-financeira", response_model=SolicitacaoOut)
def decisao_financeira(solicitacao_id: int, dados: DecisaoInput, db: Session = Depends(get_db),
                       usuario: Usuario = Depends(exigir_perfis("financeiro"))):
    item = buscar_solicitacao(db, solicitacao_id)
    if item.solicitante_id == usuario.id:
        raise HTTPException(status_code=403, detail="Não é permitido aprovar solicitação de sua própria autoria.")
    if item.situacao != "aguardando_financeiro":
        raise HTTPException(status_code=409, detail="A solicitação ainda não aguarda análise financeira.")
    if dados.decisao == "recusar" and not (dados.observacao or "").strip():
        raise HTTPException(status_code=422, detail="A recusa exige justificativa.")
    item.situacao = "aprovada" if dados.decisao == "aprovar" else "recusada"
    registrar_historico(db, item, usuario, "financeiro", dados.decisao, dados.observacao)
    db.commit(); db.refresh(item)
    return item

@router.post("/{solicitacao_id}/pagamento", response_model=SolicitacaoOut)
def registrar_pagamento(solicitacao_id: int, dados: PagamentoInput, db: Session = Depends(get_db),
                        usuario: Usuario = Depends(exigir_perfis("financeiro"))):
    item = buscar_solicitacao(db, solicitacao_id)
    if item.situacao != "aprovada":
        raise HTTPException(status_code=409, detail="Só é possível registrar pagamento após aprovação financeira.")
    item.situacao = "paga"
    registrar_historico(db, item, usuario, "pagamento", "paga", dados.observacao)
    db.commit(); db.refresh(item)
    return item
