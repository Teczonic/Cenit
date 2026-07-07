## h) Matriz de riesgos técnicos

Ordenada por severidad (Probabilidad × Impacto). Cada riesgo trae señal temprana y mitigación concreta anclada al estado real del proyecto.

| # | Riesgo | Prob. | Impacto | Señal temprana | Mitigación |
|---|---|---|---|---|---|
| 1 | **Deuda por construir 12 módulos** antes de validar | Alta | Alto | El menú de navegación crece más rápido que los usuarios activos | Roadmap con compuertas de datos/dinero; ningún módulo entra al menú sin retención de Kanban+KPIs (regla del panel). Metrics Engine para que agregar métrica = fila, no módulo. |
| 2 | **Equipo de 1-2 personas** — bus factor, ritmo insostenible | Alta | Alto | Semanas sin release; features a medio terminar | XP interno (tests, CI ya en verde); alcance por sprints de 2 sem.; Codex/IA como segundo par; decir NO al 80% de las metodologías. |
| 3 | **UI de Streamlit toca su techo** para B2B competitivo | Media | Alto | Piloto dice "se siente lento/limitado", no vuelve por UX | Arquitectura ya lo contempla: `ui/` solo habla HTTP → migrar a Next.js no toca `api/`/`domain/`. Migrar **solo** una superficie y solo con señal (V3). |
| 4 | **Vercel serverless ↔ Supabase**: cold starts, límite de conexiones | Media | Alto | Timeouts intermitentes, "too many connections" | Ya mitigado: pooler IPv4 (`6543`), `pool_size=1`, `pool_pre_ping`. Vigilar `/api/health`. Si escala, subir a plan con más funciones concurrentes. |
| 5 | **Queries agregadas caras en Postgres** (flujo, DORA, snapshots) sobre historial creciente | Media | Medio | Cockpit tarda >2s; `/api/analytics/flow` lento | `metric_snapshots` pre-calcula por cron en vez de agregar on-read; índices en `task_state_transitions(task_id, changed_at)`; paginar historial. |
| 6 | **Vendor lock-in** (Supabase, Vercel, Streamlit Cloud) | Baja | Medio | Cambio de precios o límites del proveedor | Bajo por diseño: SQLAlchemy → cualquier Postgres; `Dockerfile.api`/`Dockerfile.ui` corren en cualquier host; el dominio no sabe dónde vive. Migrar = cambiar env vars, no reescribir. |
| 7 | **Escalabilidad del Metrics Engine** con múltiples fuentes (flow, dora, okr, space) | Baja | Medio | Snapshots que se pisan; providers que divergen en formato | Contrato `MetricProvider` único; snapshots append-only con `UNIQUE(metric_id, periodo)`; tests de dominio por provider. |
| 8 | **Secretos en el historial de git** (el repo es público) | Media | Alto | Credenciales viejas visibles en commits antiguos | Ya remediado en código (env vars); **acción pendiente**: rotar/borrar el proyecto Supabase viejo (`liwpsnbpghontykngznn`) cuyo password quedó en historial. |
| 9 | **IA que aconseja sobre personas** alucina o sesga (V3) | Media | Alto | Recomendaciones sin sustento en los datos | Evals antes de exponer (sección DORA/IA); IA solo sobre datos propios acumulados; nunca rankear individuos (antipatrón SPACE/DORA). |
| 10 | **Migraciones de esquema sin Alembic** (hoy `create_all`) | Media | Medio | Un `ALTER` manual rompe prod o diverge de local | `create_all` sirve para añadir tablas; en cuanto haya que **alterar** columnas con datos de piloto, introducir Alembic antes de tocar producción. |

### Lectura del panel

Los tres riesgos de mayor severidad (**deuda de 12 módulos, equipo de 1-2, techo de Streamlit**) no son técnicos en su raíz — son de **disciplina de alcance**. La arquitectura ya neutraliza los técnicos "duros" (lock-in bajo, UI desacoplada, pooler configurado). El riesgo real de Cenit no es que la tecnología falle, sino que el fundador construya de más antes de validar. Por eso la mitigación más importante de toda la matriz es la regla de producto: **nada nuevo entra al menú sin señal de retención**, y la matriz RICE es el instrumento para sostener esa disciplina cuando la tentación de construir aparezca.
