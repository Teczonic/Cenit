# Sección 10 — KPIs (Key Performance Indicators)

## 10. KPIs

### 1. Principio central y origen

Un KPI (Key Performance Indicator) es una métrica cuantitativa, acordada de antemano, que refleja el grado de avance hacia un objetivo crítico del negocio o del equipo. La palabra clave es **Key**: no toda métrica es un KPI. Un equipo puede medir cientos de cosas; un KPI es la métrica que, si se mueve en la dirección incorrecta, obliga a actuar. La diferencia entre "una métrica" y "un KPI" es contractual: un KPI tiene dueño, meta explícita, frecuencia de revisión y umbral de alerta. Sin esos cuatro elementos es solo un número decorativo en un dashboard.

El concepto tiene raíces en el *management by objectives* de Peter Drucker (años 50) y se consolidó con el **Balanced Scorecard** de Kaplan y Norton (Harvard Business Review, 1992), que propuso medir el desempeño organizacional en cuatro perspectivas (financiera, cliente, procesos internos, aprendizaje) en lugar de solo la financiera — de ahí viene la práctica moderna de tener 4–8 KPIs por área, no 40. En la industria del software, la práctica de KPIs de delivery se cruza con el movimiento Lean/Agile de los 2000 (métricas de flujo: lead time, throughput, WIP) y con la analítica de producto SaaS de los 2010 (MRR, churn, activation), donde los indicadores se volvieron computables en tiempo real.

**Qué problema resuelve.** Los equipos técnicos pequeños operan por sensaciones: "vamos bien", "estamos ahogados", "ese cliente siempre se queja". Los KPIs convierten esas sensaciones en números comparables en el tiempo. El error de gestión que previenen es doble:

1. **Gestión por anécdota**: tomar decisiones (contratar, repriorizar, escalar con un cliente) basadas en el incidente más reciente o más ruidoso, no en la tendencia real. En un equipo de 5 sin KPIs, el founder cree que "vamos bien" porque hubo mucho movimiento en el tablero; tres semanas después descubre que el 60 % de lo movido eran tareas Q4 y que la tarea crítica del cliente ancla lleva 20 días pausada.
2. **Teatro de métricas**: el error opuesto — medir 40 cosas que nadie mira. Un buen sistema de KPIs impone la disciplina de elegir 3–7 indicadores con dueño, meta y umbral de alerta, y descartar el resto.

Para Cenit esto es estratégico y no accesorio: el pitch a un CTO de un equipo de 10–50 personas en LatAm que hoy usa Trello es exactamente "Trello te muestra tarjetas; Cenit te dice si tu equipo está mejorando o empeorando, y en qué". La diferencia con la vista de Analytics actual (`ui/views/analytics.py`, `AnalyticsService`) es sutil pero central: Analytics *describe* (throughput mensual, tareas por responsable); un sistema de KPIs *prescribe* — define metas, compara el valor actual contra la meta, y alerta cuando hay desviación. La metodología KPI no agrega más métricas a Cenit: agrega la **capa de gobierno** (metas, umbrales, semáforos, tendencia, snapshots históricos) sobre las métricas que ya existen.

**Distinción con metodologías hermanas.** Un KPI no es un OKR: el OKR es aspiracional y trimestral ("aumentar la adopción del producto"), el KPI es operativo y continuo ("lead time promedio ≤ 5 días, medido semanalmente"). Tampoco es DORA ni SPACE: esos son *conjuntos predefinidos* de KPIs para dominios específicos (delivery de software, productividad del developer). El framework de KPIs es la infraestructura genérica sobre la que DORA, SPACE y hasta los Key Results cuantitativos de OKRs pueden montarse. Esa es la tesis arquitectónica de esta sección: **construir el motor genérico una vez, y que las otras metodologías métricas sean catálogos de definiciones sobre ese motor**.

### 2. Métricas y fórmulas exactas

El catálogo inicial de KPIs de Cenit debe salir de datos que las tablas `tasks` y `users` ya contienen, sin pedir al usuario ningún dato nuevo. Propuesta de los 6 KPIs de lanzamiento, con fórmula exacta:

| KPI | Fórmula | Fuente en el esquema actual | Dirección buena |
|---|---|---|---|
| Throughput semanal | `COUNT(tasks WHERE fecha_completado ∈ semana)` | `tasks.fecha_completado` | ↑ |
| Lead time promedio (días) | `AVG(fecha_completado − fecha_inicio)` de completadas en el periodo | propiedad `lead_time_days` | ↓ |
| Tasa de cumplimiento a tiempo (%) | `100 × completadas con fecha_completado ≤ fecha_fin / completadas con fecha_fin` | `fecha_fin`, `fecha_completado` | ↑ |
| WIP por persona | `COUNT(estado='En Proceso') / usuarios activos` | `tasks.estado`, `users` | → (banda, ej. 1–3) |
| Tasa de tareas pausadas (%) | `100 × COUNT(estado='Pausado') / COUNT(estado ≠ 'Completado')` | `tasks.estado` | ↓ |
| Exposición a riesgo | `SUM(risk_score de tareas no completadas)` | propiedad `risk_score` | ↓ |

**Ejemplo numérico paso a paso** — equipo ficticio "Nébula" de 5 personas (Ana, Beto, Carla, David, Elena), semana del 22 al 28 de junio de 2026. Estado del tablero al cierre: 42 tareas visibles; 9 se completaron durante la semana, 11 están "En Proceso", 4 "Pausado", 18 "No Iniciado" (33 activas no completadas).

1. **Throughput semanal** = 9 tareas completadas. Histórico de las 4 semanas previas: 7, 8, 6, 9 → media móvil = (7+8+6+9)/4 = **7.5**. La semana actual (9) está +20 % sobre la media: verde.

2. **Lead time promedio**: las 9 completadas tienen lead times individuales (días): 2.1, 3.4, 1.0, 8.2, 4.5, 2.9, 12.3, 3.1, 5.0. Suma = 42.5 → promedio = 42.5/9 = **4.72 días**. Meta: ≤ 5 días → verde. Pero la mediana es 3.4 y hay dos outliers (8.2 y 12.3); por eso el sistema guarda también el **percentil 85**: ordenando la serie, p85 ≈ 8.2 días. Reportar promedio + p85 evita que la asimetría de la distribución engañe al lead.

3. **Tasa de cumplimiento a tiempo**: de las 9 completadas, 7 tenían `fecha_fin` definida; de esas, 5 se completaron en o antes de la fecha. Tasa = 5/7 × 100 = **71.4 %**. Meta: ≥ 80 %, umbral rojo: < 60 % → ámbar. Las 2 sin `fecha_fin` se excluyen del denominador y se reportan aparte como "% de tareas sin compromiso de fecha": 2/9 = 22 %, un KPI de higiene de datos en sí mismo.

4. **WIP por persona**: 11 en proceso / 5 personas = **2.2**. Banda saludable: 1–3 → verde. Si Carla sola tiene 5 de las 11, el drill-down por responsable lo revela aunque el agregado esté bien.

5. **Tasa de pausadas**: 4 / 33 activas × 100 = **12.1 %**. Umbral de alerta: > 15 % → verde, cerca del límite.

6. **Exposición a riesgo**: suma de `risk_score` de las 33 activas = 187.4 puntos, contra 165.0 la semana anterior → **+13.6 %**. Umbral: crecimiento > 10 % semana a semana → rojo. Interpretación: entraron tareas de clientes de alto impacto (uniandes, impacto 10) en áreas de baja cobertura de test.

Semáforo de la semana para Nébula: 4 verdes, 1 ámbar, 1 rojo. Esa fila de 6 celdas es el producto entero de esta sección.

**Fórmula genérica de evaluación de estado** que el motor aplica a cualquier KPI:

```
estado(v, meta, umbral, direccion):
    direccion = "up":   verde si v >= meta; ambar si umbral <= v < meta; rojo si v < umbral
    direccion = "down": verde si v <= meta; ambar si meta < v <= umbral; rojo si v > umbral
    direccion = "band": verde si banda_min <= v <= banda_max; fuera -> ambar/rojo segun distancia
    v is None o muestra < minimo -> "sin_datos"
```

### 3. Modelo de datos

Diseño en tres tablas núcleo más una de trazabilidad: **definiciones** (qué se mide y contra qué meta), **mediciones** (snapshots periódicos, materializados para conservar histórico aunque las tareas se editen o borren) y **alertas**. Extienden `users` y `tasks` sin duplicarlas; los valores se calculan desde `tasks` y se congelan en `kpi_measurements`.

```sql
-- Catálogo de KPIs: qué se mide, cómo, y contra qué meta.
CREATE TABLE kpi_definitions (
    id              SERIAL PRIMARY KEY,
    clave           VARCHAR(60) UNIQUE NOT NULL,        -- 'throughput_semanal', 'lead_time_avg'
    nombre          VARCHAR(120) NOT NULL,
    descripcion     TEXT,
    unidad          VARCHAR(30) NOT NULL,               -- 'tareas/semana', 'dias', '%', 'puntos'
    direccion       VARCHAR(10) NOT NULL DEFAULT 'up'
                    CHECK (direccion IN ('up','down','band')),
    metrica_fuente  VARCHAR(60) NOT NULL,               -- id de la función de cálculo en domain/
    periodicidad    VARCHAR(15) NOT NULL DEFAULT 'weekly'
                    CHECK (periodicidad IN ('daily','weekly','monthly')),
    meta            NUMERIC(12,2),                      -- valor objetivo (verde)
    umbral_alerta   NUMERIC(12,2),                      -- frontera ámbar/rojo
    banda_min       NUMERIC(12,2),                      -- solo direccion='band'
    banda_max       NUMERIC(12,2),
    -- alcance opcional: NULL = todo el equipo
    entidad         VARCHAR(50),                        -- espeja tasks.entidad
    proyecto        VARCHAR(80),                        -- espeja tasks.proyecto
    responsable_id  INTEGER REFERENCES users(id) ON DELETE SET NULL,
    owner_id        INTEGER NOT NULL REFERENCES users(id),  -- dueño del KPI (rinde cuentas)
    activo          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ
);

-- Snapshots periódicos: histórico inmutable que hace posibles las tendencias.
CREATE TABLE kpi_measurements (
    id              SERIAL PRIMARY KEY,
    kpi_id          INTEGER NOT NULL REFERENCES kpi_definitions(id) ON DELETE CASCADE,
    periodo_inicio  DATE NOT NULL,
    periodo_fin     DATE NOT NULL,
    valor           NUMERIC(12,2) NOT NULL,
    valor_p85       NUMERIC(12,2),                      -- percentil 85 para métricas de tiempo
    numerador       NUMERIC(12,2),                      -- trazabilidad del cálculo
    denominador     NUMERIC(12,2),
    n_tareas        INTEGER NOT NULL DEFAULT 0,         -- tamaño de muestra
    estado          VARCHAR(10) NOT NULL
                    CHECK (estado IN ('verde','ambar','rojo','sin_datos')),
    calculado_en    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (kpi_id, periodo_inicio, periodo_fin)
);
CREATE INDEX idx_kpi_meas_kpi_periodo ON kpi_measurements (kpi_id, periodo_inicio DESC);

-- Alertas generadas cuando una medición cruza umbral o rompe tendencia.
CREATE TABLE kpi_alerts (
    id              SERIAL PRIMARY KEY,
    kpi_id          INTEGER NOT NULL REFERENCES kpi_definitions(id) ON DELETE CASCADE,
    measurement_id  INTEGER NOT NULL REFERENCES kpi_measurements(id) ON DELETE CASCADE,
    tipo            VARCHAR(20) NOT NULL
                    CHECK (tipo IN ('umbral','tendencia','sin_datos')),
    mensaje         TEXT NOT NULL,
    severidad       VARCHAR(10) NOT NULL DEFAULT 'ambar'
                    CHECK (severidad IN ('ambar','rojo')),
    reconocida_por  INTEGER REFERENCES users(id) ON DELETE SET NULL,
    reconocida_en   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Trazabilidad fina (fase 2): qué tareas alimentaron cada medición, para que
-- el drill-down "¿por qué subió el lead time?" abra las tareas exactas.
CREATE TABLE kpi_measurement_tasks (
    measurement_id  INTEGER NOT NULL REFERENCES kpi_measurements(id) ON DELETE CASCADE,
    task_id         INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    aporte          NUMERIC(12,2),                      -- ej. lead_time_days de esa tarea
    PRIMARY KEY (measurement_id, task_id)
);
```

Decisiones deliberadas: (a) `entidad`/`proyecto` se guardan como VARCHAR espejando `tasks` porque hoy no existen tablas maestras de entidad/proyecto — si en el futuro se normalizan, la migración queda local a esta tabla; (b) `metrica_fuente` es una clave que mapea a una función registrada en el dominio, no SQL arbitrario embebido — evita inyección y mantiene la lógica testeable en Python; (c) los snapshots son inmutables (UNIQUE por periodo) y guardan numerador/denominador para poder auditar el cálculo meses después ante un cliente escéptico.

### 4. Casos de uso del domain layer

Nuevo módulo `domain/kpi_service.py`, siguiendo el estilo de los servicios existentes (operan sobre listas de dicts tal como devuelve la API), más dataclasses de resultado en `domain/entities.py`:

```python
from dataclasses import dataclass
from datetime import date
from typing import Callable, Literal, Optional

Direccion = Literal["up", "down", "band"]
Estado = Literal["verde", "ambar", "rojo", "sin_datos"]

@dataclass(frozen=True)
class KpiResult:
    clave: str
    valor: Optional[float]
    valor_p85: Optional[float]
    numerador: Optional[float]
    denominador: Optional[float]
    n_tareas: int
    estado: Estado

@dataclass(frozen=True)
class KpiTrend:
    clave: str
    puntos: list[tuple[date, float]]     # (periodo_inicio, valor)
    variacion_pct: Optional[float]       # último vs media móvil de 4 periodos
    direccion_tendencia: Literal["mejorando", "empeorando", "estable"]


class KpiService:
    """Motor genérico: registro de métricas + evaluación contra metas."""

    # Registro: clave -> función pura (tareas, ini, fin) -> (valor, num, den, n, p85)
    _REGISTRO: dict[str, Callable] = {}

    def calcular_kpi(
        self,
        definicion: dict,
        tareas: list[dict],
        periodo_inicio: date,
        periodo_fin: date,
    ) -> KpiResult:
        # 1. filtrar tareas por alcance (entidad/proyecto/responsable de la
        #    definición) reutilizando FiltroService.filtrar(...)
        # 2. fn = self._REGISTRO[definicion["metrica_fuente"]]
        # 3. valor, num, den, n, p85 = fn(tareas_filtradas, periodo_inicio, periodo_fin)
        # 4. estado = self.evaluar_estado(valor, n, definicion)
        # 5. return KpiResult(...)
        ...

    def evaluar_estado(
        self, valor: Optional[float], n_tareas: int, definicion: dict
    ) -> Estado:
        # valor is None o n_tareas == 0 -> "sin_datos"
        # 'up':   valor >= meta -> verde; >= umbral_alerta -> ambar; else rojo
        # 'down': valor <= meta -> verde; <= umbral_alerta -> ambar; else rojo
        # 'band': banda_min <= valor <= banda_max -> verde; else ambar/rojo
        ...

    def calcular_tendencia(
        self, clave: str, mediciones: list[dict], ventana: int = 4
    ) -> KpiTrend:
        # media móvil de `ventana` periodos previos;
        # variacion_pct = (ultimo - mm) / mm * 100
        # 'mejorando'/'empeorando' según direccion del KPI y signo de la variación
        ...

    def detectar_alertas(
        self, resultado: KpiResult, tendencia: KpiTrend, definicion: dict
    ) -> list[dict]:
        # tipo 'umbral' si estado == 'rojo'
        # tipo 'tendencia' si 3 periodos consecutivos empeorando aunque siga verde
        # tipo 'sin_datos' si n_tareas == 0 (higiene: nadie llena fechas)
        ...


# ── Funciones de métrica: puras, sin I/O, registradas en _REGISTRO ──────────

def throughput(tareas: list[dict], ini: date, fin: date) -> tuple:
    # n = count(t["fecha_completado"] en [ini, fin]); return (n, n, None, n, None)
    ...

def lead_time_promedio(tareas: list[dict], ini: date, fin: date) -> tuple:
    # lts = [t["lead_time_days"] for t completadas en periodo con lead_time no nulo]
    # return (mean(lts), sum(lts), len(lts), len(lts), percentil(lts, 85))
    ...

def tasa_cumplimiento(tareas: list[dict], ini: date, fin: date) -> tuple:
    # den = completadas en periodo con fecha_fin
    # num = las que cumplen fecha_completado <= fecha_fin
    # return (100*num/den if den else None, num, den, den, None)
    ...

def wip_por_persona(tareas: list[dict], ini: date, fin: date) -> tuple:
    # count(estado == 'En Proceso') / usuarios activos (inyectado en cierre)
    ...

def tasa_pausadas(tareas: list[dict], ini: date, fin: date) -> tuple:
    # 100 * count(Pausado) / count(estado != 'Completado')
    ...

def exposicion_riesgo(tareas: list[dict], ini: date, fin: date) -> tuple:
    # sum(t["risk_score"]) de tareas con estado != 'Completado' al cierre
    ...
```

El patrón de registro (`_REGISTRO`) es la pieza que después permite que DORA y SPACE sean solo *filas en `kpi_definitions`* apuntando a nuevas funciones registradas, sin tocar el motor. Nota QA: todas las funciones de métrica son puras (listas de dicts → tupla), lo que las hace trivialmente testeables con pytest sin base de datos, igual que `AnalyticsService` hoy.

### 5. Diseño de API REST

Consistente con el estilo actual (`/api/tasks`, `/api/analytics/...`). Se añade el router `api/routers/kpis.py`:

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/api/kpis` | Listar definiciones activas (con última medición embebida) |
| POST | `/api/kpis` | Crear definición (solo `role='admin'`) |
| PATCH | `/api/kpis/{id}` | Editar meta/umbral/alcance |
| DELETE | `/api/kpis/{id}` | Desactivar (soft delete: `activo=false`) |
| GET | `/api/kpis/{id}/measurements?limit=12` | Serie histórica para sparklines |
| POST | `/api/kpis/recalculate` | Recalcular el periodo en curso (idempotente: upsert del snapshot) |
| GET | `/api/kpis/dashboard` | Payload agregado para la vista: todos los KPIs + estado + tendencia |
| GET | `/api/kpis/alerts?ack=false` | Alertas pendientes |
| POST | `/api/kpis/alerts/{id}/ack` | Reconocer alerta |

Ejemplo de creación:

```json
POST /api/kpis
{
  "clave": "lead_time_avg_desarrollo",
  "nombre": "Lead time promedio — Desarrollo",
  "unidad": "dias",
  "direccion": "down",
  "metrica_fuente": "lead_time_promedio",
  "periodicidad": "weekly",
  "meta": 5.0,
  "umbral_alerta": 8.0,
  "proyecto": "Desarrollo",
  "owner_id": 2
}
```

Respuesta de `GET /api/kpis/dashboard` (el contrato que consume Streamlit en una sola llamada, evitando N+1 desde la UI):

```json
{
  "periodo": {"inicio": "2026-06-22", "fin": "2026-06-28"},
  "kpis": [
    {
      "id": 3,
      "clave": "lead_time_avg_desarrollo",
      "nombre": "Lead time promedio — Desarrollo",
      "unidad": "dias",
      "valor": 4.72,
      "valor_p85": 8.2,
      "meta": 5.0,
      "estado": "verde",
      "n_tareas": 9,
      "tendencia": {"variacion_pct": -6.3, "direccion": "mejorando"},
      "sparkline": [5.9, 5.4, 5.1, 5.0, 4.72],
      "owner": {"id": 2, "name": "Ana Ruiz"}
    }
  ],
  "alertas_pendientes": 1
}
```

`POST /api/kpis/recalculate` lo invoca un job programado (cron en el contenedor `api` del Docker Compose, o GitHub Actions scheduled en fase temprana) cada lunes 06:00; también se expone para el botón "Recalcular ahora" de la UI. Debe ser idempotente: recalcular dos veces el mismo periodo hace upsert sobre la restricción UNIQUE, nunca duplica filas.

### 6. Vista o componente de UI

Nueva vista `ui/views/kpis.py`, entrada "KPIs" en la navegación de `ui/app.py`, entre Analytics y Equipo.

**Zona 1 — Cabecera de periodo.** Selector de periodo (`st.selectbox`: "Esta semana", "Semana pasada", "Últimas 4 semanas") + selector de alcance reutilizando los filtros de entidad/proyecto existentes + botón "Recalcular ahora" (con `st.spinner`). A la derecha, badge rojo con el número de alertas sin reconocer.

**Zona 2 — Semáforo (el hero de la vista).** Grid de tarjetas (`st.columns(3)`, dos filas para 6 KPIs). Cada tarjeta: nombre del KPI, valor grande con unidad (`st.metric` con `delta` = variación vs periodo anterior — clave usar `delta_color="inverse"` en KPIs donde bajar es bueno, como lead time), emoji/borde de estado (verde/ámbar/rojo), sparkline de 8 periodos (`st.line_chart` compacto) y en letra pequeña "meta: ≤ 5 días · dueño: Ana". Las tarjetas rojas van primero (orden por severidad, no alfabético): la vista debe responder "¿qué está mal?" en 3 segundos.

**Zona 3 — Drill-down.** Al hacer clic en una tarjeta (patrón Streamlit: botón por tarjeta + `st.session_state["kpi_seleccionado"]`), debajo del grid se expande: gráfico grande de la serie histórica con línea horizontal de meta y banda ámbar sombreada, y tabla `st.dataframe` con las tareas que alimentaron la medición (vía `kpi_measurement_tasks`), ordenadas por aporte descendente — para lead time, las tareas más lentas arriba. Esta tabla convierte el KPI de "número que da miedo" a "lista de cosas accionables". Junto al gráfico, los campos `numerador`/`denominador`/`n_tareas` visibles: transparencia total del cálculo.

**Zona 4 — Administración (solo admin).** `st.expander("Configurar KPIs")` con `st.data_editor` sobre las definiciones: editar meta, umbral, dueño, activo. Crear KPI nuevo = formulario con select de `metrica_fuente` limitado al registro del dominio (no texto libre).

Principio de producto: la vista por defecto **no debe requerir configuración**. Al activar el módulo, Cenit siembra (seed) los 6 KPIs del catálogo con metas por defecto razonables calculadas del propio histórico del equipo (ej. meta de throughput = media de las últimas 8 semanas × 1.1). Un CTO piloto debe ver valor en la primera sesión, no después de una tarde configurando — el error clásico de Jira.

### 7. Estrategia de testing E2E

**Unitarios pytest (`tests/test_kpi_service.py`)** — el grueso de la confianza, sobre funciones puras:

- `evaluar_estado`: tabla parametrizada (`@pytest.mark.parametrize`) cubriendo las 3 direcciones × valor en meta exacta, dentro de banda ámbar, en umbral exacto, fuera de umbral, y `None` → `sin_datos`. Los bordes exactos (valor == meta, valor == umbral) son donde viven los bugs de `>` vs `>=`.
- Cada función de métrica con fixtures de tareas: lista vacía → `sin_datos` (sin división por cero); tareas sin `fecha_inicio`/`fecha_fin` excluidas del denominador correcto; fechas timezone-naive vs aware (el mismo bug que ya maneja `Task.eisenhower`); completadas fuera del periodo no cuentan.
- `lead_time_promedio` con el dataset exacto del ejemplo de la sección 2: aserción de 4.72 y del p85 — el ejemplo documentado se convierte en test de regresión.
- `calcular_tendencia`: series crecientes/decrecientes/planas, menos de 4 puntos históricos, y verificación de que "empeorando" respeta la dirección del KPI (lead time subiendo = empeorando; throughput subiendo = mejorando).
- `detectar_alertas`: 3 periodos consecutivos degradándose estando en verde → alerta de tendencia; idempotencia (recalcular no duplica alertas).

**Integración API (`tests/test_kpi_api.py`, TestClient de FastAPI)**: CRUD de definiciones con permisos (member no puede crear → 403); `recalculate` dos veces → mismo número de filas en `kpi_measurements`; `dashboard` devuelve el contrato JSON completo con tendencia y sparkline.

**E2E con Playwright para Python (`tests/e2e/test_kpis_e2e.py`)** — flujos críticos contra la app Streamlit levantada con Docker Compose y datos sembrados:

1. **Flujo semáforo**: login → navegar a "KPIs" → `expect(page.get_by_text("Lead time promedio")).to_be_visible()` → la tarjeta sembrada como roja aparece antes que las verdes y muestra el valor esperado.
2. **Flujo causa-efecto (el más valioso)**: crear vía UI del Kanban una tarea con fechas que violan la meta de lead time → pulsar "Recalcular ahora" → volver a KPIs → asertar que el valor cambió y el estado pasó a ámbar. Cruza UI → API → dominio → DB → UI: es el smoke test del módulo entero.
3. **Flujo drill-down**: clic en tarjeta → la tabla de tareas contribuyentes contiene la descripción de la tarea lenta sembrada.
4. **Flujo admin/permisos**: como admin, cambiar la meta de 5 a 3 en el editor → recalcular → el estado pasa de verde a rojo sin recargar sesión. Como member, el expander de configuración no existe.
5. **Flujo alerta**: sembrar medición roja → badge de alertas visible → reconocer → el badge decrementa.

Nota Streamlit + Playwright: apoyar selectores en textos y en los `data-testid` que Streamlit emite (`stMetric`, `stMetricDelta`); esperar con `expect(...).to_be_visible()` y nunca con sleeps, porque Streamlit re-renderiza el árbol completo en cada interacción.

### 8. Integraciones externas

- **Slack (incoming webhook)** — la integración de mayor ROI y la primera a construir. Un KPI que solo vive en un dashboard que hay que recordar visitar muere en semanas; el resumen del lunes ("Semana Nébula: 4 verdes, 1 ámbar, 1 rojo — Exposición a riesgo +13.6 %") empujado al canal del equipo crea el hábito. Costo bajísimo: un POST desde el job de recálculo.
- **WhatsApp Business API (roadmap LatAm)** — en pymes colombianas y mexicanas el canal operativo real es WhatsApp, no Slack; ningún competidor global lo hace bien. Es un diferenciador de venta concreto para el segmento de Cenit, aunque su costo de homologación (Meta) lo empuja a fase posterior.
- **Google Calendar / Outlook (lectura, fase posterior)** — para KPIs de capacidad (horas de foco disponibles vs WIP). No necesario para el catálogo inicial.
- **GitHub/GitLab API** — *no* para este módulo en sí, sino como fuente futura cuando el motor sirva a DORA (deployment frequency y lead time for changes requieren commits/deploys, no tareas). El registro de métricas debe dejar la puerta abierta a funciones cuya fuente no sea `tasks`, sin construirlo aún.
- **Exportación CSV/Excel** — no es una API de terceros pero sí una integración crítica de facto en LatAm: el CTO piloto va a pegar los KPIs en la presentación mensual a gerencia. `st.download_button` sobre `kpi_measurements` cuesta una tarde y desbloquea conversaciones de renovación.

### 9. Conflictos o solapamientos

| Metodología | Tipo de conflicto | Resolución |
|---|---|---|
| **DORA** | Es un *subconjunto* de KPIs (4 métricas predefinidas de delivery). Riesgo: dos vistas, dos motores, dos jobs de snapshot. | DORA = pack de filas en `kpi_definitions` + funciones registradas. Una sola vista con secciones/tabs. Nunca un motor paralelo. |
| **SPACE** | Igual que DORA: catálogo de métricas de productividad/bienestar; varias no derivan de `tasks` (requieren encuestas). | Mismo motor; sus métricas de percepción esperan a la integración de encuestas (Typeform). No bloquea. |
| **OKRs** | El solapamiento más peligroso: un Key Result cuantitativo ("bajar lead time a 4 días") es indistinguible de un KPI con meta. Riesgo de duplicar la entidad "meta sobre una métrica" en dos tablas. | Los Key Results cuantitativos referencian `kpi_definitions.id` (columna `kpi_id` en la futura tabla de key results). El KPI es el sensor; el OKR es la ambición trimestral montada sobre el sensor. |
| **Analytics actual** | Solapamiento de UI directo: throughput y lead time ya se muestran en `ui/views/analytics.py`. | Analytics = exploración descriptiva sin metas; KPIs = compromiso con semáforo. Misma función de dominio como fuente única para no mostrar el mismo número con dos valores distintos. A mediano plazo, los gráficos de Analytics que ganen meta migran a KPIs. |
| **Scrum** | La velocity de sprint es un KPI con periodicidad = sprint. Compite por atención: ¿burndown o semáforo? | Si Cenit añade sprints, velocity entra al motor como KPI (periodicidad extendida a 'sprint'). Una sola fuente de verdad. |
| **Kanban / Lean** | Cero conflicto de datos — son la *fuente* de los KPIs de flujo. Conflicto menor de UI: los límites WIP de Kanban y el KPI "WIP por persona" deben usar el mismo umbral. | La definición del KPI WIP lee el límite configurado en el tablero, no un número aparte. |
| **Waterfall / PMBOK** | PMBOK trae sus propios indicadores (SPI, CPI de earned value). | Si algún día se implementan, son más filas en el catálogo. El motor genérico es el seguro contra esta proliferación. |
| **XP / Design Thinking / SAFe** | Sin conflicto material de datos ni de UI a esta escala. | No aplica resolución específica; SAFe además queda fuera del segmento objetivo (10–50 personas). |

Conclusión transversal: **KPIs es infraestructura, no una metodología rival**. Bien construido, reduce el costo de las secciones DORA, SPACE, OKRs y Scrum de "construir un módulo" a "escribir definiciones y funciones de métrica".

### 10. Antipatrones conocidos

- **Jira — el dashboard-cementerio**: gadgets infinitamente configurables (Filter Results, Two-Dimensional Stats…) sin metas ni semáforos nativos. Resultado típico: cada lead arma su dashboard una vez, nadie lo vuelve a abrir, y las "métricas serias" terminan en un plugin pago (eazyBI). Lección: un KPI sin meta y sin alerta no es un KPI, es un gráfico; meta y umbral son campos del modelo, no un extra opcional.
- **Jira — métricas que castigan**: al exponer velocity y story points por persona, muchas organizaciones los convirtieron en instrumento de evaluación individual, y los equipos respondieron inflando estimaciones (ley de Goodhart: cuando una medida se convierte en objetivo, deja de ser una buena medida). Cenit debe sesgar el catálogo por defecto a métricas de *equipo* y de *flujo*; el drill-down por responsable existe para diagnosticar cuellos de botella, nunca como ranking de "productividad" individual en la UI por defecto.
- **Trello — la ausencia total**: sin métricas nativas, delegó todo a power-ups (Screenful, etc.), fragmentando experiencia y dato. Consecuencia estratégica: los equipos que maduraban *abandonaban Trello* porque no podían responder "¿cómo vamos?". Ese éxodo es literalmente el mercado de Cenit: las métricas nativas son retención.
- **Asana — métricas de vanidad**: su módulo de Goals/Dashboards enfatiza "% de tareas completadas" y celebraciones (el unicornio volador), métricas que siempre suben y nunca duelen. Un KPI que no puede ponerse rojo no cambia comportamiento. Cenit debe incluir por diseño KPIs "incómodos" (tasa de pausadas, exposición a riesgo, % sin fecha comprometida).
- **Todos — analytics sin snapshots**: calcular métricas al vuelo sobre el estado actual de las tareas hace imposible la pregunta más valiosa ("¿estamos mejor que hace un mes?") porque editar/borrar tareas reescribe el pasado. De ahí la insistencia en `kpi_measurements` como tabla inmutable desde el día uno — la decisión de modelo de datos más importante de esta sección y la más cara de retrofitear.

### 11. Caso real

**Linear** es la referencia de ejecución. Su módulo **Insights** y los *project/initiative health updates* aplican exactamente la filosofía propuesta: pocas métricas opinadas (scope, velocity, cycle time), calculadas sin configuración, con histórico automático, y un semáforo brutalmente simple (On track / At risk / Off track) que un humano confirma. Tres decisiones a copiar y una a evitar:

1. **Opinión sobre configuración**: Linear no pregunta "¿qué quieres medir?"; mide lo correcto por defecto y permite ajustar después. Cenit debe sembrar el catálogo de 6 KPIs con metas autocalculadas del histórico.
2. **La métrica vive junto al trabajo**: los insights se abren desde el mismo tablero, con drill-down a los issues concretos — el equivalente exacto de la Zona 3 (tabla de tareas contribuyentes). La métrica que no enlaza a trabajo accionable es decoración.
3. **Push, no pull**: los health updates llegan a Slack; el hábito se construye en el canal donde el equipo ya vive. Valida la prioridad de la integración Slack (y la apuesta WhatsApp para LatAm).
4. **A evitar**: Insights es exclusivo de planes pagos altos y opera como caja negra (no expone numerador/denominador). En LatAm, donde el CTO desconfía y compara contra "lo hago en Excel", la transparencia del cálculo (numerador/denominador visibles en el drill-down) es un diferenciador de confianza, no un detalle técnico.

Caso organizacional complementario: **Intercom** documentó públicamente cómo su equipo de producto operaba con un puñado de KPIs de delivery semanales revisados en un ritual fijo de 15 minutos. La lección no es técnica sino de producto: el KPI funciona cuando tiene *ritual* asociado. Cenit puede codificar el ritual en el producto mismo (resumen de lunes por Slack + vista ordenada por severidad).

### 12. Costo de implementación

**Estimación: MEDIO — 3 sprints de 2 semanas para 1–2 desarrolladores** (asumiendo el perfil real del equipo: 1 dev fuerte en QA/Python con apoyo parcial).

| Sprint | Alcance | Detalle |
|---|---|---|
| **Sprint 1** | Motor de dominio + datos | Migración de `kpi_definitions`/`kpi_measurements`; `KpiService` con las 6 funciones de métrica y `evaluar_estado`; seed del catálogo con metas autocalculadas; suite pytest completa (la parte más testeable — hacerla primero con TDD encaja con el perfil del fundador). |
| **Sprint 2** | API + UI mínima | Router FastAPI (dashboard, measurements, recalculate, CRUD admin); job de snapshot semanal (cron en contenedor); vista Streamlit Zonas 1–2 (semáforo + sparklines); tests de integración TestClient. |
| **Sprint 3** | Drill-down + alertas + E2E | `kpi_measurement_tasks` y tabla de contribuyentes; `kpi_alerts` + badge + webhook Slack; Zona 4 admin; suite Playwright (5 flujos); export CSV; datos demo para pilotos. |

Riesgo de desviación: +0.5–1 sprint si el histórico de los pilotos tiene mala higiene de fechas (habrá que endurecer la tolerancia a nulls y construir el KPI de higiene antes de lo previsto). Recorte posible: el Sprint 3 completo es diferible — con Sprints 1–2 ya hay demo vendible ("semáforo semanal automático"), es decir un **MVP real de ~2 sprints**.

### 13. Cuándo NO construir esto todavía

Señales concretas de que sería prematuro:

- **Menos de ~8 semanas de datos reales de pilotos.** Un KPI sin histórico es un número sin contexto: no hay tendencia, no hay meta autocalculada creíble, y el semáforo miente. Si los pilotos llevan 3 semanas cargando tareas, la prioridad es que carguen tareas (fricción de captura, hábito), no medirlas.
- **Higiene de datos insuficiente.** Si en los tableros piloto menos del ~60 % de las tareas completadas tienen `fecha_inicio` y `fecha_fin` reales, el lead time y la tasa de cumplimiento saldrán de muestras minúsculas y los CTOs concluirán "estos números están mal" — un golpe de credibilidad del que es difícil volver en venta B2B. Primero mejorar la UX de captura de fechas.
- **La vista Analytics actual aún no tiene uso.** Si los usuarios piloto no abren la analítica descriptiva que ya existe, añadir metas y alertas encima es apilar sofisticación sobre una necesidad no demostrada. La señal de "ya toca" es la contraria: un piloto exporta datos a Excel para calcular sus propias metas, o pregunta "¿puedo ver si mejoramos vs el mes pasado?" — en ese momento este módulo pasa de sobre-ingeniería a feature de cierre de venta.
- **Sin ritual de equipo donde consumirlos.** Si el equipo cliente no tiene reunión semanal ni canal activo donde revisar el semáforo, los KPIs serán un dashboard-cementerio estilo Jira. En etapa de validación es legítimo que el founder calcule 2–3 de estos números a mano (SQL directo sobre Supabase) y los mande por WhatsApp al piloto cada lunes: valida el apetito por el módulo con costo cero de ingeniería — exactamente el "do things that don't scale" correcto antes de escribir la primera migración.

Lo que **sí** conviene asegurar desde ya, se construya o no el módulo: no destruir historia. Evitar borrados físicos de tareas y mantener `fecha_completado` fiable — el costo de retrofitear snapshots sobre datos ya mutados es el más alto de todo este documento.
