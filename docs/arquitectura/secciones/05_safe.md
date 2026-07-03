# 05. SAFe

## 05. SAFe (Scaled Agile Framework)

### 1. Principio central y origen

SAFe (Scaled Agile Framework) nace en 2011 de la mano de Dean Leffingwell, consultor con trayectoria en Rational Software y Rally, como respuesta a un problema muy concreto: **la agilidad de equipo (Scrum, XP, Kanban) no escala por sí sola cuando hay 5, 10 o 50 equipos trabajando sobre el mismo producto o portafolio**. Su industria de origen es el software empresarial de gran escala — banca, aeroespacial, telecomunicaciones, gobierno — donde ya existían jerarquías de portafolio, programas y proyectos heredadas del mundo PMBOK, y donde "hacer Scrum" en cada equipo producía islas ágiles que no se sincronizaban entre sí.

El principio central de SAFe es la **alineación mediante cadencia sincronizada**: todos los equipos de un Agile Release Train (ART, típicamente 50-125 personas) planifican juntos en un evento llamado PI Planning (Program Increment Planning, cada 8-12 semanas), se comprometen a objetivos de negocio medibles (PI Objectives), visualizan sus dependencias cruzadas en un Program Board, y priorizan el backlog de programa con una fórmula económica explícita: **WSJF (Weighted Shortest Job First)**, derivada del trabajo de Don Reinertsen sobre costo de retraso (Cost of Delay).

El error de gestión que previene es doble:

1. **Optimización local sin alineación global**: equipos individualmente "veloces" que entregan piezas que no encajan, se bloquean mutuamente por dependencias no visibilizadas, o construyen lo equivocado porque nadie priorizó a nivel de programa.
2. **Priorización por opinión o por jerarquía** (HiPPO — Highest Paid Person's Opinion): WSJF obliga a cuantificar valor, urgencia y reducción de riesgo relativos antes de decidir qué se construye primero.

Para Cenit hay una lectura honesta que el panel debe hacer desde el inicio: **SAFe es el framework menos alineado con el segmento objetivo de Cenit** (equipos de 10-50 personas). SAFe está diseñado para organizaciones donde el ART es la unidad mínima (~50 personas) y existen múltiples ARTs. Sin embargo, hay **tres piezas de SAFe que sí son extraíbles y valiosas para equipos pequeños**, y son las que esta sección propone digitalizar de forma quirúrgica:

- **WSJF** como método de priorización económica (complementa la Matriz de Eisenhower que Cenit ya tiene: Eisenhower responde "¿qué atiendo hoy?", WSJF responde "¿qué construyo primero este trimestre?").
- **PI Objectives con valor de negocio planificado vs. real**, que produce la métrica de *predictability* — un dato que un CTO comprador de Cenit puede mostrar a su gerencia.
- **El Program Board de dependencias**, que en un equipo de 10-50 personas se traduce en "qué tarea bloquea a qué tarea entre áreas" (Desarrollo bloquea a Operaciones, Soporte espera a Wallet — exactamente las entidades/proyectos que ya existen en la columna `proyecto` de `tasks`).

La postura del panel: **no construir "SAFe" como marca en Cenit** (espantaría al segmento: un tech lead de un equipo de 15 personas que huye de Jira huye precisamente de esto), sino ofrecer un módulo de **"Planificación por Incrementos"** con WSJF y dependencias, sin la liturgia (sin ARTs, sin RTEs, sin Solution Trains).

### 2. Métricas y fórmulas exactas

Las tres métricas núcleo de SAFe digitalizables en Cenit:

**a) WSJF (Weighted Shortest Job First)**

```
WSJF = Cost of Delay / Job Size
Cost of Delay (CoD) = Valor de Negocio + Criticidad Temporal + Reducción de Riesgo / Habilitación de Oportunidad
```

Cada componente se estima en escala Fibonacci modificada (1, 2, 3, 5, 8, 13, 20) de forma **relativa**: el ítem más pequeño del lote recibe 1 en cada dimensión, el resto se compara contra él.

**Ejemplo numérico — equipo ficticio de 5 personas** (Andrés tech lead, Beatriz backend, Camilo frontend, Diana QA, Esteban soporte/ops) que debe priorizar 4 features para el próximo incremento de 10 semanas:

| Feature | Valor Negocio (VN) | Criticidad Temporal (CT) | Riesgo/Oportunidad (RR) | CoD = VN+CT+RR | Job Size (JS) | WSJF = CoD/JS |
|---|---|---|---|---|---|---|
| F1: Portal de autoconsulta clientes | 8 | 3 | 5 | 16 | 8 | **2.00** |
| F2: Migrar generador de certificados | 5 | 13 | 8 | 26 | 13 | **2.00** |
| F3: Integración pasarela de pagos | 13 | 8 | 3 | 24 | 5 | **4.80** |
| F4: Refactor módulo de reportes | 2 | 1 | 5 | 8 | 3 | **2.67** |

Cálculo paso a paso de F3: VN=13 (el más alto: desbloquea cobros recurrentes), CT=8 (el cliente ancla lo pidió para este trimestre), RR=3 (riesgo técnico moderado). CoD = 13+8+3 = **24**. Job Size = 5 (Beatriz y Camilo estiman ~3 semanas de dos personas, el segundo trabajo más pequeño del lote). WSJF = 24/5 = **4.80** → F3 se construye primero, pese a que F2 tiene el CoD más alto (26): su tamaño 13 lo hunde. Orden final: F3 (4.80) → F4 (2.67) → F1 y F2 empatados (2.00; desempate por CoD absoluto: F2 primero).

**b) PI Predictability (predictibilidad del incremento)**

```
Predictability % = (Σ Valor de Negocio REAL logrado / Σ Valor de Negocio PLANIFICADO comprometido) × 100
```

Cada PI Objective recibe del "negocio" (en Cenit: el rol `admin`) un valor planificado 1-10 al inicio del PI, y un valor real 0-10 al cierre. Los objetivos *stretch* (no comprometidos) suman al numerador pero no al denominador.

Ejemplo con el mismo equipo, PI de 10 semanas con 4 objetivos comprometidos y 1 stretch:

| Objetivo | Tipo | Valor plan. | Valor real |
|---|---|---|---|
| O1: Pasarela de pagos operando con 2 clientes | Comprometido | 10 | 9 |
| O2: Reportes refactorizados sin regresiones | Comprometido | 6 | 6 |
| O3: Portal autoconsulta en beta | Comprometido | 8 | 4 |
| O4: Reducir tickets de soporte 20% | Comprometido | 7 | 8 |
| O5: PoC firma digital (stretch) | Stretch | 5 | 0 |

Denominador (solo comprometidos): 10+6+8 = 24... paso a paso: 10+6 = 16; 16+8 = 24; 24+7 = **31**. Numerador (todo lo logrado): 9+6+4+8+0 = **27**. Predictability = 27/31 × 100 = **87.1%**. El rango saludable SAFe es 80-100%: este equipo es confiable para comprometerse; por debajo de 80% sobre-promete, y sostenido en 100% probablemente sub-promete.

**c) Load vs. Capacity (carga del incremento)**

```
Capacity = Σ (días hábiles disponibles por persona en el PI) × factor de foco
Load % = Σ Job Size comprometido convertido a días / Capacity × 100
```

Ejemplo: PI de 10 semanas = 50 días hábiles × 5 personas = 250 días-persona. Restas: vacaciones de Camilo (5 días), soporte de Esteban (50% de su tiempo = 25 días), overhead reuniones (factor de foco 0.8). Capacity = (250 − 5 − 25) × 0.8 = 220 × 0.8 = **176 días**. Si el lote comprometido (F3+F4+F1) suma en estimación 160 días → Load = 160/176 = **90.9%**, ligeramente sobrecargado; SAFe recomienda planificar a ≤80% para absorber imprevistos — señal de que F1 debería recortarse o pasar a stretch.

### 3. Modelo de datos

Extiende `users` y `tasks` existentes. Diseño deliberadamente sin tabla de ARTs: en el segmento de Cenit el "tren" es la organización entera; si algún día se necesita, se agrega `train_id` a `program_increments`.

```sql
-- Incremento de Programa (ciclo de planificación de 8-12 semanas)
CREATE TABLE program_increments (
    id              SERIAL PRIMARY KEY,
    nombre          VARCHAR(80)  NOT NULL,              -- ej: "PI 2026-Q3"
    entidad         VARCHAR(50)  NOT NULL,              -- alineado con tasks.entidad
    fecha_inicio    DATE         NOT NULL,
    fecha_fin       DATE         NOT NULL,
    estado          VARCHAR(20)  NOT NULL DEFAULT 'planificacion',
                    -- planificacion | en_ejecucion | cerrado
    capacity_dias   NUMERIC(6,1),                       -- capacidad calculada (días-persona)
    created_by      INTEGER REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT pi_fechas_validas CHECK (fecha_fin > fecha_inicio)
);

-- Feature: unidad de valor priorizable con WSJF; agrupa tareas existentes
CREATE TABLE features (
    id                  SERIAL PRIMARY KEY,
    pi_id               INTEGER REFERENCES program_increments(id) ON DELETE SET NULL,
    titulo              VARCHAR(200) NOT NULL,
    descripcion         TEXT,
    -- Componentes WSJF (escala Fibonacci 1,2,3,5,8,13,20)
    valor_negocio       SMALLINT CHECK (valor_negocio      IN (1,2,3,5,8,13,20)),
    criticidad_temporal SMALLINT CHECK (criticidad_temporal IN (1,2,3,5,8,13,20)),
    riesgo_oportunidad  SMALLINT CHECK (riesgo_oportunidad IN (1,2,3,5,8,13,20)),
    job_size            SMALLINT CHECK (job_size           IN (1,2,3,5,8,13,20)),
    wsjf                NUMERIC(6,2) GENERATED ALWAYS AS (
                            CASE WHEN job_size IS NULL OR job_size = 0 THEN NULL
                                 ELSE (COALESCE(valor_negocio,0)
                                     + COALESCE(criticidad_temporal,0)
                                     + COALESCE(riesgo_oportunidad,0))::numeric / job_size
                            END) STORED,
    estado              VARCHAR(20) NOT NULL DEFAULT 'backlog',
                        -- backlog | comprometida | stretch | hecha | descartada
    responsable_id      INTEGER REFERENCES users(id),
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ
);

-- Vínculo N:1 de tareas existentes a features (no rompe el flujo actual de tasks)
ALTER TABLE tasks ADD COLUMN feature_id INTEGER REFERENCES features(id) ON DELETE SET NULL;
CREATE INDEX idx_tasks_feature ON tasks(feature_id);

-- Objetivos del PI con valor planificado vs. real (base de predictability)
CREATE TABLE pi_objectives (
    id               SERIAL PRIMARY KEY,
    pi_id            INTEGER NOT NULL REFERENCES program_increments(id) ON DELETE CASCADE,
    descripcion      TEXT NOT NULL,
    es_stretch       BOOLEAN NOT NULL DEFAULT FALSE,
    valor_planificado SMALLINT NOT NULL CHECK (valor_planificado BETWEEN 1 AND 10),
    valor_real       SMALLINT CHECK (valor_real BETWEEN 0 AND 10),  -- NULL hasta el cierre
    feature_id       INTEGER REFERENCES features(id) ON DELETE SET NULL,
    created_at       TIMESTAMPTZ DEFAULT now()
);

-- Dependencias entre tareas (Program Board); dirigidas: bloqueante -> bloqueada
CREATE TABLE task_dependencies (
    id               SERIAL PRIMARY KEY,
    tarea_bloqueante INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tarea_bloqueada  INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tipo             VARCHAR(20) NOT NULL DEFAULT 'bloquea',  -- bloquea | relacionada
    resuelta         BOOLEAN NOT NULL DEFAULT FALSE,
    creada_por       INTEGER REFERENCES users(id),
    created_at       TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT no_self_dependency CHECK (tarea_bloqueante <> tarea_bloqueada),
    CONSTRAINT dependencia_unica  UNIQUE (tarea_bloqueante, tarea_bloqueada)
);
```

Decisiones de diseño: (1) `wsjf` es columna generada — imposible que se desincronice de sus componentes; (2) `feature_id` en `tasks` es nullable — el 100% del producto actual sigue funcionando sin features; (3) `task_dependencies` es reutilizable por Kanban (bloqueos en columna) y por Waterfall (predecesoras), amortizando el costo entre tres secciones de este documento.

### 4. Casos de uso del domain layer

Nuevo servicio en `domain/services.py` (o `domain/safe_service.py`), siguiendo el estilo existente de operar sobre dicts serializados:

```python
from dataclasses import dataclass
from datetime import date
from typing import Optional

FIBONACCI_SAFE: tuple[int, ...] = (1, 2, 3, 5, 8, 13, 20)

@dataclass
class WsjfResult:
    feature_id: int
    cost_of_delay: int
    job_size: int
    wsjf: float
    ranking: int

@dataclass
class PredictabilityReport:
    pi_id: int
    valor_planificado_total: int      # solo objetivos comprometidos
    valor_real_total: int             # incluye stretch logrados
    predictability_pct: float         # 0-150+ (stretch puede superarlo)
    en_rango_saludable: bool          # 80 <= pct <= 100
    objetivos: list[dict]

@dataclass
class CapacityReport:
    pi_id: int
    capacity_dias: float
    load_dias: float
    load_pct: float
    sobrecargado: bool                # load_pct > 80


class IncrementoService:
    """Casos de uso de Planificación por Incrementos (SAFe destilado)."""

    def calcular_wsjf(self, features: list[dict]) -> list[WsjfResult]:
        # 1. validar que cada componente pertenece a FIBONACCI_SAFE
        # 2. cod = valor_negocio + criticidad_temporal + riesgo_oportunidad
        # 3. wsjf = cod / job_size  (job_size == 0 -> ValueError)
        # 4. ordenar desc por wsjf; desempate: mayor cod primero
        # 5. asignar ranking 1..n y devolver
        ...

    def calcular_predictability(
        self, pi: dict, objetivos: list[dict]
    ) -> PredictabilityReport:
        # 1. comprometidos = [o for o in objetivos if not o["es_stretch"]]
        # 2. plan_total = sum(o["valor_planificado"] for o in comprometidos)
        # 3. real_total = sum(o["valor_real"] or 0 for o in objetivos)  # stretch suma
        # 4. pct = real_total / plan_total * 100  (plan_total == 0 -> 0.0, no crash)
        # 5. en_rango_saludable = 80 <= pct <= 100
        ...

    def calcular_capacity(
        self,
        pi: dict,
        miembros: list[dict],              # users activos
        dias_no_disponibles: dict[int, int],  # user_id -> días fuera
        factor_foco: float = 0.8,
        dias_por_punto: float = 1.5,       # calibrable con histórico
    ) -> CapacityReport:
        # 1. dias_habiles = habiles_entre(pi["fecha_inicio"], pi["fecha_fin"])
        # 2. capacity = sum(max(dias_habiles - fuera.get(u), 0)) * factor_foco
        # 3. load = sum(job_size de features comprometidas) * dias_por_punto
        # 4. load_pct = load / capacity * 100; sobrecargado = pct > 80
        ...

    def detectar_dependencias_circulares(
        self, dependencias: list[dict]
    ) -> list[list[int]]:
        # DFS sobre el grafo dirigido (tarea_bloqueante -> tarea_bloqueada);
        # devuelve ciclos como listas de task_ids para alertar en UI.
        ...

    def dependencias_criticas(
        self, dependencias: list[dict], tareas: list[dict], hoy: date
    ) -> list[dict]:
        # cruce con RiesgoService: una dependencia es crítica si la tarea
        # bloqueada tiene fecha_fin <= hoy+7 y la bloqueante no está Completada.
        # Ordenar por risk_score de la bloqueada (reutiliza tasks.risk_score).
        ...

    def progreso_feature(self, feature: dict, tareas: list[dict]) -> dict:
        # pct = tareas Completadas con ese feature_id / total tareas del feature;
        # sugiere estado 'hecha' cuando pct == 100.
        ...
```

Nótese la integración con lo existente: `dependencias_criticas` reutiliza el `risk_score` que ya calcula `api/models.py`, y `progreso_feature` se apoya en los estados actuales de `tasks` sin modificarlos.

### 5. Diseño de API REST

Consistente con los prefijos existentes (`/api/tasks`, `/api/analytics/...`). Router nuevo `api/routers/incrementos.py`:

| Método | Ruta | Propósito |
|---|---|---|
| POST | `/api/pis` | Crear PI |
| GET | `/api/pis?entidad=&estado=` | Listar PIs |
| PATCH | `/api/pis/{pi_id}` | Cambiar estado / cerrar PI |
| POST | `/api/features` | Crear feature con componentes WSJF |
| GET | `/api/features?pi_id=&ordenar=wsjf` | Backlog priorizado |
| PATCH | `/api/features/{id}` | Re-estimar / comprometer / stretch |
| POST | `/api/tasks/{task_id}/feature` | Vincular tarea existente a feature |
| POST | `/api/pis/{pi_id}/objectives` | Crear PI Objective |
| PATCH | `/api/objectives/{id}` | Asignar `valor_real` al cierre |
| POST | `/api/dependencies` | Declarar dependencia entre tareas |
| GET | `/api/dependencies?pi_id=&solo_criticas=true` | Program Board / alertas |
| GET | `/api/analytics/wsjf-ranking?pi_id=` | Ranking WSJF calculado |
| GET | `/api/analytics/predictability?pi_id=` | Reporte de predictibilidad |
| GET | `/api/analytics/capacity?pi_id=` | Load vs. capacity |

Payloads de ejemplo:

```json
POST /api/features
{
  "pi_id": 3,
  "titulo": "Integración pasarela de pagos",
  "descripcion": "Cobros recurrentes para clientes ancla",
  "valor_negocio": 13,
  "criticidad_temporal": 8,
  "riesgo_oportunidad": 3,
  "job_size": 5,
  "estado": "backlog",
  "responsable_id": 2
}
```

```json
GET /api/analytics/predictability?pi_id=3   → 200
{
  "pi_id": 3,
  "nombre": "PI 2026-Q3",
  "valor_planificado_total": 31,
  "valor_real_total": 27,
  "predictability_pct": 87.1,
  "en_rango_saludable": true,
  "objetivos": [
    {"id": 11, "descripcion": "Pasarela operando con 2 clientes",
     "es_stretch": false, "valor_planificado": 10, "valor_real": 9}
  ]
}
```

```json
POST /api/dependencies
{
  "tarea_bloqueante": 142,
  "tarea_bloqueada": 187,
  "tipo": "bloquea"
}
→ 409 si crea ciclo: {"detail": "Dependencia circular: 142 → 187 → 142"}
```

Validaciones de dominio en el endpoint: componentes WSJF restringidos a la escala Fibonacci (422 si no), detección de ciclos antes de insertar dependencia (409), y `valor_real` solo asignable cuando el PI está `en_ejecucion` o `cerrado`.

### 6. Vista o componente de UI

**`ui/views/incrementos.py`** — una sola vista con tres pestañas (`st.tabs`), etiquetada en la navegación como **"Planificación"** (nunca "SAFe"):

**Pestaña 1 — Priorización WSJF.** Arriba, `st.selectbox` para elegir el PI activo. Cuerpo: `st.data_editor` con las features del backlog; columnas editables Valor Negocio, Criticidad, Riesgo y Tamaño como `SelectboxColumn` limitadas a (1,2,3,5,8,13,20); columnas calculadas CoD y WSJF (solo lectura, con barra de progreso `ProgressColumn` para lectura rápida). Al editar cualquier celda la tabla se reordena por WSJF. A la derecha de cada fila, botón "Comprometer" que la pasa al PI. Un `st.expander` "¿Cómo estimo?" explica la estimación relativa en tres frases — crítico para el usuario LatAm que nunca vio WSJF. Debajo, `st.metric` triple: capacidad del PI, carga comprometida, % de carga (rojo si >80%).

**Pestaña 2 — Tablero de dependencias.** Grafo ligero renderizado con `st.graphviz_chart`: nodos = tareas con dependencias (coloreados por el mismo `ESTADO_COLORS` de `KanbanService`), aristas = bloqueos; aristas rojas si la dependencia es crítica (bloqueada vence en ≤7 días). Panel lateral: formulario para declarar dependencia (dos `st.selectbox` de tareas + botón), y lista de dependencias críticas ordenadas por `risk_score` con botón "Marcar resuelta". Si `detectar_dependencias_circulares` encuentra ciclos, `st.error` con la cadena del ciclo.

**Pestaña 3 — Objetivos y predictibilidad.** Lista de PI Objectives como tarjetas: descripción, chip "Comprometido"/"Stretch", `st.slider` 1-10 de valor planificado (bloqueado tras iniciar el PI, solo `admin` edita), y al cerrar el PI un segundo slider de valor real. Header: gauge de predictability del PI actual y `st.line_chart` histórico de predictability por PI — el gráfico que el tech lead pega en su reporte trimestral. Interacción de cierre: botón "Cerrar PI" exige que todo objetivo comprometido tenga `valor_real` asignado.

### 7. Estrategia de testing E2E

**Pytest (dominio, `tests/test_incremento_service.py`)** — donde vive el grueso del valor de QA:

- `test_wsjf_ordena_por_ratio_no_por_cod`: reproduce exactamente la tabla del punto 2 (F3 gana con CoD menor que F2).
- `test_wsjf_desempata_por_cod`: F1 y F2 con WSJF 2.00 → F2 primero.
- `test_wsjf_job_size_cero_lanza_error` y `test_componente_fuera_de_fibonacci_rechazado`.
- `test_predictability_stretch_suma_solo_al_numerador`: caso del 87.1%.
- `test_predictability_sin_objetivos_devuelve_cero_sin_dividir_por_cero`.
- `test_capacity_descuenta_vacaciones_y_factor_foco`: caso de los 176 días.
- `test_deteccion_ciclo_simple` (A→B→A), `test_deteccion_ciclo_largo` (A→B→C→A) y `test_grafo_aciclico_no_reporta`.
- `test_dependencia_critica_requiere_vencimiento_proximo_y_bloqueante_incompleta`.

**Playwright para Python (`tests/e2e/test_incrementos_e2e.py`)** — flujos críticos, usando `page.get_by_role`/`get_by_test_id` sobre la app Streamlit levantada por Docker Compose:

1. **Flujo de priorización completo**: login → Planificación → crear feature → asignar los 4 componentes → verificar que la columna WSJF muestra el valor esperado y la fila salta a la posición correcta del ranking (asserts sobre el orden del `data_editor`).
2. **Flujo de compromiso con sobrecarga**: comprometer features hasta superar 80% de carga → assert de que la métrica de carga se pinta en rojo y aparece la advertencia.
3. **Flujo de dependencia circular**: declarar A bloquea B, luego B bloquea A → assert del `st.error` con el mensaje de ciclo y de que la API devolvió 409 (interceptando con `page.expect_response`).
4. **Flujo de cierre de PI**: intentar cerrar con un objetivo sin `valor_real` → bloqueado; asignar valores → cerrar → assert del gauge de predictability con el porcentaje calculado.
5. **Regresión de integración**: vincular una tarea existente del Kanban a una feature y verificar que la tarea sigue apareciendo y moviéndose en `ui/views/kanban.py` (la extensión no rompe el core).

Dado el perfil del fundador (QA/E2E), estos tests son además el mejor artefacto de venta técnica: demuestran en CI que el módulo nuevo no degrada el producto base.

### 8. Integraciones externas

| Integración | Para qué | Prioridad |
|---|---|---|
| **Google Calendar API** | Crear los eventos de cadencia del PI (planning al inicio, review/cierre al final) al crear el PI; el valor de SAFe está en el ritual sincronizado, y el ritual vive en el calendario del equipo | Alta |
| **Slack (webhooks entrantes)** | Alertas de dependencias críticas ("La tarea #142 de Beatriz bloquea a #187 que vence el viernes") y recordatorio de scoring de objetivos al cierre del PI | Alta |
| **GitHub API (issues/milestones)** | Mapear features a milestones y tareas a issues para que el progreso de feature se calcule solo desde el trabajo real del repo; opcionalmente leer PRs mergeados como señal de avance | Media |
| **Typeform / Google Forms** | Encuesta de confidence vote post-planning (ritual SAFe de "fist of five"); nice-to-have, se puede hacer nativo en Streamlit con menos fricción | Baja |

Explícitamente **no** se necesita integración con herramientas de portafolio (Jira Align, Targetprocess): ese es justo el territorio enterprise que Cenit no debe pisar.

### 9. Conflictos o solapamientos

SAFe es, por naturaleza, un meta-framework que engulle a los demás — el riesgo de canibalización de UI/datos/atención es el más alto de las 12 metodologías:

| Metodología | Conflicto | Resolución en Cenit |
|---|---|---|
| **Scrum** | SAFe contiene Scrum (los sprints serían las iteraciones del PI); dos jerarquías de planificación compiten | El PI se define como contenedor opcional de sprints: `sprints.pi_id` nullable; si no usas PIs, Scrum funciona igual |
| **Kanban** | El Program Board compite visualmente con el tablero Kanban | Nunca duplicar tarjetas: la pestaña de dependencias muestra un grafo, no columnas; la tarjeta Kanban gana un badge de bloqueo que enlaza a Planificación |
| **OKRs** | PI Objectives y OKRs son casi la misma entidad (objetivo + medición) con vocabulario distinto — el solapamiento más peligroso del producto | Una sola tabla subyacente de objetivos con `marco` (`okr` \| `pi`); la UI elige el vocabulario. Jamás dos vistas de "objetivos" separadas |
| **Eisenhower (core actual)** | WSJF y Eisenhower son ambos priorizadores; el usuario preguntará cuál manda | Separar horizontes en el copy: Eisenhower prioriza *tareas de hoy*, WSJF prioriza *features del trimestre*. No aplicar WSJF a tareas individuales |
| **Lean** | WSJF *es* economía Lean (Reinertsen); la sección Lean querrá CoD también | WSJF vive una sola vez, en features; la vista Lean lo referencia |
| **Waterfall / PMBOK** | `task_dependencies` es exactamente la tabla de predecesoras de un Gantt | Compartir la tabla deliberadamente: una inversión, tres metodologías servidas |
| **DORA / KPIs** | Predictability compite por espacio en Analytics | Un solo dashboard de Analytics con secciones; predictability es una tarjeta más, no una vista propia |
| **XP, SPACE, Design Thinking** | Sin conflicto estructural relevante | N/A |

Regla de producto transversal: **Cenit ofrece "modos", no "frameworks apilados"**. Si el equipo activa Planificación por Incrementos, la vista aparece; si no, ni un píxel de SAFe contamina el Kanban.

### 10. Antipatrones conocidos

- **Jira (+ Jira Align): digitalizar la burocracia completa.** Jira Align modela ARTs, Solution Trains, Portfolio Epics, Lean Budgets… y el resultado es que configurar la herramienta exige un consultor SPC certificado. El antipatrón: convertir cada caja del "Big Picture" de SAFe en una entidad de base de datos. Lección para Cenit: modelar solo las 4 entidades que producen métricas (PI, feature, objetivo, dependencia) y ni una más.
- **Jira: jerarquías rígidas de issue types.** Epic→Story sin flexibilidad obligó a plugins (Advanced Roadmaps) para representar features de programa, generando dos fuentes de verdad. Cenit lo evita con `feature_id` nullable sobre la tabla `tasks` existente: una jerarquía de exactamente un nivel, opcional.
- **Trello: ignorar dependencias por completo.** Trello nunca tuvo dependencias nativas (solo power-ups de terceros), así que los equipos las simulaban con checklists y enlaces manuales que se pudrían. Lección: si se ofrecen dependencias, deben ser de primera clase (FK real, detección de ciclos, alertas) o no ofrecerse.
- **Asana: dependencias sin semántica de riesgo.** Asana marca "waiting on" pero no responde la pregunta útil: *¿cuáles de estos bloqueos van a explotar esta semana?* Cenit cruza dependencias con `risk_score` y `fecha_fin` — el bloqueo se vuelve accionable, no decorativo.
- **Todos: WSJF como campo numérico libre.** Cuando la herramienta permite escribir "7" o "42" en valor de negocio, la estimación relativa muere y vuelve el HiPPO con decimales. Cenit fuerza la escala Fibonacci con CHECK constraints y selectboxes cerrados.
- **Antipatrón organizacional que la herramienta puede inducir: "SAFe cargo cult".** Si Cenit vendiera el módulo como "SAFe certificado", invitaría a equipos de 8 personas a montar PI Plannings de 2 días. El naming ("Planificación") y el onboarding deben empujar el uso destilado.

### 11. Caso real

El caso más instructivo no es un adoptante enterprise de SAFe sino una herramienta: **Targetprocess (hoy Apptio Targetprocess, adquirida por IBM)**. Fue la primera plataforma en digitalizar SAFe bien, y lo que hizo distinto fue: (1) **el modelo de datos era un grafo flexible, no una jerarquía cableada** — cualquier entidad podía relacionarse con cualquier otra, y las "vistas SAFe" (Program Board, WSJF ranking) eran solo lentes sobre ese grafo; (2) **el Program Board era interactivo de verdad**: arrastrar una feature entre iteraciones re-dibujaba las líneas de dependencia al instante, convirtiendo el planning de un ejercicio de post-its fotografiados en un artefacto vivo; (3) **soportaba SAFe sin exigirlo** — el mismo producto servía a un equipo Scrum plano.

La lección transferible a Cenit es exactamente la tercera: las entidades de esta sección (`features`, `task_dependencies`, `pi_objectives`) deben diseñarse como **capacidades componibles sobre `tasks`**, no como un "modo SAFe" monolítico. Contraejemplo del mismo mercado: VersionOne (hoy Digital.ai) se casó tanto con la nomenclatura SAFe que quedó ilegible para equipos pequeños y cedió todo ese segmento a Linear y ClickUp. En LatAm, además, casi ningún equipo de 10-50 personas declara "hacemos SAFe", pero muchos CTOs sí preguntan "¿puedo ver qué bloquea a qué y si vamos a cumplir el trimestre?" — esa es la feature; el framework es irrelevante para el pitch.

### 12. Costo de implementación

**Costo: MEDIO-ALTO** para el estándar de Cenit — **5-6 sprints de 2 semanas** con 1-2 desarrolladores:

| Sprint | Entregable | Detalle |
|---|---|---|
| 1 | Modelo de datos + dominio WSJF | Migraciones (4 tablas + `ALTER tasks`), `IncrementoService.calcular_wsjf`, pytest completo |
| 2 | API de PIs y features | Routers, schemas Pydantic, validaciones Fibonacci, CRUD probado |
| 3 | UI pestaña WSJF | `data_editor` con recálculo, capacity/load, comprometer features |
| 4 | Dependencias | Tabla + detección de ciclos + grafo graphviz + badge en Kanban |
| 5 | Objetivos y predictability | CRUD objetivos, cierre de PI, gauge + histórico en Analytics |
| 6 | E2E + integraciones mínimas | Suite Playwright completa, webhook Slack de dependencias críticas, pulido |

Riesgo de cronograma: el grafo de dependencias en Streamlit (sprint 4) es la pieza con más incertidumbre de UX — `st.graphviz_chart` es estático; si se exige interactividad tipo Targetprocess habría que evaluar un componente custom (`streamlit-agraph`), lo que puede añadir un sprint. Recomendación del panel: **entregable por fases** — sprints 1-3 (solo WSJF) ya son un módulo vendible por sí mismo; dependencias y predictability pueden esperar señal de demanda.

### 13. Cuándo NO construir esto todavía

**Ahora mismo es prematuro construir la mayor parte de esta sección.** Señales concretas de sobre-ingeniería:

- **Etapa actual (pilotos B2B, pre-ingresos, equipo de 1-2):** Cenit compite contra Trello/Jira por simplicidad. Un módulo de PIs con objetivos y capacity planning es exactamente el tipo de superficie que hace que un piloto de 12 personas diga "esto es otro Jira" y abandone en el onboarding. Ningún cliente piloto del segmento 10-50 ha operado jamás un PI Planning.
- **Umbral de activación:** construir WSJF (solo sprints 1-3) cuando **≥3 clientes pagantes pidan priorización de mediano plazo** con sus propias palabras ("no sé qué hacer primero el próximo trimestre"). Construir dependencias cuando ≥3 pidan bloqueos entre tareas. Construir PI Objectives/predictability solo con clientes de 40+ personas con un CTO que reporte a gerencia — probablemente año 2+.
- **Qué sí rescatar hoy (costo casi cero):** la tabla `task_dependencies` es la única pieza candidata a adelantarse, porque sirve simultáneamente a Kanban (bloqueos), Waterfall (predecesoras) y riesgos (bloqueos críticos por `risk_score`) — pero incluso esa debe esperar a que el core actual (Mi Día, Kanban, Eisenhower, Riesgos) esté validado y retenga usuarios.
- **Señal inequívoca de que llegó el momento:** un cliente quiere pasar de 30 a 80 usuarios y pregunta cómo coordina Cenit varios equipos. Ese día, esta sección es el plano. Antes de ese día, es un documento de arquitectura — y debe quedarse así.

En una frase: SAFe en Cenit no es núcleo; es un **módulo de expansión de cuenta** (expansion revenue) para cuando los clientes pequeños de hoy crezcan, y su versión mínima viable se llama WSJF, no SAFe.
