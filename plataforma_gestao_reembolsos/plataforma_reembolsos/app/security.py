import os
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import Usuario

SECRET_KEY = os.getenv("SECRET_KEY", "chave-local-insegura-troque-antes-de-publicar")
ALGORITHM = "HS256"
TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "60"))
password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_senha(senha: str) -> str:
    return password_hash.hash(senha)

def verificar_senha(senha: str, senha_hash: str) -> bool:
    return password_hash.verify(senha, senha_hash)

def criar_token(usuario: Usuario) -> str:
    agora = datetime.now(timezone.utc)
    payload = {"sub": str(usuario.id), "perfil": usuario.perfil, "iat": agora, "exp": agora + timedelta(minutes=TOKEN_MINUTES)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def usuario_atual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    erro = HTTPException(status_code=401, detail="Credenciais inválidas ou sessão expirada.", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id = int(payload.get("sub", ""))
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise erro
    usuario = db.get(Usuario, usuario_id)
    if not usuario or not usuario.ativo:
        raise erro
    return usuario

def exigir_perfis(*perfis):
    def dependencia(usuario: Usuario = Depends(usuario_atual)):
        if usuario.perfil not in perfis:
            raise HTTPException(status_code=403, detail="Você não tem permissão para esta operação.")
        return usuario
    return dependencia
