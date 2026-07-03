# (Seccion 07 de 12 — Panel de expertos Cenit)

## 07. DORA

### 1. Principio central y origen

DORA (DevOps Research and Assessment) nace del programa de investigacion iniciado en 2014 por Nicole Forsgren, Jez Humble y Gene Kim, materializado en los reportes anuales *State of DevOps* y en el libro *Accelerate* (2018). Google adquirio DORA en 2018 y hoy mantiene la investigacion como parte de Google Cloud. La tesis central, validada con datos de mas de 30.000 profesionales a lo largo de una decada: **el rendimiento en entrega de software es medible con cuatro metricas, y ese rendimiento predice resultados de negocio** (rentabilidad, cuota de mercado, satisfaccion del equipo).

El problema que resuelve es concreto: antes de DORA, los equipos median su "productividad" con proxies toxicos — lineas de codigo, horas trabajadas, story points completados, numero de commits. DORA reencuadra la pregunta: no importa cuanto *produces*, importa **con que velocidad y estabilidad entregas valor a produccion**. Las cuatro metricas capturan dos tensiones que la industria creia opuestas y que la investigacion demostro correlacionadas: *throughput* (frecuencia de despliegue, lead time de cambios) y *estabilidad* (tasa de fallo de cambios, tiempo de restauracion). Los equipos de elite son rapidos **y** estables a la vez; no existe el trade-off que los gerentes tradicionales asumian.

El error de gestion que previene es doble. Primero, el **teatro de la productividad**: premiar actividad visible (tickets movidos, horas registradas) en vez de resultados entregados. Segundo, la **falsa dicotomia velocidad-calidad**: gerentes que frenan despliegues "para reducir riesgo" y logran exactamente lo contrario, porque lotes grandes de cambios son mas riesgosos que lotes pequenos y frecuentes. Para el fundador de Cenit — con perfil QA — este es terreno natural: DORA es, en esencia, la formalizacion estadistica de que la calidad continua y la entrega continua son la misma disciplina.

Para Cenit, DORA es ademas un diferenciador comercial en LatAm: Jira lo ofrece solo via marketplace (plugins de pago como LinearB o Sleuth), Trello y Asana no lo ofrecen en absoluto. Un tablero que combine gestion de tareas con metricas DORA nativas habla directamente al CTO de un equipo de 10-50 personas que quiere demostrar madurez de ingenieria a su junta o a sus clientes enterprise, sin pagar 15-25 USD/dev/mes por una herramienta adicional.

### 2. Metricas y formulas exactas

Las cuatro metricas canonicas (mas la quinta anadida en 2021, confiabilidad, que omitimos por requerir SLOs operacionales que Cenit no captura):

| Metrica | Formula | Elite (reporte 2023) | Media | Baja |
|---|---|---|---|---|
| **Deployment Frequency (DF)** | despliegues exitosos a produccion / periodo | on-demand (varios/dia) | 1/semana a 1/mes | < 1/mes |
| **Lead Time for Changes (LTC)** | mediana(fecha_despliegue − fecha_primer_commit) por cambio | < 1 dia | 1 semana a 1 mes | > 1 mes |
| **Change Failure Rate (CFR)** | despliegues que causan fallo en prod / despliegues totales × 100 | 0–15% | 16–30% | > 30% |
| **Mean Time to Restore (MTTR)** | media(fin_incidente − inicio_incidente) | < 1 hora | 1 dia a 1 semana | > 1 semana |

Nota metodologica importante (voz QA): LTC usa **mediana**, no media, porque la distribucion de lead times tiene cola larga y un solo hotfix de 3 meses distorsionaria el promedio. MTTR historicamente usa media, aunque el reporte 2023 tambien migro a "failed deployment recovery time" con mediana; para Cenit calcularemos ambas y mostraremos la mediana por defecto.

**Ejemplo numerico — equipo ficticio "Nebular" (5 personas: 3 devs, 1 QA, 1 tech lead), periodo: junio 2026 (30 dias, 21 dias habiles).**

Datos crudos del mes:

- Despliegues a produccion: dias 2, 5, 9, 12, 16, 19, 23, 26, 30 → **9 despliegues**.
- De esos 9, los despliegues del dia 12 y del dia 26 causaron incidentes en produccion → **2 fallos**.
- Lead times por despliegue (dias desde primer commit del cambio hasta despliegue): 1.5, 2.0, 3.5, 2.5, 4.0, 1.0, 6.5, 2.0, 3.0.
- Incidentes: el del dia 12 se detecto a las 10:15 y se restauro a las 14:45 (rollback); el del dia 26 se detecto a las 16:00 y se restauro al dia siguiente a las 9:30.

Calculo paso a paso:

1. **DF** = 9 despliegues / 30 dias = **0.30 despliegues/dia** ≈ 2.1/semana. Clasificacion DORA: entre "1/dia" y "1/semana" → banda **alta** (no elite, porque no es on-demand diario).
2. **LTC**: ordenamos lead times: [1.0, 1.5, 2.0, 2.0, 2.5, 3.0, 3.5, 4.0, 6.5]. Con n=9, la mediana es el 5.º valor = **2.5 dias**. Clasificacion: entre 1 dia y 1 semana → banda **alta**.
3. **CFR** = 2 fallos / 9 despliegues × 100 = **22.2%**. Clasificacion: banda **media** (16-30%).
4. **MTTR**: incidente 1 = 14:45 − 10:15 = 4.5 h. Incidente 2 = de 16:00 a 9:30 del dia siguiente = 17.5 h. Media = (4.5 + 17.5) / 2 = **11.0 horas**; mediana = 11.0 h (n=2). Clasificacion: menos de 1 dia → banda **alta**.

Diagnostico integrado que Cenit deberia renderizar: "Nebular despliega rapido y restaura rapido, pero 1 de cada 4-5 despliegues rompe produccion. Accion sugerida: reforzar suite E2E pre-deploy (correlaciona con la vista de riesgos: las tareas del proyecto Desarrollo tienen test_base 20%)". Ese cruce DORA × risk_score existente es algo que ninguna herramienta genericas de LatAm ofrece.

### 3. Modelo de datos

Extendemos `users` y `tasks` existentes. Necesitamos tres entidades nuevas (despliegues, incidentes, eventos de cambio que vinculan commits/PRs con tareas) y una tabla de snapshots para no recalcular historicos en cada carga de la vista.

```sql
-- Repositorios conectados (un equipo puede tener varios repos)
CREATE TABLE repositories (
    id            SERIAL PRIMARY KEY,
    provider      VARCHAR(20)  NOT NULL DEFAULT 'github',   -- github | gitlab | bitbucket
    external_id   VARCHAR(100) NOT NULL,                    -- id del repo en el proveedor
    name          VARCHAR(200) NOT NULL,                    -- ej: teczonic/cenit
    default_branch VARCHAR(100) NOT NULL DEFAULT 'main',
    entidad       VARCHAR(50),                              -- espeja tasks.entidad para filtrar
    connected_by  INTEGER REFERENCES users(id),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (provider, external_id)
);

-- Despliegues a un entorno (la unidad de medida de DF, LTC y CFR)
CREATE TABLE deployments (
    id             SERIAL PRIMARY KEY,
    repository_id  INTEGER NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    environment    VARCHAR(30) NOT NULL DEFAULT 'production', -- production | staging
    status         VARCHAR(20) NOT NULL DEFAULT 'success',    -- success | failed | rolled_back
    commit_sha     VARCHAR(64) NOT NULL,
    deployed_at    TIMESTAMPTZ NOT NULL,
    triggered_by   INTEGER REFERENCES users(id),              -- NULL si vino por CI
    external_ref   VARCHAR(200),                              -- url del run de CI / release
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_deployments_repo_env_date
    ON deployments (repository_id, environment, deployed_at);

-- Cambios individuales (commits o PRs) incluidos en un despliegue.
-- Vincula el mundo git con el mundo tasks: aqui vive el LTC.
CREATE TABLE change_events (
    id              SERIAL PRIMARY KEY,
    repository_id   INTEGER NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    deployment_id   INTEGER REFERENCES deployments(id) ON DELETE SET NULL,
    task_id         INTEGER REFERENCES tasks(id) ON DELETE SET NULL,  -- via "CENIT-123" en el mensaje
    author_id       INTEGER REFERENCES users(id),
    commit_sha      VARCHAR(64) NOT NULL,
    pr_number       INTEGER,
    first_commit_at TIMESTAMPTZ NOT NULL,          -- inicio del reloj de LTC
    merged_at       TIMESTAMPTZ,
    UNIQUE (repository_id, commit_sha)
);
CREATE INDEX ix_change_events_task ON change_events (task_id);
CREATE INDEX ix_change_events_deployment ON change_events (deployment_id);

-- Incidentes en produccion (la unidad de medida de CFR y MTTR)
CREATE TABLE incidents (
    id                     SERIAL PRIMARY KEY,
    repository_id          INTEGER REFERENCES repositories(id) ON DELETE SET NULL,
    caused_by_deployment_id INTEGER REFERENCES deployments(id) ON DELETE SET NULL,
    resolved_by_task_id    INTEGER REFERENCES tasks(id) ON DELETE SET NULL, -- tarea de hotfix
    severity               VARCHAR(10) NOT NULL DEFAULT 'sev2',  -- sev1 | sev2 | sev3
    title                  VARCHAR(200) NOT NULL,
    detected_at            TIMESTAMPTZ NOT NULL,                 -- inicio del reloj de MTTR
    restored_at            TIMESTAMPTZ,                          -- NULL = incidente abierto
    reported_by            INTEGER REFERENCES users(id),
    postmortem             TEXT,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (restored_at IS NULL OR restored_at >= detected_at)
);
CREATE INDEX ix_incidents_detected ON incidents (detected_at);

-- Snapshot semanal precalculado (evita agregaciones pesadas en la UI Streamlit)
CREATE TABLE dora_snapshots (
    id                    SERIAL PRIMARY KEY,
    repository_id         INTEGER REFERENCES repositories(id) ON DELETE CASCADE,
    period_start          DATE NOT NULL,
    period_end            DATE NOT NULL,
    deploy_count          INTEGER NOT NULL DEFAULT 0,
    deploy_freq_per_day   NUMERIC(6,3),
    lead_time_p50_hours   NUMERIC(8,1),
    lead_time_p90_hours   NUMERIC(8,1),
    change_failure_rate   NUMERIC(5,2),          -- porcentaje 0-100
    mttr_median_hours     NUMERIC(8,1),
    dora_band             VARCHAR(10),           -- elite | high | medium | low
    computed_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, period_start, period_end)
);
```

Decisiones de diseno (voz arquitecto): (a) `change_events.task_id` es nullable a proposito — no todo commit referencia una tarea, y forzar la relacion mataria la adopcion; (b) el vinculo commit→tarea se resuelve parseando `CENIT-{id}` en el mensaje del commit/PR, patron probado por Jira y Linear; (c) `dora_snapshots` es una desnormalizacion deliberada: Streamlit rerenderiza en cada interaccion y no queremos un `GROUP BY` sobre miles de deployments por rerun; (d) los incidentes pueden crearse a mano (boton en la UI) ademas de via webhook, porque en equipos LatAm de 10-50 personas el "sistema de incidentes" suele ser un chat de WhatsApp — la friccion de captura debe ser minima.

### 4. Casos de uso del domain layer

Nuevo servicio `DoraService` en `domain/services.py` (o `domain/dora.py` si crece), con dataclasses en `domain/entities.py`. Sigue el patron existente: funciones puras que operan sobre dicts/listas serializadas, sin tocar SQLAlchemy, para que sean testeables sin base de datos.

```python
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

@dataclass
class DoraReport:
    period_start: date
    period_end: date
    deploy_count: int
    deploy_freq_per_day: float
    lead_time_p50_hours: Optional[float]
    lead_time_p90_hours: Optional[float]
    change_failure_rate: Optional[float]   # None si no hubo despliegues
    mttr_median_hours: Optional[float]     # None si no hubo incidentes
    dora_band: str                          # "elite" | "high" | "medium" | "low"


class DoraService:

    def calcular_deployment_frequency(
        self, deployments: list[dict], period_start: date, period_end: date
    ) -> float:
        """
        exitosos = [d for d in deployments
                    if d["status"] == "success"
                    and d["environment"] == "production"
                    and period_start <= d["deployed_at"].date() <= period_end]
        dias = (period_end - period_start).days + 1
        return len(exitosos) / dias
        """

    def calcular_lead_time(
        self, change_events: list[dict], deployments_by_id: dict[int, dict]
    ) -> tuple[Optional[float], Optional[float]]:
        """Devuelve (p50_horas, p90_horas).
        horas = []
        for ce in change_events:
            dep = deployments_by_id.get(ce["deployment_id"])
            if dep is None: continue                      # cambio aun no desplegado
            delta = dep["deployed_at"] - ce["first_commit_at"]
            horas.append(delta.total_seconds() / 3600)
        if not horas: return (None, None)
        return (percentil(horas, 50), percentil(horas, 90))  # mediana, no media
        """

    def calcular_change_failure_rate(
        self, deployments: list[dict], incidents: list[dict]
    ) -> Optional[float]:
        """
        prod = [d for d in deployments if d["environment"] == "production"]
        if not prod: return None
        fallidos = {i["caused_by_deployment_id"] for i in incidents
                    if i["caused_by_deployment_id"] is not None}
        fallidos |= {d["id"] for d in prod if d["status"] in ("failed", "rolled_back")}
        return round(len(fallidos & {d["id"] for d in prod}) / len(prod) * 100, 1)
        """

    def calcular_mttr(self, incidents: list[dict]) -> Optional[float]:
        """Mediana en horas de (restored_at - detected_at) de incidentes cerrados.
        Ignora incidentes abiertos (restored_at is None) para no premiar
        dejar incidentes sin cerrar. La UI muestra los abiertos por separado.
        """

    def clasificar_banda(self, report_parcial: dict) -> str:
        """Aplica los umbrales del reporte DORA 2023 a las 4 metricas y
        devuelve la banda MINIMA (un equipo es tan bueno como su peor metrica).
        Regla conservadora deliberada: evita el vanity dashboard.
        """

    def generar_reporte(
        self,
        deployments: list[dict],
        change_events: list[dict],
        incidents: list[dict],
        period_start: date,
        period_end: date,
    ) -> DoraReport:
        """Orquesta las 4 funciones anteriores. Punto de entrada unico
        para API y para el job de snapshots."""

    def correlacionar_con_riesgo(
        self, incidents: list[dict], tareas: list[dict]
    ) -> list[dict]:
        """Cruce diferenciador de Cenit: para cada incidente con
        resolved_by_task_id, une el risk_score de la tarea y agrega por
        proyecto. Responde: 'los proyectos con menor cobertura de test,
        generan mas incidentes?' — insight que alimenta la vista riesgos."""
```

La ingestion de webhooks vive en `api/` (adaptador), nunca en `domain/`: `api/webhooks.py` traduce el payload de GitHub a dicts neutros y llama a un `IngestService.registrar_despliegue(payload_neutro: dict) -> int` que si pertenece al dominio. Asi el dia que se agregue GitLab solo se escribe otro traductor.

### 5. Diseno de API REST

Consistente con el estilo existente (`/api/tasks`, `/api/analytics/...`), agrupado bajo `/api/dora`:

| Metodo | Ruta | Proposito |
|---|---|---|
| GET | `/api/dora/report?from=2026-06-01&to=2026-06-30&repo_id=1` | Reporte de las 4 metricas del periodo |
| GET | `/api/dora/trend?weeks=12&repo_id=1` | Serie semanal desde `dora_snapshots` para graficas |
| GET | `/api/dora/deployments?repo_id=1&limit=50` | Lista de despliegues recientes |
| POST | `/api/dora/deployments` | Registro manual de despliegue (equipos sin CI) |
| POST | `/api/dora/incidents` | Abrir incidente |
| PATCH | `/api/dora/incidents/{id}/restore` | Cerrar incidente (setea `restored_at`) |
| POST | `/api/webhooks/github` | Ingesta de eventos `deployment_status`, `push`, `pull_request` (verificando firma HMAC `X-Hub-Signature-256`) |

Respuesta de `GET /api/dora/report`:

```json
{
  "period": {"from": "2026-06-01", "to": "2026-06-30"},
  "repo": "teczonic/cenit",
  "metrics": {
    "deployment_frequency": {"value": 0.30, "unit": "per_day", "band": "high"},
    "lead_time_hours": {"p50": 60.0, "p90": 132.0, "band": "high"},
    "change_failure_rate": {"value": 22.2, "unit": "percent", "band": "medium"},
    "mttr_hours": {"median": 11.0, "band": "high", "open_incidents": 0}
  },
  "dora_band": "medium",
  "insight": "CFR 22.2% es tu cuello de botella: 2 de 9 despliegues causaron incidentes."
}
```

Payload de `POST /api/dora/incidents`:

```json
{
  "title": "Error 500 en generacion de certificados",
  "severity": "sev1",
  "detected_at": "2026-06-12T10:15:00-05:00",
  "caused_by_deployment_id": 42,
  "resolved_by_task_id": 918
}
```

Todos los endpoints requieren el JWT existente; `POST /api/webhooks/github` es la excepcion (autentica por firma HMAC del secreto del webhook, no por JWT). Los endpoints de escritura manual exigen `role` admin o member; el reporte es de solo lectura para todos — transparencia radical, como recomienda la propia investigacion DORA (las metricas son del equipo, no armas del gerente).

### 6. Vista o componente de UI

Nueva vista `ui/views/dora.py`, entrada "DORA" en la navegacion de `ui/app.py` junto a Analytics.

**Zona superior — filtros**: `st.selectbox` de repositorio, `st.select_slider` de periodo (4 / 12 / 26 semanas), `st.toggle` "comparar con periodo anterior".

**Fila de 4 tarjetas** (`st.columns(4)` con `st.metric`): una por metrica DORA. Cada tarjeta muestra el valor (ej. "2.1 despliegues/sem"), el delta contra el periodo anterior (verde/rojo — ojo QA: para CFR y MTTR el delta se invierte, bajar es bueno, usar `delta_color="inverse"`) y un badge de color con la banda: morado elite, verde high, amarillo medium, rojo low. Debajo, una quinta tarjeta ancha con la **banda global** del equipo y el insight textual generado por `DoraService` ("tu cuello de botella es CFR...").

**Zona media — tendencias**: dos graficas lado a lado con `st.plotly_chart` (o `st.line_chart` en v1): izquierda throughput (DF en barras + LTC p50 en linea, doble eje), derecha estabilidad (CFR en barras + MTTR en linea). Fuente: `/api/dora/trend`. Banda de referencia sombreada con los umbrales "high" para que el usuario vea a que distancia esta.

**Zona inferior — dos tabs** (`st.tabs`): *Despliegues* lista los ultimos 20 con fecha, SHA corto linkeado al proveedor, estado con los colores de `ESTADO_COLORS`, y tareas asociadas (via `change_events.task_id`, clicables hacia el Kanban). *Incidentes* lista abiertos primero con un boton "Restaurar" por fila (`st.button` que llama al PATCH) y un `st.expander` "Reportar incidente" con formulario minimo (titulo, severidad, hora de deteccion con default `now`, despliegue causante opcional). Este formulario manual es critico para la adopcion en LatAm: funciona desde el dia 1 sin integrar CI.

**Estado vacio** (voz producto, no negociable): si no hay repositorio conectado ni despliegues manuales, la vista no muestra ceros — muestra un onboarding de 3 pasos: "1) Conecta GitHub o 2) registra tu ultimo despliegue a mano; 3) mira tu primera metrica en 30 segundos". Un dashboard DORA en ceros es la forma mas rapida de que el piloto B2B lo descarte.

### 7. Estrategia de testing E2E

**pytest unitario del dominio** (lo mas valioso, porque las formulas son el producto):

- `test_df_excluye_staging_y_fallidos`: despliegues mixtos → solo cuenta `production` + `success`.
- `test_ltc_usa_mediana_no_media`: dataset con outlier de 90 dias → p50 no se contamina; verificar con los 9 valores del ejemplo Nebular esperando exactamente 2.5 dias (60.0 h).
- `test_ltc_ignora_cambios_no_desplegados`: `deployment_id=None` no entra al calculo.
- `test_cfr_deduplica`: despliegue con status `rolled_back` Y ademas vinculado a un incidente cuenta una sola vez (usa sets, verificar la interseccion).
- `test_cfr_none_sin_despliegues`: cero despliegues → `None`, nunca division por cero.
- `test_mttr_ignora_incidentes_abiertos` y `test_mttr_con_incidente_multidia`: el incidente de 17.5 h del ejemplo cruza medianoche — clasico bug de resta de datetimes naive; fixture con timezone America/Bogota.
- `test_banda_global_es_la_minima`: 3 metricas elite + 1 low → banda "low".
- Property-based (hypothesis): CFR siempre en [0,100]; LTC nunca negativo aunque lleguen timestamps desordenados del webhook.

**Playwright para Python** (E2E sobre Streamlit, aprovechando la experiencia del fundador):

1. **Flujo de incidente completo**: login → vista DORA → expandir "Reportar incidente" → llenar y enviar → el incidente aparece en el tab con badge "abierto" → click "Restaurar" → MTTR de la tarjeta se recalcula. Es el flujo que un piloto ejecutara en la demo.
2. **Registro manual de despliegue**: crear despliegue a mano → la tarjeta DF pasa de estado vacio a "0.03/dia" → verifica el onboarding y el primer valor.
3. **Ingesta de webhook simulada**: el test hace POST directo a `/api/webhooks/github` con un payload `deployment_status` firmado (fixture con el HMAC correcto y otro con firma invalida esperando 401) → recarga la vista → el despliegue aparece. Cubre la integracion API↔UI sin depender de GitHub real.
4. **Correlacion tarea-despliegue**: crear tarea via UI, simular commit "CENIT-{id}: fix" via webhook, verificar que el despliegue lista la tarea como link navegable al Kanban.
5. **Regresion visual ligera**: `expect(page.locator("[data-testid='stMetric']")).to_have_count(4)` y screenshot-diff de la fila de tarjetas — Streamlit cambia el DOM entre versiones y esto detecta roturas de layout baratas.

Nota tecnica Playwright+Streamlit: usar `page.get_by_test_id` sobre los `data-testid` que Streamlit emite (`stMetric`, `stTab`) y esperas explicitas a `networkidle` tras cada interaccion, porque Streamlit rerenderiza la pagina completa por evento.

### 8. Integraciones externas

| Integracion | Para que | Prioridad |
|---|---|---|
| **GitHub (webhooks + REST)** | `deployment_status` → tabla deployments; `push`/`pull_request` → change_events (primer commit, merge, parseo de `CENIT-123`). Es la fuente de verdad de DF/LTC sin friccion. | P0 |
| **GitHub Actions** | Alternativa si el equipo no usa GitHub Deployments: un step `curl -X POST /api/dora/deployments` documentado en el onboarding (2 lineas de YAML). Realista para equipos LatAm con CI casero. | P0 |
| **GitLab** | Mismo modelo (`repositories.provider='gitlab'`); en Colombia/Mexico hay una minoria relevante en GitLab self-hosted por politicas de datos. | P1 |
| **Slack (incoming webhook)** | Alertas: incidente abierto, CFR cruza umbral, resumen DORA semanal al canal. Cierra el loop de habito — el dashboard que nadie visita no cambia comportamiento. | P1 |
| **Sentry / UptimeRobot / Better Stack** | Apertura automatica de incidentes (`detected_at` real, no el recuerdo del dev), mejora la honestidad del MTTR. | P2 |
| **Google Calendar** | Explicitamente NO para DORA. No aporta a ninguna de las 4 metricas; evitarlo es disciplina de alcance. | — |

Riesgo de la P0 (voz arquitecto): los webhooks exigen que la API de Cenit sea alcanzable publicamente con HTTPS — en el Docker Compose actual eso significa desplegar la API (Railway/Fly/Render) antes de poder demostrar la integracion; el registro manual y el curl desde CI son el puente mientras tanto.

### 9. Conflictos o solapamientos

| Metodologia | Tipo de conflicto | Resolucion |
|---|---|---|
| **KPIs** | El mas directo: DORA *son* KPIs de ingenieria. Riesgo de dos vistas que muestran lo mismo. | DORA es un modulo especializado; la vista KPIs generales puede *embeber* la banda DORA como un KPI mas, con fuente unica en `dora_snapshots`. Nunca duplicar el calculo. |
| **SPACE** | SPACE (de los mismos autores: Forsgren et al.) abarca DORA como su dimension "Performance/Activity". Compite por la narrativa "asi medimos al equipo". | Posicionar DORA = sistema de entrega, SPACE = personas y satisfaccion. Si ambos se construyen, DORA alimenta a SPACE, no al reves. Para la etapa actual: DORA primero (datos objetivos, integracion barata), SPACE despues (requiere encuestas). |
| **Kanban / Analytics existente** | `lead_time_days` de `tasks` ya existe y se llama igual que LTC. Confusion garantizada: uno mide flujo de tareas (creacion→completado), otro mide flujo de codigo (commit→produccion). | Renombrar en UI: "Lead time de tarea" (Analytics) vs "Lead time de cambio" (DORA). Un tooltip que explique la diferencia. El glosario del producto debe fijarlo. |
| **Scrum** | Presion de usuarios ex-Jira por "velocity en story points". DORA existe precisamente para reemplazar esa metrica. | La vista DORA no muestra puntos jamas. Si se construye modulo Scrum, que la velocity viva alli y el insight de DORA pueda contradecirla ("tu velocity subio pero tu CFR tambien"). |
| **Lean / XP** | Solapamiento amistoso: DORA es la medicion empirica de lo que Lean (lotes pequenos) y XP (CI, TDD) prescriben como practica. | Sin conflicto de datos; en marketing, usar DORA como "prueba de que las practicas XP/Lean funcionan". |
| **OKRs** | Los equipos querran poner "ser elite en DORA" como OKR, convirtiendo la metrica en objetivo (ley de Goodhart). | Permitir vincular una metrica DORA a un Key Result pero mostrando siempre las 4 juntas — el diseno de pares throughput/estabilidad es el antidoto natural al gaming. |
| **Waterfall / PMBOK / SAFe** | Conflicto filosofico: fases con release unico al final hacen DF/LTC absurdos (1 despliegue cada 6 meses). | No resolver en UI; resolver en segmentacion de mercado: DORA se vende a equipos que ya despliegan iterativamente. |
| **Design Thinking** | Ninguno relevante — opera antes del ciclo de entrega. | N/A. |

Espacio de atencion (voz producto): Cenit ya tiene 6 vistas; DORA seria la 7.ª. Regla: cada vista nueva debe justificar un *job-to-be-done* distinto. El de DORA es "demostrar y mejorar la salud de mi entrega ante mi CTO/cliente" — distinto de "organizar mi trabajo" (Kanban/Eisenhower). Pasa el filtro, pero obliga a que Analytics y DORA no se canibalicen: Analytics = flujo de tareas y personas, DORA = flujo de codigo y estabilidad.

### 10. Antipatrones conocidos

- **Jira — DORA como plugin de pago y por proxy**: Atlassian nunca hizo DORA nativo en Jira; lo delego al marketplace (LinearB, Sleuth, Swarmia) y luego a Compass/Atlassian Analytics en tiers enterprise. Peor: muchos plugins calculan LTC desde transiciones de estado del ticket ("In Progress"→"Done") en vez de commit→deploy, midiendo la disciplina de mover tarjetas, no la entrega real. Leccion para Cenit: LTC se ancla en `change_events.first_commit_at`, jamas en `tasks.updated_at`.
- **Jira — el ticket como centro del universo**: exigir que todo commit tenga issue para poder medir genera tickets basura creados post-hoc. Cenit: la vinculacion tarea-commit es opcional y las metricas DORA funcionan al 100% sin ella (solo la correlacion con riesgo la necesita).
- **Trello — ausencia total**: Trello nunca modelo despliegues ni incidentes; los equipos simulaban DORA con columnas "Deployed" y power-ups fragiles, contando movimientos de tarjeta como despliegues. Resultado: numeros que nadie defiende ante un CTO. Leccion: si no hay entidad `deployment` de primera clase, no hay DORA — no intentar inferirlo del Kanban.
- **Asana — metricas de actividad disfrazadas**: Asana reporta "tareas completadas por semana" y lo vende como productividad de equipo; es exactamente el proxy que *Accelerate* desacredito. Leccion: en la vista DORA de Cenit no mostrar nunca conteo de tareas junto a las 4 metricas — contamina el marco mental.
- **Antipatron transversal — el ranking de desarrolladores**: toda herramienta que mostro DF o LTC *por persona* (varios plugins de Jira lo hacen) convirtio la metrica en vigilancia, destruyo la confianza y provoco gaming (despliegues vacios para inflar DF). La investigacion DORA es explicita: son metricas de **sistema/equipo**. Cenit: agregacion minima = repositorio/equipo; `author_id` existe en el esquema solo para depurar ingesta, nunca se expone en el dashboard.
- **Antipatron de digitalizacion — el dashboard sin accion**: mostrar 4 numeros sin siguiente paso. Los reportes DORA siempre acompanan la medicion con *capabilities* (24 capacidades tecnicas y culturales). El campo `insight` del reporte es la version minima viable de eso.

### 11. Caso real

**Sleuth** (sleuth.io, fundada 2019 por ex-Atlassian Dylan Etkin) es el caso mas instructivo para Cenit, precisamente por venir de adentro de Jira. Sleuth construyo "DORA metrics tracking" como producto entero y capturo equipos de 10-100 devs que Jira no atendia. Que hicieron bien y que copiar:

1. **El deploy como entidad de primera clase**: todo el modelo gira alrededor del despliegue (igual que nuestra tabla `deployments`), no del ticket. La ingesta acepta desde webhooks sofisticados hasta un `curl` en el pipeline — exactamente la estrategia P0 propuesta arriba.
2. **Time-to-value brutal**: conectas un repo y ves tu DF historico en minutos, porque backfillean desde la API de GitHub los ultimos 90 dias de releases/merges. Para Cenit: al conectar un repo, un job de backfill puebla `deployments` y `change_events` retroactivamente — el dashboard nace lleno, no vacio.
3. **Metricas de equipo, nunca de individuo**: resistieron la presion comercial de vender "developer productivity scores" (a diferencia de competidores que si cedieron y pagaron el costo reputacional cuando el debate McKinsey 2023 estallo).
4. **El insight, no el numero**: Sleuth etiqueta cada despliegue como "healthy/risky" y sugiere donde actuar. Validacion de nuestro campo `insight` y del cruce con `risk_score`.
5. **Leccion de negocio** (voz GTM): Sleuth cobraba ~20-30 USD/dev/mes solo por metricas; los equipos LatAm de 10-50 personas rara vez pagan eso por una herramienta *adicional*. La oportunidad de Cenit es inversa: DORA como modulo incluido dentro del tablero que ya usan, a precio LatAm. El pitch al CTO colombiano: "las metricas que Sleuth te cobraria 500 USD/mes, incluidas en tu tablero de tareas". Tambien es advertencia: Sleuth como producto independiente tuvo techo de mercado — senal de que DORA vende mejor como *feature diferenciadora* que como producto solo, lo cual valida la arquitectura de Cenit.

Mencion honrosa: **Google/DORA mismo** publica el "DORA DevOps Quick Check" (encuesta de 5 minutos que te da tu banda). Copiable como growth hack: una calculadora DORA publica y gratuita en la web de Teczonic como iman de leads de CTOs.

### 12. Costo de implementacion

**Estimacion global: MEDIO — 3 sprints de 2 semanas (6 semanas) para 1-2 desarrolladores**, apoyandose en que auth, CRUD, capa de dominio y patron de vistas ya existen.

| Sprint | Entregable | Detalle | Esfuerzo |
|---|---|---|---|
| **S1 — nucleo manual** | Migraciones de las 5 tablas; `DoraService` completo con pytest (las formulas del punto 7); endpoints `report`, `deployments` (POST manual), `incidents` + `restore`; vista `ui/views/dora.py` con 4 tarjetas y tabs, estado vacio con onboarding. | Todo funciona con captura manual. Demostrable a pilotos al final del sprint. | 10 dias-persona |
| **S2 — integracion GitHub** | `POST /api/webhooks/github` con verificacion HMAC; parseo `deployment_status`/`push`/`pull_request`; vinculacion `CENIT-{id}`; backfill de 90 dias al conectar repo; despliegue publico de la API (requisito de webhooks); tests de ingesta con payloads fixture. | El riesgo tecnico vive aqui (idempotencia de webhooks, reintentos, firmas). | 10 dias-persona |
| **S3 — tendencias y pulido** | Job de snapshots semanales (`dora_snapshots` via cron del compose o GitHub Actions schedule); endpoint `trend` + graficas; comparativa de periodos; insight textual; correlacion con `risk_score`; alertas Slack; suite Playwright E2E de los 5 flujos; documentacion de onboarding (el snippet de CI). | Recortable: si S2 se desborda, Slack y correlacion pasan a backlog sin comprometer el valor central. | 10 dias-persona |

Supuestos: PostgreSQL/Supabase ya operativo (cierto), 1 dev full-time + fundador en QA/tests (media persona), sin GitLab (P1 pospuesto, +1 sprint si se necesita). Costo recurrente post-lanzamiento: mantenimiento de contratos de webhook cuando GitHub versiona su API (~1-2 dias por trimestre) y hosting publico de la API (~5-20 USD/mes).

### 13. Cuando NO construir esto todavia

Senales de que DORA seria sobre-ingenieria para Cenit **hoy**:

1. **Antes de validar el nucleo de tareas**: si los pilotos aun no usan Kanban + Eisenhower + riesgos de forma recurrente (retencion semanal), anadir una 7.ª vista diluye el foco del producto y del fundador. DORA no salva un producto cuyo loop basico no engancha.
2. **Sin al menos 2-3 pilotos que desplieguen a produccion iterativamente**: si los clientes piloto actuales son equipos que liberan una vez al trimestre (frecuente en software a la medida en LatAm), sus 4 metricas daran banda "low" perpetua y el dashboard les resultara humillante, no util — un anti-feature en la demo de ventas. Validar primero con una pregunta en las entrevistas: "cada cuanto despliegan?".
3. **Sin API desplegada publicamente**: la mitad del valor (webhooks) exige infraestructura que el Docker Compose local no da. Si Teczonic aun no tiene la API en un hosting publico con HTTPS, el prerequisito es ese, no el modulo.
4. **Con un solo usuario por cuenta**: DORA es una metrica de equipo; con los pilotos usando Cenit individualmente (1 licencia por empresa), no hay "sistema de entrega" que medir. Esperar a cuentas con 5+ usuarios activos.
5. **Regla practica de secuencia**: construirlo cuando al menos **un piloto pregunte espontaneamente por metricas de despliegue o el fundador pierda un deal por no tenerlas**. Hasta entonces, la version de costo casi cero es: (a) la calculadora DORA publica como lead magnet (2 dias de trabajo, valida demanda), y (b) renombrar el lead time existente de Analytics para preparar el glosario. Si la calculadora genera leads y las demos lo piden, S1-S3 se justifican solos; si nadie la usa, se ahorraron 6 semanas de ingenieria.

En sintesis: DORA es probablemente el modulo con mejor relacion diferenciacion/esfuerzo del roadmap de Cenit *despues* de que el nucleo de gestion de tareas demuestre retencion — no antes. Es la feature que convierte a Cenit de "otro Trello" en "el tablero que habla el idioma del CTO", pero solo tiene sentido cuando ya hay CTOs escuchando.
