from fastapi import FastAPI
from .database import Base, engine
from .routers import auth, departamentos, usuarios, reembolsos

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Plataforma de Gestão de Reembolsos Corporativos",
    version="1.0.0",
    description="API acadêmica para gerenciar solicitações de reembolso com controle de acesso e histórico."
)

app.include_router(auth.router)
app.include_router(departamentos.router)
app.include_router(usuarios.router)
app.include_router(reembolsos.router)

@app.get("/", tags=["Início"])
def inicio():
    return {"mensagem": "API de Gestão de Reembolsos Corporativos", "documentacao": "/docs"}
