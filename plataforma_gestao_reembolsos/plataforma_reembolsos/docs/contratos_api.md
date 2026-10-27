# Contratos resumidos da API

Todos os endpoints protegidos exigem `Authorization: Bearer <token>`.

## Criar solicitação — `POST /reembolsos/`
Entrada:
```json
{
  "categoria": "transporte",
  "valor": "180.00",
  "data_despesa": "2026-10-20",
  "justificativa": "Deslocamento para atendimento externo",
  "referencia_comprovante": "REC-2026-0001"
}
```
Sucesso: `201 Created`, com a solicitação criada e situação `rascunho`.

## Enviar para análise — `POST /reembolsos/{id}/enviar`
Sucesso: `200 OK`, situação passa a `aguardando_gestor`.

## Decisão do gestor — `POST /reembolsos/{id}/decisao-gestor`
Entrada:
```json
{"decisao": "aprovar", "observacao": "Despesa compatível com a atividade"}
```
`decisao` pode ser `aprovar` ou `recusar`. Recusa exige observação.

## Decisão financeira — `POST /reembolsos/{id}/decisao-financeira`
Mesma estrutura da decisão do gestor. Só pode ocorrer após aprovação do gestor.

## Registrar pagamento — `POST /reembolsos/{id}/pagamento`
Entrada:
```json
{"observacao": "Pagamento registrado em controle interno"}
```
Sucesso: situação passa a `paga`. Não ocorre transferência bancária real.

## Códigos esperados
- `200`: consulta ou operação concluída.
- `201`: recurso criado.
- `204`: exclusão concluída sem corpo.
- `401`: autenticação inválida/expirada.
- `403`: usuário autenticado sem permissão.
- `404`: recurso inexistente ou ocultado por confidencialidade.
- `409`: conflito de estado ou duplicidade.
- `422`: entrada inválida ou regra de validação violada.
