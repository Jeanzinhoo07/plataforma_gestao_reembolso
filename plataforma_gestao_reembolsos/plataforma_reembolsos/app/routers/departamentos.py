from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Departamento
from ..schemas import DepartamentoCreate, DepartamentoOut
from ..security import exigir_perfis

router = APIRouter(prefix="/departamentos", tags=["Departamentos"])

@router.post("/", response_model=DepartamentoOut, status_code=201)
def criar_departamento(dados: DepartamentoCreate, db: Session = Depends(get_db), _=Depends(exigir_perfis("financeiro"))):
    nome = dados.nome.strip()
    if db.query(Departamento).filter(Departamento.nome == nome).first():
        raise HTTPException(status_code=409, detail="Departamento já cadastrado.")
    item = Departamento(nome=nome)
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.get("/", response_model=list[DepartamentoOut])
def listar_departamentos(db: Session = Depends(get_db), _=Depends(exigir_perfis("financeiro", "gestor"))):
    return db.query(Departamento).order_by(Departamento.nome).all()
