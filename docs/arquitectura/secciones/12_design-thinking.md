## 12. Design Thinking

### 1. Principio central y origen

Design Thinking es un marco de resolución de problemas centrado en el humano que estructura la innovación en cinco fases iterativas: **Empatizar, Definir, Idear, Prototipar y Testear**. Su principio central es que los equipos no deben construir lo que creen que el usuario necesita, sino lo que descubren observándolo y conversando con él, validando cada hipótesis con prototipos baratos antes de invertir en construcción real. El patrón subyacente es el "doble diamante" (British Design Council, 2005): divergir para explorar el problema, converger en una definición, divergir en ideas, converger en un prototipo testeable.

Su origen es doble. La raíz académica está en Stanford (la d.school, fundada en 2005 por David Kelley con financiación de Hasso Plattner, cofundador de SAP), que destila décadas de métodos de diseño (Herbert Simon, *The Sciences of the Artificial*, 1969; Horst Rittel y los "wicked problems"). La raíz comercial está en **IDEO** (Palo Alto, años 90), la consultora que popularizó el método aplicándolo desde el primer mouse de Apple hasta carritos de supermercado; Tim Brown (CEO de IDEO) lo canonizó en Harvard Business Review (2008) y en *Change by Design* (2009). A diferencia de Scrum o Kanban —que nacen de la manufactura y el software y responden a "cómo ejecutar mejor"—, Design Thinking nace del diseño y responde a "**qué** vale la pena ejecutar".

El error de gestión que previene es el más caro de todos: **construir eficientemente el producto equivocado**. Un equipo puede tener velocity impecable, WIP controlado y DORA élite, y aun así quebrar porque nadie validó que la funcionalidad resolvía un dolor real. Previene además dos errores secundarios: la "solución enamorada" (defender una idea por apego y no por evidencia) y el "usuario proxy" (decidir con base en lo que dice el jefe en vez del usuario final). Hoy, una fila de `tasks` en Cenit tiene `descripcion`, `prioridad`, `estado` y `cliente`, pero ningún dato responde "¿qué evidencia de usuario justifica esta tarea?" — ese es exactamente el hueco que esta metodología llena.

Para Cenit hay dos lecturas de la metodología, y conviene separarlas desde ya:

1. **Design Thinking como práctica interna de Teczonic**: el fundador entrevistando pilotos, sintetizando insights y priorizando el roadmap de Cenit. Esto no requiere código: requiere disciplina.
2. **Design Thinking como módulo de producto**: dar a los equipos que usan Cenit un espacio para capturar hallazgos de descubrimiento (entrevistas, insights, hipótesis, experimentos) y conectarlos con las tareas de ejecución que ya viven en la tabla `tasks`. Esta es la versión que se diseña en esta sección, y su propuesta de valor diferencial es el eslabón que Jira y Trello nunca cerraron: **trazabilidad insight → hipótesis → experimento → tarea**.

Desde la perspectiva de calidad, esa trazabilidad es oro: permite preguntar "¿qué evidencia respalda este requisito?" y obtener respuesta con un clic. Desde la perspectiva go-to-market, es un discurso potente ante CTOs de LatAm que sufren backlogs llenos de tickets sin justificación: "en Cenit, cada tarea sabe de qué aprendizaje nació". La versión correcta para Cenit es un subconjunto quirúrgico del método — no un módulo de "talleres virtuales con post-its".

### 2. Métricas y fórmulas exactas

Design Thinking no tiene métricas tan estandarizadas como DORA, pero la práctica de product discovery moderna (Teresa Torres, IDEO, Google Ventures) converge en un conjunto medible. Definimos cinco, con fórmulas exactas y un ejemplo aplicado al equipo ficticio **"Nébula"** (5 personas: Ana PM, Bruno dev, Carla dev, David QA, Elena diseñadora) durante un ciclo de descubrimiento de 4 semanas.

| Métrica | Fórmula | Qué detecta |
|---|---|---|
| Cadencia de contacto con usuarios (CCU) | `entrevistas_realizadas / semanas` | Equipos que dejan de empatizar |
| Tasa de validación de hipótesis (TVH) | `hipotesis_validadas / hipotesis_testeadas × 100` | Calidad de las hipótesis (ni obvias ni delirantes) |
| Tiempo de ciclo de aprendizaje (TCA) | `avg(fecha_veredicto − fecha_creacion_hipotesis)` en días | Lentitud entre idea y evidencia |
| Trazabilidad insight→tarea (TIT) | `tareas_con_insight_vinculado / tareas_nuevas × 100` | Backlog que crece sin evidencia |
| Costo por aprendizaje (CPA) | `horas_invertidas_descubrimiento / hipotesis_con_veredicto` | Experimentos sobredimensionados |

**Cálculo paso a paso para Nébula (ciclo de 4 semanas):**

Datos del ciclo: Ana y Elena hicieron 10 entrevistas (semanas 1-2: 3+4; semanas 3-4: 2+1). De ellas salieron 14 insights, sintetizados en 6 hipótesis. Se testearon 5 (una quedó en backlog): 3 validadas, 2 refutadas. Los veredictos llegaron a los 6, 9, 12, 15 y 18 días de creada cada hipótesis. En el mismo período se crearon 20 tareas en el Kanban, 8 de ellas vinculadas a un insight. El equipo invirtió 60 horas totales en descubrimiento.

1. **CCU** = 10 / 4 = **2.5 entrevistas/semana**. Umbral saludable según Teresa Torres: ≥ 1/semana sostenida; Nébula está bien, pero la caída de 7 entrevistas (sem. 1-2) a 3 (sem. 3-4) es una alerta de tendencia que la UI debe mostrar.
2. **TVH** = 3 / 5 × 100 = **60 %**. Rango sano: 30-70 %. Si TVH > 85 %, el equipo solo testea obviedades; si < 20 %, está ideando sin empatizar.
3. **TCA** = (6+9+12+15+18) / 5 = 60 / 5 = **12 días**. Objetivo: ≤ 14 días (un ciclo de aprendizaje por sprint de ejecución).
4. **TIT** = 8 / 20 × 100 = **40 %**. Interpretación: 6 de cada 10 tareas nuevas entraron al backlog sin evidencia de usuario. No toda tarea necesita insight (deuda técnica, bugs), así que el objetivo razonable es 50-60 % para tareas tipo "feature".
5. **CPA** = 60 h / 5 veredictos = **12 horas por aprendizaje**. Si un experimento individual supera ~3× el CPA promedio, es candidato a simplificarse (prototipo más barato).

Estas cinco métricas caben en el patrón ya existente de `AnalyticsService` (agregaciones puras sobre listas de dicts) y se exponen por el mismo estilo de endpoint `/api/analytics/...`.

### 3. Modelo de datos

Cuatro tablas nuevas más una puente que **extienden** `users` y `tasks` sin tocarlas. La cadena de trazabilidad es `dt_entrevistas → dt_insights → dt_hipotesis`, y el cierre del ciclo es la tabla puente hacia `tasks`.

```sql
-- Ciclo o "reto de diseño": agrupa un esfuerzo de descubrimiento acotado
CREATE TABLE dt_retos (
    id            SERIAL PRIMARY KEY,
    entidad       VARCHAR(50) NOT NULL,          -- mismo eje multi-tenant que tasks.entidad
    titulo        VARCHAR(200) NOT NULL,
    pregunta_hmw  TEXT NOT NULL,                 -- "How Might We..."
    fase          VARCHAR(20) NOT NULL DEFAULT 'empatizar'
                  CHECK (fase IN ('empatizar','definir','idear','prototipar','testear','cerrado')),
    fecha_inicio  DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_cierre  DATE,
    owner_id      INTEGER NOT NULL REFERENCES users(id),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Fase Empatizar: sesiones con usuarios reales
CREATE TABLE dt_entrevistas (
    id               SERIAL PRIMARY KEY,
    reto_id          INTEGER NOT NULL REFERENCES dt_retos(id) ON DELETE CASCADE,
    entrevistador_id INTEGER NOT NULL REFERENCES users(id),
    perfil_usuario   VARCHAR(120) NOT NULL,      -- ej. "Tech Lead, equipo 12 devs, usa Jira"
    fecha            TIMESTAMPTZ NOT NULL,
    duracion_min     INTEGER CHECK (duracion_min > 0),
    notas            TEXT,
    grabacion_url    VARCHAR(500),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Fase Definir: hallazgos sintetizados
CREATE TABLE dt_insights (
    id            SERIAL PRIMARY KEY,
    reto_id       INTEGER NOT NULL REFERENCES dt_retos(id) ON DELETE CASCADE,
    entrevista_id INTEGER REFERENCES dt_entrevistas(id) ON DELETE SET NULL,
    autor_id      INTEGER NOT NULL REFERENCES users(id),
    texto         TEXT NOT NULL,                 -- "Los TL pierden 3h/sem consolidando estados"
    tipo          VARCHAR(20) NOT NULL DEFAULT 'dolor'
                  CHECK (tipo IN ('dolor','deseo','contexto','objecion')),
    votos         INTEGER NOT NULL DEFAULT 0,    -- dot-voting del equipo
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Fases Idear/Prototipar/Testear: hipótesis y su experimento
CREATE TABLE dt_hipotesis (
    id               SERIAL PRIMARY KEY,
    reto_id          INTEGER NOT NULL REFERENCES dt_retos(id) ON DELETE CASCADE,
    insight_id       INTEGER REFERENCES dt_insights(id) ON DELETE SET NULL,
    enunciado        TEXT NOT NULL,              -- "Creemos que X logrará Y; lo sabremos si Z"
    metrica_exito    VARCHAR(200) NOT NULL,
    umbral_exito     VARCHAR(100) NOT NULL,      -- ej. ">= 6 de 10 pilotos lo usan 2 veces/sem"
    tipo_prototipo   VARCHAR(30) DEFAULT 'mockup'
                     CHECK (tipo_prototipo IN ('mockup','wizard_of_oz','landing','concierge','mvp_funcional')),
    veredicto        VARCHAR(15) NOT NULL DEFAULT 'pendiente'
                     CHECK (veredicto IN ('pendiente','validada','refutada','inconclusa')),
    resultado_observado TEXT,
    horas_invertidas NUMERIC(6,1) DEFAULT 0,
    fecha_veredicto  TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Cierre del ciclo: qué tareas de ejecución nacen de qué evidencia
CREATE TABLE dt_insight_tasks (
    insight_id INTEGER NOT NULL REFERENCES dt_insights(id) ON DELETE CASCADE,
    task_id    INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (insight_id, task_id)
);

CREATE INDEX idx_dt_entrevistas_reto ON dt_entrevistas(reto_id, fecha);
CREATE INDEX idx_dt_insights_reto    ON dt_insights(reto_id);
CREATE INDEX idx_dt_hipotesis_reto   ON dt_hipotesis(reto_id, veredicto);
CREATE INDEX idx_dt_it_task          ON dt_insight_tasks(task_id);
```

Decisiones de diseño: (a) la tabla puente `dt_insight_tasks` en vez de una columna en `tasks` evita migrar la tabla más caliente del sistema y permite N:M (un insight genera varias tareas; una tarea puede responder a varios insights); (b) `entidad` en `dt_retos` replica el eje de filtrado multi-cliente que `tasks` ya usa; (c) los CHECK constraints validan en BD lo que el dominio valida en Python — defensa en profundidad para cuando alguien escriba directo a Supabase; (d) `ON DELETE SET NULL` en `insight_id`/`entrevista_id` preserva hipótesis y hallazgos aunque se depure material fuente.

### 4. Casos de uso del domain layer

Un `DesignThinkingService` en `domain/` siguiendo el patrón existente de `services.py`: opera sobre dicts serializados por la API, sin dependencia de SQLAlchemy, 100 % testeable con pytest sin base de datos.

```python
from dataclasses import dataclass
from typing import Optional

FASES: list[str] = ["empatizar", "definir", "idear", "prototipar", "testear", "cerrado"]

@dataclass
class DiscoveryHealthReport:
    cadencia_entrevistas: float            # entrevistas/semana (CCU)
    tasa_validacion_pct: Optional[float]   # TVH; None si no hay veredictos
    ciclo_aprendizaje_dias: Optional[float]  # TCA
    trazabilidad_pct: float                # TIT
    costo_por_aprendizaje_h: Optional[float]  # CPA
    alertas: list[str]

class FaseInvalidaError(Exception): ...
class VeredictoYaEmitidoError(Exception): ...

class DesignThinkingService:

    def avanzar_fase(self, reto: dict, entrevistas: list[dict], insights: list[dict]) -> str:
        """Devuelve la siguiente fase válida del reto o lanza FaseInvalidaError.
        pseudocódigo:
          idx = FASES.index(reto["fase"])
          si idx == len(FASES) - 1: raise FaseInvalidaError("reto cerrado")
          siguiente = FASES[idx + 1]
          # reglas de calidad (anti 'teatro de post-its'):
          si siguiente == "definir" y len(entrevistas) < 3: raise FaseInvalidaError(...)
          si siguiente == "idear" y not any(i["votos"] > 0 for i in insights): raise ...
          return siguiente
        """

    def calcular_salud_descubrimiento(
        self, reto: dict, entrevistas: list[dict], hipotesis: list[dict],
        tareas_nuevas: list[dict], vinculos: list[dict],
    ) -> DiscoveryHealthReport:
        """Calcula las 5 métricas de la sección 2 (función pura).
        pseudocódigo:
          semanas = max((hoy - reto["fecha_inicio"]).days / 7, 1)
          ccu = len(entrevistas) / semanas
          cerradas = [h for h in hipotesis if h["veredicto"] in ("validada", "refutada")]
          tvh = 100 * n_validadas / len(cerradas) si cerradas else None
          tca = avg((h["fecha_veredicto"] - h["created_at"]).days for h in cerradas) o None
          ids_vinculadas = {v["task_id"] for v in vinculos}
          tit = 100 * len([t for t in tareas_nuevas if t["id"] in ids_vinculadas]) / max(len(tareas_nuevas), 1)
          cpa = sum(h["horas_invertidas"]) / len(cerradas) si cerradas else None
          alertas: ccu < 1 -> "Sin contacto con usuarios"; tvh > 85 -> "Hipótesis obvias";
                   tvh < 20 -> "Ideación sin empatía"; tca > 14 -> "Aprendizaje lento"
          return DiscoveryHealthReport(...)
        """

    def priorizar_insights(self, insights: list[dict]) -> list[dict]:
        """Ordena por votos desc, luego tipo ('dolor' > 'deseo' > 'objecion' > 'contexto'),
        luego recencia. Mismo estilo que RiesgoService.ordenar_por_riesgo."""

    def emitir_veredicto(self, hipotesis: dict, resultado_observado: str,
                         veredicto: str, horas: float) -> dict:
        """Cierra una hipótesis: setea veredicto, resultado y fecha_veredicto=now().
        Regla de inmutabilidad: si hipotesis['veredicto'] != 'pendiente'
        lanza VeredictoYaEmitidoError — el aprendizaje no se reescribe."""

    def tareas_sin_evidencia(self, tareas: list[dict], vinculos: list[dict],
                             entidad: str = "") -> list[dict]:
        """Devuelve tareas activas (estado != 'Completado') sin insight vinculado
        — el 'backlog huérfano'. Reusa FiltroService.filtrar_por_entidad."""
```

El punto arquitectónicamente importante: `calcular_salud_descubrimiento` es una función pura sobre datos ya cargados; el endpoint FastAPI solo orquesta la carga vía `crud.py`. Exactamente la separación que ya existe entre `api/` y `domain/`.

### 5. Diseño de API REST

Consistente con `/api/tasks` y `/api/analytics/...`, todo bajo el auth JWT existente.

| Método | Ruta | Propósito |
|---|---|---|
| POST | `/api/dt/retos` | Crear reto de diseño |
| GET | `/api/dt/retos?entidad=&fase=` | Listar retos |
| PATCH | `/api/dt/retos/{id}/fase` | Avanzar fase (valida precondiciones) |
| POST | `/api/dt/retos/{id}/entrevistas` | Registrar entrevista |
| GET | `/api/dt/retos/{id}/entrevistas` | Listar entrevistas del reto |
| POST | `/api/dt/retos/{id}/insights` | Capturar insight |
| POST | `/api/dt/insights/{id}/votos` | Dot-voting (+1) |
| POST | `/api/dt/retos/{id}/hipotesis` | Crear hipótesis |
| PATCH | `/api/dt/hipotesis/{id}/veredicto` | Cerrar experimento (409 si ya cerrado) |
| POST | `/api/dt/insights/{id}/tasks` | Vincular insight → tarea existente o nueva |
| GET | `/api/analytics/dt/salud/{reto_id}` | DiscoveryHealthReport |
| GET | `/api/analytics/dt/backlog-huerfano?entidad=` | Tareas sin evidencia |

Payloads de ejemplo:

```json
POST /api/dt/retos
{
  "entidad": "Desarrollo",
  "titulo": "Onboarding de pilotos",
  "pregunta_hmw": "¿Cómo podríamos lograr que un tech lead configure su tablero en menos de 10 minutos?",
  "owner_id": 1
}
```

```json
PATCH /api/dt/hipotesis/7/veredicto
{
  "veredicto": "validada",
  "resultado_observado": "7 de 10 pilotos completaron el onboarding guiado sin ayuda",
  "horas_invertidas": 14.5
}
```

```json
POST /api/dt/insights/12/tasks
{
  "task_id": null,
  "nueva_tarea": {
    "entidad": "Desarrollo",
    "proyecto": "Desarrollo",
    "descripcion": "Wizard de onboarding en 3 pasos",
    "prioridad": "Alta",
    "responsable": "Bruno"
  }
}
```

Ese último endpoint es el corazón del módulo: si `task_id` es null, crea la tarea vía el `crud` existente de tasks y luego inserta el vínculo en `dt_insight_tasks`, todo en una transacción. Respuesta: `{"task_id": 123, "insight_id": 12}`.

### 6. Vista o componente de UI

Nueva vista `ui/views/descubrimiento.py`, registrada en la navegación de `ui/app.py` junto a mi_dia, kanban, eisenhower, riesgos, analytics y equipo.

**Wireframe textual (de arriba abajo):**

1. **Cabecera**: `st.selectbox` para elegir el reto activo + badge de fase renderizado como los chips de estado del Kanban (misma técnica de color que `ESTADO_COLORS`). Botón `st.button("Avanzar fase →")` que llama al PATCH; si falla, `st.error` con la precondición incumplida ("Necesitas al menos 3 entrevistas para pasar a Definir").
2. **Stepper de fases**: cinco `st.columns` con Empatizar → Definir → Idear → Prototipar → Testear; la fase actual resaltada. Es el mapa mental del método: un usuario que nunca oyó "Design Thinking" entiende dónde está.
3. **Fila de métricas**: cinco `st.metric` con CCU (con delta vs. período anterior), TVH, TCA, TIT y CPA, alimentados por `/api/analytics/dt/salud/{reto_id}`. Las alertas del reporte se muestran como `st.warning`.
4. **Tres pestañas** (`st.tabs`):
   - **Entrevistas**: tabla de sesiones + `st.form` de registro rápido (perfil, fecha, duración, notas, URL de grabación), pensado para llenarse en 30 segundos después de la llamada.
   - **Muro de insights**: tarjetas en 3 columnas, cada una con texto, tipo (chip: dolor/deseo/contexto/objeción), contador de votos y botón "▲ Votar". Botón secundario "→ Crear tarea" que abre un `st.dialog` con el mini-formulario de tarea prellenado (descripción sugerida desde el insight); al guardar, la tarjeta muestra el chip "vinculada a #123".
   - **Hipótesis**: tabla con enunciado, tipo de prototipo, métrica/umbral y veredicto (chip: gris pendiente, verde validada, rojo refutada, ámbar inconclusa). Al seleccionar una pendiente, panel de cierre de veredicto; las cerradas son de solo lectura.
5. **Pie — "Backlog huérfano"**: `st.expander` con las tareas activas de la entidad sin insight vinculado, con botón de vincular a un insight existente. Es el puente hacia el Kanban y el recordatorio incómodo que ningún otro tablero da.

Interacción clave: el flujo entrevista → insight → tarea se completa sin salir de esta pantalla, y la tarea creada aparece de inmediato en el Kanban existente.

### 7. Estrategia de testing E2E

**Playwright para Python** (flujos críticos contra la app Streamlit servida por Docker Compose, mismo arnés que el resto de vistas):

1. **Ciclo completo feliz**: login → crear reto → registrar 3 entrevistas → avanzar a Definir → capturar insight → votar → crear hipótesis → emitir veredicto "validada" → crear tarea desde el insight → navegar al Kanban y verificar que la tarea aparece en "No Iniciado". Cubre la trazabilidad de punta a punta, que es el valor diferencial del módulo.
2. **Precondiciones de fase**: intentar avanzar de Empatizar a Definir con 0 entrevistas → asertar `st.error` visible con el mensaje de precondición.
3. **Inmutabilidad del veredicto**: cerrar una hipótesis como "refutada" y verificar que el panel de veredicto ya no está disponible para ella (y que un PATCH directo a la API responde 409).
4. **Métricas reactivas**: registrar una entrevista y verificar que el `st.metric` de CCU se actualiza tras el rerun de Streamlit. Punto frágil típico del stack: anclar los localizadores por `key` de widget / `data-testid`, nunca por posición o texto de layout, y usar `expect(...).to_have_text` con timeout generoso.
5. **Backlog huérfano**: crear tarea directa en el Kanban → verificar que aparece en el expander de huérfanas → vincularla a un insight → verificar que desaparece.

**pytest unitario del dominio** (sin BD, sobre dicts, como los tests existentes):

- `test_salud_descubrimiento_ejemplo_nebula`: fixture con los datos exactos de la sección 2; asertar CCU=2.5, TVH=60.0, TCA=12.0, TIT=40.0, CPA=12.0 — el ejemplo documental se vuelve test de regresión.
- `test_salud_sin_veredictos_devuelve_none`: TVH/TCA/CPA en None con listas vacías (guard contra división por cero).
- `test_avanzar_fase_orden_valido` / `test_avanzar_desde_cerrado_lanza_error` (parametrizados sobre las 6 fases).
- `test_avanzar_a_definir_requiere_3_entrevistas`.
- `test_priorizar_insights_dolor_antes_que_deseo_a_igualdad_de_votos`.
- `test_emitir_veredicto_dos_veces_lanza_veredicto_ya_emitido`.
- `test_tareas_sin_evidencia_excluye_completadas_y_vinculadas`.

Dado el perfil QA/E2E del equipo, este módulo es candidato ideal a TDD estricto: las reglas de fase y las fórmulas son completamente especificables antes de la primera línea de implementación.

### 8. Integraciones externas

| Integración | Para qué | Prioridad |
|---|---|---|
| **Google Calendar API** | Agendar entrevistas y auto-crear el registro en `dt_entrevistas` al terminar el evento (menos fricción = más CCU real) | Alta |
| **Typeform / Google Forms API** | Encuestas de validación cuantitativa; cada respuesta puede materializarse como insight tipo "contexto" vía webhook | Alta |
| **Slack API** | Comando `/cenit-insight "texto"` para capturar hallazgos en caliente sin abrir la app; notificar veredictos al canal del equipo | Media |
| **Zoom / Google Meet (transcripciones)** | Adjuntar `grabacion_url` y, a futuro, extraer candidatos a insight de la transcripción con un LLM | Baja (v2) |
| **Miro / FigJam (link embebido)** | Los talleres de ideación seguirán ocurriendo en canvas visuales; Cenit no debe competir ahí, solo enlazar el board al reto | Baja |

Criterio del panel: ninguna integración es bloqueante para el MVP del módulo. La regla para un equipo de 1-2 personas en LatAm es empezar con el flujo manual (formularios Streamlit) y agregar Calendar+Typeform solo cuando ≥ 3 pilotos usen la vista semanalmente, porque cada integración OAuth añade superficie de soporte que esta etapa no puede sostener.

### 9. Conflictos o solapamientos

| Metodología | Naturaleza del conflicto | Resolución |
|---|---|---|
| **Lean** | El mayor solapamiento: Prototipar-Testear de DT ≈ Build-Measure-Learn; ambas hablan de hipótesis y experimentos | **No construir dos modelos de datos**: `dt_hipotesis` es LA tabla de hipótesis del sistema; el módulo Lean debe consumirla, no duplicarla. DT aporta las fases previas (empatizar/definir) que Lean da por hechas |
| **Scrum** | Compite por el origen del backlog: ¿el PO decide o la evidencia decide? | Posicionar DT como *upstream*: los insights alimentan el backlog; el sprint es *downstream*. La tabla puente `dt_insight_tasks` es literalmente esa frontera |
| **Kanban** | Compite por espacio de UI y atención: una vista más en la navegación | El pie "backlog huérfano" y el chip "vinculada a #123" hacen que Kanban y DT se refuercen en vez de fragmentar la atención |
| **OKRs** | Un reto se parece a un Objective; la métrica de éxito de una hipótesis se parece a un KR | Distinguir por horizonte: OKR = compromiso trimestral de resultado; hipótesis = apuesta falsable de 1-2 semanas. Un OKR puede referenciar retos, nunca al revés |
| **KPIs / SPACE / DORA** | Riesgo de "métrica-itis": 5 métricas DT + DORA + SPACE + KPIs saturan al usuario | Las métricas DT viven SOLO dentro de la vista descubrimiento, no en el dashboard general de analytics |
| **Waterfall / PMBOK** | Filosóficamente opuestos: requisitos fijados al inicio vs. descubiertos iterando | Sin conflicto de código; sí de narrativa de venta: ante clientes PMBOK-céntricos, presentar DT como "gestión de requisitos basada en evidencia" |
| **XP** | Menor: ambos valoran feedback rápido; XP lo busca en el código, DT en el usuario | Complementarios por definición; sin acción |
| **SAFe** | SAFe ya incorpora "Design Thinking" como competencia (Lean UX) con vocabulario propio | Si un cliente enterprise pide SAFe, mapear retos→epics; no antes |

El conflicto que más importa resolver es **DT vs. Lean**, porque es de modelo de datos y no de opinión: o hay una sola tabla de hipótesis compartida o el sistema tendrá dos verdades.

### 10. Antipatrones conocidos

- **Jira — el descubrimiento como producto aparte**: Jira Product Discovery (2023) llegó dos décadas tarde y como producto *separado* con su propio modelo de "ideas", conectado a Jira Software por links frágiles. Los equipos viven en dos herramientas y la trazabilidad se rompe en la costura. Lección: mismo esquema, misma app, tabla puente con FKs reales.
- **Jira — el campo obligatorio como sustituto de evidencia**: organizaciones que "implementan discovery" agregando un campo custom "Justificación" a cada issue; se llena con copy-paste y nadie lo lee. Lección: la evidencia debe ser una entidad con ciclo de vida (entrevista con fecha, insight con votos, hipótesis con veredicto), no un textarea.
- **Trello — la anarquía del board de ideas**: Trello permite montar un funnel de discovery con listas ("Ideas", "Entrevistando", "Validado"), pero sin tipos ni reglas: una "idea" es indistinguible de una tarea, no hay veredicto ni umbral de éxito, y el board degenera en cementerio de ideas. Lección: las precondiciones de `avanzar_fase` y el veredicto inmutable existen para impedir exactamente esto.
- **Asana — formularios sin síntesis**: Asana Forms convierte input de usuarios en tareas directamente, saltándose Definir e Idear: cada queja se vuelve un ticket. Es la digitalización del antipatrón "feature factory". Lección: en Cenit el camino es entrevista → insight → hipótesis → tarea; no existe el atajo formulario→tarea dentro del módulo DT.
- **Antipatrón transversal — el teatro de post-its digital**: replicar el taller de notas de colores (columnas infinitas de post-its) sin conectar nada con la ejecución; el taller se siente productivo y el backlog no cambia. Por eso TIT (trazabilidad insight→tarea) es la métrica estrella del módulo: mide exactamente lo que el teatro no produce.

### 11. Caso real

**Linear** — relevante además porque es el competidor aspiracional directo de Cenit — ejecuta la esencia de Design Thinking sin llamarlo así, a través del **Linear Method**: (1) descubrimiento continuo con una comunidad de usuarios técnicos en Slack — contacto semanal real con usuarios: su CCU; (2) cada feature grande nace de un *project spec* de una página que enuncia el problema observado y el resultado esperado — su formato de hipótesis; (3) construyen la versión mínima detrás de un feature flag y la validan con un subconjunto de usuarios antes del release general — su prototipar/testear; y (4) mantienen la trazabilidad problema → proyecto → issues dentro de la misma herramienta.

Qué aprender de su enfoque, en orden de importancia para Cenit:

1. **Integración sobre separación**: el discovery vive en el mismo producto que la ejecución. Es exactamente la tesis de `dt_insight_tasks`.
2. **Formato mínimo con reglas duras**: una hipótesis en Linear es una página, no un canvas de 40 post-its. Cenit debe resistir la tentación de construir un Miro; sus formularios de 5 campos son una feature, no una limitación.
3. **Dogfooding como fuente primaria**: Linear se construye con Linear. Teczonic debería gestionar el descubrimiento de Cenit dentro del propio módulo DT — cada piloto B2B es una fila en `dt_entrevistas`. Eso convierte al fundador en el primer test E2E humano del módulo y genera el screenshot de venta más honesto posible.

Mención secundaria: **Intercom**, con su framework RICE y las pausas de discovery entre ciclos de build, demuestra que la cadencia alternada descubrir/construir escala hasta cientos de personas; referencia útil cuando Cenit venda a equipos de 50.

### 12. Costo de implementación

**Medio: 3 sprints de 2 semanas** para 1-2 desarrolladores, asumiendo que la infraestructura (auth JWT, crud base, Docker Compose, CI) ya existe.

| Sprint | Entregable | Detalle |
|---|---|---|
| 1 | Modelo + API núcleo | 5 tablas (migración), modelos SQLAlchemy, CRUD de retos/entrevistas/insights, endpoints POST/GET/PATCH de fase con precondiciones, pytest de dominio (fases, priorización). ~60 h |
| 2 | Hipótesis + vista Streamlit | Tabla hipótesis + veredicto inmutable (409), `calcular_salud_descubrimiento` con TDD (fixture Nébula), vista `descubrimiento.py` con stepper, métricas y 3 pestañas. ~70 h |
| 3 | Trazabilidad + E2E + pulido | Endpoint insight→tarea transaccional, backlog huérfano, chip en tarjetas Kanban, 5 flujos Playwright, seeds de demo para pilotos, ajustes de UX tras primera demo. ~60 h |

Riesgo de desviación: +0.5 sprint si el dot-voting y los `st.dialog` de Streamlit dan problemas de estado entre reruns — la parte más frágil del stack elegido. Las integraciones externas de la sección 8 NO están incluidas; cada una cuesta ~0.5-1 sprint adicional.

### 13. Cuándo NO construir esto todavía

Este módulo es el candidato número uno a sobre-ingeniería de las doce metodologías, y el panel es unánime: **no construirlo hasta que el núcleo de ejecución esté validado**. Señales concretas de que sería prematuro:

- **Menos de 3-5 pilotos usando Kanban/Eisenhower semanalmente**. Si nadie usa la ejecución, un módulo de descubrimiento es una segunda hipótesis apilada sobre una primera sin validar — irónicamente, la violación exacta del principio que el módulo predica.
- **Ningún piloto ha pedido gestionar discovery**. El mercado objetivo (equipos dev de 10-50 en LatAm que migran de Jira/Trello) compra primero visibilidad de ejecución y riesgos; el discovery estructurado es un dolor de madurez posterior. Construirlo antes de que lo pidan es inventario, en el sentido Lean puro.
- **El propio Teczonic no practica aún el método a mano**. Regla práctica: primero 8-10 entrevistas de pilotos gestionadas en una hoja de cálculo o como tareas normales de Cenit; cuando esa hoja duela (insights perdidos, cero trazabilidad), ese dolor es el spec del módulo. Dogfooding antes que features.
- **Restricción de recursos**: con 1-2 personas, 3 sprints en DT son 3 sprints no invertidos en onboarding, estabilidad o en las vistas que hoy cierran ventas (riesgos y analytics son diferenciadores más inmediatos frente a Trello).

Lo que SÍ hacer ya, con costo casi cero: practicar Design Thinking manualmente sobre los pilotos, y reservar las decisiones de diseño de esta sección (los nombres `dt_*`, la tabla de hipótesis compartida con Lean, la tabla puente hacia `tasks`) para que, cuando llegue el momento — probablemente después de las primeras 5-10 cuentas pagas —, el módulo se construya sobre un esquema ya pensado y con los casos reales del propio fundador como datos semilla.
