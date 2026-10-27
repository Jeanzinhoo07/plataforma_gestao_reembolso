# Modelo de dados

- **Departamento** (`departamentos`): `id`, `nome`.
- **Usuário** (`usuarios`): `id`, `nome`, `email`, `senha_hash`, `perfil`, `departamento_id`, `ativo`.
- **Solicitação** (`solicitacoes`): `id`, `solicitante_id`, `categoria`, `valor`, `data_despesa`, `justificativa`, `referencia_comprovante`, `situacao`, `criada_em`.
- **Histórico de análise** (`historico_analise`): `id`, `solicitacao_id`, `responsavel_id`, `etapa`, `decisao`, `observacao`, `data_decisao`.

## Relacionamentos
- Um departamento possui vários usuários.
- Um usuário pertence a um departamento.
- Um usuário colaborador pode registrar várias solicitações.
- Uma solicitação pode ter vários registros no histórico.
- Cada registro do histórico referencia a solicitação e o usuário responsável.

A referência do comprovante é textual. O banco impõe unicidade da combinação solicitante + referência, impedindo que a mesma pessoa reutilize a mesma referência em solicitações diferentes.
