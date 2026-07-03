# Sección 13 — Cenit Flow System

## 13. Cenit Flow System

### 1. Principio central y origen

Cenit Flow System es una metodología organizacional híbrida diseñada para equipos de 10 a 50 personas que necesitan combinar **claridad estratégica, flujo operativo, disciplina técnica y reporting ejecutivo** sin caer en la sobrecarga procesal de marcos enterprise. Su principio central es simple: **descubrir con evidencia, priorizar por impacto, ejecutar con flujo visible, medir salud del sistema y reportar sin contaminar la operación diaria**.

No nace de una escuela única, sino de una decisión de arquitectura organizacional: tomar de cada marco solo la pieza que resuelve un problema real y encaja con el segmento objetivo de Cenit. De **Design Thinking** toma la disciplina de entender al usuario antes de construir; de **OKRs**, la dirección trimestral; de **Kanban** y **Lean**, la gestión del flujo y la reducción de desperdicio; de **XP**, la calidad técnica en el día a día; de **DORA**, la medición de la entrega de software; de **KPIs**, el motor de gobierno continuo; de **Scrum**, la cadencia ligera opcional para equipos que ya piensan en iteraciones; y de **Waterfall/PMBOK**, únicamente la capa de baseline, hitos y control de cambios necesaria para proyectos contractuales.

El error de gestión que este sistema previene es el más común en empresas de software pequeñas y medianas de LatAm: **tener demasiados marcos incompletos al mismo tiempo y ninguno operando de punta a punta**. El resultado típico es un equipo que dice que hace Scrum, se organiza como Kanban, reporta como Waterfall, prioriza por intuición, descubre por chat y mide productividad por actividad. Cenit Flow System ordena ese caos separando explícitamente cinco capas:

1. **Descubrimiento** — qué vale la pena construir.
2. **Dirección** — hacia qué resultado del trimestre se mueve el equipo.
3. **Priorización** — qué entra primero y qué se atiende hoy.
4. **Ejecución** — cómo fluye el trabajo real.
5. **Medición y reporting** — cómo se evalúa salud, entrega y compromiso.

Para Cenit esto tiene una ventaja estratégica directa: permite ofrecer una metodología propia, consistente con el producto, en vez de convertirse en un collage de features “tipo Jira”. El mensaje comercial deja de ser “también tenemos sprints, KPIs y discovery” y pasa a ser: **“Cenit integra discovery, ejecución y reporting en un solo sistema ligero”**.

### 2. Métricas y fórmulas exactas

El Cenit Flow System usa un set mínimo de métricas por capa. La regla es deliberada: pocas métricas, cada una con dueño, umbral y acción asociada.

| Capa | Métrica | Fórmula | Qué responde |
|---|---|---|---|
| Descubrimiento | Cadencia de contacto con usuarios (CCU) | `entrevistas_realizadas / semanas` | ¿Seguimos aprendiendo del usuario real? |
| Descubrimiento | Trazabilidad insight→tarea (TIT) | `tareas_con_insight / tareas_nuevas × 100` | ¿El backlog nace de evidencia o de opinión? |
| Dirección | Progreso de objective | `Σ(progreso_kr × peso) / Σ(peso)` | ¿El trimestre avanza hacia lo importante? |
| Priorización | Alignment ratio | `tareas_activas_vinculadas_a_KR / tareas_activas × 100` | ¿El trabajo diario tiene dirección? |
| Ejecución | Throughput semanal | `COUNT(tareas completadas) / semana` | ¿Cuánto entrega el equipo? |
| Ejecución | Lead time promedio | `AVG(fecha_completado − fecha_inicio)` | ¿Cuánto tarda en salir una tarea? |
| Ejecución | WIP por persona | `COUNT(En Proceso) / personas_activas` | ¿Estamos saturados? |
| Ejecución | Flow efficiency | `tiempo_activo / (tiempo_activo + tiempo_pausado) × 100` | ¿Cuánto del tiempo es trabajo real vs espera? |
| Calidad técnica | TDD ratio | `tareas_test_first / tareas_dev_completadas × 100` | ¿La calidad se construye desde el inicio? |
| Calidad técnica | CI health | `builds_verdes / builds_totales × 100` | ¿El pipeline es estable? |
| Entrega | Deployment Frequency | `deploys_exitosos / periodo` | ¿Con qué frecuencia entregamos valor? |
| Entrega | Change Failure Rate | `deploys_con_fallo / deploys_totales × 100` | ¿Qué tan segura es la entrega? |
| Gobierno | KPI status | evaluación contra meta y umbral | ¿Qué está fuera de control hoy? |
| Reporting contractual | SPI | `EV / PV` | ¿Vamos adelantados o atrasados contra el plan? |
| Reporting contractual | CPI | `EV / AC` | ¿Gastamos mejor o peor que lo planeado? |

**Ejemplo numérico integrado — equipo ficticio de 5 personas, periodo mensual**

Datos del mes:

- 8 entrevistas en 4 semanas.
- 18 tareas nuevas, 9 vinculadas a insights.
- 2 objectives activos con progreso 0.72 y 0.61.
- 36 tareas completadas.
- Lead times (días): 2, 3, 4, 5, 3, 8, 2, 6, 4, 5.
- 10 tareas en `En Proceso` con 5 personas.
- 140 días-tarea activos, 28 días-tarea pausados.
- 24 tareas de desarrollo completadas; 16 con test-first.
- 52 builds, 46 verdes.
- 9 despliegues a producción; 2 con incidente.

Cálculos:

1. **CCU** = 8 / 4 = **2 entrevistas/semana**.
2. **TIT** = 9 / 18 × 100 = **50 %**.
3. **Progreso estratégico promedio** = (0.72 + 0.61) / 2 = **66.5 %**.
4. **Throughput semanal** = 36 / 4 = **9 tareas/semana**.
5. **Lead time promedio** = 42 / 10 = **4.2 días**.
6. **WIP por persona** = 10 / 5 = **2.0**.
7. **Flow efficiency** = 140 / (140 + 28) × 100 = **83.3 %**.
8. **TDD ratio** = 16 / 24 × 100 = **66.7 %**.
9. **CI health** = 46 / 52 × 100 = **88.5 %**.
10. **Deployment Frequency** = 9 despliegues/mes.
11. **Change Failure Rate** = 2 / 9 × 100 = **22.2 %**.

Diagnóstico del sistema:

- El equipo descubre con frecuencia suficiente.
- La mitad del trabajo nuevo ya nace de evidencia, lo cual es sano.
- El flujo operativo está bien controlado.
- La calidad técnica y la estabilidad de entrega aún no están al nivel del resto del sistema.

La lectura importante del marco no es cada cifra individual sino la coherencia entre capas: **si el flujo y el discovery se ven sanos, pero DORA no, el cuello está en ingeniería; si DORA está fuerte y los OKRs no avanzan, el problema es dirección o priorización**.

### 3. Modelo de datos

Cenit Flow System no propone un modelo de datos paralelo a las metodologías anteriores, sino una **composición explícita de capacidades compartidas**. La regla de diseño es: una entidad base, múltiples vistas metodológicas.

Las entidades mínimas del sistema son:

```sql
-- Núcleo operativo
-- users(id), tasks(id) ya existentes

-- Historial de transiciones: base de flujo, aging, SPACE, Lean y parte de Riesgos
CREATE TABLE task_state_transitions (
    id            SERIAL PRIMARY KEY,
    task_id       INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    from_state    VARCHAR(30),
    to_state      VARCHAR(30) NOT NULL,
    changed_by    INTEGER REFERENCES users(id),
    changed_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    reason        TEXT
);

-- Vínculo evidencia -> ejecución
CREATE TABLE insights (
    id            SERIAL PRIMARY KEY,
    entidad       VARCHAR(50) NOT NULL,
    tipo          VARCHAR(20) NOT NULL CHECK (tipo IN ('dolor','deseo','contexto','objecion')),
    texto         TEXT NOT NULL,
    created_by    INTEGER REFERENCES users(id),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE task_insights (
    task_id       INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    insight_id    INTEGER NOT NULL REFERENCES insights(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, insight_id)
);

-- Dirección trimestral
CREATE TABLE okr_cycles (
    id            SERIAL PRIMARY KEY,
    nombre        VARCHAR(40) NOT NULL,
    fecha_inicio  DATE NOT NULL,
    fecha_fin     DATE NOT NULL,
    estado        VARCHAR(20) NOT NULL DEFAULT 'activo'
);

CREATE TABLE objectives (
    id            SERIAL PRIMARY KEY,
    cycle_id      INTEGER NOT NULL REFERENCES okr_cycles(id) ON DELETE CASCADE,
    titulo        VARCHAR(200) NOT NULL,
    owner_id      INTEGER REFERENCES users(id),
    parent_id     INTEGER REFERENCES objectives(id) ON DELETE SET NULL
);

CREATE TABLE key_results (
    id            SERIAL PRIMARY KEY,
    objective_id  INTEGER NOT NULL REFERENCES objectives(id) ON DELETE CASCADE,
    titulo        VARCHAR(200) NOT NULL,
    valor_inicial NUMERIC(12,2) NOT NULL,
    valor_meta    NUMERIC(12,2) NOT NULL,
    valor_actual  NUMERIC(12,2) NOT NULL DEFAULT 0,
    peso          NUMERIC(4,2) NOT NULL DEFAULT 1.0
);

CREATE TABLE task_key_results (
    task_id       INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    kr_id         INTEGER NOT NULL REFERENCES key_results(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, kr_id)
);

-- Capa de sprint opcional
CREATE TABLE sprints (
    id            SERIAL PRIMARY KEY,
    entidad       VARCHAR(50) NOT NULL,
    nombre        VARCHAR(80) NOT NULL,
    objetivo      TEXT,
    fecha_inicio  DATE NOT NULL,
    fecha_fin     DATE NOT NULL,
    estado        VARCHAR(20) NOT NULL DEFAULT 'planificado'
);

CREATE TABLE sprint_tasks (
    sprint_id     INTEGER NOT NULL REFERENCES sprints(id) ON DELETE CASCADE,
    task_id       INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    committed     BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (sprint_id, task_id)
);

-- Motor genérico de métricas
CREATE TABLE kpi_definitions (
    id            SERIAL PRIMARY KEY,
    clave         VARCHAR(60) UNIQUE NOT NULL,
    nombre        VARCHAR(120) NOT NULL,
    metrica_fuente VARCHAR(60) NOT NULL,
    direccion     VARCHAR(10) NOT NULL CHECK (direccion IN ('up','down','band')),
    meta          NUMERIC(12,2),
    umbral_alerta NUMERIC(12,2),
    banda_min     NUMERIC(12,2),
    banda_max     NUMERIC(12,2),
    entidad       VARCHAR(50),
    owner_id      INTEGER REFERENCES users(id)
);

CREATE TABLE kpi_measurements (
    id            SERIAL PRIMARY KEY,
    kpi_id        INTEGER NOT NULL REFERENCES kpi_definitions(id) ON DELETE CASCADE,
    periodo_inicio DATE NOT NULL,
    periodo_fin    DATE NOT NULL,
    valor         NUMERIC(12,2) NOT NULL,
    estado        VARCHAR(10) NOT NULL CHECK (estado IN ('verde','ambar','rojo','sin_datos')),
    UNIQUE (kpi_id, periodo_inicio, periodo_fin)
);

-- Entrega técnica
CREATE TABLE deployments (
    id            SERIAL PRIMARY KEY,
    environment   VARCHAR(30) NOT NULL DEFAULT 'production',
    status        VARCHAR(20) NOT NULL DEFAULT 'success',
    commit_sha    VARCHAR(64) NOT NULL,
    deployed_at   TIMESTAMPTZ NOT NULL
);

CREATE TABLE incidents (
    id            SERIAL PRIMARY KEY,
    caused_by_deployment_id INTEGER REFERENCES deployments(id) ON DELETE SET NULL,
    title         VARCHAR(200) NOT NULL,
    detected_at   TIMESTAMPTZ NOT NULL,
    restored_at   TIMESTAMPTZ
);

-- Reporting contractual opt-in
CREATE TABLE projects (
    id            SERIAL PRIMARY KEY,
    nombre        VARCHAR(120) NOT NULL,
    estado        VARCHAR(20) NOT NULL DEFAULT 'planeacion',
    fecha_inicio  DATE,
    fecha_fin_plan DATE,
    manager_id    INTEGER REFERENCES users(id)
);

ALTER TABLE tasks ADD COLUMN project_id INTEGER REFERENCES projects(id);
ALTER TABLE tasks ADD COLUMN peso_presupuesto NUMERIC(14,2) DEFAULT 0;
ALTER TABLE tasks ADD COLUMN horas_reales NUMERIC(10,2) DEFAULT 0;
```

Decisión de arquitectura clave: el sistema gira alrededor de `tasks` y `task_state_transitions`. Encima de eso se acoplan las capas de discovery, objetivos, sprints, métricas, entrega y reporting formal. Esto evita tener doce micro-modelos inconexos y responde a la decisión más importante de producto en todo el documento: **un solo sistema de trabajo, múltiples lentes metodológicos**.

### 4. Casos de uso del domain layer

La capa de dominio debe modelar el sistema como un conjunto de servicios puros, organizados por capacidad y no por framework.

```python
from dataclasses import dataclass
from datetime import date

@dataclass
class FlowSystemHealth:
    discovery_ok: bool
    direction_ok: bool
    flow_ok: bool
    quality_ok: bool
    delivery_ok: bool
    alerts: list[str]


class CenitFlowService:

    def evaluar_descubrimiento(
        self, entrevistas: list[dict], insights: list[dict],
        hipotesis: list[dict], tareas_nuevas: list[dict],
        vinculos_insight: list[dict]
    ) -> dict:
        """CCU, TIT, TVH, TCA, CPA."""

    def evaluar_direccion(
        self, objectives: list[dict], krs: list[dict], tareas: list[dict],
        task_krs: list[dict], hoy: date
    ) -> dict:
        """Progreso de objectives, alignment ratio, check-ins pendientes."""

    def evaluar_flujo(
        self, tareas: list[dict], transiciones: list[dict], personas_activas: int
    ) -> dict:
        """Throughput, lead time, WIP/persona, flow efficiency, aging."""

    def evaluar_calidad_tecnica(
        self, tareas_dev: list[dict], builds: list[dict], pairing: list[dict]
    ) -> dict:
        """TDD ratio, CI health, pairing coverage, sustainable pace."""

    def evaluar_entrega(
        self, deployments: list[dict], incidents: list[dict], change_events: list[dict]
    ) -> dict:
        """DF, LTC, CFR, MTTR."""

    def evaluar_reporting(
        self, tareas_proyecto: list[dict], baseline: dict, curva_pv: list[dict],
        fecha_corte: date
    ) -> dict:
        """SPI, CPI, EAC, VAC, TCPI."""

    def evaluar_salud_integral(
        self,
        discovery: dict,
        direction: dict,
        flow: dict,
        quality: dict,
        delivery: dict
    ) -> FlowSystemHealth:
        """Integra capas y produce alertas sistémicas."""
```

La regla de arquitectura respetada es la misma de las demás secciones: el dominio recibe `list[dict]` y devuelve dataclasses o dicts puros. FastAPI, SQLAlchemy, GitHub y Slack viven en infraestructura. Eso permite probar todo el sistema sin base de datos y sin HTTP.

### 5. Diseño de API REST

La API del Cenit Flow System no introduce un router completamente nuevo para todo, sino una **convención de integración** entre routers existentes y un endpoint agregado de salud integral.

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/api/flow-system/health?entidad=X&periodo=2026-07` | Resumen integral del sistema |
| GET | `/api/flow-system/alerts?entidad=X` | Alertas consolidadas de discovery, flujo, entrega y objetivos |
| GET | `/api/flow-system/scorecard?entidad=X` | Scorecard ejecutivo resumido |

La mayoría de capacidades siguen viviendo en sus routers naturales:

- Discovery: `/api/dt/...`
- OKRs: `/api/okrs/...`
- Sprints: `/api/sprints/...`
- DORA: `/api/dora/...`
- KPIs: `/api/kpis/...`
- Projects: `/api/projects/...`

Ejemplo de respuesta de salud integral:

```json
{
  "entidad": "Desarrollo",
  "periodo": "2026-07",
  "discovery": {
    "ccu": 2.0,
    "tit": 50.0,
    "estado": "verde"
  },
  "direction": {
    "okr_progress": 0.67,
    "alignment_ratio": 0.71,
    "estado": "verde"
  },
  "flow": {
    "throughput_weekly": 9.0,
    "lead_time_avg": 4.2,
    "wip_per_person": 2.0,
    "flow_efficiency": 83.3,
    "estado": "verde"
  },
  "quality": {
    "tdd_ratio": 66.7,
    "ci_health": 88.5,
    "estado": "ambar"
  },
  "delivery": {
    "deployment_frequency": 9,
    "change_failure_rate": 22.2,
    "mttr_hours": 11.0,
    "estado": "ambar"
  },
  "alertas": [
    "La estabilidad de entrega es el cuello de botella principal del sistema."
  ]
}
```

El propósito de este endpoint no es reemplazar vistas especializadas, sino dar una lectura ejecutiva coherente sin obligar al usuario a interpretar cinco dashboards desconectados.

### 6. Vista o componente de UI

La UI del Cenit Flow System debería expresarse como una vista nueva: **`ui/views/flow_system.py`** o, en la arquitectura Next.js nueva, como la página **`/flow-system`**.

Diseño de la vista:

1. **Cabecera ejecutiva**
   - entidad/equipo seleccionado
   - periodo
   - scorecard general
   - mensaje resumen del sistema

2. **Mapa por capas**
   - cinco tarjetas principales:
     - Descubrimiento
     - Dirección
     - Flujo
     - Calidad técnica
     - Entrega
   - cada una con valor principal, semáforo y mini tendencia

3. **Zona de alertas**
   - ordenadas por severidad
   - con acción sugerida
   - ejemplo: “CFR alto → revisar suite E2E y Definition of Done”

4. **Vista de trazabilidad**
   - Insight → KR → Tarea → Deploy/Incidente
   - esta es la parte que más diferencia a Cenit de un dashboard genérico

5. **Vista contractual opcional**
   - solo visible si el equipo/proyecto opera en modo contractual
   - SPI, CPI, hitos y control de cambios

La decisión de UX más importante es esta: el usuario no debe sentir que entró a “otra metodología”, sino a una **vista integradora del sistema completo**.

### 7. Estrategia de testing E2E

El Cenit Flow System exige una estrategia de testing centrada en **consistencia entre capas**, no solo en CRUD.

**Pytest de dominio**

- `test_integracion_descubrimiento_a_tareas`: una tarea vinculada a insight sube TIT.
- `test_integracion_tareas_a_okrs`: completar tareas vinculadas mueve KRs derivados.
- `test_integracion_flujo_a_kpis`: degradar lead time mueve KPI correspondiente.
- `test_integracion_xp_a_dora`: baja de CI health correlaciona con CFR alto en dataset sintético.
- `test_integracion_reporting_con_baseline`: EV derivado de tareas produce SPI correcto.
- `test_salud_integral_detecta_cuello_de_botella`: discovery, direction y flow verdes con delivery ámbar → alerta sobre entrega.

**Playwright E2E**

1. Crear insight → crear tarea desde insight → verificar trazabilidad.
2. Vincular tarea a KR → completar tarea → verificar progreso del KR.
3. Mover tarea por Kanban → verificar impacto en flujo y KPI.
4. Registrar despliegue e incidente → verificar actualización de DORA.
5. Abrir vista integral → verificar que la alerta principal coincida con los datos sembrados.

El valor real del E2E aquí no es validar una vista aislada, sino demostrar que el sistema funciona como una metodología viva y no como módulos inconexos.

### 8. Integraciones externas

| Integración | Para qué | Prioridad |
|---|---|---|
| **GitHub / GitLab** | Alimentar DORA, CI health, trazabilidad commit→task | Alta |
| **Slack** | Recordatorios de check-ins, alertas de KPIs, incidentes y discovery | Alta |
| **Google Calendar** | Entrevistas, ceremonias ligeras, hitos contractuales | Media |
| **Typeform / Forms** | Encuestas de validación, discovery cuantitativo, SPACE perceptual | Media |
| **Toggl / Clockify** | Horas reales para EVM-lite | Media |
| **WhatsApp Business API** | Alertas y resúmenes para equipos LatAm fuera de Slack | Baja post-PMF |

La prioridad de integraciones sigue la lógica del sistema: primero lo que alimenta entrega, salud y hábito; después lo que alimenta reporting formal.

### 9. Conflictos o solapamientos

El propósito de Cenit Flow System es precisamente resolver los solapamientos entre marcos. Las reglas son explícitas:

| Conflicto | Resolución en Cenit Flow System |
|---|---|
| Scrum vs Kanban | Kanban es el sistema base; Scrum es una cadencia opcional encima |
| KPIs vs DORA vs SPACE | Un solo motor de métricas, distintos catálogos y vistas |
| OKRs vs tareas operativas | Los OKRs dan dirección; las tareas ejecutan |
| Design Thinking vs Lean experiments | Una sola cadena insight → hipótesis → experimento |
| Waterfall/PMBOK vs trabajo diario | Solo capa de reporting contractual, nunca tablero central |
| WSJF vs Eisenhower | WSJF para priorización de mediano plazo; Eisenhower para foco diario |
| XP vs métricas gerenciales | Las prácticas técnicas son del equipo, no ranking individual |

La regla más importante de todo el sistema: **nunca dos entidades distintas para el mismo problema**. Una sola tarea, una sola transición, una sola fuente de verdad por métrica y una sola cadena de trazabilidad.

### 10. Antipatrones conocidos

- **La herramienta Frankenstein**: meter Scrum, OKRs, discovery, DORA y proyectos como módulos independientes sin gramática común. Se ve completo, pero obliga al usuario a traducir entre modelos mentales incompatibles.
- **El tablero sin dirección**: Kanban activo con cero vínculo a OKRs o insights. Mucho movimiento, poco resultado.
- **El dashboard sin acción**: 20 métricas sin prioridades ni recomendación concreta.
- **El discovery teatral**: entrevistas e insights sin vínculo a tareas reales.
- **El reporting que contamina la ejecución**: pedir al equipo doble captura para satisfacer al cliente o gerente.
- **La metodología por persona**: DORA, SPACE o XP usados para rankear individuos. Destruye confianza y corrompe el dato.
- **La vista separada para todo**: cada marco con su propia isla de información. El sistema se vuelve navegable solo para quien lo diseñó.

La lección del panel es directa: el valor no está en tener muchas metodologías, sino en **integrarlas en una secuencia operativa coherente**.

### 11. Caso real

No existe un producto comercial que implemente exactamente este sistema, pero sí referentes parciales muy claros:

- **Linear** aporta el modelo de ejecución opinionado, el vínculo proyecto→issue y una lectura integrada de flujo.
- **Sleuth** demuestra el valor de DORA como feature dentro del trabajo del equipo.
- **Quantive/Gtmhub** valida que los objetivos solo viven si se conectan con sistemas fuente.
- **Wrike** muestra cómo ofrecer reporting de proyecto sin convertir todo el sistema en PMO.
- **DX** demuestra que la salud del equipo se vuelve comprable cuando se une telemetría con percepción.

La oportunidad real de Cenit es combinar esas capacidades en un producto nativo para el mercado LatAm, con un posicionamiento que ninguno de esos jugadores tiene: **discovery, flujo, riesgo y reporting en una sola superficie, en español, con pragmatismo operacional**.

### 12. Costo de implementación

**Costo: MEDIO-ALTO si se construye de cero como visión completa; MEDIO si se implementa por capas reutilizando módulos existentes.**

Estimación por fases para 1-2 desarrolladores:

| Fase | Alcance | Detalle |
|---|---|---|
| F1 | Núcleo compartido | `task_state_transitions`, motor de métricas, separación dominio/aplicación/infraestructura |
| F2 | Dirección + flujo | OKRs, KPIs, Kanban mejorado, Mi Día, Riesgos |
| F3 | Calidad + entrega | XP-lite, DORA, CI health, alertas Slack |
| F4 | Discovery | insights, hipótesis, trazabilidad hacia tareas |
| F5 | Reporting contractual | projects, baseline, EVM-lite, control de cambios |

Recomendación del panel: no construir “la metodología completa” como big bang. El sistema debe emerger en este orden:

1. Flujo y riesgo
2. Objetivos y KPIs
3. Entrega técnica
4. Discovery
5. Reporting contractual

Así cada capa nueva reutiliza la anterior y evita reescrituras.

### 13. Cuándo NO construir esto todavía

Señales de que sería un error intentar implementar el Cenit Flow System completo hoy:

- **Si el tablero base aún no retiene uso real**. El sistema entero depende de una ejecución cotidiana confiable.
- **Si los pilotos no distinguen todavía entre organización diaria y reporting ejecutivo**. Meter demasiadas capas antes de que el dolor aparezca es sobre-ingeniería.
- **Si el equipo fundador aún no usa el propio flujo de forma manual**. Una metodología que no se practica antes de codificarse termina reflejando aspiración, no realidad.
- **Si se intenta lanzar todo como marca de producto al mismo tiempo**. Comercialmente conviene entrar por Kanban+Mi Día+Riesgos y dejar que el sistema híbrido emerja en la experiencia, no en un discurso demasiado abstracto.

Lo que sí conviene hacer ya:

1. Consolidar `tasks` + `task_state_transitions` como núcleo.
2. Construir el motor genérico de métricas.
3. Vincular tareas con KRs.
4. Preparar la trazabilidad insight→tarea.
5. Mantener el reporting contractual como opt-in y no como experiencia por defecto.

En una frase: **Cenit Flow System no debe construirse como un módulo aislado, sino como la arquitectura metodológica que ordena todo lo demás**.
