from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class DepartamentoCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=100)

class DepartamentoOut(DepartamentoCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    perfil: str = "colaborador"
    departamento_id: int

    @field_validator("perfil")
    @classmethod
    def perfil_valido(cls, v):
        if v not in {"colaborador", "gestor", "financeiro"}:
            raise ValueError("Perfil deve ser colaborador, gestor ou financeiro.")
        return v

class UsuarioOut(BaseModel):
    id: int
    nome: str
    email: EmailStr
    perfil: str
    departamento_id: int
    ativo: bool
    model_config = ConfigDict(from_attributes=True)

class LoginInput(BaseModel):
    email: EmailStr
    senha: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class SolicitacaoCreate(BaseModel):
    categoria: str = Field(min_length=2, max_length=60)
    valor: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    data_despesa: date
    justificativa: str = Field(min_length=5, max_length=2000)
    referencia_comprovante: str = Field(min_length=1, max_length=150)

class SolicitacaoUpdate(BaseModel):
    categoria: str | None = Field(default=None, min_length=2, max_length=60)
    valor: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    data_despesa: date | None = None
    justificativa: str | None = Field(default=None, min_length=5, max_length=2000)
    referencia_comprovante: str | None = Field(default=None, min_length=1, max_length=150)

class DecisaoInput(BaseModel):
    decisao: str
    observacao: str | None = Field(default=None, max_length=2000)

    @field_validator("decisao")
    @classmethod
    def decisao_valida(cls, v):
        if v not in {"aprovar", "recusar"}:
            raise ValueError("A decisão deve ser aprovar ou recusar.")
        return v

class PagamentoInput(BaseModel):
    observacao: str | None = Field(default=None, max_length=2000)

class HistoricoOut(BaseModel):
    id: int
    responsavel_id: int
    etapa: str
    decisao: str
    observacao: str | None
    data_decisao: datetime
    model_config = ConfigDict(from_attributes=True)

class SolicitacaoOut(BaseModel):
    id: int
    solicitante_id: int
    categoria: str
    valor: Decimal
    data_despesa: date
    justificativa: str
    referencia_comprovante: str
    situacao: str
    criada_em: datetime
    historico: list[HistoricoOut] = []
    model_config = ConfigDict(from_attributes=True)
