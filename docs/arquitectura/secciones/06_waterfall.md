# 06. Waterfall

## 06. WATERFALL

### 1. Principio central y origen

Waterfall (cascada) es el modelo de ciclo de vida secuencial por fases: **Requisitos → Diseño → Implementación → Verificación → Mantenimiento**, donde cada fase produce entregables formales que deben aprobarse (*phase gate* o *sign-off*) antes de iniciar la siguiente. Su principio central es que **el costo de corregir un error crece exponencialmente cuanto más tarde se detecta**, por lo tanto conviene invertir fuertemente en especificación y diseño antes de escribir una sola línea de código.

El origen habitual se atribuye al artículo de **Winston Royce (1970), "Managing the Development of Large Software Systems"**, escrito desde su experiencia en proyectos aeroespaciales (TRW, programas de defensa de EE.UU.). La ironía histórica —que todo panel serio debe señalar— es que Royce presentó el diagrama en cascada pura como un modelo **defectuoso** ("invita al riesgo y al fracaso") y propuso iteraciones de retroalimentación entre fases; pero el Departamento de Defensa de EE.UU. lo codificó literalmente en el estándar **DOD-STD-2167 (1985)**, y de ahí se propagó a toda la industria como dogma durante dos décadas.

**Qué error de gestión previene**: el "arrancar a codificar sin saber qué se construye". Waterfall obliga a responder por escrito, antes de gastar presupuesto de construcción: qué se entrega, cuándo, con qué criterios de aceptación, y quién firma la aprobación. En contextos con **requisitos estables, contratos de alcance fijo y alto costo de cambio** (hardware, regulación, integraciones con terceros que exigen fechas), sigue siendo el modelo correcto.

**Relevancia real para Cenit**: los clientes piloto B2B en LatAm (universidades, entidades como las que ya aparecen en el campo `cliente` de `tasks`: Uniandes, Javeriana, UPB…) contratan **proyectos de alcance cerrado con fecha de entrega comprometida**. Aunque el equipo interno trabaje con Kanban, el compromiso hacia el cliente es waterfall: hitos, entregables, actas de aceptación. Cenit puede diferenciarse de Trello/Linear precisamente ofreciendo esta **capa de "compromiso contractual por fases" sobre un flujo Kanban interno**: por fuera cascada (lo que el cliente firmó), por dentro flujo continuo (cómo el equipo ejecuta). Ese es el ángulo de producto: no digitalizar waterfall como religión, sino como **vista de compromiso y desviación contra plan**.

### 2. Métricas y fórmulas exactas

Waterfall se controla con **gestión de valor ganado (EVM, Earned Value Management)** y desviación contra línea base. Las fórmulas canónicas:

| Métrica | Fórmula | Interpretación |
|---|---|---|
| PV (Planned Value) | Σ costo planificado del trabajo programado a la fecha | Cuánto deberíamos haber avanzado |
| EV (Earned Value) | Σ costo planificado del trabajo realmente completado | Cuánto avanzamos en términos del plan |
| AC (Actual Cost) | Σ costo real incurrido | Cuánto gastamos |
| SV (Schedule Variance) | `SV = EV − PV` | <0: atrasados |
| CV (Cost Variance) | `CV = EV − AC` | <0: sobrecosto |
| SPI (Schedule Performance Index) | `SPI = EV / PV` | <1: atrasados |
| CPI (Cost Performance Index) | `CPI = EV / AC` | <1: ineficientes en costo |
| EAC (Estimate At Completion) | `EAC = BAC / CPI` | Proyección de costo final |
| ETC (Estimate To Complete) | `ETC = EAC − AC` | Lo que falta por gastar |
| % avance de fase | `EV_fase / BAC_fase` | Avance ponderado, no "conteo de tareas" |
| Deslizamiento de hito | `fecha_real − fecha_baseline` (días) | Slippage por hito |

**Ejemplo numérico paso a paso — equipo ficticio de 5 personas** (proyecto "Integración Wallet-Universidad X", 12 semanas, presupuesto BAC = 300 horas-persona valoradas a costo interno de USD 20/h → **BAC = USD 6.000**):

Plan por fases (línea base):

| Fase | Horas plan | Costo plan | Semanas |
|---|---|---|---|
| Requisitos | 40 h | $800 | 1–2 |
| Diseño | 60 h | $1.200 | 3–4 |
| Implementación | 140 h | $2.800 | 5–9 |
| Verificación | 40 h | $800 | 10–11 |
| Despliegue | 20 h | $400 | 12 |

Corte de control al **final de la semana 6**:

1. **PV**: lo programado a semana 6 = Requisitos (100%) + Diseño (100%) + Implementación (2 de 5 semanas = 40%) = 800 + 1.200 + 0,40 × 2.800 = **PV = $3.120**.
2. **EV**: lo realmente completado = Requisitos aprobados (100% → $800), Diseño aprobado (100% → $1.200), Implementación con 12 de 35 tareas ponderadas terminadas (34,3% → 0,343 × 2.800 = $960). **EV = $2.960**.
3. **AC**: horas reales registradas = 168 h × $20 = **AC = $3.360** (el diseño tomó 72 h en vez de 60).
4. **SV = 2.960 − 3.120 = −$160** → levemente atrasados (≈ 0,5 día de trabajo del equipo).
5. **CV = 2.960 − 3.360 = −$400** → sobrecosto.
6. **SPI = 2.960 / 3.120 = 0,949** → al ritmo actual, las 6 semanas restantes se convierten en 6 / 0,949 ≈ **6,3 semanas** (2 días de deslizamiento proyectado).
7. **CPI = 2.960 / 3.360 = 0,881**.
8. **EAC = 6.000 / 0,881 = $6.810** → sobrecosto proyectado de $810 (≈ 40 horas-persona extra). Con 5 personas, es 1 día adicional de todo el equipo: manejable si se detecta en semana 6, catastrófico si se descubre en semana 11. Esa detección temprana es exactamente el valor de la vista.

Nota del panel: para un equipo de 5 en LatAm no recomendamos capturar "costo" en dinero (fricción cultural y de datos); usamos **horas-persona como moneda** y el CPI/SPI salen igual de útiles. El esquema de datos abajo lo refleja (`horas_plan`, `horas_reales`).

### 3. Modelo de datos

Extiende `users` y `tasks` existentes. La clave de diseño: **no tocar `tasks`** salvo dos FKs opcionales; todo lo waterfall vive en tablas nuevas, de modo que un equipo que no use el módulo no paga nada. La línea base se guarda **inmutable y versionada** (baseline v1, v2…): sin baseline congelada no hay SV/SPI honestos.

```sql
-- Proyecto formal con ciclo de vida en cascada.
-- Complementa el String tasks.proyecto (texto libre) con una entidad real.
CREATE TABLE waterfall_projects (
    id              SERIAL PRIMARY KEY,
    nombre          VARCHAR(120) NOT NULL,
    entidad         VARCHAR(50)  NOT NULL,           -- misma semántica que tasks.entidad
    cliente         VARCHAR(100),                    -- misma semántica que tasks.cliente
    descripcion     TEXT,
    estado          VARCHAR(20)  NOT NULL DEFAULT 'planificacion'
        CHECK (estado IN ('planificacion','en_ejecucion','pausado','cerrado','cancelado')),
    bac_horas       NUMERIC(8,1),                    -- Budget At Completion en horas-persona
    fecha_inicio_plan DATE,
    fecha_fin_plan    DATE,
    fecha_fin_real    DATE,
    owner_id        INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_by      INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ
);

-- Fases secuenciales del proyecto (Requisitos, Diseño, ...). Orden estricto.
CREATE TABLE waterfall_phases (
    id              SERIAL PRIMARY KEY,
    project_id      INTEGER NOT NULL REFERENCES waterfall_projects(id) ON DELETE CASCADE,
    nombre          VARCHAR(80) NOT NULL,            -- 'Requisitos','Diseño','Implementación','Verificación','Despliegue'
    orden           SMALLINT NOT NULL,               -- 1..N, define la secuencia
    estado          VARCHAR(20) NOT NULL DEFAULT 'pendiente'
        CHECK (estado IN ('pendiente','activa','en_revision','aprobada','rechazada')),
    horas_plan      NUMERIC(8,1) NOT NULL DEFAULT 0, -- presupuesto de la fase (PV base)
    fecha_inicio_plan DATE,
    fecha_fin_plan    DATE,
    fecha_inicio_real DATE,
    fecha_fin_real    DATE,
    criterios_salida TEXT,                           -- exit criteria del gate, texto markdown
    UNIQUE (project_id, orden)
);

-- Gate de aprobación de fase: quién firma, cuándo, veredicto. Auditable.
CREATE TABLE waterfall_gate_reviews (
    id              SERIAL PRIMARY KEY,
    phase_id        INTEGER NOT NULL REFERENCES waterfall_phases(id) ON DELETE CASCADE,
    revisor_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    veredicto       VARCHAR(20) NOT NULL
        CHECK (veredicto IN ('aprobado','aprobado_con_condiciones','rechazado')),
    comentarios     TEXT,
    firmado_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Hitos contractuales con fecha comprometida (lo que el cliente firmó).
CREATE TABLE waterfall_milestones (
    id              SERIAL PRIMARY KEY,
    project_id      INTEGER NOT NULL REFERENCES waterfall_projects(id) ON DELETE CASCADE,
    phase_id        INTEGER REFERENCES waterfall_phases(id) ON DELETE SET NULL,
    nombre          VARCHAR(120) NOT NULL,
    fecha_plan      DATE NOT NULL,                   -- de la baseline vigente
    fecha_real      DATE,
    es_contractual  BOOLEAN NOT NULL DEFAULT FALSE,  -- si el cliente lo firmó
    entregable      TEXT                             -- descripción del deliverable
);

-- Línea base versionada e inmutable: snapshot del plan al momento de congelar.
CREATE TABLE waterfall_baselines (
    id              SERIAL PRIMARY KEY,
    project_id      INTEGER NOT NULL REFERENCES waterfall_projects(id) ON DELETE CASCADE,
    version         SMALLINT NOT NULL,               -- 1,2,3... re-baseline requiere justificación
    motivo          TEXT,                            -- obligatorio desde v2 (change request)
    aprobada_por    INTEGER REFERENCES users(id) ON DELETE SET NULL,
    snapshot        JSONB NOT NULL,                  -- fases+hitos+horas_plan congelados
    created_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE (project_id, version)
);

-- Registro de horas reales por tarea y usuario (alimenta AC).
CREATE TABLE waterfall_time_entries (
    id              SERIAL PRIMARY KEY,
    task_id         INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    fecha           DATE NOT NULL DEFAULT CURRENT_DATE,
    horas           NUMERIC(5,2) NOT NULL CHECK (horas > 0 AND horas <= 24),
    nota            VARCHAR(200)
);

-- Vínculo tasks -> fase (opcional; una task puede seguir viviendo solo en Kanban).
ALTER TABLE tasks
    ADD COLUMN phase_id INTEGER REFERENCES waterfall_phases(id) ON DELETE SET NULL,
    ADD COLUMN horas_plan NUMERIC(6,1);              -- peso de la task en el EV de su fase

CREATE INDEX idx_tasks_phase        ON tasks(phase_id);
CREATE INDEX idx_phases_project     ON waterfall_phases(project_id);
CREATE INDEX idx_milestones_project ON waterfall_milestones(project_id);
CREATE INDEX idx_time_task          ON waterfall_time_entries(task_id);
```

Decisiones de diseño defendidas por el panel:

- **EV emerge de `tasks`**: `EV_fase = Σ horas_plan de tasks con estado='Completado'`. No inventamos un tracker paralelo; el Kanban existente sigue siendo la fuente de verdad de ejecución.
- **`snapshot JSONB` en baselines**: comparar plan vigente vs. congelado sin joins arqueológicos; es lectura, no transaccional.
- **`waterfall_time_entries` es opcional por diseño**: sin ella, SPI funciona igual (solo horas plan); CPI queda deshabilitado. Eso permite lanzar el módulo en dos etapas.

### 4. Casos de uso del domain layer

Nuevo servicio `WaterfallService` en `domain/services.py` (o `domain/waterfall.py`), operando sobre dicts como los servicios existentes, más dataclasses de reporte en `domain/entities.py`:

```python
from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class EvmReport:
    project_id: int
    fecha_corte: date
    pv_horas: float
    ev_horas: float
    ac_horas: Optional[float]   # None si no hay time entries
    sv: float
    spi: float
    cv: Optional[float]
    cpi: Optional[float]
    eac_horas: Optional[float]
    dias_deslizamiento_proyectado: int
    avance_por_fase: dict[str, float]   # {"Diseño": 1.0, "Implementación": 0.34}

@dataclass
class GateResult:
    phase_id: int
    puede_avanzar: bool
    bloqueos: list[str]         # criterios de salida no cumplidos


def calcular_evm(project: dict, phases: list[dict], tareas: list[dict],
                 time_entries: list[dict], fecha_corte: date) -> EvmReport:
    # PV: interpolación lineal de horas_plan de cada fase según fecha_corte
    #   pv_fase = horas_plan * clamp((corte - inicio_plan) / (fin_plan - inicio_plan), 0, 1)
    # EV: sum(t["horas_plan"] for t in tareas de la fase if t["estado"] == "Completado")
    #   fallback si tasks sin horas_plan: EV = horas_plan_fase * (completadas / total)
    # AC: sum(e["horas"] for e in time_entries if e["fecha"] <= fecha_corte) o None
    # SV = EV - PV; SPI = EV / PV (guard PV==0 -> 1.0)
    # CPI/EAC solo si AC no es None; EAC = bac / cpi
    # deslizamiento = dias_restantes_plan * (1/spi - 1), redondeado
    ...

def evaluar_gate(phase: dict, tareas_fase: list[dict],
                 gate_reviews: list[dict]) -> GateResult:
    # bloqueos: tareas no Completadas, criterios_salida sin marcar,
    #           falta veredicto 'aprobado' de un revisor con role='admin'
    # puede_avanzar = not bloqueos
    ...

def avanzar_fase(phases: list[dict], phase_id: int) -> list[dict]:
    # Precondición: evaluar_gate(...).puede_avanzar
    # Marca fase actual 'aprobada' con fecha_fin_real=hoy,
    # activa la fase con orden inmediatamente siguiente (fecha_inicio_real=hoy).
    # Regla dura: nunca dos fases 'activa' en el mismo proyecto.
    ...

def congelar_baseline(project: dict, phases: list[dict],
                      milestones: list[dict], motivo: str,
                      aprobada_por: int) -> dict:
    # Construye snapshot JSONB {fases: [...], hitos: [...], bac_horas}
    # version = max(existentes) + 1; motivo obligatorio si version > 1
    ...

def deslizamiento_hitos(milestones: list[dict], baseline: dict,
                        hoy: date) -> list[dict]:
    # Por hito: dias_slip = (fecha_real or hoy) - fecha_plan_baseline
    # estado semáforo: verde <=0, ámbar 1-5, rojo >5 días
    ...
```

Todas las funciones son puras (reciben dicts, devuelven dataclasses/dicts), consistentes con `KanbanService`/`AnalyticsService`, y por tanto testeables sin base de datos — punto en el que el QA Lead del panel no negocia.

### 5. Diseño de API REST

Consistente con el estilo existente (`/api/tasks`, `/api/analytics/...`), prefijo `/api/waterfall`:

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/waterfall/projects` | Crear proyecto con fases |
| GET | `/api/waterfall/projects` | Listar (filtro `?entidad=&estado=`) |
| GET | `/api/waterfall/projects/{id}` | Detalle con fases e hitos |
| POST | `/api/waterfall/projects/{id}/baseline` | Congelar línea base |
| POST | `/api/waterfall/phases/{id}/gate-review` | Firmar gate |
| POST | `/api/waterfall/phases/{id}/advance` | Avanzar de fase (valida gate) |
| GET | `/api/waterfall/projects/{id}/evm?fecha_corte=` | Reporte EVM |
| GET | `/api/waterfall/projects/{id}/milestones/slippage` | Semáforo de hitos |
| POST | `/api/waterfall/time-entries` | Registrar horas |

Ejemplos de payloads:

```json
POST /api/waterfall/projects
{
  "nombre": "Integración Wallet - Universidad X",
  "entidad": "Wallet",
  "cliente": "uniandes",
  "bac_horas": 300,
  "fecha_inicio_plan": "2026-07-13",
  "fecha_fin_plan": "2026-10-02",
  "owner_id": 1,
  "fases": [
    {"nombre": "Requisitos", "orden": 1, "horas_plan": 40,
     "fecha_inicio_plan": "2026-07-13", "fecha_fin_plan": "2026-07-24",
     "criterios_salida": "- [ ] Documento de alcance firmado\n- [ ] Casos de aceptación listados"},
    {"nombre": "Diseño", "orden": 2, "horas_plan": 60,
     "fecha_inicio_plan": "2026-07-27", "fecha_fin_plan": "2026-08-07"},
    {"nombre": "Implementación", "orden": 3, "horas_plan": 140,
     "fecha_inicio_plan": "2026-08-10", "fecha_fin_plan": "2026-09-11"}
  ]
}
```

```json
POST /api/waterfall/phases/2/gate-review
{
  "veredicto": "aprobado_con_condiciones",
  "comentarios": "Diseño aprobado; el diagrama de la integración SIIGO se entrega junto con la fase 3."
}
```

```json
GET /api/waterfall/projects/1/evm?fecha_corte=2026-08-21
→ 200
{
  "project_id": 1,
  "fecha_corte": "2026-08-21",
  "pv_horas": 156.0,
  "ev_horas": 148.0,
  "ac_horas": 168.0,
  "sv": -8.0,
  "spi": 0.949,
  "cpi": 0.881,
  "eac_horas": 340.5,
  "dias_deslizamiento_proyectado": 2,
  "avance_por_fase": {"Requisitos": 1.0, "Diseño": 1.0, "Implementación": 0.343}
}
```

El endpoint `advance` devuelve `409 Conflict` con la lista de `bloqueos` si el gate no está cumplido — el error es parte del contrato, no una excepción genérica. Autenticación: mismo JWT existente; firmar un gate exige `role='admin'` (o el `owner_id` del proyecto).

### 6. Vista o componente de UI

Nueva vista `ui/views/proyectos.py` ("Proyectos" en la navegación de `ui/app.py`), en tres niveles:

**Nivel 1 — Lista de proyectos**: tabla con nombre, cliente, fase activa (badge de color), SPI como semáforo (🟢 ≥0,95 / 🟡 0,85–0,95 / 🔴 <0,85), próximo hito y días al hito. Un `st.selectbox` o clic lleva al detalle.

**Nivel 2 — Detalle del proyecto (la vista estrella)**:
- **Cabecera de fases**: franja horizontal de "chevrons" (Requisitos ▸ Diseño ▸ Implementación ▸ Verificación ▸ Despliegue) renderizada con HTML/CSS en `st.markdown(unsafe_allow_html=True)`, reutilizando la paleta de `ESTADO_COLORS`: fase aprobada en verde, activa en azul, pendientes en gris. Es el mapa mental instantáneo del "dónde estamos".
- **Fila de métricas**: cuatro `st.metric` — SPI (con delta vs. corte anterior), CPI (o "sin registro de horas"), deslizamiento proyectado en días, % avance global.
- **Gráfico de curva S**: `st.line_chart`/Plotly con PV acumulado (línea punteada, del baseline) vs. EV acumulado (línea sólida) vs. AC (si existe). Es el gráfico que un CTO cliente entiende en 5 segundos.
- **Gantt liviano de hitos**: `plotly.express.timeline` con fecha_plan (barra gris del baseline) y fecha_real/proyección (barra de color) por hito; hitos contractuales marcados con 📌.
- **Tareas de la fase activa**: el mismo componente de tarjetas del Kanban existente, filtrado por `phase_id`, con la columna extra `horas_plan`. Aquí se ve la fusión Kanban-dentro-de-Waterfall.

**Nivel 3 — Gate de fase**: `st.expander` "Cerrar fase" con checklist de `criterios_salida` (checkboxes), lista de tareas incompletas bloqueantes, `st.text_area` de comentarios y botones "Aprobar y avanzar" / "Rechazar". Si hay bloqueos, el botón aparece deshabilitado con la lista en `st.error`. Congelar baseline: botón en la cabecera que abre un `st.dialog` exigiendo `motivo` cuando ya existe una versión previa.

Interacción clave de producto (voz Head of Product): la vista **nunca pide doble captura**. Las tareas se mueven en el Kanban de siempre; esta vista solo agrega el plan y lee la ejecución.

### 7. Estrategia de testing E2E

**Unitarios pytest (`tests/test_waterfall_service.py`)** — dominio puro, sin DB:

- `calcular_evm`: caso del ejemplo numérico de la sección 2 como fixture dorada (assert SPI == 0.949 ± 0.001); PV con fecha_corte anterior al inicio (PV=0, SPI=1.0 por guard); proyecto sin time_entries (CPI/EAC = None); fase sin tareas con fallback proporcional; división por cero en PV=0 y AC=0.
- `evaluar_gate`: gate con tareas pendientes → bloqueado; criterios sin marcar → bloqueado; todo cumplido sin firma admin → bloqueado; camino feliz.
- `avanzar_fase`: invariante "solo una fase activa"; intento de saltar de orden 1 a 3 → error; avance de la última fase cierra el proyecto.
- `congelar_baseline`: v1 sin motivo OK, v2 sin motivo → error; snapshot contiene todas las fases.
- `deslizamiento_hitos`: hito sin fecha_real usa `hoy`; umbrales del semáforo en los bordes exactos (0, 1, 5, 6 días).

**E2E Playwright para Python (`tests/e2e/test_waterfall_flow.py`)** — flujos críticos contra Streamlit + API en Docker Compose:

1. **Ciclo de vida completo** (el flujo de humo): login admin → crear proyecto con 3 fases → congelar baseline v1 → verificar que el chevron "Requisitos" está activo → crear 2 tareas ligadas a la fase desde el Kanban → completarlas → abrir gate, marcar criterios, aprobar → assert de que el chevron avanza a "Diseño". Streamlit re-renderiza todo el DOM, así que los selectores deben anclarse a `data-testid` de los contenedores de Streamlit más texto (`page.get_by_text("Diseño").locator(...)`) y usar `expect(...).to_be_visible()` con auto-wait, nunca sleeps.
2. **Gate bloqueado**: intentar avanzar con una tarea "En Proceso" → assert del `st.error` con la tarea listada y botón deshabilitado. Es el test que protege la regla de negocio más importante del módulo.
3. **Consistencia UI↔API**: leer el SPI del `st.metric` y compararlo con `GET /api/waterfall/projects/{id}/evm` vía `page.request` (APIRequestContext de Playwright) — detecta desincronización entre dominio y presentación, el bug más frecuente en apps Streamlit.
4. **Re-baseline**: cambiar fechas, congelar v2 con motivo, verificar que la curva S muestra la línea base v2 y que el histórico v1 sigue consultable.
5. **Permisos**: usuario `role='member'` no ve el botón de firmar gate; el POST directo al endpoint devuelve 403.

Estos E2E corren en el job de CI existente de GitHub Actions con un servicio Postgres efímero, etiquetados `@pytest.mark.e2e` para poder excluirlos del ciclo rápido local.

### 8. Integraciones externas

| Integración | Para qué | Prioridad |
|---|---|---|
| **Google Calendar API** | Publicar hitos y gates como eventos en el calendario del equipo y del cliente; el deslizamiento de un hito reprograma el evento. Es la integración de mayor valor percibido para el sponsor no técnico. | Alta |
| **Slack (webhooks entrantes)** | Notificar aprobación/rechazo de gates, SPI cayendo bajo 0,9 y hitos en rojo al canal del proyecto. Barata (un POST) y visible. | Alta |
| **GitHub API (milestones + releases)** | Mapear `waterfall_milestones` ↔ GitHub Milestones y marcar la fase de Despliegue contra un release/tag real: el gate de "Verificación" puede exigir que el CI esté en verde. | Media |
| **Generación de PDF (WeasyPrint, local)** | Acta de cierre de fase firmada digitalmente (gate review + checklist) exportable a PDF para el cliente. En B2B LatAm el "acta de entrega" es un artefacto contractual real. No es API de terceros pero es el entregable que cierra ventas. | Media |
| **SIIGO / facturación** (ya hay MCP de SIIGO en el entorno del fundador) | Hito contractual aprobado → disparar factura del hito. Conecta el módulo con caja: los contratos de alcance fijo en Colombia se facturan por hitos. | Baja (post-validación) |

Typeform/encuestas no aplica aquí (pertenece a Design Thinking/SPACE). GitLab solo si un piloto lo exige.

### 9. Conflictos o solapamientos

| Metodología | Tipo de conflicto | Resolución en Cenit |
|---|---|---|
| **Scrum** | Frontal, filosófico y de UI: sprints iterativos vs. fases secuenciales; ambos quieren "ser el plan". Un proyecto no puede tener a la vez baseline de fases y compromiso de sprint como fuente de verdad. | Regla de producto: por proyecto se elige **modo de ejecución** (Scrum o Kanban) y el modo waterfall es una **capa de compromiso externo opcional** encima. Nunca mostrar sprint burndown y curva S en la misma pantalla como si fueran lo mismo. |
| **Kanban** | Solapamiento operativo: las tareas de una fase viven en el tablero Kanban. Riesgo de doble estado (estado Kanban vs. estado de fase). | Ya resuelto en el modelo: `tasks.estado` es la única verdad de ejecución; la fase solo agrega `phase_id` y `horas_plan`. El gate lee estados, no los duplica. |
| **PMBOK/PMI** | Solapamiento casi total de datos: EVM, baselines, hitos y gates SON vocabulario PMBOK. Riesgo de construir dos módulos para lo mismo. | Compartir tablas: la sección PMBOK debe reutilizar `waterfall_baselines`, `waterfall_milestones` y el reporte EVM; PMBOK aporta encima riesgo/stakeholders, no otro plan. Decisión de arquitectura explícita: **un solo módulo de "plan y compromiso"**. |
| **SAFe** | Compite por el concepto de "planificación en cadencia grande" (PI Planning ≈ fases). | Para el segmento de Cenit (10–50 personas) SAFe es no-objetivo; si algún día existe, consume las mismas tablas de milestones. |
| **Lean / XP** | Filosófico: Lean llama "inventario/desperdicio" al gran diseño anticipado; XP propone lo opuesto (diseño emergente). | No hay conflicto de datos, solo de narrativa. La UI no debe moralizar: Cenit presenta waterfall como "modo compromiso contractual", no como método de desarrollo recomendado. |
| **OKRs / KPIs** | Atención del usuario: SPI/CPI compiten con KPIs por espacio en dashboards. | SPI/CPI viven dentro de la vista del proyecto; el dashboard global de KPIs puede *suscribirse* a "proyectos en rojo" como un KPI más. |
| **DORA / SPACE** | Mínimo: DORA mide entrega continua, ortogonal a fases. Único roce: la fase "Despliegue" como evento vs. deployment frequency como flujo. | Ninguna acción; son lentes distintos sobre datos distintos. |
| **Design Thinking** | Ninguno real: opera antes (descubrimiento) de que exista un plan. | La fase "Requisitos" puede enlazar artefactos de descubrimiento. |

El conflicto que más importa gestionar es **Scrum vs. Waterfall en la narrativa de ventas**: el CTO comprador dirá "nosotros somos ágiles". El pitch correcto (voz GTM): *"tu equipo sigue en Kanban; Cenit te da la vista de cascada que tu cliente/gerencia te exige, sin que el equipo cambie nada"*.

### 10. Antipatrones conocidos

1. **Jira — el Gantt como cosmético (Advanced Roadmaps)**: Jira añadió planes tipo Gantt desconectados de la ejecución real: las fechas del plan no se recalculan honestamente contra el trabajo del board, y no existe baseline inmutable de serie — el plan se edita y el pasado desaparece. Resultado: gráficos que siempre se ven bien porque se redibujan. Lección para Cenit: **baseline congelada o no hay métrica**; la desviación es el producto.
2. **Jira/Confluence — el gate como burocracia sin datos**: los workflows de aprobación de Jira permiten transiciones con campos obligatorios, pero el aprobador no ve *evidencia* (tests, tareas incompletas) en el momento de firmar; firma a ciegas y el gate degenera en trámite. Cenit muestra los bloqueos calculados en la misma pantalla del gate.
3. **Trello — negación total**: Trello nunca ofreció fases, hitos ni fechas comprometidas; los equipos simulaban fases con columnas ("Fase 1", "Fase 2") destruyendo el flujo Kanban en el proceso. Antipatrón de columna-como-fase: dos semánticas en un solo eje. Cenit lo evita separando `estado` (flujo) de `phase_id` (plan).
4. **Asana — el modo Timeline que promete cascada y entrega dibujo**: dependencias entre tareas y Gantt visual, pero sin EVM, sin costo/esfuerzo planificado vs. real y sin gates: sirve para *comunicar* un plan, no para *controlarlo*. Muchos equipos LatAm lo usan y luego mantienen el control real en Excel — ese Excel es exactamente el hueco de mercado de este módulo.
5. **MS Project (el antipatrón fundacional)**: tanta potencia de planificación que el plan se vuelve un artefacto de una sola persona (el PM), divorciado de lo que el equipo ejecuta. La lección estructural: **el plan debe leer la ejecución automáticamente** (EV desde `tasks.estado`), jamás pedir que alguien "actualice el porcentaje de avance" a mano — el % avance manual es la mentira más antigua de la gestión de proyectos.
6. **Todos — re-baseline silencioso**: permitir cambiar fechas del plan sin versión ni motivo. Por eso `waterfall_baselines.motivo` es obligatorio desde v2: la fricción es intencional.

### 11. Caso real

**Basecamp con Hill Charts + la práctica de Thoughtworks en contratos fixed-bid** ofrecen las dos mitades de la lección; el caso más transferible es **Basecamp (37signals)**. Basecamp rechaza Scrum y Gantt, pero su metodología Shape Up es, en esencia, una cascada corta y honesta: *shaping* (requisitos+diseño) → *betting* (gate de aprobación con presupuesto fijo de 6 semanas) → *building* (implementación con alcance recortable) → *cool-down*. Lo que hicieron bien y Cenit debe copiar:

- **El gate es de apetito, no de estimación**: se aprueba "cuánto vale la pena gastar" (presupuesto fijo) y el alcance se ajusta dentro — esto invierte el fracaso clásico de waterfall (alcance fijo, tiempo elástico) y encaja con contratos B2B por hitos.
- **Hill Charts**: visualización de avance en dos mitades ("descubriendo el problema" / "ejecutando lo conocido") actualizada con un clic sobre el trabajo real, no con % manual. Es la prueba de que se puede reportar avance contra plan sin el teatro del "90% completo durante 3 meses".
- **Escribir antes de construir**: el *pitch* de shaping es el documento de requisitos reducido a su mínimo útil (problema, apetito, solución, riesgos, no-goals) — la fase de Requisitos de Cenit debería plantillar exactamente eso en `criterios_salida`, no un SRS de 40 páginas.

Complemento del mundo clásico: **NASA/JPL y su sistema de gate reviews (SRR, PDR, CDR)** demuestran la versión correcta de gates pesados cuando el costo de error es real: cada review tiene criterios de salida públicos y evidencia adjunta. Cenit toma de ahí una sola cosa: el gate con checklist explícito y firma auditable — y deja el resto.

### 12. Costo de implementación

**Costo: MEDIO. Estimado: 3 sprints de 2 semanas (1–2 devs), 3,5 con integraciones.**

| Sprint | Alcance | Detalle |
|---|---|---|
| **Sprint 1** | Datos + dominio | Migración SQL (7 tablas + ALTER tasks), dataclasses, `calcular_evm`, `evaluar_gate`, `avanzar_fase`, `congelar_baseline` con suite pytest completa (~25 tests). Es el sprint barato porque es dominio puro. |
| **Sprint 2** | API + UI núcleo | 9 endpoints FastAPI con auth y 409 de gate; vista `proyectos.py` niveles 1 y 2 (lista, chevrons, métricas, curva S con Plotly). |
| **Sprint 3** | Gate UI + baseline + E2E | Flujo de cierre de fase, dialog de baseline, Gantt de hitos, 5 flujos Playwright, ajuste CI. Pulido de UX en Streamlit (los reruns complican formularios multi-paso; presupuestar aquí es realista, no pesimista). |
| **Sprint 3,5 (opcional)** | Integraciones | Slack webhook + Google Calendar + PDF de acta. |

Riesgo de estimación: `waterfall_time_entries` (captura de horas) parece pequeña pero arrastra UX diaria (¿dónde registra horas la gente sin odiarlo?). Recomendación firme del panel: **lanzar Fase A sin AC/CPI** (solo SPI y deslizamiento, que no requieren captura de horas) y decidir la Fase B con feedback de pilotos. Eso mantiene el compromiso en 3 sprints.

### 13. Cuándo NO construir esto todavía

**No construir si se cumple cualquiera de estas señales:**

1. **Ningún piloto ha pedido reporte contra plan**. Si los 2–3 pilotos actuales usan Cenit para el día a día (Mi Día, Kanban, Eisenhower) y nadie ha preguntado "¿cómo le muestro el avance a mi cliente/gerente?", este módulo es solución buscando problema. La señal de compra correcta: un piloto exportando datos de Cenit a Excel/PowerPoint para armar un informe de hitos — ese Excel es el ticket de entrada.
2. **Antes de que el Kanban y Analytics estén estables**. El EV se calcula desde `tasks.estado` y `horas_plan`; si el flujo básico de tareas aún cambia de esquema cada semana, la baseline congelada se vuelve deuda de migración. Waterfall es una capa *derivada*: se construye sobre cimientos quietos.
3. **Con un solo desarrollador y pista de menos de 6 meses**. Tres sprints de un módulo que no toca la retención diaria es demasiado costo de oportunidad frente a onboarding, estabilidad y la propuesta core (Kanban+Eisenhower+riesgos). Este es un módulo de **expansión/upsell** (plan de pago para líderes que reportan hacia arriba), no de adquisición.
4. **Si el ICP validado resulta ser equipos de producto continuo** (SaaS propio, sin clientes de proyecto): ahí DORA/OKRs ganan la prioridad y waterfall puede no construirse nunca.

**Momento correcto**: cuando existan ≥3 clientes pagando o a punto de pagar cuyo negocio sea **servicios/proyectos con contratos por hitos** (agencias, software factories, consultoras — abundantes en el mercado LatAm objetivo) y al menos uno condicione la compra a "reporte de avance para mi cliente final". En ese momento este módulo pasa de sobre-ingeniería a diferenciador que ni Trello ni Linear ofrecen y que en Jira cuesta un plugin enterprise.
