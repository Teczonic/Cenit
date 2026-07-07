## b) Diagrama ER completo

El diagrama combina lo que **ya existe en el repo** (`users`, `tasks`, `task_state_transitions`, `okr_cycles`, `objectives`, `key_results`, `task_key_results`) con las entidades **propuestas y deduplicadas** de las 12 metodologías. La regla de consolidación aplicada: una entidad base, múltiples lentes — nunca dos tablas para el mismo concepto.

```mermaid
erDiagram
    users ||--o{ tasks : "created_by / responsable"
    users ||--o{ task_state_transitions : "changed_by"
    users ||--o{ objectives : owns

    tasks ||--o{ task_state_transitions : "historia de estados"
    tasks ||--o{ task_key_results : "alinea a"
    tasks }o--o| sprints : "sprint_tasks"
    tasks }o--o| projects : "project_id"
    tasks ||--o{ task_insights : "nace de"

    okr_cycles ||--o{ objectives : contiene
    objectives ||--o{ key_results : mide
    key_results ||--o{ task_key_results : "avanza con"

    metric_definitions ||--o{ metric_snapshots : "serie temporal"

    insights ||--o{ task_insights : "evidencia"

    deployments ||--o{ incidents : "puede causar"

    users {
        int id PK
        string username UK
        string name
        string hashed_password
        string role
        string color
    }
    tasks {
        int id PK
        string entidad
        string proyecto
        string cliente
        text descripcion
        string prioridad
        string estado
        string responsable
        timestamptz fecha_inicio
        timestamptz fecha_fin
        timestamptz fecha_completado
        string created_by
        int project_id FK
    }
    task_state_transitions {
        int id PK
        int task_id FK
        string from_state
        string to_state
        string changed_by
        timestamptz changed_at
    }
    okr_cycles {
        int id PK
        string nombre
        date fecha_inicio
        date fecha_fin
        string estado
    }
    objectives {
        int id PK
        int cycle_id FK
        string titulo
        string owner
        string entidad
    }
    key_results {
        int id PK
        int objective_id FK
        string titulo
        float valor_inicial
        float valor_meta
        float valor_actual
        string unidad
    }
    task_key_results {
        int task_id PK,FK
        int kr_id PK,FK
    }
    metric_definitions {
        int id PK
        string clave UK
        string fuente
        string direccion
        numeric meta
        numeric umbral_alerta
    }
    metric_snapshots {
        int id PK
        int metric_id FK
        date periodo_inicio
        date periodo_fin
        numeric valor
        string estado
    }
    sprints {
        int id PK
        string entidad
        string nombre
        date fecha_inicio
        date fecha_fin
        string estado
    }
    projects {
        int id PK
        string nombre
        string estado
        date fecha_inicio
        date fecha_fin_plan
    }
    insights {
        int id PK
        string tipo
        text texto
        string created_by
    }
    deployments {
        int id PK
        string environment
        string status
        string commit_sha
        timestamptz deployed_at
    }
    incidents {
        int id PK
        int caused_by_deployment_id FK
        timestamptz detected_at
        timestamptz restored_at
    }
```

### Decisiones de consolidación

| Riesgo de duplicación | Metodologías implicadas | Resolución |
|---|---|---|
| "Una tabla de métricas por metodología" | KPIs, DORA, SPACE, Analytics, OKR (KRs cuantitativos) | Una sola pareja `metric_definitions` + `metric_snapshots`; cada metodología es un valor de `fuente`, no una tabla |
| "Una tabla de historia por vista" | Kanban (aging), Lean (flow efficiency), SPACE, Riesgos | Todas leen de `task_state_transitions` (ya existe) — es la fuente única de tiempo por estado |
| "Item de trabajo por marco" (story, card, work item, PBI) | Scrum, Kanban, XP, Waterfall, PMBOK | Una sola tabla `tasks`; sprint/proyecto se modelan como relaciones (`sprint_tasks`, `project_id`), no como tipos distintos de tarea |
| "Ciclo temporal por marco" (sprint, iteración, cadencia, ciclo OKR) | Scrum, XP, OKRs | `sprints` para iteraciones de ejecución; `okr_cycles` para dirección trimestral — conceptos distintos, no se fusionan |
| "Objetivo/meta por marco" (KR, KPI target, PI objective) | OKRs, KPIs, SAFe | `key_results` para dirección con KRs; metas operativas viven como `meta` en `metric_definitions`. No hay tabla de "goals" genérica que confunda ambos |
| Alineación tarea→resultado | OKRs, KPIs | `task_key_results` (ya existe) es el único puente; alimenta el *alignment ratio* del cockpit |

### Lo que está vivo hoy vs. propuesto

- **Vivo en el repo** (verificable): `users`, `tasks`, `task_state_transitions`, `okr_cycles`, `objectives`, `key_results`, `task_key_results`.
- **Propuesto tras señal de piloto**: `metric_definitions`/`metric_snapshots` (motor de KPIs, RICE #2), `sprints`/`sprint_tasks` (Scrum, #3), `projects` (Waterfall/PMBOK, #7), `insights`/`task_insights` (Design Thinking, #11), `deployments`/`incidents` (DORA, #6).

Ninguna entidad propuesta rompe el esquema actual: todas cuelgan de `tasks`/`users` vía FK. Esto confirma la tesis de sección 13: **un solo sistema de trabajo, múltiples lentes metodológicos** montados encima sin reescribir el núcleo.
