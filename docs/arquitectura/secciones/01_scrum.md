# (Sección generada por el panel de expertos — Arquitectura, Producto, QA y GTM)

## 01. SCRUM

### 1. Principio central y origen

Scrum resuelve un problema muy concreto: la imposibilidad de planificar con precisión trabajo complejo y cambiante a largo plazo. Su respuesta es el **empirismo iterativo**: en lugar de un plan detallado de 12 meses, el equipo se compromete a entregar un incremento funcional cada ciclo corto (el *sprint*, típicamente 1-4 semanas), inspecciona el resultado y adapta el plan siguiente con datos reales.

El origen es doble. La semilla intelectual es el paper de Takeuchi y Nonaka, *"The New New Product Development Game"* (Harvard Business Review, 1986), que observó en fabricantes japoneses (Honda, Canon, Fuji-Xerox) que los equipos multidisciplinarios que avanzaban "como en un scrum de rugby" —todos juntos, pasando el balón— superaban al modelo secuencial tipo relevos. Jeff Sutherland y Ken Schwaber formalizaron el marco para software en 1995 (OOPSLA), y desde 2010 lo mantienen en la *Scrum Guide* (última revisión relevante: 2020, que simplificó roles y eliminó jerga prescriptiva).

**Errores de gestión que previene:**

- **El síndrome del plan perfecto (Big Design Up Front):** presupuestos y fechas comprometidos sobre estimaciones hechas cuando menos se sabe del problema. Scrum obliga a re-estimar cada 2 semanas con evidencia.
- **Invisibilidad del progreso:** en gestión tradicional el "90% completado" puede durar meses. El incremento entregable por sprint hace el progreso binario y verificable — algo que resuena directamente con la mentalidad QA: *no está hecho hasta que pasa la Definition of Done*.
- **Sobrecarga y cambio de prioridades diario:** el *sprint backlog* congelado protege al equipo del "esto es para ya" constante — el dolor número uno que reportan los equipos LatAm de 10-50 personas que hoy sufren en Jira con backlogs de 800 issues sin dueño.
- **Falta de dueño de prioridades:** el rol de Product Owner concentra la responsabilidad de ordenar el backlog, evitando el comité difuso donde todo es prioridad "Urgente" (un antipatrón que Cenit ya observa en su propio campo `prioridad`, donde tiende a inflarse hacia Urgente/Alta).

Para Cenit el ángulo estratégico es claro: los equipos objetivo *ya dicen que hacen Scrum* (es el vocabulario dominante en LatAm — las ofertas de trabajo piden "experiencia en metodologías ágiles/Scrum"), pero lo hacen mal o a medias. Cenit no debe venderse como "herramienta Scrum" (ahí Jira es incumbente imbatible), sino ofrecer un **Scrum ligero y honesto**: sprints, velocity y burndown sin la burocracia de configuración de Jira.

### 2. Métricas y fórmulas exactas

Equipo ficticio: **Equipo Cóndor**, 5 personas (Ana, Bruno, Carla, David, Elena), sprints de 2 semanas (10 días hábiles).

| Métrica | Fórmula | Unidad |
|---|---|---|
| Velocity del sprint | `V_s = Σ story_points de historias COMPLETADAS en el sprint` | pts |
| Velocity promedio | `V̄ = (Σ V_s últimos n sprints) / n` (n=3 recomendado) | pts |
| Capacidad del sprint | `C = Σ (días_disponibles_persona × factor_foco)` | días-persona |
| Burndown ideal (día d) | `Ideal(d) = P_total × (1 − d/D)` con D = días del sprint | pts |
| Desviación burndown | `Δ(d) = Real(d) − Ideal(d)` (positivo = atraso) | pts |
| Sprint Goal Success Rate | `SGSR = sprints_con_meta_cumplida / sprints_totales × 100` | % |
| Say/Do Ratio (predictibilidad) | `SD = pts_completados / pts_comprometidos × 100` | % |
| Scope churn | `Churn = pts_agregados_mid_sprint / pts_comprometidos × 100` | % |
| Carryover | `CO = pts_no_terminados / pts_comprometidos × 100` | % |
| Focus factor | `FF = V_s / C` | pts/día-persona |

**Cálculo paso a paso — Sprint 7 del Equipo Cóndor:**

1. **Compromiso:** en planning toman 8 historias: 5+3+3+2+2+8+1+3 = **27 pts comprometidos**.
2. **Capacidad:** 5 personas × 10 días = 50 días; Elena toma 2 días de vacaciones → 48; factor de foco 0.7 (reuniones, soporte) → `C = 48 × 0.7 = 33.6 días-persona`.
3. **Resultado al día 10:** completan las historias de 5, 3, 3, 2, 8 y 1 = **22 pts completados**. La de 2 pts queda "En Proceso" y la de 3 pts ni se inició.
4. **Velocity:** `V_7 = 22 pts` (las incompletas valen **0** — regla estricta, no se cuenta parcial).
5. **Say/Do:** `22 / 27 × 100 = 81.5 %` — sano; el umbral de alerta típico es < 80 % sostenido.
6. **Carryover:** `(2+3) / 27 × 100 = 18.5 %`.
7. **Mid-sprint entró un bug urgente de 2 pts** (completado, incluido en los 22): `Churn = 2 / 27 × 100 = 7.4 %` — aceptable; > 20 % indica que el PO no protege el sprint.
8. **Velocity promedio** con V_5=19, V_6=24, V_7=22: `V̄ = (19+24+22)/3 = 21.7 pts` → en planning del sprint 8, comprometer 20-23 pts, no 30.
9. **Burndown día 5:** `Ideal(5) = 27 × (1 − 5/10) = 13.5 pts` restantes. Real: quedan 18 pts → `Δ = +4.5 pts` → alerta amarilla en UI de Cenit.
10. **Focus factor:** `FF = 22 / 33.6 = 0.65 pts/día-persona` — insumo para la capacidad del sprint 8: `33.6 × 0.65 ≈ 22 pts`, consistente con V̄.

Regla de producto (voz Head of Product): Cenit debe mostrar velocity **solo como rango** (`V̄ ± desviación estándar`, aquí 21.7 ± 2.5) y nunca como número comparable entre equipos — el abuso de velocity como KPI de gerencia es la forma más rápida de que el equipo infle puntos y la métrica muera.

### 3. Modelo de datos

Extiende `users` y `tasks` existentes. La decisión clave (voz Arquitecto): **no** poner `sprint_id` directo en `tasks` sino usar tabla puente `sprint_tasks` — una tarea puede pasar por varios sprints (carryover) y necesitamos el histórico de compromiso para calcular Say/Do y churn. Los snapshots de burndown se materializan a diario para no reconstruirlos desde el event log.

```sql
-- Requiere: users(id), tasks(id) ya existentes (api/models.py)

CREATE TABLE sprints (
    id              SERIAL PRIMARY KEY,
    nombre          VARCHAR(80)  NOT NULL,               -- "Sprint 7"
    objetivo        TEXT,                                 -- Sprint Goal
    entidad         VARCHAR(50)  NOT NULL,                -- mismo eje multi-equipo que tasks.entidad
    fecha_inicio    DATE         NOT NULL,
    fecha_fin       DATE         NOT NULL,
    estado          VARCHAR(20)  NOT NULL DEFAULT 'planificado',
                    -- planificado | activo | cerrado | cancelado
    capacidad_dias  NUMERIC(6,1),                         -- C calculada en planning
    factor_foco     NUMERIC(3,2) DEFAULT 0.70,
    goal_cumplido   BOOLEAN,                              -- se fija en la review
    created_by      INTEGER REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT now(),
    CHECK (fecha_fin > fecha_inicio),
    CONSTRAINT uq_sprint_nombre_entidad UNIQUE (entidad, nombre)
);
-- Solo un sprint activo por entidad/equipo:
CREATE UNIQUE INDEX uq_sprint_activo ON sprints(entidad) WHERE estado = 'activo';

-- Extensión mínima de tasks: puntos de historia (propiedad de la tarea, no del sprint)
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS story_points SMALLINT
    CHECK (story_points IN (1,2,3,5,8,13,21));            -- Fibonacci

CREATE TABLE sprint_tasks (
    id             SERIAL PRIMARY KEY,
    sprint_id      INTEGER NOT NULL REFERENCES sprints(id) ON DELETE CASCADE,
    task_id        INTEGER NOT NULL REFERENCES tasks(id)   ON DELETE CASCADE,
    committed      BOOLEAN NOT NULL DEFAULT TRUE,          -- FALSE = entró mid-sprint (churn)
    points_snapshot SMALLINT,                              -- pts al momento del compromiso
    added_at       TIMESTAMPTZ DEFAULT now(),
    removed_at     TIMESTAMPTZ,                            -- descoped
    completed_in_sprint BOOLEAN NOT NULL DEFAULT FALSE,    -- se fija al cerrar el sprint
    CONSTRAINT uq_sprint_task UNIQUE (sprint_id, task_id)
);

-- Snapshot diario para burndown (job nocturno o al cerrar el día)
CREATE TABLE sprint_burndown_snapshots (
    id              SERIAL PRIMARY KEY,
    sprint_id       INTEGER NOT NULL REFERENCES sprints(id) ON DELETE CASCADE,
    fecha           DATE    NOT NULL,
    puntos_restantes NUMERIC(6,1) NOT NULL,
    puntos_totales   NUMERIC(6,1) NOT NULL,               -- puede crecer por churn
    tareas_restantes SMALLINT NOT NULL,
    CONSTRAINT uq_burndown_dia UNIQUE (sprint_id, fecha)
);

-- Retrospectivas: el artefacto que Jira nunca integró bien
CREATE TABLE retro_items (
    id          SERIAL PRIMARY KEY,
    sprint_id   INTEGER NOT NULL REFERENCES sprints(id) ON DELETE CASCADE,
    categoria   VARCHAR(20) NOT NULL CHECK (categoria IN ('bien','mejorar','accion')),
    descripcion TEXT NOT NULL,
    autor_id    INTEGER REFERENCES users(id),
    -- una acción de retro puede convertirse en tarea real → trazabilidad:
    task_id     INTEGER REFERENCES tasks(id),
    resuelto    BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- Impedimentos levantados en la daily (conecta con la vista de riesgos de Cenit)
CREATE TABLE impediments (
    id           SERIAL PRIMARY KEY,
    sprint_id    INTEGER REFERENCES sprints(id) ON DELETE SET NULL,
    task_id      INTEGER REFERENCES tasks(id)   ON DELETE SET NULL,
    descripcion  TEXT NOT NULL,
    reportado_por INTEGER REFERENCES users(id),
    estado       VARCHAR(20) DEFAULT 'abierto',  -- abierto | resuelto
    created_at   TIMESTAMPTZ DEFAULT now(),
    resuelto_at  TIMESTAMPTZ
);
```

Notas de diseño: `points_snapshot` en la tabla puente congela la estimación al momento del compromiso (si el equipo re-estima mid-sprint, el Say/Do se calcula contra el snapshot, no contra el valor vivo). `entidad` en `sprints` reutiliza el eje de segmentación existente de `tasks.entidad` en lugar de inventar una tabla `teams` prematura.

### 4. Casos de uso del domain layer

Nuevo servicio `SprintService` en `domain/services.py` (o `domain/sprint_service.py`), operando sobre dicts como los servicios existentes, más dataclasses de reporte en `domain/entities.py`:

```python
from dataclasses import dataclass
from datetime import date

@dataclass
class VelocityReport:
    sprint_id: int
    puntos_comprometidos: int
    puntos_completados: int
    say_do_ratio: float          # 0-100
    churn_pct: float             # 0-100
    carryover_pct: float         # 0-100
    velocity_promedio_3: float | None

@dataclass
class BurndownPoint:
    fecha: date
    restante_real: float
    restante_ideal: float


class SprintService:

    def planificar_sprint(
        self, sprint: dict, tareas_candidatas: list[dict],
        velocity_promedio: float | None
    ) -> dict:
        """Valida el compromiso de planning.
        # sumar story_points de tareas_candidatas (rechazar tareas sin puntos)
        # si velocity_promedio y suma > velocity_promedio * 1.2:
        #     retornar {"ok": False, "warning": "sobre-compromiso", ...}
        # retornar {"ok": True, "puntos": suma, "tareas": ids}
        """

    def calcular_velocity(
        self, sprint: dict, sprint_tasks: list[dict],
        historial_velocity: list[int]
    ) -> VelocityReport:
        """# comprometidos = sum(points_snapshot where committed)
        # completados  = sum(points_snapshot where completed_in_sprint)
        # churn = sum(points where not committed) / comprometidos * 100
        # carryover = (comprometidos - completados_comprometidos) / comprometidos * 100
        # velocity_promedio_3 = mean(historial_velocity[-3:]) si hay >=1
        """

    def calcular_burndown(
        self, sprint: dict, snapshots: list[dict]
    ) -> list[BurndownPoint]:
        """# D = dias habiles entre fecha_inicio y fecha_fin
        # ideal(d) = puntos_totales_iniciales * (1 - d/D)
        # emparejar cada snapshot real con su ideal por fecha
        """

    def cerrar_sprint(
        self, sprint: dict, sprint_tasks: list[dict], tareas: list[dict]
    ) -> dict:
        """# para cada sprint_task: completed_in_sprint = (tarea.estado == 'Completado'
        #     and tarea.fecha_completado <= sprint.fecha_fin)
        # tareas no completadas -> candidatas a carryover (NO mover automatico:
        #     devolver lista para que el PO decida en la UI)
        # marcar sprint.estado = 'cerrado'; retornar VelocityReport
        """

    def desviacion_burndown_hoy(
        self, burndown: list[BurndownPoint]
    ) -> float:
        """# ultimo punto: real - ideal; >0 atraso, alimenta alerta en Mi Dia"""

    def say_do_historico(self, reports: list[VelocityReport]) -> float:
        """# mean(r.say_do_ratio) — metrica de predictibilidad del equipo"""
```

Regla de arquitectura respetada: el dominio no toca SQLAlchemy ni FastAPI; recibe dicts/listas y devuelve dataclasses puras. Eso mantiene los servicios 100 % testeables con pytest sin base de datos, igual que `KanbanService` y `AnalyticsService` hoy.

### 5. Diseño de API REST

Consistente con el estilo existente (`/api/tasks`, `/api/analytics/...`), routers nuevos en `api/`:

| Método | Ruta | Propósito |
|---|---|---|
| POST | `/api/sprints` | Crear sprint |
| GET | `/api/sprints?entidad=X&estado=activo` | Listar/filtrar |
| PATCH | `/api/sprints/{id}` | Editar objetivo/fechas; cambiar estado |
| POST | `/api/sprints/{id}/tasks` | Comprometer/agregar tareas |
| DELETE | `/api/sprints/{id}/tasks/{task_id}` | Descope (marca `removed_at`) |
| POST | `/api/sprints/{id}/close` | Cierre: calcula velocity, propone carryover |
| GET | `/api/sprints/{id}/burndown` | Serie real vs ideal |
| GET | `/api/analytics/velocity?entidad=X&n=6` | Histórico de velocity y Say/Do |
| POST | `/api/sprints/{id}/retro` | Agregar ítems de retro |
| POST | `/api/impediments` | Reportar impedimento |

```json
// POST /api/sprints
{
  "nombre": "Sprint 8",
  "objetivo": "Cerrar onboarding de piloto Javeriana",
  "entidad": "Desarrollo",
  "fecha_inicio": "2026-07-06",
  "fecha_fin": "2026-07-17",
  "factor_foco": 0.7
}

// POST /api/sprints/8/tasks
{ "task_ids": [341, 342, 350], "committed": true }

// Respuesta GET /api/sprints/8/burndown
{
  "sprint_id": 8,
  "puntos_totales": 27,
  "serie": [
    { "fecha": "2026-07-06", "restante_real": 27.0, "restante_ideal": 27.0 },
    { "fecha": "2026-07-10", "restante_real": 18.0, "restante_ideal": 13.5 }
  ],
  "desviacion_actual": 4.5,
  "alerta": "atraso"
}

// Respuesta POST /api/sprints/8/close
{
  "velocity": 22,
  "say_do_ratio": 81.5,
  "churn_pct": 7.4,
  "carryover_sugerido": [ { "task_id": 342, "story_points": 2 } ]
}
```

Todos los endpoints bajo el mismo JWT existente; `POST /close` restringido a `role in ("admin",)` o al creador del sprint.

### 6. Vista o componente de UI

Nueva vista `ui/views/sprint.py`, registrada en la navegación de `ui/app.py` entre "Kanban" y "Analytics".

**Zona superior (cabecera del sprint activo):** nombre + objetivo del sprint en texto destacado, `st.progress` con días transcurridos, y 4 `st.metric`: puntos comprometidos, completados, Say/Do del sprint anterior, días restantes. Si no hay sprint activo, un empty-state con botón "Planificar sprint" que abre un `st.dialog` (nombre, fechas con `st.date_input`, objetivo, factor de foco).

**Pestañas (`st.tabs`):**

1. **Tablero del sprint** — reutiliza el Kanban existente (`KanbanService.agrupar_por_estado`) pero filtrado a las tareas del sprint. Cada tarjeta muestra su badge de story points; tareas sin puntos muestran "?" en ámbar (empujando a estimar). Un `st.multiselect` de tareas del backlog general permite "traer al sprint" (marca churn automáticamente si el sprint ya está activo, con un `st.warning` explícito: "Esto cuenta como cambio de alcance").
2. **Burndown** — gráfico Plotly de línea: ideal (punteada gris) vs real (color de entidad), banda de alerta cuando `Δ > 15 %` del total. Debajo, tabla plegable de churn/descoped.
3. **Retro** — tres columnas (`st.columns(3)`): "Qué salió bien / Qué mejorar / Acciones", cada una con `st.text_input` + lista de ítems con autor. Botón "Convertir en tarea" en cada acción (crea el task y enlaza `retro_items.task_id`).
4. **Historial** — gráfico de barras de velocity de los últimos 6 sprints con línea de promedio móvil, y tabla de Say/Do y carryover por sprint.

**Botón de cierre:** "Cerrar sprint" abre diálogo con el resumen calculado por `/close`, checkbox "¿Se cumplió el Sprint Goal?", y lista de tareas incompletas con radio por tarea: *mover al siguiente sprint / devolver al backlog*. Nada se mueve sin decisión explícita del usuario.

Además, la vista **Mi Día** existente gana una línea contextual: "Sprint 8 · día 5 de 10 · vas 4.5 pts por detrás del plan".

### 7. Estrategia de testing E2E

**Pytest de dominio (rápidos, sin DB)** — en `tests/test_sprint_service.py`:

- `calcular_velocity`: caso feliz (ejemplo numérico de la sección 2 como fixture: debe dar 22 pts, 81.5 %, 7.4 %); sprint sin tareas (velocity 0, sin división por cero); todas incompletas (Say/Do 0); tarea agregada mid-sprint completada (cuenta en velocity, cuenta en churn, NO en comprometidos).
- `calcular_burndown`: ideal lineal correcto con días hábiles (excluye fin de semana); churn que sube `puntos_totales` a mitad de sprint; snapshot faltante un día (interpolación o hueco, comportamiento definido).
- `cerrar_sprint`: tarea completada *después* de `fecha_fin` no cuenta; idempotencia (cerrar dos veces no duplica); carryover propuesto correcto.
- `planificar_sprint`: warning de sobre-compromiso a > 120 % del promedio; rechazo de tareas sin `story_points`.

**Playwright para Python (E2E sobre Streamlit + API real)** — en `tests/e2e/test_sprint_flow.py`, usando `page.get_by_role`/`get_by_test_id` (Streamlit expone `data-testid` como `stMetric`, `stTab`):

1. **Ciclo de vida completo (el test crítico):** login → crear sprint → comprometer 3 tareas con puntos → verificar métrica "comprometidos" en cabecera → completar una tarea desde el tablero → verificar que el burndown baja → cerrar sprint → assert velocity mostrada == puntos de la tarea completada → assert diálogo de carryover lista las 2 incompletas.
2. **Protección del alcance:** con sprint activo, agregar tarea del backlog → assert aparece el warning de churn y el historial la marca como no comprometida.
3. **Unicidad de sprint activo:** intentar activar un segundo sprint de la misma entidad → assert error visible (esto valida el índice parcial `uq_sprint_activo` de punta a punta).
4. **Permisos:** usuario `member` no ve el botón "Cerrar sprint" (o recibe 403 reflejado en UI).
5. **Retro → tarea:** crear ítem de acción, convertirlo en tarea, verificar que aparece en el Kanban general.

Consejo del QA Lead: los tests E2E de Streamlit deben esperar el rerun (`page.wait_for_selector` sobre el spinner `[data-testid="stStatusWidget"]` desapareciendo) — es la fuente número uno de flakiness. Sembrar datos vía API (`request_context.post("/api/sprints", ...)`), no vía UI, para que cada test tarde segundos y no minutos; la UI solo se usa para el flujo bajo prueba.

### 8. Integraciones externas

| Integración | Para qué | Prioridad |
|---|---|---|
| **Slack (webhooks entrantes)** | Recordatorio de daily con resumen del burndown; alerta cuando `Δ > umbral`; resumen automático al cerrar sprint. Es la integración con mejor ratio esfuerzo/valor percibido en ventas B2B LatAm. | Alta |
| **Google Calendar API** | Crear eventos recurrentes de las ceremonias (planning, review, retro, daily) al crear el sprint; leer vacaciones/feriados para calcular `capacidad_dias` real (feriados colombianos/mexicanos importan y Jira los ignora). | Media |
| **GitHub / GitLab API** | Vincular PRs/commits a tareas (`Cenit-341` en el mensaje de commit) para que "Completado" tenga evidencia; base futura para DORA (sección 07). | Media |
| **WhatsApp Business API** | En LatAm la daily async y las alertas viven en WhatsApp, no en Slack, en equipos de 10-20 personas. Diferenciador regional real, pero costo/complejidad de la API de Meta lo pospone. | Baja (post-PMF) |
| Typeform / formularios | Encuestas de retro anónimas. Innecesario: la retro nativa de la sección 6 lo cubre. | No |

### 9. Conflictos o solapamientos

| Metodología | Tipo de conflicto | Resolución en Cenit |
|---|---|---|
| **Kanban** | El más fuerte: compiten por el mismo tablero y la misma pregunta ("¿qué hago ahora?"). Flujo continuo + WIP limits vs iteraciones con compromiso. | No duplicar tableros: el tablero de sprint **es** el Kanban existente con filtro `sprint_id`. El usuario elige "modo flujo" o "modo sprint" por entidad/equipo, no ambos. Velocity y throughput no se muestran juntos en la misma vista. |
| **Lean** | Conceptual: Lean critica el inventario (backlog gigante) y el batch (el sprint es un batch). | Compatible: el warning de sobre-compromiso y el límite de churn son ideas Lean dentro de Scrum. |
| **XP** | Complementario, no conflictivo: XP define prácticas de ingeniería (TDD, pairing) dentro del contenedor Scrum. | La Definition of Done puede referenciar prácticas XP (tests pasando) vía integración GitHub. |
| **SAFe** | SAFe absorbe Scrum en jerarquías (PI Planning = macro-sprints). | Fuera de alcance: el ICP de Cenit (10-50 personas) no necesita SAFe; no reservar espacio de datos para ARTs. |
| **Waterfall** | Antagonista directo en filosofía. | Coexisten por proyecto: un cliente puede llevar proyectos por fases y otros por sprints; `sprints.entidad` lo permite. |
| **DORA / SPACE** | Compiten por espacio en Analytics: velocity (Scrum) vs deployment frequency (DORA) vs satisfacción (SPACE) pueden saturar el dashboard. | Analytics con pestañas por marco; velocity nunca al lado de métricas individuales (SPACE prohíbe rankear personas, y velocity por persona es un antipatrón). |
| **OKRs / KPIs** | El Sprint Goal compite con el OKR trimestral por ser "el objetivo". | Jerarquía explícita: OKR (trimestre) → Sprint Goal (2 semanas) como key result parcial. Campo futuro `sprints.okr_id`. |
| **PMBOK/PMI** | Choque de vocabulario (fases, EDT vs backlog, sprints). | No mezclar léxico en la misma vista; PMBOK queda en reporting ejecutivo. |
| **Design Thinking** | Sin conflicto de datos; convive aguas arriba (descubrimiento antes del backlog). | Ninguna acción. |

La decisión de producto más importante de todo Cenit está aquí: **Scrum y Kanban comparten el 90 % del modelo de datos (tasks) y el tablero**. Resolverlo con un toggle por equipo — y no con dos módulos — es lo que evita convertirse en el Jira que los usuarios huyen.

### 10. Antipatrones conocidos

- **Jira — el sprint como formulario infinito:** digitalizó Scrum tan configurablemente (schemes, workflows, pantallas, permisos) que planificar un sprint exige un Jira-admin. Resultado: equipos de 10 personas con procesos de 200. Lección para Cenit: crear un sprint debe tomar < 60 segundos y 4 campos.
- **Jira — carryover automático silencioso:** al cerrar sprint mueve incompletas al siguiente sin fricción, normalizando el arrastre eterno (Say/Do del 50 % que nadie ve). Cenit obliga la decisión explícita por tarea en el diálogo de cierre.
- **Jira — velocity como arma gerencial:** exponer velocity comparable entre equipos en dashboards ejecutivos llevó a inflación de puntos en toda la industria. Cenit: velocity por equipo, como rango, sin vista comparativa.
- **Trello — Scrum inexistente, delegado a Power-Ups:** sin sprints nativos, la gente hace columnas "Sprint 12" o listas espejo; el burndown depende de plugins de terceros que se rompen. Lección: si se ofrece Scrum, las métricas deben ser nativas, no un plugin.
- **Asana — sprints simulados con secciones/proyectos:** sin noción de compromiso ni snapshot, es imposible saber qué se prometió al inicio; el burndown de Asana usa conteo de tareas, no puntos. Por eso `sprint_tasks.points_snapshot` existe en nuestro esquema.
- **Todos — la retro huérfana:** ninguna de las tres integra la retrospectiva; vive en Miro/Notion y las acciones nunca vuelven al backlog. `retro_items.task_id` es la respuesta directa: acción de retro → tarea trazable.
- **Estado "Completado" sin Definition of Done:** las herramientas dejan arrastrar a Done sin verificación. Con el ADN QA del fundador, Cenit puede diferenciar: checklist de DoD ligero por tarea antes de aceptar el estado.

### 11. Caso real

**Linear** es la referencia correcta (y de donde viene la voz de producto del panel). Linear no implementó "Scrum" — implementó **Cycles**: iteraciones automáticas de 1-2 semanas que empiezan y terminan solas, con carryover que exige atención (las tareas incompletas se marcan visiblemente), velocity calculada sin configurar nada, y cero campos obligatorios. Qué aprender:

1. **Opinionated > configurable:** Linear decidió cómo se hace un ciclo y eliminó el 90 % de las decisiones que Jira delega al admin. Su NPS entre desarrolladores destrozó a Jira precisamente por eso.
2. **Las métricas emergen del uso, no de la disciplina:** el burnup de Linear se llena solo porque el estado de las issues ya se actualiza; no hay "hora de actualizar Jira".
3. **El calendario manda:** los cycles arrancan automáticamente cada lunes; nadie "olvida cerrar el sprint". Cenit puede replicarlo con un job que cierre y abra sprints según `fecha_fin` (con el diálogo de carryover pendiente para el PO al entrar).
4. **Límite del modelo:** Linear cobra en USD y su soporte/onboarding no habla el idioma del CTO de una software factory de Medellín o Guadalajara. Ese hueco —precio LatAm, español, WhatsApp/Slack, y riesgos+Eisenhower que Linear no tiene— es exactamente el posicionamiento de Cenit: *"los cycles de Linear con la matriz de Eisenhower y gestión de riesgos, a precio LatAm"*.

Mención local: equipos como los de Platzi y Kavak popularizaron en la región el discurso de iteraciones cortas sin ceremonia pesada; el vocabulario "sprint" ya está vendido en el mercado objetivo — Cenit no tiene que evangelizar, solo simplificar.

### 12. Costo de implementación

**Medio. Estimación: 3 sprints de 2 semanas (6 semanas) para 1-2 desarrolladores.**

| Sprint | Entregable | Detalle |
|---|---|---|
| S1 | Núcleo de datos + API | Migración SQL (sprints, sprint_tasks, story_points), CRUD FastAPI, `SprintService.planificar/cerrar`, pytest de dominio completo. ~35 h |
| S2 | UI + burndown | Vista `ui/views/sprint.py` (cabecera, tablero filtrado, cierre con carryover), snapshots diarios, gráfico burndown, historial de velocity. ~40 h |
| S3 | Pulido + E2E + retro | Retro con conversión a tarea, impedimentos, alertas en Mi Día, suite Playwright (5 flujos), webhook Slack básico, docs. ~35 h |

Riesgo de estimación: el drag-and-drop y los reruns de Streamlit suelen inflar S2 (+20 %). Recomendación: lanzar S1+S2 a un piloto y condicionar S3 a que el piloto realmente use sprints dos ciclos seguidos.

### 13. Cuándo NO construir esto todavía

Señales claras de sobre-ingeniería:

- **Hoy mismo, probablemente.** Cenit está en validación con pilotos y su diferenciador declarado es Eisenhower + riesgos + analytics sobre un Kanban simple. Construir Scrum completo antes de que ≥ 2 pilotos lo pidan explícitamente es competir con Jira en su terreno con recursos de 1-2 personas.
- **Si los pilotos no estiman:** velocity y burndown sin story points disciplinados son ruido. Test barato antes de escribir una línea: agregar solo la columna `tasks.story_points` y un filtro manual "Sprint" por texto; si en 4 semanas los pilotos llenan puntos en > 60 % de las tareas, hay demanda real.
- **Si el equipo usuario tiene < 4 personas:** el overhead de ceremonia supera el beneficio; Kanban + Mi Día ya lo resuelven.
- **Antes de que el Kanban existente esté estable:** el sprint depende del tablero; construir encima de una base que aún cambia duplica retrabajo.
- **La retro, el snapshot diario y Google Calendar son fase 2 en cualquier escenario** — el MVP de Scrum es: sprint + compromiso + velocity + cierre honesto. Nada más.

Regla de decisión: construir la sección S1 (datos + API) solo cuando exista **un piloto pagando o con carta de intención** cuyo proceso interno ya sea Scrum y cuyo dolor sea "Jira nos queda grande". Ese es el trigger; antes de eso, Cenit gana más terminando analytics y riesgos.
