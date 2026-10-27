# Matriz de permissões

| Operação | Colaborador | Gestor | Financeiro |
|---|---|---|---|
| Criar solicitação | Sim | Não | Não |
| Consultar solicitações próprias | Sim | Sim, no seu departamento | Sim, todas |
| Alterar/excluir rascunho próprio | Sim | Não | Não |
| Enviar solicitação | Sim, própria | Não | Não |
| Decidir etapa do gestor | Não | Sim, no seu departamento | Não |
| Decidir etapa financeira | Não | Não | Sim, após gestor |
| Registrar pagamento | Não | Não | Sim, após aprovação financeira |
| Listar usuários | Não | Sim, no departamento | Sim, todos |
| Criar departamento | Não | Não | Sim |

## Restrições
- Colaboradores não visualizam solicitações de outros usuários.
- Gestores só analisam solicitações de seu departamento.
- A API não permite ao cadastro público criar contas privilegiadas.
- Solicitações só podem ser alteradas ou excluídas em rascunho.
- Recusas exigem observação justificativa.
- O histórico registra responsável, etapa, decisão, data e observação.
