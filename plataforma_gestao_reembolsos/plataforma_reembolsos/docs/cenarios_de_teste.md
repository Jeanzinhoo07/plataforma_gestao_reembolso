# Roteiro manual de testes

Preencha o resultado e anexe evidência após executar cada teste. Este arquivo é um roteiro, não uma afirmação de que os testes já passaram.

| ID | Cenário | Resultado esperado |
|---|---|---|
| CT01 | Colaborador consulta solicitação de outro usuário | Acesso negado/404, sem dados financeiros |
| CT02 | Gestor tenta decidir solicitação de outro departamento | 403 |
| CT03 | Login com senha incorreta | 401, mensagem genérica |
| CT04 | Cadastro público tenta criar perfil financeiro | Conta criada como colaborador |
| CT05 | Financeiro tenta decidir antes do gestor | 409 |
| CT06 | Solicitante tenta alterar após envio | 409 |
| CT07 | Gestor lista pendências | Somente solicitações do departamento |
| CT08 | Consultar histórico após aprovação e pagamento | Histórico com responsáveis e decisões |
| CT09 | Criar solicitação com valor zero/negativo | 422 |
| CT10 | Criar despesa com data futura | 422 |
| CT11 | Reutilizar referência do comprovante pelo mesmo colaborador | 409 |
| CT12 | Recusar sem justificativa | 422 |
| CT13 | Colaborador tenta registrar pagamento | 403 |
| CT14 | Alterar solicitação paga ou recusada | 409 |
| CT15 | Usar token expirado/inválido | 401 |

Campos para evidência: data/hora, endpoint, perfil usado, entrada enviada, status recebido, resultado observado e captura de tela do Swagger/Postman.
