from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import String, Integer, ForeignKey, Date, DateTime, Numeric, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Departamento(Base):
    __tablename__ = "departamentos"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="departamento")

class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil: Mapped[str] = mapped_column(String(20), nullable=False)  # colaborador, gestor, financeiro
    departamento_id: Mapped[int] = mapped_column(ForeignKey("departamentos.id"), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    departamento: Mapped["Departamento"] = relationship(back_populates="usuarios")
    solicitacoes: Mapped[list["Solicitacao"]] = relationship(back_populates="solicitante")

class Solicitacao(Base):
    __tablename__ = "solicitacoes"
    __table_args__ = (UniqueConstraint("solicitante_id", "referencia_comprovante", name="uq_solicitante_comprovante"),)
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    solicitante_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    categoria: Mapped[str] = mapped_column(String(60), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    data_despesa: Mapped[date] = mapped_column(Date, nullable=False)
    justificativa: Mapped[str] = mapped_column(Text, nullable=False)
    referencia_comprovante: Mapped[str] = mapped_column(String(150), nullable=False)
    situacao: Mapped[str] = mapped_column(String(30), default="rascunho", nullable=False, index=True)
    criada_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    solicitante: Mapped["Usuario"] = relationship(back_populates="solicitacoes")
    historico: Mapped[list["HistoricoAnalise"]] = relationship(back_populates="solicitacao", cascade="all, delete-orphan", order_by="HistoricoAnalise.data_decisao")

class HistoricoAnalise(Base):
    __tablename__ = "historico_analise"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    solicitacao_id: Mapped[int] = mapped_column(ForeignKey("solicitacoes.id"), nullable=False, index=True)
    responsavel_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    etapa: Mapped[str] = mapped_column(String(30), nullable=False)
    decisao: Mapped[str] = mapped_column(String(30), nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_decisao: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    solicitacao: Mapped["Solicitacao"] = relationship(back_populates="historico")
