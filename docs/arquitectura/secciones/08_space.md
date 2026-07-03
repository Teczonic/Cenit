## 08. SPACE — Framework de Productividad de Desarrolladores

### 1. Principio central y origen

SPACE nace en marzo de 2021 con el paper *"The SPACE of Developer Productivity: There's more to it than you think"* (ACM Queue), firmado por Nicole Forsgren (GitHub, coautora de DORA y de *Accelerate*), Margaret-Anne Storey (Universidad de Victoria), Chandra Maddila, Thomas Zimmermann, Brian Houck y Jenna Butler (Microsoft Research). Es, literalmente, la respuesta de la autora de DORA a la pregunta que DORA no responde: *"¿cómo medimos la productividad de las personas, no solo del pipeline?"*.

El principio central es que **la productividad de un equipo de software es multidimensional y no puede reducirse a una sola métrica de actividad**. SPACE define cinco dimensiones:

| Dimensión | Qué mide | Ejemplo de métrica |
|---|---|---|
| **S** — Satisfaction & well-being | Satisfacción con el trabajo, herramientas y equipo; riesgo de burnout | eNPS del desarrollador, encuesta de satisfacción 1-5 |
| **P** — Performance | Resultado del trabajo, no el volumen | % de tareas completadas sin retrabajo, confiabilidad |
| **A** — Activity | Volumen de acciones (con cuidado) | Tareas completadas, commits, PRs, despliegues |
| **C** — Communication & collaboration | Cómo fluye la información | Tiempo de respuesta a revisiones, tareas bloqueadas esperando a otro |
| **E** — Efficiency & flow | Capacidad de avanzar sin interrupciones | Horas de foco, número de interrupciones, tiempo en estado "Pausado" |

La regla operativa del paper: medir **al menos tres dimensiones a la vez**, incluir **siempre al menos una métrica perceptual** (encuesta, no telemetría) y **nunca usar las métricas para evaluar individuos de forma punitiva**.

**El error de gestión que previene** es el más viejo de la industria: confundir actividad con productividad. Contar líneas de código (IBM, años 70-80), contar commits (GitHub graphs, años 2010), contar story points "entregados" (cargo cult de Scrum) o contar horas en silla. Ese error produce dos patologías: (a) los desarrolladores optimizan la métrica y no el resultado (ley de Goodhart), y (b) la gerencia no detecta el burnout hasta que la persona renuncia, porque el burnout suele ir acompañado de *alta* actividad. Para el fundador de Cenit —que vende a CTOs de equipos de 10-50 personas en LatAm donde la cultura de "gestión por presencia" sigue siendo fuerte— SPACE es un argumento de venta: *"Cenit no te dice quién trabaja más; te dice si tu equipo está sano y entrega"*.

Desde la perspectiva de producto, SPACE en Cenit no es una vista más: es la capa que da sentido humano a los datos que Kanban, Eisenhower y el análisis de riesgos ya generan. Cenit ya tiene A (throughput mensual en `AnalyticsService.throughput_mensual`), parte de P (lead time por responsable) y señales de E (estado "Pausado"). Lo que falta es S y C, que requieren datos nuevos: encuestas y trazas de colaboración.

### 2. Métricas y fórmulas exactas

SPACE no prescribe fórmulas cerradas (es un framework, no un estándar), pero para implementarlo en software hay que concretar. Definimos una métrica por dimensión, con su fórmula, y las aplicamos a un equipo ficticio de 5 personas: **Ana, Bruno, Carla, David y Elena**, durante un periodo de 4 semanas (1-28 de junio).

**S — Índice de satisfacción (encuesta quincenal, escala 1-5, 3 preguntas):**

```
S = promedio(respuestas) normalizado a 0-100 = (promedio - 1) / 4 * 100
```

Respuestas de la quincena: Ana 4.3, Bruno 3.7, Carla 2.3, David 4.0, Elena 3.3.
Promedio del equipo = (4.3+3.7+2.3+4.0+3.3)/5 = 17.6/5 = **3.52** → S = (3.52-1)/4*100 = **63.0/100**. Alerta individual: Carla < 3.0 (umbral de riesgo de burnout).

**P — Tasa de entrega limpia (performance):**

```
P = tareas completadas sin reapertura / tareas completadas * 100
```

El equipo completó 42 tareas en junio; 6 fueron reabiertas (volvieron de "Completado" a "En Proceso"). P = (42-6)/42 = 36/42 = **85.7%**.

**A — Throughput per cápita:**

```
A = tareas completadas / personas / semana
```

A = 42 / 5 / 4 = **2.1 tareas por persona por semana**. Nota del panel: esta métrica se muestra solo agregada por equipo, nunca en ranking individual.

**C — Latencia de desbloqueo (proxy de colaboración con los datos que Cenit ya tiene):**

```
C = promedio(horas entre entrar a "Pausado" y salir de "Pausado")
```

En junio hubo 15 transiciones a "Pausado" con duraciones (horas): 4, 8, 12, 24, 6, 48, 3, 10, 72, 5, 9, 16, 30, 7, 11. Suma = 265 → C = 265/15 = **17.7 horas promedio de bloqueo**. Si el equipo integra GitHub, C se enriquece con *time-to-first-review* de PRs.

**E — Ratio de flujo (efficiency):**

```
E = tiempo activo / (tiempo activo + tiempo pausado) * 100
   donde tiempo activo = Σ días en "En Proceso" y tiempo pausado = Σ días en "Pausado"
```

Junio: 178 días-tarea en "En Proceso", 32 días-tarea en "Pausado". E = 178/(178+32) = 178/210 = **84.8%**.

**Índice SPACE compuesto (opcional, para el semáforo del dashboard):**

```
SPACE_index = 0.30*S + 0.25*P + 0.10*A_norm + 0.15*C_norm + 0.20*E
```

donde A_norm = min(A/3, 1)*100 (3 tareas/persona/semana como referencia) y C_norm = max(0, 100 - C/0.48) (48 h de bloqueo = 0 puntos). Con los datos: A_norm = min(2.1/3,1)*100 = 70; C_norm = 100 - 17.7/0.48 = 100 - 36.9 = 63.1.

```
SPACE_index = 0.30*63.0 + 0.25*85.7 + 0.10*70 + 0.15*63.1 + 0.20*84.8
            = 18.90 + 21.43 + 7.00 + 9.47 + 16.96
            = 73.8 / 100  →  estado "saludable con alertas" (Carla en S)
```

Los pesos son configurables por equipo; el compuesto es un resumen ejecutivo, nunca sustituye las cinco dimensiones desagregadas.

### 3. Modelo de datos

Extiende `users` y `tasks` existentes. Tres necesidades nuevas: encuestas perceptuales (S), historial de transiciones de estado (C y E — hoy `tasks` solo guarda el estado actual) y snapshots calculados para el dashboard.

```sql
-- Encuestas SPACE (dimensión S, y opcionalmente C perceptual)
CREATE TABLE space_surveys (
    id            SERIAL PRIMARY KEY,
    titulo        VARCHAR(120) NOT NULL DEFAULT 'Pulso quincenal',
    dimension     VARCHAR(1)   NOT NULL CHECK (dimension IN ('S','P','A','C','E')),
    periodo_inicio DATE        NOT NULL,
    periodo_fin    DATE        NOT NULL,
    estado        VARCHAR(20)  NOT NULL DEFAULT 'abierta'
                  CHECK (estado IN ('borrador','abierta','cerrada')),
    anonima       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_by    INTEGER      REFERENCES users(id),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE space_survey_questions (
    id          SERIAL PRIMARY KEY,
    survey_id   INTEGER NOT NULL REFERENCES space_surveys(id) ON DELETE CASCADE,
    texto       TEXT    NOT NULL,
    tipo        VARCHAR(20) NOT NULL DEFAULT 'likert_5'
                CHECK (tipo IN ('likert_5','texto_libre','nps_10')),
    orden       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE space_survey_responses (
    id           SERIAL PRIMARY KEY,
    question_id  INTEGER NOT NULL REFERENCES space_survey_questions(id) ON DELETE CASCADE,
    -- NULL si la encuesta es anónima; el token evita respuestas duplicadas
    user_id      INTEGER REFERENCES users(id),
    respuesta_num  NUMERIC(4,1),
    respuesta_texto TEXT,
    anon_token   VARCHAR(64),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT una_respuesta UNIQUE (question_id, anon_token)
);

-- Historial de transiciones de estado (base de C y E; hoy Cenit no lo persiste)
CREATE TABLE task_state_transitions (
    id            SERIAL PRIMARY KEY,
    task_id       INTEGER     NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    estado_desde  VARCHAR(30),
    estado_hasta  VARCHAR(30) NOT NULL,
    changed_by    INTEGER     REFERENCES users(id),
    changed_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    motivo_bloqueo TEXT        -- se pide solo al pasar a 'Pausado'
);
CREATE INDEX idx_transitions_task ON task_state_transitions(task_id, changed_at);

-- Reaperturas de tareas (dimensión P)
CREATE TABLE task_reopenings (
    id          SERIAL PRIMARY KEY,
    task_id     INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    reopened_by INTEGER REFERENCES users(id),
    razon       TEXT,
    reopened_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Snapshot calculado por periodo (evita recalcular todo en cada carga de UI)
CREATE TABLE space_snapshots (
    id             SERIAL PRIMARY KEY,
    entidad        VARCHAR(50) NOT NULL,          -- espeja tasks.entidad (equipo)
    periodo_inicio DATE        NOT NULL,
    periodo_fin    DATE        NOT NULL,
    s_score        NUMERIC(5,1),
    p_score        NUMERIC(5,1),
    a_score        NUMERIC(5,1),   -- tareas/persona/semana
    c_horas        NUMERIC(6,1),   -- latencia de desbloqueo promedio
    e_score        NUMERIC(5,1),
    space_index    NUMERIC(5,1),
    detalle        JSONB,          -- desgloses, alertas individuales de S (solo ids con consentimiento)
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT snapshot_unico UNIQUE (entidad, periodo_inicio, periodo_fin)
);
```

Decisión de diseño defendida por el arquitecto: `task_state_transitions` es la tabla más valiosa del bloque, porque además de SPACE alimenta al futuro cálculo fino de lead/cycle time (Kanban/DORA). Se puebla con un hook en `crud.update_task` cuando cambia `estado` — un solo punto de escritura, sin triggers de base de datos que complicarían la paridad SQLite/PostgreSQL.

### 4. Casos de uso del domain layer

Un `SpaceService` en `domain/services.py` (o `domain/space.py` si crece), puro y testeable, coherente con el estilo actual de operar sobre dicts serializados.

```python
from dataclasses import dataclass
from datetime import date

@dataclass
class SpaceReport:
    entidad: str
    periodo_inicio: date
    periodo_fin: date
    s_score: float | None      # None si no hubo encuesta en el periodo
    p_score: float
    a_score: float
    c_horas: float | None
    e_score: float
    space_index: float | None
    alertas: list[str]         # ej. ["S del equipo < 60", "1 persona bajo umbral"]

class SpaceService:

    def calcular_satisfaccion(
        self, respuestas: list[dict]
    ) -> tuple[float | None, list[str]]:
        # filtrar respuestas tipo likert_5 con respuesta_num
        # promedio = sum / n ; normalizar: (promedio - 1) / 4 * 100
        # alertas: por cada user_id (si no anónima) con promedio < 3.0
        # return (round(norm, 1), alertas) o (None, []) si n == 0
        ...

    def calcular_performance(
        self, tareas: list[dict], reaperturas: list[dict]
    ) -> float:
        # completadas = [t for t in tareas if t["estado"] == "Completado"]
        # reabiertas = {r["task_id"] for r in reaperturas}
        # limpias = completadas cuyo id no está en reabiertas
        # return round(len(limpias) / max(len(completadas), 1) * 100, 1)
        ...

    def calcular_actividad(
        self, tareas: list[dict], n_personas: int, semanas: float
    ) -> float:
        # completadas_en_periodo / n_personas / semanas, redondeado a 1 decimal
        ...

    def calcular_latencia_bloqueo(
        self, transiciones: list[dict]
    ) -> float | None:
        # emparejar por task_id: entrada a 'Pausado' con la siguiente salida
        # duraciones = [(salida.changed_at - entrada.changed_at).total_seconds()/3600]
        # bloqueos aún abiertos al cierre del periodo cuentan hasta periodo_fin
        # return round(mean(duraciones), 1) o None si no hubo bloqueos
        ...

    def calcular_flujo(self, transiciones: list[dict]) -> float:
        # acumular días-tarea en 'En Proceso' (activo) y 'Pausado' (pausado)
        # recorriendo pares consecutivos de transiciones por task_id
        # return round(activo / max(activo + pausado, 0.001) * 100, 1)
        ...

    def generar_reporte(
        self,
        entidad: str,
        periodo_inicio: date,
        periodo_fin: date,
        tareas: list[dict],
        transiciones: list[dict],
        reaperturas: list[dict],
        respuestas: list[dict],
        n_personas: int,
        pesos: dict[str, float] | None = None,
    ) -> SpaceReport:
        # orquesta las 5 funciones anteriores
        # space_index = None si s_score es None (regla: sin métrica perceptual
        # no hay índice compuesto — fidelidad al paper)
        # alertas: S < 60, C > 24h, E < 70, P < 80
        ...
```

Nótese la regla embebida en `generar_reporte`: si no hay datos de encuesta, el índice compuesto no se calcula. Es la salvaguarda del framework contra degenerarse en un dashboard de pura telemetría.

### 5. Diseño de API REST

Consistente con `/api/tasks` y `/api/analytics/...` existentes. Todo bajo auth JWT; los endpoints de creación de encuestas exigen `role == "admin"`.

| Método | Ruta | Propósito |
|---|---|---|
| POST | `/api/space/surveys` | Crear encuesta de pulso (admin) |
| GET | `/api/space/surveys?estado=abierta` | Listar encuestas |
| POST | `/api/space/surveys/{id}/responses` | Responder encuesta |
| GET | `/api/analytics/space?entidad=X&desde=...&hasta=...` | Reporte SPACE del periodo |
| GET | `/api/analytics/space/history?entidad=X&n=6` | Últimos N snapshots (tendencia) |
| GET | `/api/tasks/{id}/transitions` | Historial de estados de una tarea |

Crear encuesta:

```json
POST /api/space/surveys
{
  "titulo": "Pulso quincenal — Junio 2a",
  "dimension": "S",
  "periodo_inicio": "2026-06-15",
  "periodo_fin": "2026-06-28",
  "anonima": true,
  "preguntas": [
    {"texto": "¿Qué tan satisfecho estás con tu trabajo esta quincena?", "tipo": "likert_5", "orden": 1},
    {"texto": "¿Tienes las herramientas que necesitas?", "tipo": "likert_5", "orden": 2},
    {"texto": "¿Algo que te esté frenando?", "tipo": "texto_libre", "orden": 3}
  ]
}
```

Respuesta del reporte:

```json
GET /api/analytics/space?entidad=Desarrollo&desde=2026-06-01&hasta=2026-06-28
{
  "entidad": "Desarrollo",
  "periodo": {"inicio": "2026-06-01", "fin": "2026-06-28"},
  "s_score": 63.0,
  "p_score": 85.7,
  "a_score": 2.1,
  "c_horas": 17.7,
  "e_score": 84.8,
  "space_index": 73.8,
  "alertas": [
    "1 respuesta individual bajo umbral de satisfacción (3.0)",
    "3 bloqueos superaron 24 horas"
  ],
  "participacion_encuesta": 1.0
}
```

El campo `alertas` nunca nombra personas en respuestas de equipo; el detalle individual de S solo es visible para el propio usuario (y agregados anónimos para el admin), decisión ética alineada con el paper y con la venta B2B: un CTO en Colombia comprará antes una herramienta que su equipo no perciba como vigilancia.

### 6. Vista o componente de UI

Nueva vista `ui/views/space.py` ("Salud del equipo"), registrada en la navegación de `ui/app.py` junto a analytics.

**Zona superior — el radar.** Un `st.plotly_chart` con gráfico de radar de 5 ejes (S, P, A, C, E), cada eje normalizado 0-100, con el polígono del periodo actual en color primario y el del periodo anterior en gris translúcido para comparar de un vistazo. A la derecha, `st.metric` grande con el SPACE index (73.8) y su delta contra el periodo anterior, más un semáforo textual ("Saludable", "Con alertas", "En riesgo").

**Selector de contexto.** En la barra lateral o cabecera: `st.selectbox` de entidad/equipo (mismo patrón que `FiltroService.filtrar_por_entidad`), `st.select_slider` de periodo (últimas 2/4/8 semanas) y un expander "Pesos del índice" con 5 sliders para admins.

**Zona media — cinco tarjetas de dimensión.** `st.columns(5)`, una tarjeta por letra: valor, mini-sparkline de los últimos 6 snapshots (`st.line_chart` compacto) y el texto de la métrica ("17.7 h promedio bloqueado"). Clic (vía `st.button` en la tarjeta) expande el detalle: para C, tabla de los bloqueos más largos con su `motivo_bloqueo`; para P, lista de tareas reabiertas con razón; para S, histograma de distribución de respuestas (nunca respuestas individuales identificadas).

**Zona de alertas.** `st.warning` por cada alerta activa, con acción sugerida: "3 bloqueos > 24 h → revisa la columna Pausado del Kanban" con link que navega a la vista kanban prefiltrada.

**Widget de encuesta embebido.** Si el usuario logueado tiene una encuesta abierta sin responder, la vista (y también `mi_dia.py`, para maximizar participación) muestra un `st.form` de 3 preguntas con `st.radio` horizontal 1-5 y un `st.text_area` opcional. Enviar tarda menos de 20 segundos — la fricción de la encuesta es el principal predictor de participación, y participación < 60% invalida S.

**Estado vacío.** Si no hay encuestas ni transiciones aún, la vista muestra un onboarding: "Activa el pulso quincenal" (botón admin) y explica qué empezará a medirse. Nunca un radar vacío.

### 7. Estrategia de testing E2E

**Pytest unitario del dominio** (donde vive el valor; `SpaceService` es puro y no toca DB):

- `test_satisfaccion_normaliza_likert`: respuestas [4.3, 3.7, 2.3, 4.0, 3.3] → 63.0 y una alerta individual.
- `test_satisfaccion_sin_respuestas_devuelve_none`: lista vacía → (None, []).
- `test_performance_con_reaperturas`: 42 completadas, 6 reabiertas → 85.7.
- `test_performance_division_por_cero`: 0 completadas → 0.0 sin excepción.
- `test_latencia_bloqueo_empareja_transiciones`: entrada/salida de Pausado por task_id, incluidos bloqueos abiertos al cierre del periodo (cuentan hasta `periodo_fin`).
- `test_flujo_ignora_estados_no_relevantes`: transiciones por "No Iniciado" y "Completado" no suman al denominador.
- `test_reporte_sin_encuesta_no_calcula_indice`: `space_index is None` si `s_score is None` — el test que protege la regla de oro del framework.
- Property-based (hypothesis): el índice compuesto siempre queda en [0, 100] para cualquier combinación válida de entradas.

**Playwright para Python** (E2E sobre Streamlit + API reales, patrón `page.get_by_test_id` con `st.container(key=...)`):

1. **Flujo pulso completo**: admin crea encuesta → logout → login como member → banner de encuesta visible en Mi Día → responde 3 preguntas → submit → el banner desaparece → admin ve participación 1/N en la vista SPACE.
2. **Anonimato**: con encuesta anónima, la API de detalle no expone `user_id` (assert sobre respuesta de red interceptada con `page.expect_response`), y la UI de admin muestra solo histograma.
3. **Transiciones alimentan C/E**: mover una tarjeta a "Pausado" en Kanban (ingresando motivo) → esperar → mover a "En Proceso" → la vista SPACE refleja un bloqueo con duración > 0 y el motivo aparece en el detalle de C.
4. **Reapertura alimenta P**: completar tarea → reabrirla con razón → P baja en el reporte del periodo.
5. **Regresión visual ligera** del radar: screenshot comparativo del contenedor del gráfico (tolerancia alta; validar más bien los números con `expect(locator).to_contain_text("73.8")`).
6. **Permisos**: member no ve el botón "Crear encuesta" ni los sliders de pesos; llamada directa a `POST /api/space/surveys` con token member → 403.

Los tests de API (crear encuesta, responder duplicado → 409 por `una_respuesta`, snapshot idempotente por `snapshot_unico`) van con `TestClient` de FastAPI, más rápidos que Playwright y suficientes para el contrato.

### 8. Integraciones externas

| Integración | Dimensión | Por qué |
|---|---|---|
| **Slack (webhooks + slash command)** | S, C | Entregar el pulso quincenal donde el equipo ya vive dispara la participación (responder desde Slack sin abrir Cenit). Además, recordatorios de bloqueos > 24 h al canal del equipo. Es la integración #1 en valor/esfuerzo. |
| **GitHub API (REST/GraphQL)** | A, C, P | PRs abiertos/mergeados enriquecen A; *time-to-first-review* es la métrica C canónica de SPACE; PRs revertidos alimentan P. Para el ICP de Cenit (equipos dev LatAm), GitHub es casi universal. |
| **GitLab API** | A, C, P | Mismo rol que GitHub; en LatAm corporativo (bancos, telcos) GitLab self-hosted es frecuente. Segunda ola, misma interfaz interna (`GitProvider` abstracto). |
| **Google Calendar API** | E | Tiempo en reuniones vs. bloques de foco ≥ 2 h es la métrica E perceptualmente más potente para un CTO. Requiere OAuth por usuario y manejo cuidadoso de privacidad: solo agregados, nunca títulos de eventos. Tercera ola. |
| **Typeform / Google Forms** | S | Explícitamente **no** se integra: la encuesta nativa (o vía Slack) mantiene los datos en el modelo propio y evita fricción de cuentas externas. Construir encuestas likert de 3 preguntas es trivial; el valor está en el análisis, no en el formulario. |

Advertencia del arquitecto: cada integración introduce sincronización, tokens y rate limits. La arquitectura correcta es un módulo `integrations/` con adaptadores que escriben en tablas de staging (`external_events`), y `SpaceService` sigue leyendo solo del modelo propio — el dominio nunca conoce a GitHub.

### 9. Conflictos o solapamientos

SPACE es un framework paraguas, así que colisiona con casi todo el catálogo de Cenit. Los tres conflictos serios:

- **DORA (sección 07)**: el solapamiento más directo — misma autora, y las 4 métricas DORA son, según el propio paper, un subconjunto de SPACE (deployment frequency es A; lead time y MTTR son E/P; change failure rate es P). *Resolución*: DORA y SPACE comparten vista y modelo de datos en Cenit. DORA es la pestaña "Delivery" (máquina) y SPACE la pestaña "Equipo" (personas) de un mismo módulo "Salud de ingeniería". Nunca dos vistas hermanas compitiendo en la navegación, y `task_state_transitions` sirve a ambas.
- **KPIs (sección 10)**: riesgo de que el usuario perciba SPACE como "otros 5 KPIs más". *Resolución*: los KPIs genéricos de Cenit son configurables por el usuario; las métricas SPACE son opinadas y vienen con umbrales y alertas predefinidos. SPACE se presenta como un *producto empaquetado* ("Salud del equipo"), no como una lista de indicadores.
- **OKRs (sección 09)**: tensión conceptual — la tentación de poner "subir el SPACE index a 80" como Key Result convierte una métrica de salud en objetivo y activa Goodhart. *Resolución de producto*: la UI de OKRs permite *vincular* métricas SPACE como "métricas de salud" (health metrics, patrón de Linear/Amplitude) pero no como KRs con progreso.

Solapamientos menores: **Kanban** ya posee la columna Pausado y el throughput — SPACE consume esos datos, no los duplica (E y C se calculan de las mismas transiciones; la vista Kanban gana el campo `motivo_bloqueo` como mejora colateral). **Lean** comparte la obsesión por el flujo (E es puro Lean); **XP** comparte la preocupación por sostenibilidad (S es la versión medible del "sustainable pace"); **Scrum** puede leer S como insumo de retrospectivas. Con **Waterfall, SAFe, PMBOK y Design Thinking** no hay conflicto de datos ni de UI, solo competencia genérica por atención en la navegación, que se resuelve con el módulo unificado de salud.

### 10. Antipatrones conocidos

- **Jira: actividad disfrazada de productividad.** Los dashboards de Jira empujan velocity, burndown y "issues resueltos por asignado", exactamente la dimensión A aislada que SPACE prohíbe. Generaciones de managers hicieron ranking de desarrolladores por tickets cerrados; los desarrolladores respondieron partiendo tareas en confeti. Lección para Cenit: **nunca ofrecer una tabla ordenable de tareas completadas por persona** en el contexto SPACE (la vista `equipo.py` actual debe revisarse con este lente).
- **Jira/Azure DevOps: cero perceptual.** Ninguna herramienta grande de gestión incorpora encuestas de satisfacción junto a las métricas de entrega; delegaron S a herramientas de HR (Officevibe, CultureAmp) y así el CTO ve la entrega y HR ve el burnout, sin cruzarlos jamás. La oportunidad de Cenit es precisamente ese cruce en una sola pantalla.
- **Trello: sin memoria de estados.** Trello no persiste historial de transiciones consultable (solo un activity log plano), haciendo imposible calcular flujo o latencia de bloqueo. Antipatrón de datos: si no guardas transiciones desde el día uno, no puedes reconstruir E retroactivamente — razón para crear `task_state_transitions` *antes* de construir la vista.
- **Asana: el "productivity score" opaco.** Asana y otras (y las herramientas de vigilancia tipo Hubstaff, muy vendidas en LatAm) redujeron productividad a un número individual calculado con actividad (clics, horas activas). Es el anti-SPACE canónico: individual, punitivo, solo-A. Cenit debe diferenciarse explícitamente en el copy: métricas de equipo, con dimensión humana, sin ranking.
- **GitHub: el contribution graph.** Irónicamente, la empresa del paper mantiene el cuadrito verde que incentiva commits diarios performativos. Lección: un elemento de UI aparentemente inocuo puede instaurar el incentivo equivocado durante una década.

### 11. Caso real

**DX (getdx.com), fundada por Abi Noda con Nicole Forsgren y Margaret-Anne Storey como asesoras/investigadoras**, es la implementación comercial de referencia de SPACE (y de su evolución, los *DevEx dimensions* y el *DX Core 4*, 2023-2025). Qué hicieron bien y qué copiar:

1. **Encuesta primero, telemetría después.** DX arrancó como producto de encuestas trimestrales bien diseñadas (preguntas validadas psicométricamente) y solo después añadió métricas de sistemas. Validó que la dimensión perceptual, la más barata de construir, es la que los CTOs pagan primero — excelente noticia para un equipo de 1-2 devs: el MVP de SPACE en Cenit es la encuesta más el radar, no la integración con GitHub.
2. **Benchmarks como gancho de venta.** DX vende comparación contra percentiles de la industria ("tu time-to-first-review está en el p25"). Cenit, con datos multi-tenant en el futuro, puede ofrecer benchmarks LatAm — un activo que Jira no tiene localizado.
3. **Snippets accionables, no dashboards pasivos.** Cada métrica en DX viene con "qué hacer al respecto". El campo `alertas` con acción sugerida de la sección 6 replica este patrón.
4. **Privacidad como feature comercial.** DX publica su política de no-vigilancia individual y la usa en ventas contra herramientas de monitoreo. En LatAm, donde el monitoreo invasivo de empleados es común, esta postura diferencia y además reduce el riesgo legal (leyes de habeas data en Colombia).

Mención honrosa: LinkedIn (Developer Insights team, con Max Kanat-Alexander) publicó cómo operacionalizó SPACE internamente con su Developer Productivity & Happiness framework — su lección es la cadencia: encuesta trimestral profunda más pulso corto frecuente, exactamente el diseño de `space_surveys` propuesto.

### 12. Costo de implementacion

**Costo: MEDIO.** Estimación para 1-2 desarrolladores, sprints de 2 semanas:

| Sprint | Entregable | Detalle |
|---|---|---|
| 1 | Cimientos de datos | `task_state_transitions` + `task_reopenings` + hook en `crud.update_task`; migración; backfill parcial desde `created_at`/`fecha_completado`; `motivo_bloqueo` en la UI de Kanban; tests pytest |
| 2 | Encuestas (S) | Tablas de surveys, endpoints CRUD + responder, widget en `mi_dia.py`, `calcular_satisfaccion`, anonimato y constraint anti-duplicados; tests API |
| 3 | Motor y vista | Resto de `SpaceService` (P, A, C, E, índice), `space_snapshots`, endpoint `/api/analytics/space`, vista `ui/views/space.py` con radar y tarjetas; E2E Playwright de los flujos 1-4 |
| 4 (opcional) | Integraciones ola 1 | Slack para entrega de pulso y alertas de bloqueo; pulido, umbrales configurables, snapshot job |

**Total: 3 sprints el núcleo, 4 con Slack (6-8 semanas).** El sprint 1 es el más importante y el menos vistoso: sin historial de transiciones no hay C ni E honestas jamás. El QA lead insiste: presupuestar ~20% de cada sprint a tests, y el sprint 1 debe salir aunque SPACE completo se postergue, porque el costo de no capturar transiciones es irreversible.

### 13. Cuando NO construir esto todavia

SPACE es prematuro para Cenit **hoy**, con dos excepciones quirúrgicas. Señales concretas de sobre-ingeniería:

- **Menos de ~8 usuarios activos por equipo cliente**: con equipos de 3-4 personas, S no es anonimizable (con 3 respuestas todos saben quién puso 2/5) y las métricas agregadas tienen varianza absurda. SPACE necesita el ICP de 10-50 personas *ya usando Cenit a diario*, no pilotos tibios.
- **Pre-retención**: si los pilotos aún no usan el Kanban consistentemente, no hay transiciones de estado reales que medir; el radar mostraría ruido y quemaría la credibilidad de la vista analytics existente.
- **Sin comprador identificado**: SPACE lo compra un CTO/VP con dolor de burnout o rotación. Si en las conversaciones de venta ese dolor no aparece espontáneamente al menos en 3 de cada 10 pilotos, construirlo es empujar oferta sin demanda.
- **El propio Goodhart interno**: construir SPACE para que el pitch deck diga "tenemos IA... digo, tenemos SPACE" es hacer feature-signaling, el equivalente founder del developer que optimiza commits.

**Las dos excepciones que SÍ conviene hacer ya** (coste marginal, valor irreversible): (1) la tabla `task_state_transitions` con su hook — datos que no se pueden reconstruir después y que también sirven a Kanban y DORA; (2) el campo `motivo_bloqueo` al pausar, que mejora la vista de riesgos hoy. Todo lo demás —encuestas, radar, índice, Slack— espera a tener 3-5 clientes pagando con equipos de 10+ personas y uso diario sostenido. En el roadmap de Cenit, SPACE es la feature de *expansión y retención* (lo que hace que el CTO renueve y suba de plan), no la de adquisición.
