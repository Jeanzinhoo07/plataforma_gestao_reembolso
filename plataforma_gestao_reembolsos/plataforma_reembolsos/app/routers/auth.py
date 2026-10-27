from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Usuario
from ..schemas import LoginInput, TokenOut, UsuarioCreate, UsuarioOut
from ..security import hash_senha, verificar_senha, criar_token, usuario_atual

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/cadastro", response_model=UsuarioOut, status_code=201)
def cadastrar_usuario(dados: UsuarioCreate, db: Session = Depends(get_db)):
    # Para o trabalho acadêmico: o cadastro público sempre cria colaborador.
    # Perfis privilegiados devem ser criados por procedimento administrativo seguro.
    if db.query(Usuario).filter(Usuario.email == dados.email.lower()).first():
        raise HTTPException(status_code=409, detail="Já existe usuário com este e-mail.")
    usuario = Usuario(nome=dados.nome, email=dados.email.lower(), senha_hash=hash_senha(dados.senha),
                      perfil="colaborador", departamento_id=dados.departamento_id)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

@router.post("/login", response_model=TokenOut)
def login(dados: LoginInput, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == dados.email.lower()).first()
    if not usuario or not usuario.ativo or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos.")
    return {"access_token": criar_token(usuario), "token_type": "bearer"}

@router.get("/me", response_model=UsuarioOut)
def meu_usuario(usuario: Usuario = Depends(usuario_atual)):
    return usuario
