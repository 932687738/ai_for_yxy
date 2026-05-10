# GWMS AI Semantic Enrichment Report

## Deliverables

- Importable Neo4j Cypher: `semantic_gwms_ai_enrichment.cypher`
- Task status log: `ai_semantic_task_status.md`
- Existing static graph files were not modified.
- GWMS source code under `C:\Users\BG518089\IdeaProjects\gwms` was not modified.

## Incremental Graph Size

- New/updated semantic node MERGEs: 161
- New/updated relationship MERGEs: 166
- Format: Neo4j Cypher using stable `id` keys.
- Scope: semantic augmentation layer over the existing `graph_nodes.jsonl` / `graph_edges.jsonl`.

## Covered Core Modules

- Outbound order: order creation, carrier defaulting and validation, order delete rules, wave allocation, pick task release, manual allocation, close/release and packed box close.
- Inbound receipt: receipt creation defaults, inspection confirmation, auto-receive after inspect, close validation, receive-by-user/LPN, return inspect-confirm-receive-putaway flow.
- Stock: `StockChangeCache` commit, async stock flow, stock log generation, allocation stock split, required stock dimensions for receive-stock creation.
- Task: task APIs, put-away task generation, task obtain/start, pick group assignment and task stage update.
- Cross-cutting: `ControllerInterceptor`, order/receipt revision AOP, local cache AOP, FSM AOP, RabbitMQ producer/queue dependencies.
- Persistence: core MyBatis tables including `ob_order_header`, `ib_receipt_header`, `stock`, `stock_log`, `stock_change_flow`, `task_header`, `task_detail`, `bas_code_info`, `bas_configuration`.

## Inferred Or Uncertain Parts

- `StockCoreServiceImpl.batchCommit` method name is inferred from the stock commit block read around lines 300-337; the behavior is confirmed by the code block.
- State machines are partly inferred from `CodeConstant` names and confirmed transitions. Confirmed examples: receipt create sets `DUE_IN`, receipt close sets `CLOSED`, pick group moves to `PICKING`, wave allocation checks `WAVE_ALLOCATED`.
- Target state of auto receive after inspect is inferred as `RECEIVED` or `OVER_RECEIVED` because `getReceiptWrapWhenClose` explicitly treats those as valid post-receive close states.
- External Xing service internals are not expanded; only project interaction points are modeled.

## Example Questions And Queries

1. What happens when an outbound pick list is created?

```cypher
MATCH (f:BusinessFlow {id:'flow:outbound-pick-release'})-[:HAS_STEP]->(step)
OPTIONAL MATCH (step)-[:ENFORCES]->(rule:BusinessRule)
RETURN step.id, step.name, rule.description
ORDER BY step.id;
```

2. Which rules block or modify outbound order carrier behavior?

```cypher
MATCH (:JavaClass {id:'class:OrderHeaderServiceImpl'})-[:DECLARES_METHOD]->(m)-[:ENFORCES]->(r:BusinessRule)
WHERE r.id CONTAINS 'carrier'
RETURN m.signature, r.description, r.source;
```

3. Which configuration keys affect inbound receipt auto receive and put-away?

```cypher
MATCH (m:Method)-[:USES_CONFIG]->(c:ConfigurationProperty)
WHERE m.id STARTS WITH 'method:ReceiptHeaderServiceImpl'
RETURN m.signature, c.key, c.meaning;
```

4. Which tables does the stock core flow touch?

```cypher
MATCH (:BusinessFlow {id:'flow:stock-change-core'})-[:HAS_STEP]->(m:Method)
MATCH (:JavaClass {id:'class:StockCoreServiceImpl'})-[:MAPS_TO]->(t:DatabaseTable)
RETURN DISTINCT m.signature, t.name, t.domain;
```

5. What state transitions are modeled for receipt lifecycle?

```cypher
MATCH (:StateMachine {id:'sm:ReceiptLifecycle'})-[:HAS_STATE]->(s:State)
OPTIONAL MATCH (m:Method)-[:TRIGGERS]->(tr:Transition)
WHERE tr.id CONTAINS 'receipt'
RETURN s.code AS stateCode, collect(DISTINCT tr.action) AS relatedActions;
```

## Self-Validation Notes

- Outbound pick flow is answerable from API -> service method -> allocation rule -> wave/pick-group/task transitions.
- Inbound receive flow is answerable from receipt APIs -> service methods -> process configuration -> receipt/task transitions.
- Stock update impact is answerable from `flow:stock-change-core`, stock tables, stock log/flow nodes, and RabbitMQ event relation.
- AOP/MQ implicit dependencies are explicit nodes, so queries no longer depend only on direct method calls.
