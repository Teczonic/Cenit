## g) Glosario de términos (modo aprendizaje)

Pensado para tooltips o un "modo aprendizaje" embebido — el fundador viene de edtech, y explicar la métrica en el punto donde se muestra es un diferencial de producto, no solo documentación. Definiciones de ≤30 palabras, aptas para un popover.

| Término | Definición breve | Metodología |
|---|---|---|
| Aging | Días que una tarea abierta lleva sin cambiar de estado. Alto = estancada. | Kanban / Lean |
| Alignment ratio | % de tareas abiertas conectadas a un Key Result. Mide si el trabajo diario tiene dirección. | OKRs |
| Backlog | Lista priorizada de trabajo pendiente aún no comprometido a un ciclo. | Scrum / Kanban |
| Baseline | Foto congelada del plan (alcance, fechas, costo) contra la que se mide la desviación. | Waterfall / PMBOK |
| Burndown | Gráfico del trabajo restante de un sprint día a día hacia cero. | Scrum |
| Change Failure Rate (CFR) | % de despliegues que causan un incidente en producción. | DORA |
| Ciclo (Cycle) | Iteración de trabajo de duración fija; en Cenit, sprint ligero estilo Linear. | Scrum / XP |
| Cycle time | Tiempo desde que una tarea entra "En Proceso" hasta que se completa. | Kanban / Lean |
| Cuadrante de Eisenhower | Clasificación urgente×importante en 4 zonas: hacer ya, planificar, delegar, posponer. | Eisenhower |
| Deployment Frequency | Con qué frecuencia el equipo despliega a producción. Más = mejor entrega. | DORA |
| Flow efficiency | % del tiempo activo vs. tiempo total (activo + en pausa). Mide cuánto es trabajo real vs. espera. | Lean |
| Insight | Aprendizaje sobre el usuario (dolor, deseo, contexto) que puede originar una tarea. | Design Thinking |
| Kaizen / PDCA | Mejora continua en ciclos Planear-Hacer-Verificar-Actuar. | Lean |
| Key Result (KR) | Resultado medible que indica si un objetivo se está logrando. | OKRs |
| KPI | Indicador clave con meta y umbral; se evalúa con semáforo verde/ámbar/rojo. | KPIs |
| Lead time | Tiempo total desde que se crea una tarea hasta que se completa. | Kanban / DORA |
| Lead time for changes | Tiempo desde el commit hasta que ese cambio corre en producción. | DORA |
| MTTR | Tiempo medio de recuperación tras un incidente en producción. | DORA |
| Objective | Meta cualitativa e inspiradora del trimestre, medida por sus Key Results. | OKRs |
| Risk score | Probabilidad × impacto × (1 − cobertura de tests); prioriza qué tarea vigilar. | Síntesis Cenit |
| Snapshot de métrica | Valor congelado de una métrica en un periodo; nunca se sobrescribe (memoria histórica). | Metrics Engine |
| Sprint | Iteración de trabajo con un compromiso fijo y una duración de 1-4 semanas. | Scrum |
| Story points | Unidad relativa de esfuerzo para estimar tareas sin usar horas. | Scrum / XP |
| Throughput | Número de tareas completadas por unidad de tiempo (ej. por semana). | Kanban |
| Transición de estado | Registro de un cambio de estado de una tarea (de→a, quién, cuándo). Base de todo el flujo. | Kanban / Lean |
| Velocity | Promedio de story points completados por sprint; sirve para planear capacidad. | Scrum |
| WIP (Work In Progress) | Cantidad de tareas en curso a la vez; limitarla acelera el flujo. | Kanban |
| WSJF | Weighted Shortest Job First: prioriza por costo de retraso ÷ tamaño. | SAFe |

### Cómo implementar el "modo aprendizaje"

- **En Streamlit:** el parámetro `help=` de `st.metric`, `st.selectbox`, etc. ya renderiza un tooltip nativo — poblarlo desde este glosario es casi gratis. Para definiciones más ricas, `st.popover` junto a cada métrica del cockpit.
- **En la API:** un endpoint `GET /api/glossary` que sirva este diccionario permite que el mismo texto alimente la UI de Streamlit hoy y un frontend Next.js mañana, sin duplicar contenido.
- **Regla de producto:** cada métrica que el cockpit muestre debe tener su entrada de glosario. Una métrica sin explicación es decoración; con explicación, es formación embebida — coherente con el ADN edtech del fundador y con el hecho de que muchos líderes de equipo en el ICP no dominan estos términos.
