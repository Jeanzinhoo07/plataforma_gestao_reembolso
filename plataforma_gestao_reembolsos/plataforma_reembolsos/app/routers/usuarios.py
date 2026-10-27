from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Usuario
from ..schemas import UsuarioOut
from ..security import usuario_atual, exigir_perfis

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

@router.get("/me", response_model=UsuarioOut)
def perfil_atual(usuario: Usuario = Depends(usuario_atual)):
    return usuario

@router.get("/", response_model=list[UsuarioOut])
def listar_usuarios(db: Session = Depends(get_db), usuario: Usuario = Depends(exigir_perfis("financeiro", "gestor"))):
    q = db.query(Usuario)
    if usuario.perfil == "gestor":
        q = q.filter(Usuario.departamento_id == usuario.departamento_id)
    return q.order_by(Usuario.nome).all()

@router.get("/{usuario_id}", response_model=UsuarioOut)
def consultar_usuario(usuario_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual)):
    alvo = db.get(Usuario, usuario_id)
    if not alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if usuario.perfil == "colaborador" and alvo.id != usuario.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para consultar este usuário.")
    if usuario.perfil == "gestor" and alvo.departamento_id != usuario.departamento_id:
        raise HTTPException(status_code=403, detail="Usuário fora do seu departamento.")
    return alvo
