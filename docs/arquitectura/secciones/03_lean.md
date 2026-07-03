# (Sección generada por el panel de expertos — Arquitectura, Producto, QA y GTM)

## 03. Lean

### 1. Principio central y origen

Lean nace en la manufactura japonesa de posguerra, concretamente en el **Toyota Production System (TPS)** desarrollado por Taiichi Ohno y Shigeo Shingo entre las décadas de 1950 y 1970. El término "Lean" lo acuñan John Krafcik (1988) y luego Womack y Jones en *The Machine That Changed the World* (1990). Su traslado al software lo formalizan Mary y Tom Poppendieck en *Lean Software Development: An Agile Toolkit* (2003), que traduce los principios de fábrica a los siete principios del software lean: eliminar desperdicio, amplificar el aprendizaje, decidir lo más tarde posible, entregar lo más rápido posible, empoderar al equipo, construir integridad y optimizar el todo.

El principio central es simple de enunciar y difícil de practicar: **maximizar el valor entregado al cliente eliminando sistemáticamente el desperdicio (muda) del flujo de trabajo**. Desperdicio es todo aquello que consume recursos sin agregar valor percibido por el cliente. En software, los siete desperdicios clásicos se mapean así:

| Desperdicio TPS | Equivalente en software | Cómo se ve en Cenit hoy |
|---|---|---|
| Sobreproducción | Features que nadie usa | Tareas completadas de proyectos sin cliente activo |
| Inventario | Trabajo parcialmente hecho (WIP) | Tareas "En Proceso" o "Pausado" durante semanas |
| Sobre-procesamiento | Burocracia, re-aprobaciones | Comentarios interminables sin decisión |
| Transporte | Handoffs entre personas/áreas | Tarea que rebota entre `responsable`s |
| Movimiento | Cambio de contexto (task switching) | Un responsable con 12 tareas activas simultáneas |
| Espera | Bloqueos, colas | Tiempo en "Pausado" o esperando revisión |
| Defectos | Bugs, retrabajos | Tareas reabiertas después de "Completado" |

El error de gestión que Lean previene es el más común en equipos pequeños de LatAm que migran de Trello/Jira: **confundir estar ocupado con generar valor**. Un tablero lleno de tarjetas "En Proceso" da sensación de productividad, pero si el 80% del lead time de cada tarea es espera (cola, bloqueo, pausa), el equipo está optimizando utilización de personas en lugar de flujo de valor. Lean invierte la pregunta: no "¿está todo el mundo ocupado?" sino "¿cuánto tarda una unidad de valor en llegar al cliente y cuánto de ese tiempo fue trabajo real?".

Para Cenit esto es estratégico: el modelo `Task` ya captura `fecha_inicio`, `fecha_completado` y `lead_time_days`, pero **no distingue tiempo activo de tiempo de espera**. Esa distinción —flow efficiency— es exactamente el dato que un CTO de un equipo de 15 personas en Bogotá no puede sacar de Trello sin plugins de pago, y es un diferenciador vendible en demos piloto.

### 2. Métricas y fórmulas exactas

Las cuatro métricas Lean núcleo, con su cálculo aplicado a un equipo ficticio de 5 personas (Ana, Beto, Carla, David, Elena) durante un mes:

**a) Lead Time (ya parcialmente en Cenit)**

```
lead_time = fecha_completado - fecha_inicio   (en días)
```

**b) Tiempo activo vs. tiempo de espera (requiere historial de transiciones)**

```
tiempo_activo  = Σ duración de intervalos en estado "En Proceso"
tiempo_espera  = Σ duración en "Pausado" + colas ("No Iniciado" tras fecha_inicio)
```

**c) Flow Efficiency (eficiencia de flujo) — la métrica Lean por excelencia**

```
flow_efficiency = tiempo_activo / lead_time × 100
```

**d) Ley de Little (valida la consistencia del sistema)**

```
WIP_promedio = throughput × lead_time_promedio
⇒ lead_time_promedio = WIP_promedio / throughput
```

**e) Tasa de desperdicio por retrabajo**

```
tasa_retrabajo = tareas_reabiertas / tareas_completadas × 100
```

**Ejemplo numérico paso a paso.** El equipo completó 20 tareas en junio. Tomemos una tarea representativa de Carla:

1. Creada el 2 de junio, `fecha_inicio` 2 de junio, pasa a "En Proceso" el 6 de junio (4 días en cola).
2. Trabaja 3 días, pasa a "Pausado" el 9 de junio esperando respuesta del cliente (5 días pausada).
3. Retoma el 14 de junio, trabaja 2 días, `fecha_completado` 16 de junio.

- Lead time = 16 − 2 = **14 días**.
- Tiempo activo = 3 + 2 = **5 días**.
- Tiempo de espera = 4 (cola) + 5 (pausa) = **9 días**.
- Flow efficiency = 5 / 14 × 100 = **35.7%**.

Un 35% es de hecho bueno; la media de la industria está entre 15% y 40%. Si el promedio del equipo diera 12%, el mensaje accionable es: "el problema no es que la gente trabaje lento, es que las tareas esperan; ataquen los bloqueos".

**Ley de Little sobre el equipo completo:** en junio hubo en promedio 18 tareas en WIP (No Iniciado con fecha_inicio + En Proceso + Pausado) y el throughput fue 20 tareas / 4.3 semanas ≈ 4.65 tareas/semana.

```
lead_time_esperado = 18 / 4.65 ≈ 3.9 semanas ≈ 27 días
```

Si el lead time medido promedia 14 días pero Little predice 27, hay tareas zombis infladas en el WIP que nunca se completan — otra forma de inventario/desperdicio que la métrica delata. Con 5 personas y 18 tareas en WIP, cada persona carga 3.6 tareas simultáneas: el multitasking (desperdicio de "movimiento") es el primer kaizen candidato: bajar a WIP ≤ 2 por persona reduciría el lead time esperado a 10/4.65 ≈ 2.2 semanas sin contratar a nadie.

**Retrabajo:** de las 20 completadas, 3 fueron reabiertas (pasaron de Completado a otro estado). Tasa = 3/20 = **15%**. Objetivo kaizen trimestral: < 8%.

### 3. Modelo de datos

Lo esencial que falta en el esquema actual es el **historial de transiciones de estado** (para descomponer lead time en activo/espera), el **registro de desperdicio/bloqueos** y los **experimentos kaizen (PDCA)**. Todo extiende `tasks` y `users` existentes:

```sql
-- Historial de transiciones: la base de toda métrica Lean.
-- Se puebla desde crud.update_task cada vez que cambia tasks.estado.
CREATE TABLE task_state_transitions (
    id            SERIAL PRIMARY KEY,
    task_id       INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    from_estado   VARCHAR(30),                -- NULL en la creación
    to_estado     VARCHAR(30) NOT NULL,       -- No Iniciado | En Proceso | Pausado | Completado
    changed_by    INTEGER REFERENCES users(id) ON DELETE SET NULL,
    changed_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    duration_prev_seconds BIGINT              -- segundos que la tarea pasó en from_estado
);
CREATE INDEX idx_tst_task ON task_state_transitions(task_id, changed_at);

-- Registro de bloqueos/desperdicio con taxonomía Lean (7 mudas de software).
CREATE TABLE waste_events (
    id            SERIAL PRIMARY KEY,
    task_id       INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    waste_type    VARCHAR(30) NOT NULL CHECK (waste_type IN
                  ('espera','handoff','retrabajo','multitasking',
                   'sobreproceso','defecto','trabajo_parcial')),
    descripcion   TEXT,
    reported_by   INTEGER REFERENCES users(id) ON DELETE SET NULL,
    started_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at   TIMESTAMPTZ,                -- NULL = bloqueo activo
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_waste_open ON waste_events(task_id) WHERE resolved_at IS NULL;

-- Experimentos de mejora continua (ciclo PDCA / kaizen).
CREATE TABLE kaizen_experiments (
    id             SERIAL PRIMARY KEY,
    titulo         VARCHAR(140) NOT NULL,
    hipotesis      TEXT NOT NULL,             -- "Si limitamos WIP a 2, el lead time baja 30%"
    metrica_objetivo VARCHAR(50) NOT NULL,    -- flow_efficiency | lead_time | tasa_retrabajo | wip
    valor_baseline NUMERIC(10,2),
    valor_meta     NUMERIC(10,2),
    valor_resultado NUMERIC(10,2),
    estado         VARCHAR(20) NOT NULL DEFAULT 'plan'
                   CHECK (estado IN ('plan','do','check','act','descartado')),
    owner_id       INTEGER REFERENCES users(id) ON DELETE SET NULL,
    fecha_inicio   TIMESTAMPTZ,
    fecha_revision TIMESTAMPTZ,
    aprendizaje    TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Snapshot diario de WIP para Ley de Little y CFD (job programado o cálculo lazy).
CREATE TABLE wip_snapshots (
    id            SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    entidad       VARCHAR(50),                -- espeja tasks.entidad para filtrar
    estado        VARCHAR(30) NOT NULL,
    task_count    INTEGER NOT NULL,
    UNIQUE (snapshot_date, entidad, estado)
);
```

Decisión de arquitectura deliberada: `task_state_transitions` se alimenta como efecto secundario dentro de `crud.py` (una función `registrar_transicion`) y no con triggers de base de datos, para que funcione idéntico en SQLite (tests) y PostgreSQL (Supabase). `duration_prev_seconds` se denormaliza al escribir para que las agregaciones de flow efficiency sean un `SUM ... GROUP BY` barato en lugar de window functions sobre pares de filas.

### 4. Casos de uso del domain layer

Nuevo servicio `LeanService` en `domain/services.py` (o `domain/lean.py` si crece), operando sobre dicts serializados igual que los servicios existentes, más dataclasses en `domain/entities.py`:

```python
from dataclasses import dataclass
from datetime import date

@dataclass
class FlowReport:
    task_id: int
    lead_time_days: float
    active_days: float
    wait_days: float
    flow_efficiency_pct: float   # active / lead * 100

@dataclass
class TeamFlowSummary:
    periodo: str                 # "2026-06"
    avg_flow_efficiency: float
    avg_lead_time: float
    throughput: int
    wip_promedio: float
    lead_time_little_days: float # WIP / throughput (Ley de Little)
    tareas_zombi: list[int]      # WIP sin transición en >14 días

class LeanService:
    ESTADOS_ACTIVOS = {"En Proceso"}
    ESTADOS_ESPERA = {"Pausado", "No Iniciado"}

    def calcular_flow_efficiency(
        self, task_id: int, transiciones: list[dict]
    ) -> FlowReport:
        # 1. ordenar transiciones por changed_at
        # 2. active = sum(duration_prev_seconds donde from_estado in ESTADOS_ACTIVOS)
        # 3. wait   = sum(duration_prev_seconds donde from_estado in ESTADOS_ESPERA)
        # 4. lead   = active + wait (o fecha_completado - fecha_inicio si existe)
        # 5. efficiency = active / lead * 100 si lead > 0, else 0.0
        ...

    def resumen_flujo_equipo(
        self, tareas: list[dict], transiciones: list[dict],
        snapshots: list[dict], periodo: str,
    ) -> TeamFlowSummary:
        # 1. throughput = count(fecha_completado en periodo)
        # 2. wip_promedio = mean(task_count de snapshots del periodo, estados != Completado)
        # 3. lead_time_little = wip_promedio / (throughput / semanas_periodo) * 7
        # 4. zombis = tareas WIP cuya última transición > 14 días atrás
        ...

    def detectar_desperdicio(
        self, tareas: list[dict], waste_events: list[dict]
    ) -> dict[str, list[dict]]:
        # Agrupa por waste_type; añade detecciones automáticas:
        # - multitasking: responsable con >3 tareas "En Proceso"
        # - trabajo_parcial: "Pausado" > 7 días sin waste_event asociado
        # - retrabajo: transición Completado -> otro estado
        ...

    def tasa_retrabajo(self, transiciones: list[dict], periodo: str) -> float:
        # reabiertas = count(from_estado == "Completado")
        # completadas = count(to_estado == "Completado")
        # return reabiertas / completadas * 100 (0.0 si no hay completadas)
        ...

    def evaluar_kaizen(self, experimento: dict, valor_actual: float) -> dict:
        # Compara valor_actual vs valor_meta y baseline; sugiere transición
        # PDCA: 'check' -> 'act' si meta alcanzada, o 'descartado' + aprendizaje.
        ...
```

Todo es lógica pura sin I/O: recibe listas de dicts y devuelve dataclasses/dicts, testeable con pytest sin base de datos, consistente con `KanbanService` y `AnalyticsService` existentes.

### 5. Diseño de API REST

Endpoints FastAPI en `api/`, consistentes con el estilo `/api/tasks` y `/api/analytics/...` existente:

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/api/tasks/{task_id}/transitions` | Historial de estados de una tarea |
| GET | `/api/analytics/lean/flow-efficiency?periodo=2026-06&entidad=` | Resumen de flujo del equipo |
| GET | `/api/analytics/lean/waste?periodo=2026-06` | Pareto de desperdicio por tipo |
| POST | `/api/tasks/{task_id}/waste` | Reportar bloqueo/desperdicio |
| PATCH | `/api/waste/{id}/resolve` | Resolver un bloqueo |
| GET / POST | `/api/kaizen` | Listar / crear experimentos |
| PATCH | `/api/kaizen/{id}` | Avanzar ciclo PDCA |

Ejemplo — `GET /api/analytics/lean/flow-efficiency?periodo=2026-06`:

```json
{
  "periodo": "2026-06",
  "avg_flow_efficiency": 35.7,
  "avg_lead_time": 14.0,
  "throughput": 20,
  "wip_promedio": 18.0,
  "lead_time_little_days": 27.1,
  "tareas_zombi": [104, 87, 92],
  "por_responsable": [
    {"responsable": "Carla", "flow_efficiency": 41.2, "wip_actual": 2},
    {"responsable": "Beto", "flow_efficiency": 19.5, "wip_actual": 5}
  ]
}
```

Ejemplo — `POST /api/tasks/104/waste`:

```json
{
  "waste_type": "espera",
  "descripcion": "Bloqueada esperando credenciales del cliente Uniandes"
}
```

Ejemplo — `POST /api/kaizen`:

```json
{
  "titulo": "Limitar WIP a 2 tareas por persona",
  "hipotesis": "Si nadie tiene más de 2 tareas En Proceso, el lead time promedio baja de 14 a 10 días en 4 semanas",
  "metrica_objetivo": "lead_time",
  "valor_baseline": 14.0,
  "valor_meta": 10.0
}
```

### 6. Vista o componente de UI

Nueva vista `ui/views/lean_flujo.py` ("Flujo"), registrada en la navegación de `ui/app.py` junto a Kanban y Analytics. Wireframe textual, de arriba hacia abajo:

1. **Fila de KPIs (4 `st.metric` en `st.columns(4)`):** Flow Efficiency del mes (con delta vs mes anterior), Lead Time promedio, Throughput, WIP actual. Si Little predice un lead time >1.5× el medido, un `st.warning` señala tareas zombi con enlace-filtro.
2. **Gráfico de flujo acumulado (CFD)** con Plotly (`st.plotly_chart`): áreas apiladas por estado a lo largo de 90 días desde `wip_snapshots`. Es la visualización Lean canónica: bandas que se ensanchan = cuellos de botella visibles de un vistazo.
3. **Pareto de desperdicio:** barras horizontales por `waste_type` (horas acumuladas), con expander por tipo listando las tareas afectadas. Selector de periodo (`st.selectbox` mes).
4. **Panel de bloqueos activos:** tabla `st.dataframe` de `waste_events` sin resolver, ordenada por antigüedad, con botón "Resolver" por fila (patrón ya usado en `equipo.py`). Un bloqueo >3 días se pinta rojo.
5. **Tablero Kaizen (PDCA):** cuatro columnas Plan / Do / Check / Act con tarjetas de experimentos (título, métrica, baseline→meta, sparkline del valor actual). Botón `st.button` para avanzar de fase; formulario `st.form` en un `st.expander` para crear experimento nuevo.

Interacción clave de bajo costo: en el Kanban existente, al mover una tarea a "Pausado", un `st.popover` pregunta el motivo (waste_type) — así el registro de desperdicio se captura en el flujo natural sin ceremonia extra. Esa fricción mínima es lo que Trello nunca resolvió.

### 7. Estrategia de testing E2E

**Unitarios pytest (`tests/test_lean_service.py`)** sobre `LeanService` puro:

- `calcular_flow_efficiency`: caso feliz (activo 5d, espera 9d → 35.7%), tarea sin transiciones (0.0, sin división por cero), tarea solo activa (100%), transiciones desordenadas.
- Ley de Little: throughput 0 no revienta; WIP 0 → lead esperado 0.
- `detectar_desperdicio`: responsable con 4 tareas activas dispara `multitasking`; "Pausado" 8 días dispara `trabajo_parcial`; reapertura dispara `retrabajo`.
- `tasa_retrabajo`: 3 reaperturas / 20 completadas = 15.0; 0 completadas → 0.0.
- `evaluar_kaizen`: meta alcanzada sugiere `act`, no alcanzada tras `fecha_revision` sugiere `descartado`.
- Test de integración crud: actualizar `tasks.estado` vía API inserta fila en `task_state_transitions` con `duration_prev_seconds` correcto (con `freezegun` para controlar el reloj).

**E2E Playwright para Python (`tests/e2e/test_lean_flow.py`)** contra el stack Docker Compose completo:

1. **Flujo de vida de transiciones:** login → crear tarea → moverla No Iniciado → En Proceso → Pausado (capturando motivo en el popover) → Completado; abrir vista Flujo y verificar que el lead time y la flow efficiency renderizados coinciden con lo esperado (`expect(page.get_by_test_id("flow-efficiency")).to_contain_text(...)`).
2. **Bloqueo activo:** reportar waste en una tarea, verificar que aparece en el panel de bloqueos; resolverlo y verificar que desaparece y suma al Pareto.
3. **Ciclo PDCA completo:** crear experimento kaizen, avanzarlo Plan→Do→Check→Act, verificar persistencia tras recargar página (Streamlit rerun es traicionero con el estado — este test caza regresiones de `st.session_state`).
4. **Consistencia multi-vista:** completar tarea en Kanban y verificar que Analytics y Flujo muestran el mismo throughput (test de integridad entre vistas, barato y de alto valor).

Nota QA: los reruns de Streamlit hacen frágiles los selectores CSS; estandarizar `key=` en widgets y localizar por texto/rol. Sembrar datos vía API REST (no UI) en los fixtures para que los E2E sean rápidos y determinísticos.

### 8. Integraciones externas

- **GitHub/GitLab API (la más valiosa):** enlazar PRs a tareas permite medir espera real en "code review" — típicamente el mayor desperdicio oculto de un equipo dev. Un webhook `pull_request` que registre `waste_events` de tipo `espera` cuando un PR lleva >24h sin review convierte a Cenit en detector automático de muda.
- **Slack API (webhooks entrantes):** alertas de bloqueos >3 días y digest semanal de flow efficiency al canal del equipo. Para el GTM en LatAm es la integración que los pilotos piden primero; el valor Lean es acortar el desperdicio de "espera" haciendo visible el bloqueo donde el equipo ya conversa.
- **Google Calendar (opcional, fase posterior):** estimar capacidad real descontando reuniones, refinando el denominador de tiempo activo. Costo/beneficio dudoso en etapa piloto; documentado como "no ahora".
- **No se necesita** Typeform ni herramientas de encuesta: el desperdicio se captura en el flujo de trabajo, no con formularios — instrumentar, no preguntar.

### 9. Conflictos o solapamientos

| Metodología | Solapamiento | Resolución en Cenit |
|---|---|---|
| **Kanban** | El mayor: Kanban ES la aplicación de Lean al trabajo del conocimiento; comparten WIP, lead time, CFD | No duplicar: el tablero vive en la vista Kanban (con límites WIP); la vista Flujo es la capa analítica/kaizen. Una sola fuente: `task_state_transitions` |
| **DORA** | Lead time DORA (commit→producción) vs Lean (inicio→completado) | Nombrarlas distinto en UI ("Lead time de tarea" vs "Lead time de cambio") y glosario compartido; comparten pipeline de datos de GitHub |
| **Scrum** | Velocity/sprint compite por atención con flow efficiency/throughput | Coexisten: throughput continuo no requiere sprints; si el equipo usa Scrum, la retro consume el Pareto de desperdicio como insumo |
| **KPIs / SPACE** | Los KPIs de eficiencia y la "E" de SPACE (Efficiency & Flow) son literalmente estas métricas | Las métricas Lean se exponen como fuente para el módulo KPIs, no se recalculan aparte |
| **XP** | Ambos atacan defectos (retrabajo); XP con prácticas, Lean con medición | La tasa de retrabajo Lean es el termómetro; XP el tratamiento |
| **OKRs** | Los experimentos kaizen se parecen a key results trimestrales | Kaizen = mejoras de proceso del equipo; OKR = resultados de negocio. Un KR puede apuntar a una métrica Lean |
| **SAFe / PMBOK / Waterfall** | Filosóficamente opuestos (batch grande, planificación pesada = desperdicio según Lean) | Sin conflicto de UI en Cenit: no son el segmento objetivo (equipos de 10-50) |
| **Design Thinking** | Comparte espíritu de "aprender rápido" con kaizen | Sin colisión de datos ni de vistas |

Riesgo real de producto: sobrecargar la navegación con 12 vistas metodológicas. Decisión recomendada: Lean no es una "metodología" más en el menú sino **la capa de métricas de flujo que alimenta a Kanban, Analytics y KPIs**.

### 10. Antipatrones conocidos

- **Jira:** enterró las métricas de flujo bajo capas de configuración (Control Chart casi indescifrable, sin flow efficiency nativa) y convirtió el "proceso" en workflows de 12 estados con aprobaciones — sobre-procesamiento puro, lo contrario de Lean. Lección: la métrica debe ser visible por defecto, no un reporte que hay que saber buscar, y el workflow debe tener los 4 estados que ya tiene Cenit.
- **Trello:** el extremo opuesto — cero historial de transiciones nativo, sin límites WIP reales (solo con power-ups de pago), sin lead time. Digitalizó la pizarra pero no el sistema de mejora: un tablero Trello de 2 años es un cementerio de tarjetas (inventario/desperdicio invisible). Lección: capturar transiciones desde el día uno; el dato que no guardas hoy es la métrica que no puedes vender mañana.
- **Asana:** métricas orientadas a "% de tareas completadas a tiempo" — mide cumplimiento de fechas, no flujo, incentivando inflar estimaciones (desperdicio de sobreproducción de buffer). Lección: medir el sistema (flujo), no a las personas (cumplimiento), o el dato se corrompe por el efecto Goodhart.
- **Antipatrón transversal:** los tres registran quién bloqueó pero no *por qué* ni *cuánto costó* el bloqueo. Sin taxonomía de desperdicio no hay kaizen posible, solo culpa. `waste_events` con tipología existe exactamente para eso.

### 11. Caso real

**Toyota es el origen, pero el caso aplicable a Cenit es Spotify en sus años tempranos y, como herramienta, ActionableAgile (hoy parte de 55 Degrees, integrada a Jira) junto con el enfoque de Linear.** El más instructivo para un SaaS pequeño es **Linear**: no vende "Lean" como etiqueta, pero implementó sus principios — límites de WIP suaves, ciclos cortos con "cooldowns", detección automática de issues estancados (su feature *Triage* y las alertas de issues sin actividad son, en vocabulario Lean, detección de trabajo parcial y espera), e *Insights* con lead/cycle time visible sin configuración. Qué aprender de su enfoque: (1) las métricas aparecen donde el usuario ya trabaja, no en un módulo aparte que nadie abre; (2) opiniones fuertes con defaults — Linear no deja configurar 12 estados, igual que Cenit no debería; (3) el lenguaje de producto evita jerga metodológica: nadie ve la palabra "muda", ven "esta tarea lleva 8 días sin movimiento". Para el GTM de Cenit en LatAm la traducción es directa: en la demo al CTO no se vende "Lean", se muestra el Pareto de bloqueos de SU equipo tras 2 semanas de piloto — ese momento "ajá" es el que cierra la venta.

### 12. Costo de implementación

**Medio: 3 sprints de 2 semanas para 1-2 desarrolladores.**

| Sprint | Alcance | Entregable |
|---|---|---|
| 1 | `task_state_transitions` + hook en `crud.py` + backfill aproximado desde `created_at`/`fecha_completado` + `LeanService.calcular_flow_efficiency` con pytest | El dato empieza a acumularse (crítico: cuanto antes, más historia para las demos) |
| 2 | Endpoints `/api/analytics/lean/*`, `waste_events` + popover de motivo en Kanban, vista Flujo con KPIs y CFD | Vista demostrable a pilotos |
| 3 | Tablero kaizen + `wip_snapshots` + Pareto de desperdicio + E2E Playwright + alerta Slack básica | Ciclo de mejora completo |

El sprint 1 es el de mayor ROI y menor riesgo: es solo persistencia y lógica pura. El 3 es recortable (kaizen puede esperar). Riesgo de estimación: el backfill de datos históricos sin transiciones reales da eficiencias ficticias — marcar métricas pre-implementación como "estimadas" en la UI.

### 13. Cuándo NO construir esto todavía

Señales de que sería sobre-ingeniería en la etapa actual de Cenit:

- **Menos de 3 equipos piloto activos usando el Kanban a diario.** Flow efficiency con 15 tareas/mes de datos es ruido estadístico; primero retención del tablero básico, luego analítica de flujo.
- **Si el propio equipo de Cenit (1-2 personas) es el único usuario:** con 2 personas no hay handoffs ni colas significativas; las métricas Lean brillan a partir de ~5 personas con trabajo interdependiente.
- **El tablero kaizen (sprint 3) es prematuro hasta que algún piloto pregunte "¿y ahora qué hago con estos datos?"** — construir el ciclo de mejora antes de que exista el hábito de mirar la métrica es sobreproducción (irónicamente, desperdicio Lean).
- **La excepción que SÍ vale la pena ya:** la tabla `task_state_transitions` y su hook en `crud.py` (3-4 días de trabajo). Es infraestructura de datos, no feature: si no se captura hoy, cuando los pilotos crezcan no habrá historia que mostrar. Guardar el dato ≠ construir la vista.

Regla de decisión práctica: construir sprint 1 ahora, sprint 2 cuando haya 3+ pilotos activos, sprint 3 cuando un cliente lo pida con nombre y apellido.
