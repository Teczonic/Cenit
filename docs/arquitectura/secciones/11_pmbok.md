## 11. PMBOK/PMI

### 1. Principio central y origen

El PMBOK (Project Management Body of Knowledge) es el cuerpo de conocimiento del Project Management Institute (PMI), fundado en 1969 en Pensilvania, EE.UU., como respuesta a la explosión de proyectos de ingeniería, defensa y aeroespacial de la posguerra (el programa Polaris y el Apolo son sus ancestros culturales directos). La primera edición formal del PMBOK Guide se publicó en 1996; hoy va por la 7ª edición (2021), que pivotó de "49 procesos en 10 áreas de conocimiento" a 12 principios y 8 dominios de desempeño, reconociendo explícitamente los enfoques ágiles e híbridos.

El problema que resuelve es la **gestión de restricciones en proyectos con inicio y fin definidos**: alcance, cronograma, costo, calidad, riesgos, recursos, comunicaciones, adquisiciones e interesados, integrados bajo una responsabilidad única (el project manager). Su artefacto conceptual más potente es la **triple restricción** (alcance–tiempo–costo) y su instrumento de medición estrella es el **Earned Value Management (EVM)**: la única técnica de las 12 metodologías de este documento que responde con un número la pregunta "¿cuánto valor del plan hemos producido realmente por cada peso gastado?".

El error de gestión que previene es doble. Primero, el **avance fantasma**: equipos que reportan "90% completado" durante meses porque miden esfuerzo consumido y no valor entregado contra una línea base. Segundo, el **scope creep silencioso**: cambios de alcance aceptados informalmente por chat que destruyen el cronograma sin que nadie haya decidido conscientemente aceptarlos (el control integrado de cambios existe exactamente para eso).

Para Cenit la lectura estratégica es matizada. Nuestro comprador objetivo —equipos de desarrollo de 10-50 personas en LatAm que huyen de la burocracia de Jira— no quiere "un Jira con más ceremonias PMI". Pero hay una realidad comercial innegable en la región: muchos clientes de esos equipos (bancos, universidades, gobierno, grandes industrias en Colombia y México) **contratan por proyecto cerrado, con alcance y presupuesto fijos, y exigen informes de avance formales**. Las agencias de software y consultoras —un segmento enorme del mercado LatAm— viven en modo híbrido: ejecutan con Kanban por dentro y reportan con lenguaje PMI por fuera. Cenit puede capturar ese híbrido con una capa ligera de PMBOK (proyectos con baseline, EVM simplificado y control de cambios) sin convertirse en Microsoft Project. Desde la óptica de calidad, además, una baseline formal es un oráculo de testing magnífico: define de forma verificable qué significa "el proyecto va bien".

### 2. Métricas y fórmulas exactas

El núcleo cuantitativo del PMBOK es el EVM. Variables base:

| Sigla | Nombre | Fórmula | Significado |
|---|---|---|---|
| BAC | Budget at Completion | Σ presupuesto planeado | Presupuesto total del proyecto |
| PV | Planned Value | % planeado a la fecha × BAC | Lo que deberíamos haber producido |
| EV | Earned Value | % real completado × BAC | Valor de lo realmente producido |
| AC | Actual Cost | Σ costos reales incurridos | Lo que hemos gastado |
| SV | Schedule Variance | EV − PV | Adelanto/atraso en valor |
| CV | Cost Variance | EV − AC | Ahorro/sobrecosto |
| SPI | Schedule Performance Index | EV / PV | >1 adelantado, <1 atrasado |
| CPI | Cost Performance Index | EV / AC | >1 eficiente, <1 sobrecosto |
| EAC | Estimate at Completion | BAC / CPI | Costo total proyectado |
| ETC | Estimate to Complete | EAC − AC | Lo que falta por gastar |
| VAC | Variance at Completion | BAC − EAC | Desviación final proyectada |
| TCPI | To-Complete Performance Index | (BAC − EV) / (BAC − AC) | Eficiencia requerida para terminar en presupuesto |

**Ejemplo numérico — equipo ficticio de 5 personas.** El equipo "Andina Dev" (2 backend, 1 frontend, 1 QA, 1 líder técnico) ejecuta el proyecto "Portal de Certificados" para una universidad: 12 semanas, BAC = 60.000.000 COP (costo blended de 5 personas × 12 semanas × 1.000.000 COP/persona-semana). En Cenit, el proyecto se descompone en 40 tareas con peso presupuestal (para simplificar, uniforme: 1.500.000 COP por tarea).

Corte en la **semana 6** (mitad del plan):

1. **PV**: el cronograma planeaba tener 22 de 40 tareas completadas → PV = 22 × 1.500.000 = **33.000.000 COP** (55% del BAC).
2. **EV**: Cenit cuenta las tareas con `estado = 'Completado'`: son 18 → EV = 18 × 1.500.000 = **27.000.000 COP**.
3. **AC**: horas reales registradas × tarifa: el equipo consumió 6 semanas completas de los 5 → AC = 5 × 6 × 1.000.000 = **30.000.000 COP**.
4. **SV** = 27.000.000 − 33.000.000 = **−6.000.000 COP** (atrasados el equivalente a 4 tareas).
5. **CV** = 27.000.000 − 30.000.000 = **−3.000.000 COP** (sobrecosto).
6. **SPI** = 27.0M / 33.0M = **0,82** → el equipo avanza al 82% del ritmo planeado.
7. **CPI** = 27.0M / 30.0M = **0,90** → por cada peso gastado se producen 0,90 pesos de valor.
8. **EAC** = 60.0M / 0,90 = **66.666.667 COP** → si nada cambia, el proyecto costará ~6,7M más.
9. **ETC** = 66.67M − 30.0M = **36.666.667 COP** restantes.
10. **VAC** = 60.0M − 66.67M = **−6.666.667 COP** de pérdida proyectada (crítico si el contrato es precio fijo).
11. **TCPI** = (60.0M − 27.0M) / (60.0M − 30.0M) = 33.0M / 30.0M = **1,10** → para terminar en presupuesto el equipo tendría que volverse 10% más eficiente que el plan y 22% más que su desempeño actual. Regla práctica PMI: TCPI > 1,10 es señal de renegociar alcance o presupuesto, no de "apretar".

Nota de diseño de producto: en Cenit el "costo" puede expresarse en **horas-persona en lugar de dinero** para los equipos que no quieren manejar tarifas — las fórmulas son idénticas y el dato es menos sensible, lo cual reduce fricción de adopción en pilotos.

### 3. Modelo de datos

Hoy `tasks.proyecto` es un `String(80)` libre y no existe entidad de proyecto formal. PMBOK exige promover el proyecto a entidad de primera clase con baseline versionada, sin romper el esquema actual (la columna string se conserva; se añade una FK opcional).

```sql
-- Proyecto formal (charter ligero). Extiende el concepto tasks.proyecto (string libre).
CREATE TABLE projects (
    id              SERIAL PRIMARY KEY,
    nombre          VARCHAR(120) NOT NULL,
    codigo          VARCHAR(20) UNIQUE,              -- "PORT-CERT"
    cliente         VARCHAR(100),                    -- mismo dominio que tasks.cliente
    sponsor         VARCHAR(120),                    -- interesado que aprueba cambios
    objetivo        TEXT,                            -- charter resumido
    estado          VARCHAR(20) NOT NULL DEFAULT 'planeacion'
                    CHECK (estado IN ('planeacion','ejecucion','cerrado','cancelado')),
    modo_costo      VARCHAR(10) NOT NULL DEFAULT 'horas'
                    CHECK (modo_costo IN ('horas','dinero')),
    fecha_inicio    DATE,
    fecha_fin_plan  DATE,
    manager_id      INTEGER REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Vinculo opcional de tareas existentes a proyectos formales (no rompe datos legados)
ALTER TABLE tasks
    ADD COLUMN project_id       INTEGER REFERENCES projects(id),
    ADD COLUMN peso_presupuesto NUMERIC(14,2) DEFAULT 0,  -- horas o COP segun modo_costo
    ADD COLUMN horas_reales     NUMERIC(10,2) DEFAULT 0;  -- AC acumulado por tarea

-- Linea base versionada (scope + schedule + cost baseline). Inmutable una vez aprobada.
CREATE TABLE project_baselines (
    id              SERIAL PRIMARY KEY,
    project_id      INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    version         INTEGER NOT NULL DEFAULT 1,
    bac             NUMERIC(14,2) NOT NULL,          -- Budget at Completion
    fecha_fin_plan  DATE NOT NULL,
    aprobada_por    INTEGER REFERENCES users(id),
    aprobada_at     TIMESTAMPTZ,
    motivo          TEXT,                            -- por que se rebaseo (v2+)
    UNIQUE (project_id, version)
);

-- Detalle de la baseline: PV acumulado planeado por semana (curva S)
CREATE TABLE baseline_curve_points (
    id              SERIAL PRIMARY KEY,
    baseline_id     INTEGER NOT NULL REFERENCES project_baselines(id) ON DELETE CASCADE,
    fecha_corte     DATE NOT NULL,
    pv_acumulado    NUMERIC(14,2) NOT NULL,
    UNIQUE (baseline_id, fecha_corte)
);

-- Snapshot EVM periodico (job semanal): congela metricas para tendencia historica
CREATE TABLE evm_snapshots (
    id              SERIAL PRIMARY KEY,
    project_id      INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    baseline_id     INTEGER NOT NULL REFERENCES project_baselines(id),
    fecha_corte     DATE NOT NULL,
    pv              NUMERIC(14,2) NOT NULL,
    ev              NUMERIC(14,2) NOT NULL,
    ac              NUMERIC(14,2) NOT NULL,
    spi             NUMERIC(6,3),
    cpi             NUMERIC(6,3),
    eac             NUMERIC(14,2),
    tcpi            NUMERIC(6,3),
    UNIQUE (project_id, fecha_corte)
);

-- Control integrado de cambios (anti scope-creep)
CREATE TABLE change_requests (
    id              SERIAL PRIMARY KEY,
    project_id      INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    task_id         INTEGER REFERENCES tasks(id),    -- tarea nueva/afectada, opcional
    titulo          VARCHAR(200) NOT NULL,
    descripcion     TEXT,
    impacto_costo   NUMERIC(14,2) DEFAULT 0,         -- delta sobre BAC
    impacto_dias    INTEGER DEFAULT 0,               -- delta sobre fecha fin
    estado          VARCHAR(20) NOT NULL DEFAULT 'propuesto'
                    CHECK (estado IN ('propuesto','aprobado','rechazado','implementado')),
    solicitado_por  INTEGER REFERENCES users(id),
    decidido_por    INTEGER REFERENCES users(id),
    decidido_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Registro de interesados (stakeholder register, version minima)
CREATE TABLE stakeholders (
    id              SERIAL PRIMARY KEY,
    project_id      INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    nombre          VARCHAR(120) NOT NULL,
    rol             VARCHAR(80),                     -- sponsor | usuario clave | proveedor
    poder           SMALLINT CHECK (poder BETWEEN 1 AND 5),
    interes         SMALLINT CHECK (interes BETWEEN 1 AND 5),
    estrategia      VARCHAR(30)                      -- gestionar de cerca | informar | monitorear
);

CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_evm_project_fecha ON evm_snapshots(project_id, fecha_corte);
```

Decisiones deliberadas: (a) **no** se crea tabla de WBS jerárquica multinivel — las `tasks` con `peso_presupuesto` son el nivel de paquete de trabajo; una WBS de 4 niveles sería sobre-ingeniería para equipos de 10-50 personas; (b) las baselines son **inmutables** y versionadas: un cambio aprobado genera baseline v2, nunca edita la v1 — eso hace el sistema auditable y trivial de testear; (c) el registro de riesgos PMI **no se duplica**: el `risk_score` existente por tarea ya cumple ese rol y la vista de riesgos lo consume.

### 4. Casos de uso del domain layer

Nuevo servicio en `domain/services.py` (o `domain/evm.py`), puro y operando sobre dicts/dataclasses como los servicios existentes (`KanbanService`, `AnalyticsService`):

```python
from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass(frozen=True)
class EVMReport:
    fecha_corte: date
    bac: float
    pv: float
    ev: float
    ac: float
    sv: float
    cv: float
    spi: Optional[float]
    cpi: Optional[float]
    eac: Optional[float]
    etc: Optional[float]
    vac: Optional[float]
    tcpi: Optional[float]
    semaforo: str  # "verde" | "amarillo" | "rojo"


class EVMService:
    def calcular_evm(
        self,
        tareas: list[dict],            # tasks del proyecto, con peso_presupuesto y horas_reales
        curva_pv: list[dict],          # baseline_curve_points [{fecha_corte, pv_acumulado}]
        bac: float,
        fecha_corte: date,
        tarifa_hora: float = 1.0,      # 1.0 en modo horas
    ) -> EVMReport:
        # PV: interpolar pv_acumulado de la curva S al ultimo punto <= fecha_corte
        # EV: sum(peso_presupuesto de tareas con estado == "Completado"
        #         y fecha_completado <= fecha_corte)
        #     + credito parcial 50% para "En Proceso" (regla 50/50, configurable)
        # AC: sum(horas_reales) * tarifa_hora
        # Derivadas: sv, cv, spi=ev/pv (None si pv==0), cpi=ev/ac (None si ac==0)
        # eac = bac/cpi; etc = eac-ac; vac = bac-eac
        # tcpi = (bac-ev)/(bac-ac) si bac>ac, si no None (presupuesto agotado)
        # semaforo: rojo si spi<0.85 o cpi<0.85; amarillo si <0.95; verde en el resto
        ...

    def construir_curva_s(
        self, tareas: list[dict], fecha_inicio: date, fecha_fin: date
    ) -> list[dict]:
        # Distribuye el peso_presupuesto de cada tarea entre su fecha_inicio y
        # fecha_fin (lineal); acumula por semana -> puntos de la curva S planeada.
        ...


class ChangeControlService:
    def evaluar_impacto(self, cr: dict, baseline: dict) -> dict:
        # Retorna {"bac_nuevo": bac + impacto_costo,
        #          "fecha_fin_nueva": fecha_fin + impacto_dias,
        #          "requiere_rebaseline": impacto_costo/bac > 0.10 or impacto_dias > 14}
        ...

    def aprobar_cambio(
        self, cr: dict, baseline_actual: dict, aprobador_id: int
    ) -> dict:
        # Si requiere_rebaseline -> construye payload de baseline v(n+1)
        # Si no -> solo marca CR aprobado (absorbido en reservas)
        # Regla de negocio: solo role == "admin" o manager del proyecto aprueba
        ...


class StakeholderService:
    def matriz_poder_interes(self, stakeholders: list[dict]) -> dict[str, list[dict]]:
        # Cuadrantes: "gestionar_de_cerca" (poder>=4, interes>=4),
        # "mantener_satisfecho", "informar", "monitorear"
        ...
```

Todo determinista y sin I/O: el CRUD lee `tasks`, `project_baselines` y `evm_snapshots` en `api/crud.py` y delega el cálculo aquí — mismo patrón que `AnalyticsService`. Eso permite testear el EVM con pytest puro, sin base de datos.

### 5. Diseño de API REST

Consistente con el estilo existente (`/api/tasks`, `/api/analytics/...`), bajo un router `api/routers/projects.py`:

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/projects` | Crear proyecto (charter ligero) |
| GET | `/api/projects` | Listar proyectos con semáforo EVM |
| GET | `/api/projects/{id}` | Detalle + baseline activa |
| POST | `/api/projects/{id}/baseline` | Aprobar baseline (v1 o rebase) |
| GET | `/api/projects/{id}/evm?fecha_corte=2026-07-01` | Reporte EVM al corte |
| GET | `/api/projects/{id}/evm/history` | Serie de snapshots (tendencia SPI/CPI) |
| POST | `/api/projects/{id}/change-requests` | Registrar solicitud de cambio |
| PATCH | `/api/change-requests/{id}` | Aprobar/rechazar (solo admin/manager) |
| POST | `/api/projects/{id}/stakeholders` | Registrar interesado |
| PATCH | `/api/tasks/{id}/effort` | Registrar horas reales y peso (extiende tasks) |

Ejemplo — respuesta de `GET /api/projects/7/evm?fecha_corte=2026-07-01`:

```json
{
  "project_id": 7,
  "codigo": "PORT-CERT",
  "baseline_version": 1,
  "fecha_corte": "2026-07-01",
  "modo_costo": "dinero",
  "bac": 60000000,
  "pv": 33000000,
  "ev": 27000000,
  "ac": 30000000,
  "sv": -6000000,
  "cv": -3000000,
  "spi": 0.82,
  "cpi": 0.90,
  "eac": 66666667,
  "etc": 36666667,
  "vac": -6666667,
  "tcpi": 1.10,
  "semaforo": "rojo",
  "recomendacion": "TCPI > 1.10: renegociar alcance o presupuesto con el sponsor"
}
```

Ejemplo — `POST /api/projects/7/change-requests`:

```json
{
  "titulo": "Agregar firma digital de certificados",
  "descripcion": "El sponsor solicita integrar firma con vigencia legal",
  "impacto_costo": 9000000,
  "impacto_dias": 21,
  "task_id": null
}
```

Autorización: reutiliza el JWT existente; `PATCH /api/change-requests/{id}` y `POST .../baseline` exigen `role == "admin"` o ser `manager_id` del proyecto — primera funcionalidad de Cenit que explota de verdad la columna `users.role`.

### 6. Vista o componente de UI

Nueva vista `ui/views/proyectos.py` ("Proyectos"), añadida a la navegación de `ui/app.py`. Wireframe textual, de arriba hacia abajo:

1. **Cabecera con selector**: `st.selectbox` de proyecto activo + badge de estado (planeación/ejecución/cerrado) + chip con versión de baseline vigente ("Baseline v2 · aprobada 2026-06-10").
2. **Fila de 4 `st.metric`**: SPI (con delta vs. snapshot anterior), CPI (con delta), EAC vs. BAC, y "Días de atraso proyectados". Un `st.caption` traduce a lenguaje humano: "Al ritmo actual el proyecto costará 6,7M más y terminará 11 días tarde".
3. **Curva S** (`st.plotly_chart`): tres líneas — PV planeado (baseline), EV real y AC real — con la fecha de corte como línea vertical. Es el gráfico que el usuario exporta y pega en el informe a su cliente: ahí vive el valor de venta de toda la vista.
4. **Tabs**: `st.tabs(["Tareas y pesos", "Cambios", "Interesados"])`.
   - *Tareas y pesos*: `st.data_editor` con las tareas del proyecto, columnas editables `peso_presupuesto` y `horas_reales`; fila de totales que valida Σ pesos = BAC (`st.warning` si no cuadra).
   - *Cambios*: tabla de change requests con estado; `st.form` para crear una nueva (título, impacto en costo/días); botones Aprobar/Rechazar visibles solo para admin/manager; si el cambio aprobado supera el umbral, `st.warning` propone re-baseline con un clic.
   - *Interesados*: matriz poder/interés 2×2 como scatter simple + formulario de alta.
5. **Sidebar contextual**: botón "Congelar snapshot EVM de hoy" y descarga CSV del histórico.

Interacción clave de onboarding: si el proyecto no tiene baseline, la vista muestra un asistente de 3 pasos (asignar pesos → revisar curva S propuesta por `construir_curva_s` → aprobar baseline) en lugar de un dashboard vacío.

### 7. Estrategia de testing E2E

**Unitarios pytest del dominio** (`tests/test_evm_service.py`) — donde vive el riesgo real porque son fórmulas:

- `calcular_evm` con el caso del ejemplo numérico (5 personas, semana 6): asserts exactos de SPI=0.82, CPI=0.90, EAC≈66.67M, TCPI=1.10.
- Bordes: proyecto sin avance (EV=0 → SPI=0, CPI=None si AC=0, sin división por cero); proyecto completado (EV=BAC); AC ≥ BAC (TCPI None); curva PV vacía; fecha_corte anterior al inicio.
- Regla 50/50 de crédito parcial: tarea "En Proceso" aporta exactamente 50% de su peso.
- `evaluar_impacto`: umbral de re-baseline en 10% de BAC y en 14 días (test parametrizado en el límite exacto).
- Property-based (hypothesis) opcional: para cualquier conjunto de tareas, EV ≤ BAC y la curva S es monótona no decreciente.
- `matriz_poder_interes`: clasificación de los 4 cuadrantes con valores frontera (poder=4, interés=4).

**E2E con Playwright para Python** (`tests/e2e/test_pmbok_flow.py`), contra el stack de Docker Compose:

1. **Flujo baseline feliz**: login como admin → crear proyecto → asignar pesos en el `data_editor` → aprobar baseline v1 → verificar que aparecen las 4 métricas y la curva S (`page.get_by_test_id("metric-spi")`).
2. **Flujo EVM se mueve**: completar 2 tareas desde el Kanban existente → volver a Proyectos → congelar snapshot → assert de que EV subió y el semáforo cambió (verifica la integración Kanban↔EVM, el punto de mayor riesgo de regresión).
3. **Flujo control de cambios**: como `member`, crear change request → verificar que NO ve botones de aprobación → login como admin → aprobar un CR grande → verificar el prompt de re-baseline y que la vista muestra "Baseline v2".
4. **Flujo permisos negativos vía API**: request directo `PATCH /api/change-requests/{id}` con JWT de member → assert 403 (contexto `request` de Playwright, sin UI).
5. **Regresión visual ligera** de la curva S con `expect(locator).to_have_screenshot()` sobre datos deterministas (seed fija).

Los flujos 3 y 4 serían los primeros tests de autorización por rol de todo Cenit: valor de QA que trasciende esta metodología.

### 8. Integraciones externas

| Integración | Para qué | Prioridad |
|---|---|---|
| **Toggl / Clockify API** | Importar `horas_reales` automáticamente — el AC digitado a mano es el punto donde el EVM muere en la práctica | Alta |
| **Slack (webhooks)** | Alerta cuando SPI o CPI cruzan el umbral rojo, y notificación de change request pendiente al aprobador | Alta |
| **Google Calendar / Microsoft Graph** | Sincronizar hitos de baseline y recordatorio semanal de snapshot EVM | Media |
| **GitHub/GitLab API** | Cerrar tareas (EV) desde merges de PRs, evitando el doble registro de avance | Media |
| **Exportación a Google Sheets / PDF** | El informe de curva S que el equipo entrega a su cliente/sponsor; en LatAm el reporte formal sigue siendo un entregable contractual | Media |
| **Siigo / facturación electrónica (Colombia)** | Cruzar AC con facturación real del proyecto para agencias | Baja, exploratoria |

La de mayor apalancamiento es la de time-tracking: sin AC confiable el CPI es ficción, y pedirle a desarrolladores que digiten horas en una segunda herramienta garantiza datos basura.

### 9. Conflictos o solapamientos

| Metodología | Conflicto | Resolución |
|---|---|---|
| **Waterfall** | Solapamiento casi total: baseline, fases y control de cambios son mecánica waterfall | Una sola implementación: la capa "Proyectos" sirve a ambas secciones; Waterfall aporta el Gantt, PMBOK aporta EVM y CRs. No construir dos modelos de datos |
| **Scrum** | Filosofías de planeación opuestas: baseline fija vs. re-planeación por sprint; velocity y SPI compiten por ser "la" métrica de avance | Modo por proyecto: un proyecto es "ágil" (velocity, sin baseline) o "predictivo" (EVM). Nunca mostrar ambas métricas juntas sin contexto |
| **Kanban** | Ninguno de datos (el EVM consume el `estado` del tablero), pero compite por atención: el flujo continuo no tiene "fin de proyecto" | Kanban es la vista de ejecución diaria; Proyectos es la vista mensual/contractual. EV se deriva del tablero, cero doble captura |
| **Lean** | Tensión conceptual: PMBOK añade proceso (CRs, baselines) que Lean llamaría desperdicio | Aplicar Lean al propio PMBOK: solo 3 artefactos (baseline, EVM, CR), nada de los 49 procesos |
| **OKRs / KPIs** | Los KPIs de proyecto (SPI/CPI) pueden confundirse con los KPIs de equipo de Analytics | Namespace claro en UI: métricas de proyecto viven solo en la vista Proyectos; Analytics conserva throughput/lead time |
| **DORA / SPACE** | Riesgo de cóctel de métricas incoherente (CPI junto a deployment frequency) | Separación por audiencia: DORA/SPACE para el equipo interno, EVM para el sponsor/cliente externo |
| **SAFe** | SAFe incorpora Lean Portfolio Management, que reemplaza al EVM clásico | Irrelevante a nuestra escala (10-50 personas); si algún día hay SAFe, PMBOK queda subsumido |
| **XP, Design Thinking** | Sin solape estructural; Design Thinking puede alimentar el charter del proyecto | Ninguna acción |

El conflicto maestro es **Scrum vs. PMBOK por la identidad del producto**: si Cenit muestra EVM por defecto, espanta a los equipos ágiles que son el ICP. La resolución es que PMBOK sea **opt-in por proyecto** ("este proyecto tiene contrato de alcance fijo") y jamás parte del flujo por defecto.

### 10. Antipatrones conocidos

- **Jira — la burocracia configurable infinita**: Jira clásico permitió modelar cualquier proceso PMI con esquemas de workflow, campos obligatorios y pantallas de transición. Resultado: administradores convirtieron el tablero en un formulario de 30 campos; el equipo llenaba datos falsos para poder mover la tarjeta, y un EV calculado sobre datos falsos es peor que no tener EV. Lección para Cenit: máximo 2 campos nuevos en la tarea (`peso_presupuesto`, `horas_reales`) y ambos opcionales fuera de proyectos formales.
- **Jira + BigPicture/Structure — EVM como plugin caro y desacoplado**: la función vive en el marketplace, con su propio modelo de datos que se desincroniza del tablero. Lección: en Cenit el EV se **deriva** del `estado` que el equipo ya mueve en el Kanban; nunca es un registro paralelo.
- **Trello — la negación total**: Trello nunca digitalizó nada de PMBOK; los equipos que necesitaban un baseline migraban de herramienta al firmar su primer contrato de precio fijo. Es exactamente el momento de churn que Cenit puede capturar: "creciste, firmaste un contrato formal, no necesitas irte".
- **Asana — Portfolios con % de avance sin baseline**: Asana muestra "proyecto al 68%" promediando tareas sin peso ni línea base: avance fantasma institucionalizado (ese 68% no se compara contra nada planeado). Lección: nunca mostrar % de avance sin su PV de referencia; SPI sin baseline no existe.
- **Microsoft Project — el plan que nadie ejecuta**: el antipatrón inverso; el PM mantiene un .mpp perfecto desconectado del trabajo real del equipo. Cenit lo evita por construcción: la única fuente de EV es el tablero donde el equipo trabaja de verdad.
- **Antipatrón transversal — regla 0/100 mal elegida**: dar crédito de EV solo al completar tareas grandes produce curvas escalonadas que asustan al sponsor sin razón. De ahí la regla 50/50 configurable y tareas con pesos pequeños.

### 11. Caso real

**Wrike** (adquirida por Citrix en 2021 por 2.250 MUSD) es el mejor referente de PMBOK digitalizado sin asfixiar al usuario: baselines de cronograma con comparación visual plan-vs-real, esfuerzo/costo por tarea, workload de recursos y reportes para sponsors — todo opcional por proyecto, con un tablero ágil normal como cara por defecto. Su insight de producto, que Cenit debe copiar, es la **audiencia dual**: el colaborador ve un Kanban simple; el manager y el cliente ven curvas y variaciones calculadas a partir de los mismos datos, sin que nadie llene un formulario extra. Wrike ganó agencias y equipos de servicios profesionales —el mismo perfil abundante en LatAm— precisamente porque esas empresas venden proyectos de alcance fijo pero ejecutan de forma iterativa.

Segunda referencia con lectura inversa: **Primavera P6 (Oracle)**, el estándar en construcción e infraestructura, demuestra el techo del EVM completo — potentísimo y absolutamente invendible a un equipo de software de 15 personas. Marca la línea que Cenit no debe cruzar: baseline y 12 fórmulas sí; CPM de 4 niveles, nivelación de recursos y calendarios múltiples, no.

### 12. Costo de implementación

**Medio-alto: 4 sprints de 2 semanas** para 1-2 desarrolladores (8 semanas), asumiendo que la capa de proyectos formales no existe aún.

| Sprint | Entregable | Detalle |
|---|---|---|
| 1 | Modelo + dominio | Migración SQL (projects, baselines, curve_points, ALTER tasks), `EVMService` + `ChangeControlService` con pytest completo (las fórmulas son el 60% del riesgo y se cierran aquí) |
| 2 | API + snapshots | Routers FastAPI, autorización por rol, job de snapshot semanal, seeds de demo |
| 3 | UI Proyectos | Vista Streamlit: métricas, curva S, editor de pesos, asistente de baseline |
| 4 | Cambios + E2E + pulido | Tab de change requests con re-baseline, matriz de interesados, suite Playwright, export CSV/PDF básico |

Recortable a **2 sprints (versión "EVM-lite")** eliminando control de cambios y stakeholders: solo baseline v1 + curva S + SPI/CPI. Recomendación del panel: validar la versión de 2 sprints con 2-3 pilotos tipo agencia antes de invertir los otros 2.

### 13. Cuándo NO construir esto todavía

**No construir mientras Cenit esté en la etapa actual** (validación con pilotos, pre-ingresos recurrentes). Señales concretas de que sería prematuro:

- **Ningún piloto lo ha pedido con contrato en la mano.** EVM sin un cliente que facture proyectos de precio fijo es una feature de vanidad. La señal de compra correcta es literal: "necesito reportarle avance formal a mi cliente/sponsor cada mes".
- **El ICP declarado es anti-burocracia.** El pitch de Cenit es Kanban+Eisenhower+riesgos simple contra el Jira inflado; meter baselines en los primeros 6 meses contamina el posicionamiento antes de consolidarlo.
- **Dependencia de datos que aún no existen**: sin hábito de time-tracking (`horas_reales`) el CPI será basura, y ese hábito ni siquiera está en el producto hoy. Primero registro de esfuerzo simple, después EVM.
- **Costo de oportunidad**: 4 sprints es más de lo que costó la migración a Python; en esta etapa esos sprints valen más invertidos en onboarding, multi-tenancy real y en pulir las 6 vistas existentes.

Umbral para reconsiderar: **≥3 clientes pagos del segmento agencias/consultoría** que ejecuten proyectos con alcance contractual, o un deal enterprise (universidad, banco) que condicione la compra a reportes de avance formales. En ese momento, arrancar con la versión EVM-lite de 2 sprints en modo opt-in por proyecto.
