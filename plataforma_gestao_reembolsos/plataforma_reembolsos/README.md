# Plataforma de Gestão de Reembolsos Corporativos

API REST em Python com FastAPI e SQLAlchemy, persistência em banco relacional SQLite, autenticação por token JWT, senhas com hash Argon2 e controle de acesso por perfil.

## 1. Requisitos
- Python 3.11 ou superior recomendado
- pip

## 2. Instalação (Windows / PowerShell)
Abra o terminal na pasta do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copie `.env.example` para `.env` e ajuste `SECRET_KEY`. Para que as variáveis do `.env` sejam carregadas automaticamente, instale `python-dotenv` e use-o conforme a configuração local, ou defina as variáveis no terminal. O exemplo funciona sem `.env`, mas usa uma chave local insegura.

```powershell
$env:SECRET_KEY="coloque-uma-chave-longa-e-aleatoria-aqui"
uvicorn app.main:app --reload
```

A API ficará em `http://127.0.0.1:8000` e a documentação interativa em `http://127.0.0.1:8000/docs`.

## 3. Criar departamentos iniciais
O cadastro de colaborador exige um departamento existente. Inicialize o banco com este comando na pasta raiz:

```powershell
python -c "from app.database import Base,engine,SessionLocal; from app.models import Departamento; Base.metadata.create_all(engine); db=SessionLocal(); [db.add(Departamento(nome=n)) for n in ['Comercial','Tecnologia','Financeiro'] if not db.query(Departamento).filter_by(nome=n).first()]; db.commit(); db.close()"
```

## 4. Criar contas
`POST /auth/cadastro` recebe `nome`, `email`, `senha`, `perfil` (o campo é aceito pelo schema, mas o cadastro público sempre cria perfil colaborador) e `departamento_id`. Para cumprir o princípio de menor privilégio, o cadastro público não permite que a pessoa escolha perfil privilegiado.

Para testes de gestor e financeiro, crie essas contas por procedimento administrativo local seguro. Exemplo de comando para criar uma conta de teste com perfil definido:

```powershell
python -c "from app.database import SessionLocal; from app.models import Usuario; from app.security import hash_senha; db=SessionLocal(); u=Usuario(nome='Gestor Teste',email='gestor@exemplo.com',senha_hash=hash_senha('SenhaForte123!'),perfil='gestor',departamento_id=1); db.add(u); db.commit(); db.close()"
```

Altere e-mail, perfil e departamento conforme necessário. Use `perfil='financeiro'` para uma conta financeira. Não exponha essas rotinas administrativas em uma API pública.

## 5. Autenticação
1. Faça `POST /auth/login` com e-mail e senha.
2. Copie `access_token` da resposta.
3. No Swagger, clique em **Authorize** e informe `Bearer SEU_TOKEN` quando solicitado, ou use o cabeçalho `Authorization: Bearer SEU_TOKEN`.

## 6. Principais rotas
| Método | Rota | Permissão / finalidade |
|---|---|---|
| POST | `/auth/cadastro` | Criar colaborador |
| POST | `/auth/login` | Obter token |
| GET | `/auth/me` | Ver usuário autenticado |
| POST/GET | `/departamentos/` | Financeiro cria; gestor/financeiro lista |
| GET | `/usuarios/` | Gestor vê seu departamento; financeiro vê todos |
| GET | `/reembolsos/` | Lista conforme perfil, aceita filtros |
| POST | `/reembolsos/` | Colaborador cria rascunho |
| GET | `/reembolsos/{id}` | Consulta respeitando permissões |
| PUT/DELETE | `/reembolsos/{id}` | Solicitante altera/exclui apenas rascunho |
| POST | `/reembolsos/{id}/enviar` | Envia para gestor |
| POST | `/reembolsos/{id}/decisao-gestor` | Gestor aprova/recusa |
| POST | `/reembolsos/{id}/decisao-financeira` | Financeiro aprova/recusa após gestor |
| POST | `/reembolsos/{id}/pagamento` | Financeiro registra pagamento |

## 7. Exemplo de solicitação
```json
{
  "categoria": "transporte",
  "valor": "180.00",
  "data_despesa": "2026-10-20",
  "justificativa": "Deslocamento para atendimento externo",
  "referencia_comprovante": "REC-2026-0001"
}
```

## 8. Situações
`rascunho` → `aguardando_gestor` → `aguardando_financeiro` → `aprovada` → `paga`.
Uma recusa encerra o fluxo com situação `recusada`.

## 9. Observações acadêmicas importantes
- O banco SQLite é persistente no arquivo `reembolsos.db`.
- A API não recebe comprovantes em arquivo nem realiza transferências bancárias, conforme o enunciado.
- Para produção, configure uma chave JWT segura, HTTPS, migrações (ex.: Alembic), política de logs, backups e revisão de segurança.
- A versão inicial cria tabelas automaticamente para facilitar a execução. Em uma entrega com migrations obrigatórias, substitua essa abordagem por Alembic.
- Execute testes dos cenários do enunciado antes da entrega e documente resultados reais; não declare testes como aprovados sem executá-los.
