# Sección 09 — OKRs (Objectives and Key Results)

## 09. OKRs

### 1. Principio central y origen

Los OKRs (Objectives and Key Results) resuelven el problema más caro de la gestión: **equipos ocupados que no avanzan hacia nada**. Un tablero Kanban lleno de tarjetas "Completado" puede coexistir perfectamente con un trimestre perdido, porque el Kanban mide *flujo*, no *dirección*. El OKR introduce la pregunta que ninguna columna de estado responde: ¿completar esta tarea nos acercó a algo que importa?

El origen es doble. Andy Grove lo formalizó en Intel en los años 70 como "iMBO" (una evolución del Management by Objectives de Peter Drucker, 1954), corrigiendo el defecto central del MBO: los objetivos anuales atados a compensación, que incentivaban metas timoratas y sandbagging. Grove los hizo trimestrales, públicos y desacoplados del salario. John Doerr los llevó a Google en 1999 —cuando Google tenía ~40 empleados, es decir, el tamaño exacto del segmento objetivo de Cenit— y desde ahí se propagaron a LinkedIn, Twitter, Spotify y prácticamente todo el B2B SaaS moderno. El libro *Measure What Matters* (Doerr, 2018) los canonizó.

La estructura mínima:

- **Objective (O)**: cualitativo, inspirador, con horizonte temporal (típicamente un trimestre). "Convertirnos en la herramienta de gestión preferida de los pilotos".
- **Key Results (KRs)**: 2–5 resultados medibles por objetivo, con línea base y meta. "Pasar de 2 a 6 equipos piloto activos". Un KR es un *outcome* (resultado observable), no un *output* (tarea hecha).
- **Iniciativas**: el trabajo que mueve los KRs. En Cenit, las iniciativas ya existen: son las filas de la tabla `tasks`.

El error de gestión que previene es la **confusión output/outcome**: medir productividad por volumen de tareas cerradas ("shipped ≠ done" en la jerga de producto). Para el fundador de Cenit hay un segundo beneficio, casi personal: un founder solo, en transición de QA a CEO, con clientes piloto, es la persona más susceptible del mundo a la trampa de "estuve ocupado todo el trimestre". Un ciclo OKR de 12 semanas con check-ins semanales es un mecanismo de accountability barato cuando no hay cofundador ni board que lo exija.

Desde la perspectiva de calidad, los OKRs son además el criterio de aceptación del negocio: igual que un test E2E verifica que el flujo de login *funciona*, un KR verifica que el trimestre *funcionó*. Esa analogía (KR = assertion sobre el negocio) es la que hace natural incorporarlos a un producto construido por alguien con mentalidad de testing.

### 2. Métricas y fórmulas exactas

Las métricas canónicas de OKR, con ejemplo numérico sobre un equipo ficticio de 5 personas ("Equipo Andino": Ana — líder, Bruno, Carla, Diego, Elena) en el ciclo Q3-2026.

**a) Progreso de un KR (normalizado 0.0–1.0):**

```
progreso_kr = clamp((valor_actual − valor_inicial) / (valor_meta − valor_inicial), 0, 1)
```

Funciona también para métricas decrecientes (meta < inicial) porque numerador y denominador comparten signo.

**b) Progreso de un Objective** = promedio (opcionalmente ponderado) de sus KRs:

```
progreso_obj = Σ(progreso_kr_i × peso_i) / Σ(peso_i)
```

**Ejemplo paso a paso.** Objective O1: "Estabilizar la plataforma para los pilotos" (peso uniforme, 3 KRs):

| KR | Responsable | Inicial | Meta | Actual (semana 8) | Cálculo | Progreso |
|---|---|---|---|---|---|---|
| KR1: bugs críticos abiertos | Bruno | 14 | 2 | 6 | (14−6)/(14−2) = 8/12 | 0.67 |
| KR2: cobertura de tests E2E (%) | Carla | 35 | 70 | 61 | (61−35)/(70−35) = 26/35 | 0.74 |
| KR3: uptime mensual (%) | Diego | 98.1 | 99.5 | 99.2 | (99.2−98.1)/(99.5−98.1) = 1.1/1.4 | 0.79 |

`progreso_O1 = (0.67 + 0.74 + 0.79) / 3 = 2.20 / 3 = 0.733 ≈ 73%`

**c) Progreso esperado vs. real (indicador de salud del ciclo):**

```
progreso_esperado = dias_transcurridos / dias_totales_ciclo
salud = progreso_real − progreso_esperado
```

Semana 8 de 13 → esperado = 56/91 = 0.615. Salud de O1 = 0.733 − 0.615 = **+0.118** → "on track" (verde). Convención de semáforo: salud ≥ −0.10 verde; −0.25 ≤ salud < −0.10 amarillo; < −0.25 rojo.

**d) Calificación final estilo Google (0.0–1.0 por KR, al cierre):** 0.7 es el punto dulce de un KR aspiracional ("stretch"); 1.0 sostenido indica metas timoratas. Grade del ciclo del equipo:

```
grade_ciclo = promedio(grade_obj_i)
```

Si el Equipo Andino cierra Q3 con O1 = 0.81, O2 = 0.55, O3 = 0.68 → grade_ciclo = (0.81+0.55+0.68)/3 = **0.68** → ciclo saludable si O2 y O3 eran aspiracionales.

**e) Cobertura de alineación (la métrica que solo Cenit puede dar gratis):**

```
alineacion = tareas_vinculadas_a_algun_KR / tareas_activas_del_ciclo
```

Si el equipo tiene 40 tareas activas y 26 vinculadas a KRs → alineación = 26/40 = **65%**. El 35% restante es "trabajo huérfano": o es keep-the-lights-on legítimo, o es desperdicio (aquí OKR le da la mano a Lean). Benchmark razonable: 60–80%; 100% es sospechoso (todo forzado a encajar).

**f) Cadencia de check-in:** `check_in_rate = check_ins_hechos / (n_krs × semanas_transcurridas)`. Con 3 KRs y 8 semanas: 24 esperados; si hubo 19 → 79%. Por debajo de ~60%, los OKRs están muertos aunque el dashboard diga verde: el dato es stale.

### 3. Modelo de datos

Extiende `users` y `tasks` existentes. La decisión clave de diseño: **las tareas de Cenit son las iniciativas**, así que la vinculación tarea↔KR es una tabla puente N:M (una tarea puede empujar dos KRs; un KR se mueve por muchas tareas). Los KRs soportan medición manual (check-in) o automática derivada de tareas (`measure_type`).

```sql
-- Ciclos (trimestres u otros periodos)
CREATE TABLE okr_cycles (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(40)  NOT NULL,              -- 'Q3-2026'
    fecha_inicio DATE        NOT NULL,
    fecha_fin    DATE        NOT NULL,
    estado      VARCHAR(20)  NOT NULL DEFAULT 'activo'
                CHECK (estado IN ('borrador','activo','cerrado')),
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CHECK (fecha_fin > fecha_inicio)
);

-- Objetivos
CREATE TABLE objectives (
    id          SERIAL PRIMARY KEY,
    cycle_id    INTEGER NOT NULL REFERENCES okr_cycles(id) ON DELETE CASCADE,
    owner_id    INTEGER NOT NULL REFERENCES users(id),
    titulo      VARCHAR(200) NOT NULL,
    descripcion TEXT,
    nivel       VARCHAR(20) NOT NULL DEFAULT 'equipo'
                CHECK (nivel IN ('empresa','equipo','individual')),
    parent_id   INTEGER REFERENCES objectives(id) ON DELETE SET NULL, -- alineación vertical
    estado      VARCHAR(20) NOT NULL DEFAULT 'activo'
                CHECK (estado IN ('activo','cerrado','cancelado')),
    grade_final NUMERIC(3,2) CHECK (grade_final BETWEEN 0 AND 1),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ
);
CREATE INDEX idx_objectives_cycle ON objectives(cycle_id);

-- Key Results
CREATE TABLE key_results (
    id            SERIAL PRIMARY KEY,
    objective_id  INTEGER NOT NULL REFERENCES objectives(id) ON DELETE CASCADE,
    owner_id      INTEGER NOT NULL REFERENCES users(id),
    titulo        VARCHAR(200) NOT NULL,
    measure_type  VARCHAR(20) NOT NULL DEFAULT 'manual'
                  CHECK (measure_type IN ('manual','task_count','task_pct')),
    -- 'task_count': valor_actual = COUNT(tareas vinculadas completadas)
    -- 'task_pct'  : valor_actual = % de tareas vinculadas completadas
    unidad        VARCHAR(30) NOT NULL DEFAULT 'numero',   -- 'numero','%','COP','equipos'...
    valor_inicial NUMERIC(12,2) NOT NULL DEFAULT 0,
    valor_meta    NUMERIC(12,2) NOT NULL,
    valor_actual  NUMERIC(12,2) NOT NULL DEFAULT 0,
    peso          NUMERIC(4,2) NOT NULL DEFAULT 1.0 CHECK (peso > 0),
    es_aspiracional BOOLEAN NOT NULL DEFAULT FALSE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ,
    CHECK (valor_meta <> valor_inicial)
);
CREATE INDEX idx_kr_objective ON key_results(objective_id);

-- Check-ins semanales (historial inmutable → gráfica de progreso y confianza)
CREATE TABLE kr_checkins (
    id           SERIAL PRIMARY KEY,
    kr_id        INTEGER NOT NULL REFERENCES key_results(id) ON DELETE CASCADE,
    user_id      INTEGER NOT NULL REFERENCES users(id),
    valor        NUMERIC(12,2) NOT NULL,
    confianza    VARCHAR(10) NOT NULL DEFAULT 'verde'
                 CHECK (confianza IN ('verde','amarillo','rojo')),
    comentario   TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_checkin_kr_fecha ON kr_checkins(kr_id, created_at);

-- Puente tareas ↔ KRs: la tarea existente ES la iniciativa
CREATE TABLE task_key_results (
    task_id  INTEGER NOT NULL REFERENCES tasks(id)       ON DELETE CASCADE,
    kr_id    INTEGER NOT NULL REFERENCES key_results(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, kr_id)
);
CREATE INDEX idx_tkr_kr ON task_key_results(kr_id);
```

Notas de arquitectura: (1) no se toca la tabla `tasks` — la relación vive en el puente, cero riesgo de regresión sobre Kanban/Eisenhower/Riesgos; (2) `parent_id` en `objectives` habilita el árbol empresa→equipo→individuo sin tabla extra, suficiente para equipos de 10–50; (3) `kr_checkins` es append-only: el valor vigente se denormaliza en `key_results.valor_actual` para lecturas baratas desde Streamlit, y el historial alimenta la gráfica burn-up.

### 4. Casos de uso del domain layer

Un `OKRService` en `domain/services.py` (o `domain/okr_service.py`), puro, operando sobre dicts como los demás servicios, más dataclasses ligeras en `domain/entities.py`.

```python
from dataclasses import dataclass
from datetime import date

@dataclass
class KRProgress:
    kr_id: int
    titulo: str
    progreso: float          # 0.0-1.0
    confianza: str           # ultimo check-in: verde|amarillo|rojo
    dias_sin_checkin: int

@dataclass
class ObjectiveReport:
    objective_id: int
    titulo: str
    progreso: float
    progreso_esperado: float
    salud: float             # progreso - esperado
    semaforo: str            # verde|amarillo|rojo
    krs: list[KRProgress]

@dataclass
class AlignmentReport:
    total_tareas_activas: int
    tareas_vinculadas: int
    ratio: float
    huerfanas: list[dict]    # tareas sin KR


class OKRService:

    @staticmethod
    def progreso_kr(inicial: float, meta: float, actual: float) -> float:
        # span = meta - inicial; si span == 0 -> ValueError (bloqueado por CHECK en BD)
        # return clamp((actual - inicial) / span, 0.0, 1.0)
        ...

    def progreso_objective(self, krs: list[dict]) -> float:
        # suma ponderada de progreso_kr(kr) * kr["peso"] / suma de pesos
        # lista vacia -> 0.0
        ...

    def reporte_objective(
        self, objective: dict, krs: list[dict],
        checkins: list[dict], hoy: date,
        ciclo_inicio: date, ciclo_fin: date,
    ) -> ObjectiveReport:
        # 1. progreso = self.progreso_objective(krs)
        # 2. esperado = (hoy - ciclo_inicio).days / (ciclo_fin - ciclo_inicio).days, clamp 0..1
        # 3. salud = progreso - esperado
        # 4. semaforo: >= -0.10 verde; >= -0.25 amarillo; else rojo
        # 5. por KR: ultimo check-in -> confianza y dias_sin_checkin
        ...

    def valor_actual_derivado(self, kr: dict, tareas_vinculadas: list[dict]) -> float:
        # measure_type == 'task_count' -> len([t for t in tareas si estado == 'Completado'])
        # measure_type == 'task_pct'   -> completadas / total * 100 (0 si total == 0)
        # measure_type == 'manual'     -> kr["valor_actual"] sin cambios
        ...

    def alineacion(self, tareas: list[dict], vinculos: set[int]) -> AlignmentReport:
        # activas = tareas con estado != 'Completado'
        # vinculadas = [t for t in activas if t["id"] in vinculos]
        # huerfanas = resto; ratio = vinculadas/activas (0 si no hay activas)
        ...

    def grade_final(self, krs: list[dict]) -> float:
        # promedio simple de progreso_kr al cierre, redondeado a 2 decimales
        # (Google style: se congela en objectives.grade_final al cerrar el ciclo)
        ...

    def checkins_pendientes(self, krs: list[dict], checkins: list[dict],
                            hoy: date, umbral_dias: int = 7) -> list[dict]:
        # KRs cuyo ultimo check-in tiene mas de umbral_dias -> alimenta recordatorios
        ...
```

Todo es determinista y sin I/O: `crud.py` trae los dicts, el servicio calcula, la vista pinta. Idéntico patrón que `AnalyticsService.por_responsable`, lo que mantiene la testabilidad unitaria al 100% sin base de datos.

### 5. Diseño de API REST

Consistente con `/api/tasks` y `/api/analytics/...`, routers nuevos en `api/routers/okrs.py`, protegidos por el JWT existente.

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/api/okrs/cycles` | Listar ciclos |
| POST | `/api/okrs/cycles` | Crear ciclo (solo `role=admin`) |
| POST | `/api/okrs/cycles/{id}/close` | Cerrar ciclo y congelar grades |
| GET | `/api/okrs/objectives?cycle_id=1` | Objetivos con progreso calculado |
| POST | `/api/okrs/objectives` | Crear objetivo |
| PATCH | `/api/okrs/objectives/{id}` | Editar/cancelar |
| POST | `/api/okrs/key-results` | Crear KR bajo un objetivo |
| POST | `/api/okrs/key-results/{id}/checkins` | Registrar check-in |
| GET | `/api/okrs/key-results/{id}/checkins` | Historial (burn-up) |
| POST | `/api/okrs/key-results/{id}/tasks` | Vincular tarea existente |
| DELETE | `/api/okrs/key-results/{kr_id}/tasks/{task_id}` | Desvincular |
| GET | `/api/okrs/alignment?cycle_id=1` | Ratio de alineación + tareas huérfanas |

Ejemplos de payload:

```json
POST /api/okrs/objectives
{
  "cycle_id": 1,
  "titulo": "Estabilizar la plataforma para los pilotos",
  "nivel": "equipo",
  "owner_id": 3,
  "parent_id": null
}
```

```json
POST /api/okrs/key-results
{
  "objective_id": 7,
  "titulo": "Reducir bugs criticos abiertos de 14 a 2",
  "owner_id": 4,
  "measure_type": "manual",
  "unidad": "numero",
  "valor_inicial": 14,
  "valor_meta": 2,
  "es_aspiracional": false
}
```

```json
POST /api/okrs/key-results/12/checkins
{
  "valor": 6,
  "confianza": "verde",
  "comentario": "Cerramos los 3 bugs del generador esta semana"
}
```

Respuesta de `GET /api/okrs/objectives?cycle_id=1` (recortada):

```json
[
  {
    "id": 7,
    "titulo": "Estabilizar la plataforma para los pilotos",
    "owner": {"id": 3, "name": "Ana", "color": "#2563EB"},
    "progreso": 0.73,
    "progreso_esperado": 0.62,
    "semaforo": "verde",
    "key_results": [
      {"id": 12, "titulo": "Reducir bugs criticos de 14 a 2",
       "progreso": 0.67, "confianza": "verde",
       "valor_actual": 6, "valor_meta": 2, "tareas_vinculadas": 5}
    ]
  }
]
```

Regla de consistencia: los KRs con `measure_type` derivado recalculan `valor_actual` en el GET (o vía trigger de aplicación al completar una tarea), nunca en la UI.

### 6. Vista o componente de UI

Nueva vista `ui/views/okrs.py`, entrada "OKRs" en la navegación de `ui/app.py`, entre "Analytics" y "Equipo".

**Zona superior (contexto del ciclo):** un `st.selectbox` de ciclo (default: el activo), y a su derecha 4 `st.metric`: progreso global del ciclo, progreso esperado (con delta = salud), % de alineación de tareas, y % de check-ins al día. Una barra de progreso fina (`st.progress`) muestra cuánto del trimestre transcurrió.

**Cuerpo (lista de objetivos):** cada Objective es un `st.expander` cuyo título compone semáforo + título + progreso: "🟢 Estabilizar la plataforma para los pilotos — 73%". Dentro:

- Fila por KR: avatar de color del owner (reusa `users.color` como en Equipo), título, `st.progress` con el porcentaje, chip de confianza del último check-in y "hace N días". Si N > 7, el chip se pinta ámbar con "check-in pendiente".
- Botón "Registrar check-in" que abre un `st.dialog` (patrón modal de Streamlit): `st.number_input` para el valor, `st.radio` horizontal verde/amarillo/rojo, `st.text_area` de comentario.
- Pestaña interna (`st.tabs`: "Progreso" / "Tareas"): "Progreso" grafica el burn-up de check-ins contra la línea diagonal ideal (Plotly, como en Analytics); "Tareas" lista las tareas vinculadas con su estado Kanban y un `st.multiselect` para vincular/desvincular tareas existentes (búsqueda por descripción).

**Zona inferior ("Trabajo huérfano"):** tabla de tareas activas sin KR, con acción rápida "vincular a...". Es deliberadamente incómoda de ignorar: es el gancho de comportamiento que diferencia a Cenit de un tracker de OKRs standalone.

**Integración transversal (el detalle que vende):** en la tarjeta de tarea del Kanban y en el formulario de creación/edición de tarea aparece un selector opcional "🎯 Key Result". Así la vinculación ocurre donde el usuario ya vive —el tablero—, no en una vista aparte que nadie visita. Solo `role=admin` (o el owner del objetivo) puede crear/editar objetivos; todos pueden hacer check-in de sus KRs.

### 7. Estrategia de testing E2E

**Unitarios pytest (dominio puro, `tests/test_okr_service.py`):**

- `progreso_kr`: creciente (14→2 con actual 6 = 0.67), decreciente, clamp por encima de meta (=1.0), clamp por debajo de inicial (=0.0), parametrizado con `@pytest.mark.parametrize`.
- `progreso_objective`: pesos uniformes, pesos distintos, lista vacía → 0.0.
- `reporte_objective`: los tres cortes del semáforo exactamente en las fronteras (−0.10, −0.25) — el clásico bug off-by-epsilon.
- `valor_actual_derivado`: `task_pct` con 0 tareas vinculadas (división por cero), `task_count` con estados mixtos.
- `alineacion`: excluye completadas, ratio con 0 activas.
- `grade_final` y `checkins_pendientes` con fechas fijas inyectadas (`hoy: date` como parámetro — nunca `date.today()` dentro del servicio, para que los tests sean deterministas).

**Integración FastAPI (`tests/test_okr_api.py`, TestClient + SQLite):** CRUD de ciclo/objetivo/KR, check-in actualiza `valor_actual`, vincular tarea inexistente → 404, cerrar ciclo congela `grade_final` y bloquea nuevos check-ins (409), member no puede crear ciclo (403).

**E2E Playwright para Python (`tests/e2e/test_okr_flow.py`):** flujos críticos, en orden de valor:

1. **Ciclo de vida completo:** login admin → crear ciclo Q3 → crear objetivo con 2 KRs → verificar que aparecen con 0% → `expect(page.get_by_text("0%")).to_be_visible()`.
2. **Check-in mueve el número:** abrir dialog de check-in, registrar valor, verificar que la barra y el % del objetivo cambian sin recargar sesión (los `st.dialog` y reruns de Streamlit son terreno frágil: usar `page.get_by_role` y esperas explícitas por texto, nunca sleeps).
3. **Vinculación desde Kanban:** crear tarea en Kanban → asignarle un KR desde la tarjeta → completar la tarea → verificar que un KR `task_count` incrementa su valor actual. Este test cruza dos vistas y es el más valioso: cubre la integración que define al feature.
4. **Trabajo huérfano:** crear tarea sin KR → verificar que aparece en la tabla de huérfanas → vincular → desaparece.
5. **Permisos:** login como member → botón "Nuevo objetivo" no visible; check-in de su propio KR sí funciona.
6. **Cierre de ciclo:** cerrar ciclo → grades visibles y controles de edición deshabilitados.

Regla de oro heredada del perfil QA del founder: la matemática vive en unitarios (rápidos, exhaustivos en bordes); Playwright solo verifica *cableado* UI→API→BD, con un test por flujo, no por permutación.

### 8. Integraciones externas

En orden de retorno/esfuerzo para la etapa piloto:

1. **Slack (webhooks entrantes — esfuerzo mínimo, retorno máximo):** recordatorio semanal de check-in ("Bruno, tu KR 'bugs críticos' lleva 9 días sin actualización") y resumen de lunes con semáforos del ciclo. La cadencia es el 80% del éxito de OKRs; sin recordatorio, mueren en la semana 4. Un `POST` a un incoming webhook no requiere OAuth ni app review.
2. **GitHub API (fase 2):** KRs técnicos auto-medibles — "reducir issues abiertos con label bug", "aumentar % de PRs con tests". Encaja con el público (equipos dev LatAm que ya viven en GitHub) y con futuras métricas DORA: la misma integración sirve a dos metodologías.
3. **Google Sheets export (fase 2):** los CEOs de las pymes objetivo reportan a inversionistas/juntas en Sheets. Un export del cierre de ciclo elimina fricción de adopción real en Colombia/México.
4. **Google Calendar (opcional):** crear el evento recurrente de check-in semanal y la retro de cierre de ciclo.

Explícitamente **no** necesarias todavía: Typeform (los check-ins viven en la propia UI), Jira/Linear sync (Cenit compite con ellos, no se subordina en etapa piloto).

### 9. Conflictos o solapamientos

| Metodología | Tipo de conflicto | Resolución |
|---|---|---|
| **KPIs (sección 10)** | El más grave: ambos son "números con meta en un dashboard". Confundirlos es el error #1 de la industria. | Regla editorial dura en producto y docs: KPI = salud continua (motor: uptime, churn), sin fecha de fin; KR = cambio con deadline (viaje: de X a Y este trimestre). En datos pueden compartir la serie temporal de mediciones, pero un KR referencia ciclo y objetivo; un KPI no. Una sola vista "Métricas" con dos pestañas evita dos dashboards rivales. |
| **Scrum** | Cadencias que compiten (sprint de 2 sem vs. ciclo de 12) y dos jerarquías sobre las mismas tareas (sprint backlog vs. KR). | Son ortogonales: el sprint es el *cómo/cuándo* del trabajo, el KR es el *para qué*. La tabla puente lo refleja: una tarea puede tener sprint y KR a la vez. En la planeación de sprint, mostrar el KR de cada tarea candidata. |
| **Kanban** | Espacio de UI en la tarjeta (ya carga prioridad, estado, riesgo, cuadrante). | Un solo chip 🎯 discreto, tooltip con el KR. Nada más. |
| **DORA / SPACE** | Solapamiento de datos: deployment frequency o satisfacción pueden SER el valor de un KR. | Sinergia, no conflicto: `measure_type` futuro `'metric_ref'` apuntando a la métrica DORA/SPACE, una sola fuente de verdad. |
| **Eisenhower** | Conceptual: "importante" en Eisenhower debería significar "alineado a un OKR". | Oportunidad: una tarea vinculada a KR puede subir su señal de importancia en la clasificación Q1–Q4. Documentar la regla, no duplicar el dato. |
| **Lean** | Ninguno real: la vista de trabajo huérfano *es* detección de desperdicio Lean. | Compartir componente. |
| **SAFe / PMBOK** | SAFe trae sus propios OKRs a nivel de portfolio; PMBOK objetivos de proyecto. | Fuera de alcance para 10–50 personas; si algún día llega SAFe, los objectives de nivel 'empresa' con `parent_id` ya modelan el árbol. |
| **Waterfall / XP / Design Thinking** | Marginal (atención del usuario en docs, no en UI). | Sin acción. |

El conflicto de fondo es de **atención**: cada metodología añadida diluye el pitch de Cenit ("simple donde Jira es pesado"). OKRs debe entrar como una vista + un chip en la tarjeta, no como un módulo con sub-navegación propia.

### 10. Antipatrones conocidos

- **Jira Align (ex-AgileCraft):** enterprise-izó los OKRs — jerarquías de 5 niveles, campos obligatorios, workflows de aprobación. Resultado: los OKRs se vuelven reporting hacia arriba en vez de foco del equipo, y solo el PMO los mira. Lección para Cenit: cero campos obligatorios más allá de título, meta e inicial; crear un OKR debe tomar 60 segundos.
- **Jira "básico":** no tiene OKRs nativos; el mercado los resolvió con plugins (Oboard OKR Board etc.), y el resultado son epics disfrazados de objetivos: outputs con otro nombre ("Lanzar módulo X" como KR). Antipatrón conceptual: si un KR se puede "cerrar" como un ticket, no era un KR. Cenit lo previene estructuralmente: un KR *no tiene* estado done, solo valor numérico contra meta.
- **Trello:** sin modelo de datos para OKRs, los equipos hacen "un tablero de OKRs" con listas por objetivo y tarjetas por KR. Progreso manual en el título de la tarjeta ("KR1 [40%]"), cero conexión con el trabajo real, stale en dos semanas. Lección: OKRs sin vínculo automático a las tareas son un póster, no una herramienta — de ahí que `task_key_results` y los `measure_type` derivados sean el corazón del diseño, no un extra.
- **Asana Goals:** el mejor intento de los tres, con goals conectados a proyectos y actualización automática. Sus dos fallos: (a) el auto-progreso por % de tareas completadas invita a medir output ("hicimos 80% de las tareas" ≠ "logramos 80% del resultado") — Cenit lo mitiga haciendo `manual` el default y los tipos derivados una elección explícita; (b) Goals vive detrás del paywall Advanced, así que los equipos pequeños nunca lo prueban y se van a una herramienta OKR aparte. Lección GTM: en Cenit, OKRs va en el plan que usan los pilotos, porque es el feature que le habla al CTO/CEO comprador (quien firma no mueve tarjetas Kanban, pero sí mira semáforos de trimestre).
- **Antipatrón universal (todas las herramientas):** permitir OKRs atados a evaluación de desempeño individual. Grove lo advirtió hace 50 años: mata las metas aspiracionales. Cenit no debe construir jamás un reporte "grade por persona para RRHH".

### 11. Caso real

**Gtmhub (hoy Quantive)** es el caso más instructivo para Cenit, más que el manido Google. Fundada en Sofía, Bulgaria en 2015 —mercado periférico, como Colombia—, llegó a valuación >$1B especializándose en una sola cosa: OKRs conectados a datos reales. Su apuesta diferencial fueron los **"insights"**: 150+ conectores (Jira, GitHub, Salesforce, hojas de cálculo) para que el valor actual de un KR se actualice solo desde el sistema fuente. Entendieron que el punto de muerte de los OKRs es la actualización manual: si el número no se mueve solo, el ritual muere en la semana 4.

Qué copiar: (1) el KR auto-medible como ciudadano de primera clase — en Cenit, los `measure_type` derivados de `tasks` son el "conector" número uno y sale gratis porque la fuente de datos ya vive en casa, ventaja que Quantive tuvo que construir con 150 integraciones; (2) la cadencia como producto: recordatorios y resúmenes automáticos, no solo CRUD; (3) plantillas de OKRs por industria para arrancar en minutos — para Cenit, 5 plantillas para equipos dev LatAm ("estabilizar producto para pilotos", "reducir deuda de testing") reducen la página en blanco, que es la barrera real de adopción.

Qué no copiar: Quantive migró a enterprise (Whiteboards, strategy AI, precios opacos) y abandonó al equipo de 15 personas; ese hueco de "OKRs simples + ejecución en el mismo lugar, precio pyme LatAm" es exactamente el espacio de Cenit. Mención honorable: **Linear**, que resolvió el mismo problema sin llamarlo OKR — sus "Initiatives + Projects con targets" demuestran que la conexión objetivo→trabajo diario importa más que la ortodoxia del vocabulario.

### 12. Costo de implementación

**Medio: 3 sprints de 2 semanas** para 1–2 desarrolladores (asumiendo el patrón api/domain/ui ya establecido).

| Sprint | Entregable | Detalle |
|---|---|---|
| 1 | Núcleo de datos y dominio | Migración de las 5 tablas; `OKRService` completo con unitarios pytest (la matemática es simple; los bordes, muchos); routers CRUD de ciclos/objetivos/KRs con tests de integración. ~60% backend. |
| 2 | UI y vinculación | Vista `ui/views/okrs.py` (expanders, dialog de check-in, burn-up Plotly); chip/selector de KR en tarjeta Kanban y formulario de tarea; endpoint y tabla de alineación; `measure_type` derivados. |
| 3 | Cadencia y cierre | Recordatorios Slack (webhook), cierre de ciclo con grades congelados, vista de trabajo huérfano pulida, plantillas de arranque, suite E2E Playwright (6 flujos), documentación de usuario. |

Riesgo de estimación: el sprint 2 es el que se desborda — los `st.dialog` y el estado de sesión de Streamlit en interacciones anidadas (dialog dentro de expander dentro de tabs) suelen costar más de lo presupuestado. Colchón: recortar la pestaña burn-up a post-MVP si aprieta. Un MVP honesto (sprint 1 + vista básica sin Slack ni derivados) cabe en 2 sprints si el objetivo es solo demo a pilotos.

### 13. Cuándo NO construir esto todavía

Construir OKRs hoy sería prematuro si se da cualquiera de estas señales:

1. **Menos de ~3 equipos piloto usando el Kanban a diario.** OKRs es un feature de *retención y expansión* (le habla al CEO/CTO), no de *adquisición* (el usuario entra por el tablero). Poner objetivos encima de un hábito de ejecución que aún no existe es decorar una casa sin cimientos: el ratio de alineación daría 0% porque no hay tareas vivas que alinear.
2. **Ningún piloto lo ha pedido.** Con perfil QA, el founder debería tratar el roadmap como hipótesis testeable: si en las entrevistas de piloto nadie menciona "objetivos", "metas de trimestre" o "reportar a la junta", construirlo es sobre-ingeniería especulativa. La prueba barata: llevar el wireframe de la sección 6 a 3 conversaciones antes de escribir una línea.
3. **El propio equipo Teczonic (1–2 personas) no corre sus OKRs en una hoja de cálculo primero.** Dogfooding manual de un ciclo completo (12 semanas) enseña más sobre qué automatizar que cualquier spec. Si el ritual no sobrevive en Sheets, no sobrevivirá en Cenit.
4. **Las 5 vistas actuales aún tienen bugs abiertos o carecen de E2E estables.** Cada vista nueva multiplica superficie de regresión; para un equipo de 1–2, la deuda de calidad de lo existente siempre cobra interés antes que el feature nuevo.

La señal de "ya es hora": un piloto que renueva y pregunta "¿cómo le muestro a mi jefe que esto sirvió este trimestre?". Esa pregunta es, literalmente, el pitch de OKRs — y quien la hace es el comprador económico. Hasta entonces: hoja de cálculo, plantilla descargable en el blog como imán de leads, y el esquema SQL de la sección 3 guardado en este documento, listo para el sprint en que la demanda sea real.
