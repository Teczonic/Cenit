# (Sección 02) Kanban

## 02. KANBAN

### 1. Principio central y origen

Kanban (看板, "tarjeta visual" o "señal") nace en Toyota en los años 40-50, dentro del Toyota Production System diseñado por Taiichi Ohno. El problema que resolvía era físico y brutal: la sobreproducción. Las fábricas producían piezas "por si acaso", acumulando inventario que ocultaba defectos, congelaba capital y retrasaba la detección de problemas. La tarjeta kanban era una señal de demanda: la estación aguas abajo "tiraba" (pull) trabajo de la estación aguas arriba solo cuando tenía capacidad real. Nada se producía sin una señal de demanda.

En 2004-2007, David J. Anderson adaptó el método al trabajo de conocimiento (Microsoft, luego Corbis) y lo formalizó en su libro *Kanban: Successful Evolutionary Change for Your Technology Business* (2010). El Kanban para software se sostiene sobre seis prácticas:

1. **Visualizar el flujo de trabajo** — el tablero de columnas que todo el mundo asocia con la palabra.
2. **Limitar el trabajo en curso (WIP limits)** — la práctica que casi nadie implementa y que es el corazón real del método.
3. **Gestionar el flujo** — medir lead time, cycle time y throughput, y actuar sobre ellos.
4. **Hacer las políticas explícitas** — qué significa "Done", cuándo una tarjeta puede moverse.
5. **Implementar bucles de retroalimentación** — cadencias de revisión (replenishment, delivery review).
6. **Mejorar colaborativamente, evolucionar experimentalmente** — kaizen aplicado al proceso.

El error de gestión que previene es doble. Primero, la **ilusión de productividad por ocupación**: un equipo con 40 tareas "En Proceso" para 5 personas no está siendo productivo, está haciendo multitasking destructivo (cada cambio de contexto cuesta ~20-40% de capacidad cognitiva según los estudios de Gerald Weinberg). Segundo, la **invisibilidad del cuello de botella**: sin visualización ni límites, el trabajo se acumula silenciosamente en una etapa (típicamente QA o code review) y nadie lo nota hasta que la fecha de entrega explota. La Ley de Little — que veremos en métricas — convierte esto en matemática: más WIP con el mismo throughput significa, inevitablemente, más tiempo de entrega.

Para Cenit esto es estratégico: Kanban ya es el **núcleo del producto** (la vista `ui/views/kanban.py` existe y `KanbanService.agrupar_por_estado` ya agrupa por los cuatro estados `No Iniciado | En Proceso | Pausado | Completado`). Lo que falta no es el tablero — es la disciplina que lo convierte en método: límites WIP, políticas explícitas y métricas de flujo. Ahí está el diferencial vendible frente a Trello ("tablero sin método") y la simplicidad vendible frente a Jira ("método enterrado en configuración"). Para un CTO de un equipo de 15 personas en Bogotá o CDMX, el pitch es: *"Trello te muestra las tarjetas; Cenit te dice cuándo tu equipo está saturado y cuánto va a tardar lo que entra hoy."*

### 2. Métricas y fórmulas exactas

Las cuatro métricas canónicas de Kanban, con sus fórmulas:

| Métrica | Fórmula | Unidad | Qué responde |
|---|---|---|---|
| **Lead Time** | `fecha_completado − fecha_creacion` (o `fecha_inicio` según política) | días | ¿Cuánto tarda algo desde que se pide hasta que se entrega? |
| **Cycle Time** | `fecha_completado − fecha_primer_movimiento_a_En_Proceso` | días | ¿Cuánto tarda desde que se empieza a trabajar? |
| **Throughput** | `COUNT(tareas completadas) / periodo` | tareas/semana | ¿Cuánto entrega el equipo por unidad de tiempo? |
| **WIP** | `COUNT(tareas en estados activos)` en un instante | tareas | ¿Cuánto hay abierto ahora mismo? |
| **Ley de Little** | `Lead Time promedio = WIP promedio / Throughput promedio` | — | Relación estructural entre las tres anteriores |
| **Flow Efficiency** | `tiempo_activo / lead_time × 100` | % | ¿Qué porcentaje del tiempo la tarea estuvo realmente trabajándose (vs. esperando/pausada)? |
| **Aging WIP** | `hoy − fecha_entrada_al_estado_actual` por tarea abierta | días | ¿Qué tarjetas están estancadas? |

**Ejemplo numérico paso a paso — equipo ficticio de 5 personas** (Ana, Bruno, Carla, Diego, Elena), ventana de observación: 4 semanas (20 días hábiles).

Datos observados:
- Tareas completadas en las 4 semanas: 24 → **Throughput = 24 / 4 = 6 tareas/semana**.
- WIP medido cada lunes (tareas en `En Proceso` + `Pausado`): 14, 16, 15, 15 → **WIP promedio = (14+16+15+15)/4 = 15 tareas**.
- **Ley de Little**: Lead Time esperado = 15 / 6 = **2.5 semanas = 12.5 días naturales de calendario laboral (~17.5 días naturales)**. Es decir: cualquier tarea que entra hoy al sistema, en promedio, saldrá en dos semanas y media — *sin importar quién la haga ni cuán "prioritaria" se declare*, mientras el WIP siga en 15.
- Verificación empírica con lead times reales de las 24 tareas completadas (días): `[3, 5, 2, 18, 7, 4, 6, 21, 3, 8, 5, 12, 4, 6, 9, 15, 2, 7, 5, 11, 6, 30, 4, 8]`.
  - Suma = 201 → **Lead Time promedio = 201/24 = 8.4 días** (consistente con Little si contamos días hábiles y el WIP incluye tareas pausadas que inflan la cola).
  - Ordenados: `[2,2,3,3,4,4,4,5,5,5,5,6,6,6,7,7,8,8,9,11,12,15,18,21,30]`… con 24 valores, **percentil 85 = valor en posición ⌈24×0.85⌉ = posición 21 = 15 días**. Este P85 es la cifra comprometible con un cliente: *"el 85% de las tareas se entregan en 15 días o menos"*. Nunca prometas con el promedio: la distribución de lead time es asimétrica (cola larga a la derecha, ese outlier de 30 días).
- **Flow Efficiency** de la tarea de 18 días: estuvo 4 días en `En Proceso` activo y 14 días entre `Pausado` y esperas → 4/18 = **22%**. Valores típicos de la industria: 5-15%. Si Cenit muestra este número, será la primera vez que el cliente lo ve, y duele — eso vende.
- **Experimento de WIP limit**: si el equipo baja el WIP de 15 a 10 (límite de 2 tareas activas por persona) y el throughput se mantiene en 6/semana, Little predice Lead Time = 10/6 = **1.67 semanas (−33%)**. En la práctica el throughput suele *subir* al reducir multitasking, mejorando aún más la cifra.

El modelo `Task` actual ya calcula `lead_time_days` (`fecha_completado − fecha_inicio`), pero **no puede calcular cycle time, flow efficiency ni aging** porque no persiste las transiciones de estado. Ese es el vacío de datos número uno a cerrar.

### 3. Modelo de datos

Tres piezas: (a) historial de transiciones (la tabla más importante — sin ella no hay métricas de flujo), (b) configuración de columnas y límites WIP, (c) snapshot diario opcional para el CFD (Cumulative Flow Diagram). Todo extiende `users` y `tasks` existentes:

```sql
-- 1. Historial de transiciones de estado: fuente de verdad para cycle time,
--    flow efficiency, aging y CFD. Se inserta una fila en cada cambio de estado.
CREATE TABLE task_state_transitions (
    id              SERIAL PRIMARY KEY,
    task_id         INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    from_state      VARCHAR(30),                 -- NULL en la creación de la tarea
    to_state        VARCHAR(30) NOT NULL,        -- 'No Iniciado' | 'En Proceso' | 'Pausado' | 'Completado'
    transitioned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    changed_by      INTEGER REFERENCES users(id) ON DELETE SET NULL,
    wip_at_moment   INTEGER,                     -- WIP total del tablero al momento del cambio (para correlaciones)
    CONSTRAINT chk_states_differ CHECK (from_state IS DISTINCT FROM to_state)
);
CREATE INDEX idx_tst_task ON task_state_transitions(task_id, transitioned_at);
CREATE INDEX idx_tst_when ON task_state_transitions(transitioned_at);

-- 2. Configuración de columnas del tablero: límites WIP y políticas explícitas
--    (práctica 2 y 4 de Anderson). Una fila por estado.
CREATE TABLE kanban_columns (
    id               SERIAL PRIMARY KEY,
    estado           VARCHAR(30) NOT NULL UNIQUE, -- mapea 1:1 a tasks.estado
    posicion         SMALLINT NOT NULL,           -- orden visual en el tablero
    wip_limit        INTEGER,                     -- NULL = sin límite (columnas No Iniciado / Completado)
    wip_limit_scope  VARCHAR(10) NOT NULL DEFAULT 'board',  -- 'board' | 'person'
    policy_text      TEXT,                        -- "Definition of Done" / criterio de entrada explícito
    is_active_state  BOOLEAN NOT NULL DEFAULT FALSE, -- cuenta para WIP y flow efficiency
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ
);
INSERT INTO kanban_columns (estado, posicion, wip_limit, is_active_state, policy_text) VALUES
    ('No Iniciado', 1, NULL, FALSE, 'Backlog priorizado. Entra al tablero solo con descripción y responsable.'),
    ('En Proceso',  2, 10,   TRUE,  'Máximo 2 por persona. Debe tener fecha_inicio.'),
    ('Pausado',     3, 5,    FALSE, 'Requiere comentario con motivo del bloqueo.'),
    ('Completado',  4, NULL, FALSE, 'Verificado por alguien distinto al responsable.');

-- 3. Eventos de violación de WIP: auditoría de cuándo y quién sobrepasó el límite
--    (Cenit alerta pero no bloquea — decisión de producto: fricción suave).
CREATE TABLE wip_violations (
    id           SERIAL PRIMARY KEY,
    column_id    INTEGER NOT NULL REFERENCES kanban_columns(id) ON DELETE CASCADE,
    task_id      INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id      INTEGER REFERENCES users(id) ON DELETE SET NULL,
    wip_limit    INTEGER NOT NULL,
    wip_actual   INTEGER NOT NULL,
    occurred_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    acknowledged BOOLEAN NOT NULL DEFAULT FALSE
);

-- 4. Snapshot diario para el Cumulative Flow Diagram (cron 23:59).
--    Alternativa: reconstruir desde task_state_transitions; el snapshot
--    simplifica el query del CFD a un SELECT plano.
CREATE TABLE flow_snapshots (
    id            SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    estado        VARCHAR(30) NOT NULL,
    entidad       VARCHAR(50),                    -- permite CFD filtrado por entidad/equipo
    task_count    INTEGER NOT NULL,
    UNIQUE (snapshot_date, estado, entidad)
);
CREATE INDEX idx_fs_date ON flow_snapshots(snapshot_date);
```

Nota de migración: al desplegar, poblar `task_state_transitions` retroactivamente con una fila sintética por tarea usando `created_at` (→ `No Iniciado`), `fecha_inicio` (→ `En Proceso`) y `fecha_completado` (→ `Completado`) para no arrancar con métricas vacías.

### 4. Casos de uso del domain layer

Extienden `KanbanService` en `domain/services.py` (o mejor: nuevo módulo `domain/flow_metrics.py` que mantiene `services.py` legible). Entidades de retorno como dataclasses en `domain/entities.py`:

```python
from dataclasses import dataclass
from datetime import date, datetime

@dataclass(frozen=True)
class FlowMetricsReport:
    periodo_dias: int
    throughput_semanal: float
    wip_promedio: float
    lead_time_promedio: float
    lead_time_p50: float
    lead_time_p85: float          # cifra comprometible con clientes
    cycle_time_promedio: float
    flow_efficiency_pct: float
    little_lead_time_estimado: float  # WIP / throughput — contraste con el real

@dataclass(frozen=True)
class WipStatus:
    estado: str
    wip_limit: int | None
    ocupacion_actual: int
    excedido: bool
    tareas_por_persona: dict[str, int]

@dataclass(frozen=True)
class AgingTask:
    task_id: int
    descripcion: str
    estado: str
    dias_en_estado: float
    percentil_vs_historico: float  # 0-100: qué tan atípica es esta permanencia


def calcular_metricas_de_flujo(
    transiciones: list[dict], tareas: list[dict],
    desde: date, hasta: date, entidad: str | None = None,
) -> FlowMetricsReport:
    """
    completadas = tareas con transición a 'Completado' en [desde, hasta]
    lead_times  = [t_completado - t_creacion por tarea]  -> promedio, p50, p85
    cycle_times = [t_completado - primera transición a 'En Proceso']
    throughput  = len(completadas) / semanas del periodo
    wip_prom    = promedio de reconstruir WIP diario desde transiciones
    flow_eff    = sum(tiempo en estados activos) / sum(lead_time) * 100
    little      = wip_prom / throughput
    """

def verificar_wip(
    tareas: list[dict], columnas: list[dict],
) -> list[WipStatus]:
    """
    Para cada columna con wip_limit no nulo:
      ocupacion = count(tareas en ese estado)
      si scope == 'person': agrupar por responsable, límite aplica por persona
      excedido = ocupacion > wip_limit (o alguna persona > límite)
    Se invoca ANTES de mover una tarjeta (dry-run) y DESPUÉS (registrar violación).
    """

def detectar_tareas_estancadas(
    tareas: list[dict], transiciones: list[dict],
    umbral_percentil: float = 85.0,
) -> list[AgingTask]:
    """
    Para cada tarea abierta: dias_en_estado = now - última transición.
    Comparar contra distribución histórica de permanencia en ese estado.
    Devolver las que superan el percentil umbral, ordenadas desc.
    Esta lista alimenta la vista Riesgos (sinergia con RiesgoService).
    """

def construir_cfd(
    snapshots: list[dict], desde: date, hasta: date, entidad: str | None = None,
) -> dict[str, list[tuple[date, int]]]:
    """
    { estado: [(fecha, count acumulado), ...] } listo para area chart apilado.
    Bandas que se ensanchan = cuello de botella en ese estado.
    """

def simular_reduccion_wip(
    reporte: FlowMetricsReport, nuevo_wip: int,
) -> float:
    """
    Ley de Little inversa: lead_time_proyectado = nuevo_wip / throughput_semanal.
    Widget "¿qué pasaría si...?" — argumento de venta del WIP limit.
    """
```

Diseño clave: las funciones reciben datos como `list[dict]` (mismo contrato que los servicios existentes que operan sobre `TaskOut` serializado) y no tocan la base de datos — la capa `api/crud.py` les inyecta los datos. Eso las hace testeables con pytest puro, sin fixtures de DB.

### 5. Diseño de API REST

Consistentes con los prefijos existentes (`/api/tasks`, `/api/analytics/...`):

| Método | Ruta | Propósito |
|---|---|---|
| `PATCH` | `/api/tasks/{id}/move` | Mover tarjeta con validación WIP (reemplaza el update genérico de estado) |
| `GET` | `/api/kanban/columns` | Columnas, límites y políticas |
| `PUT` | `/api/kanban/columns/{estado}` | Editar límite WIP / política (solo admin) |
| `GET` | `/api/kanban/wip-status` | Ocupación actual vs. límites |
| `GET` | `/api/analytics/flow?desde=&hasta=&entidad=` | FlowMetricsReport |
| `GET` | `/api/analytics/cfd?desde=&hasta=` | Series para el diagrama de flujo acumulado |
| `GET` | `/api/analytics/aging` | Tareas estancadas |

`PATCH /api/tasks/42/move` — request:

```json
{
  "to_estado": "En Proceso",
  "force": false
}
```

Respuesta `200` (movimiento válido) o `409 Conflict` si viola WIP y `force=false`:

```json
{
  "detail": "WIP limit excedido",
  "estado": "En Proceso",
  "wip_limit": 10,
  "wip_actual": 10,
  "sugerencia": "Completa o pausa una tarea antes de iniciar otra. Reintenta con force=true para registrar la excepción.",
  "tareas_mas_antiguas": [{"id": 17, "descripcion": "Migrar reportes", "dias_en_estado": 12.4}]
}
```

Con `force=true` el movimiento procede y se inserta en `wip_violations` — el sistema persuade, no bloquea (decisión de producto: en LatAm un tool que "no deja trabajar" se abandona en la semana 1; uno que registra excepciones da al lead la conversación de retro).

`GET /api/analytics/flow?desde=2026-06-01&hasta=2026-06-28` — respuesta:

```json
{
  "periodo_dias": 28,
  "throughput_semanal": 6.0,
  "wip_promedio": 15.0,
  "lead_time_promedio": 8.4,
  "lead_time_p50": 6.0,
  "lead_time_p85": 15.0,
  "cycle_time_promedio": 5.1,
  "flow_efficiency_pct": 34.2,
  "little_lead_time_estimado": 12.5
}
```

### 6. Vista o componente de UI

Evolución de `ui/views/kanban.py` (no una vista nueva — el tablero ya existe; se le añade el método):

**Cabecera del tablero**: fila de `st.metric` con Throughput semanal, Lead Time P85 y Flow Efficiency, cada una con delta vs. periodo anterior (`st.metric(delta=...)` verde/rojo). A la derecha, un selector `st.selectbox` de entidad (reutilizando `FiltroService`).

**Columnas**: 4 columnas con `st.columns(4)`. Cada encabezado de columna muestra `En Proceso — 8/10` con el contador de ocupación sobre límite; si ocupación ≥ límite, el encabezado se pinta ámbar (límite alcanzado) o rojo (excedido) usando markdown con color inline. Debajo del título, un `st.caption` con la política explícita de la columna (tooltip permanente de "qué significa estar aquí").

**Tarjetas**: cada tarjeta (`st.container(border=True)`) muestra descripción, responsable con su chip de color (columna `users.color` ya existente), prioridad, y — novedad — un **badge de aging**: "⏱ 12d en esta columna" que aparece solo cuando la tarea supera el P85 histórico de permanencia. Es la señal visual más accionable del tablero: el ojo va directo a lo estancado.

**Interacción de movimiento**: Streamlit no tiene drag & drop nativo confiable, así que cada tarjeta tiene un `st.selectbox` compacto o botones ‹ › para mover de estado. Al mover, la UI llama a `PATCH /api/tasks/{id}/move`; si responde 409, se muestra `st.warning` con el mensaje del límite y un botón "Mover de todas formas" (que reintenta con `force=true`) más la lista de "tareas más antiguas que podrías cerrar primero". Este micro-momento — el sistema sugiriendo terminar antes de empezar — ES el producto.

**Pestaña secundaria "Flujo"** (`st.tabs(["Tablero", "Flujo"])`): CFD como area chart apilado (Plotly, colores de `ESTADO_COLORS`), histograma de lead time con líneas verticales en P50/P85, y el widget de simulación: un `st.slider` de WIP objetivo que recalcula en vivo el lead time proyectado por Little ("si bajas el WIP a 10, entregarías en ~12 días en vez de 17").

**Panel admin** (visible solo si `role == "admin"`): editar límites WIP por columna y el texto de políticas, con `st.number_input` y `st.text_area`.

### 7. Estrategia de testing E2E

**Pytest de dominio** (`tests/test_flow_metrics.py`) — puro, sin DB, la parte donde el perfil QA del fundador brilla:

- `test_little_law_consistency`: con transiciones sintéticas donde WIP y throughput son constantes, `little_lead_time_estimado ≈ lead_time_promedio` (tolerancia 10%).
- `test_percentil_85_con_cola_larga`: dataset del ejemplo de la sección 2, asserts exactos de P50=6 y P85=15.
- `test_wip_por_persona_vs_por_tablero`: mismo dataset, ambos scopes, resultados distintos verificados.
- `test_flow_efficiency_tarea_pausada`: tarea con 4 días activos y 14 pausados → 22.2%.
- `test_aging_ignora_completadas` y `test_cfd_bandas_monotonicamente_acumuladas`.
- Casos borde: cero tareas completadas (throughput 0, Little no divide por cero), tareas sin transiciones migradas, timezone-aware vs naive datetimes (bug clásico ya presente en `Task.eisenhower`).

**Playwright para Python** (`tests/e2e/test_kanban_flow.py`), contra el Docker Compose completo (db+api+ui):

1. **Flujo feliz de movimiento**: login → tablero → mover tarjeta de `No Iniciado` a `En Proceso` → assert de que la tarjeta aparece en la nueva columna y el contador `n/10` incrementa.
2. **Bloqueo suave por WIP**: seed con 10 tareas en `En Proceso` → intentar mover la 11ª → assert del `st.warning` con el texto del límite → click en "Mover de todas formas" → assert de que se movió y (vía API) de que existe la fila en `wip_violations`.
3. **Aging badge**: seed con una tarea cuya transición a `En Proceso` es de hace 20 días → assert de que el badge "⏱" es visible en esa tarjeta y no en las recientes.
4. **Métricas reaccionan al flujo**: completar 3 tareas vía UI → ir a pestaña Flujo → assert de que throughput y el CFD reflejan los nuevos datos (tolerancia: Streamlit rerun, usar `expect(...).to_contain_text` con timeout).
5. **Permisos**: usuario `member` no ve el panel de edición de límites; `admin` sí, edita el límite de 10→8 y el encabezado de columna se actualiza.

Nota técnica Playwright+Streamlit: usar `data-testid` no es posible directamente; anclar selectores en `st.container(border=True)` + texto, y esperar el estado "Running..." del spinner de Streamlit antes de los asserts (helper `wait_for_streamlit_idle(page)` reutilizable en todos los E2E del proyecto).

### 8. Integraciones externas

| Integración | Para qué | Prioridad |
|---|---|---|
| **GitHub / GitLab (webhooks + REST)** | Mover tarjetas automáticamente: PR abierto → `En Proceso`, PR merged → `Completado`. Elimina la queja #1 de todo tablero: "está desactualizado". Además, cada transición automática alimenta `task_state_transitions` con timestamps honestos (no cuando alguien se acordó de mover la tarjeta). | Alta — es la integración que hace las métricas creíbles |
| **Slack (Incoming Webhooks / Bot API)** | Alertas de flujo: "⚠️ En Proceso lleva 3 días al límite WIP", "⏱ Tarea #42 lleva 12 días estancada". Kanban vive de la respuesta rápida a señales; si la señal solo vive en Cenit, se ve tarde. Digest semanal de métricas al canal del equipo. | Alta — en LatAm el equipo vive en Slack/WhatsApp; Slack primero por API |
| **Google Calendar** | Solo lectura: mostrar capacidad real (vacaciones, feriados colombianos/mexicanos) para contextualizar caídas de throughput. | Media |
| **CSV/Excel export** | Los gerentes en LatAm siguen reportando en Excel. Export de flow metrics = adopción por el jefe del jefe. | Media, esfuerzo trivial |

No se necesita Typeform ni herramientas de encuesta para Kanban (eso pertenece a SPACE/Design Thinking).

### 9. Conflictos o solapamientos

| Metodología | Tipo de conflicto | Resolución en Cenit |
|---|---|---|
| **Scrum** | El clásico: sprint (lote de tiempo, push) vs. flujo continuo (pull). Compiten por la vista central y por la métrica reina (velocity vs. throughput). | No forzar la elección: ofrecer "Scrumban" — tablero Kanban con WIP limits dentro de un contenedor de sprint opcional. Si el equipo activa sprints, el tablero se filtra por sprint; las métricas de flujo se calculan igual. La dupla del piloto decide con datos cuál cadencia le sirve. |
| **Lean** | Solapamiento casi total, no conflicto: Kanban ES la herramienta operativa de Lean (pull, waste, kaizen). | Kanban implementa; Lean da el vocabulario. La sección Lean del producto no necesita UI propia de flujo — referencia las métricas de Kanban. Riesgo: duplicar "waste" y "tareas estancadas" como conceptos separados; unificar en aging. |
| **DORA** | Compiten por "lead time": DORA lo mide de commit a deploy; Kanban de solicitud a entrega. Mismo nombre, definiciones distintas → confusión garantizada en la UI. | Nombrar explícitamente: "Lead Time (flujo)" vs. "Lead Time for Changes (DORA)". Glosario compartido en el producto. |
| **Eisenhower (core actual de Cenit)** | Eisenhower prioriza qué entra; Kanban regula cuánto entra. Compiten por la atención del usuario en el momento de decidir qué hacer. | Sinergia deliberada: el replenishment del tablero (qué tarjeta pasa de backlog a `En Proceso` cuando se libera un slot WIP) se ordena por cuadrante Eisenhower. Q1 primero. Es el diferencial único de Cenit — nadie más une ambas. |
| **KPIs / OKRs** | Riesgo de que throughput se convierta en KPI-target ("suban el throughput a 8/semana") — Goodhart: la gente partirá tareas en pedacitos para inflar el conteo. | Las métricas de flujo se presentan como diagnóstico del sistema, nunca como target individual. No permitir throughput por persona en dashboards de gerencia (sí agregado por equipo). |
| **SAFe / PMBOK / Waterfall** | Compiten por el modelo mental del gerente tradicional que quiere Gantt y fases. | Fuera del scope del piloto; si un cliente enterprise lo pide, el CFD es el puente ("esto es su avance por fases, pero honesto"). |
| **XP, SPACE, Design Thinking** | Sin conflicto de datos ni de UI relevante; XP convive (Kanban no dicta prácticas de ingeniería). | N/A. |

### 10. Antipatrones conocidos

- **Trello: el tablero sin método.** Trello digitalizó la *visualización* (práctica 1) e ignoró las otras cinco. Sin WIP limits nativos (solo vía power-ups de pago de terceros), sin métricas de flujo, sin políticas. Resultado: millones de "tableros cementerio" con 200 tarjetas que nadie mira. Lección para Cenit: el tablero es commodity; el método es el producto.
- **Jira: WIP limits cosméticos.** Jira sí tiene límites de columna… que solo pintan el encabezado de amarillo. No hay fricción, ni sugerencia, ni registro de la excepción. Nadie los nota y nadie los respeta. Además, su Control Chart es tan confuso (¿qué es cada punto?, ¿por qué la escala logarítmica por defecto?) que los equipos no lo usan. Lección: la violación de WIP necesita un momento de conversación (el 409 con sugerencia de Cenit), y las métricas necesitan una frase interpretativa junto al gráfico, no solo el gráfico.
- **Jira: columnas ≠ flujo de valor.** Jira permite mapear estados de workflow arbitrarios a columnas, y los admins crean workflows de 14 estados que nadie entiende. El lead time se vuelve incalculable porque nadie sabe qué estados "cuentan". Lección: Cenit mantiene 4 estados fijos con `is_active_state` explícito — la simplicidad es una feature, resistir la tentación de columnas custom hasta que un cliente pagante lo exija.
- **Asana: estados como metadato invisible.** Asana trató por años el estado como un campo más entre veinte, no como la posición física de la tarjeta. El "board view" llegó tarde y desconectado de reglas de flujo. Se pierde la propiedad esencial del kanban físico: *la posición ES la información*.
- **Todos: lead time desde el timestamp equivocado.** Medir desde `created_at` cuando el backlog acumula tarjetas durante meses produce lead times de 200 días que nadie cree, y la métrica muere por descrédito. Lección: Cenit debe medir cycle time desde la primera transición a `En Proceso` (por eso `task_state_transitions` es innegociable) y dejar el lead time completo como métrica secundaria con su definición visible.
- **Todos: promedios en vez de percentiles.** Prometer con el promedio de una distribución de cola larga garantiza incumplir el 30-40% de las veces. P85 o nada.

### 11. Caso real

**Microsoft XIT (2004-2005), el caso fundacional documentado por David Anderson**: un equipo de mantenimiento de aplicaciones internas con el peor cumplimiento de SLA de su división (lead time promedio de 155 días, moral por el suelo). Anderson y Dragos Dumitriu no cambiaron a las personas ni añadieron proceso: limitaron el WIP, eliminaron las estimaciones por tarea (que consumían ~33% de la capacidad y no mejoraban las promesas) y priorizaron con una cadencia simple de replenishment. En 9 meses: lead time de 155 → 22 días (−86%) y productividad +155%, con el mismo equipo. Es el experimento controlado más citado de que el problema suele ser el sistema (exceso de WIP y costo de transacción), no la gente.

Como herramienta, el referente moderno es **Linear**: no implementa Kanban ortodoxo, pero entendió la lección de flujo mejor que nadie — estados pocos y opinados (no configurables al infinito), cycle time visible sin configuración, movimiento de tarjetas automatizado desde Git (branch → In Progress, merge → Done), y cero fricción para mover trabajo. Qué aprender de su enfoque para Cenit: (1) *opinionated defaults* — Cenit debe traer WIP limits sugeridos de fábrica (2/persona) en vez de pedir configuración; (2) la automatización desde Git es lo que mantiene el tablero vivo; (3) la métrica se muestra donde se trabaja (badge de aging en la tarjeta), no escondida en una sección de reportes que nadie visita.

### 12. Costo de implementación

**Medio. Estimación: 3 sprints de 2 semanas para 1-2 desarrolladores** (asumiendo el tablero visual básico ya existente):

| Sprint | Entregable | Detalle |
|---|---|---|
| **Sprint 1** | Fundación de datos | Migración SQL (4 tablas), backfill sintético de transiciones desde fechas existentes, hook en `crud.py` para insertar transición en cada cambio de estado, endpoint `PATCH /move` con validación WIP y 409, pytest de dominio de `verificar_wip`. ~70% backend. |
| **Sprint 2** | Métricas y UI de flujo | `domain/flow_metrics.py` completo con pytest, endpoints `/api/analytics/flow`, `/aging`, `/cfd`, cron de snapshots, cabecera de métricas y badges de aging en el tablero, pestaña "Flujo" con CFD e histograma. |
| **Sprint 3** | Método y pulido | Panel admin de límites/políticas, flujo de violación con `force` y registro, simulador de Little, suite Playwright E2E (5 flujos), export CSV, documentación de glosario en la UI. |

Riesgo de cronograma: la pestaña "Flujo" con Plotly puede comerse días en detalles visuales — timeboxear. La integración GitHub (sección 8) NO está incluida: es un sprint adicional propio y debe esperar validación del piloto.

Costo recurrente bajo: las tablas de transiciones crecen linealmente (~1-3 filas por tarea por semana en un equipo de 5 — irrelevante para PostgreSQL durante años).

### 13. Cuándo NO construir esto todavía

Matiz importante: el **tablero** ya existe y es correcto para la etapa actual. Lo que esta sección propone — transiciones, WIP limits, métricas de flujo — tiene prerrequisitos de datos y de comportamiento:

- **Menos de ~2-3 equipos piloto usando el tablero a diario durante 4+ semanas.** Las métricas de flujo con 10 tareas completadas son ruido estadístico; un P85 calculado sobre 8 muestras oscilará salvajemente y desacreditará el producto. Señal de sobre-ingeniería: construir el CFD antes de tener 30 días de datos reales de un cliente que no seas tú mismo.
- **Si el piloto aún no mueve tarjetas consistentemente.** Si los usuarios actualizan el estado una vez por semana en lote, `task_state_transitions` registrará basura y todo lo construido encima mentirá. Primero resolver el hábito (o la automatización vía Git) — después medir.
- **El panel de configuración de columnas es prematuro hasta tener 3+ clientes pagantes** que pidan límites distintos. Para el piloto, límites hardcodeados con valores por defecto opinados (2/persona) entregan el 90% del valor con 10% del esfuerzo.
- **Las `wip_violations` y el scope `person` vs `board` pueden esperar al sprint 3 o más allá** — la validación simple por tablero cubre la conversación de venta.
- **Nunca antes que**: estabilidad del CRUD actual, auth confiable y el flujo Eisenhower→Kanban (replenishment priorizado), que es el diferencial de Cenit y cuesta menos que todo lo anterior.

Regla práctica para el fundador: construir el Sprint 1 (transiciones + WIP con límite fijo) ya — es barato y los datos históricos no se pueden recuperar retroactivamente (cada semana sin registrar transiciones es una semana de métricas perdidas para siempre). Diferir Sprints 2-3 hasta que exista un piloto activo mirando el tablero cada mañana.
