## e) Roadmap por fases (MVP → V2 → V3 → V4)

El roadmap parte de un hecho que las secciones teóricas no tenían: **el MVP ya existe y está desplegado**. No es un plan desde cero, sino la continuación de un producto vivo (API en Vercel + Supabase, UI en Streamlit, 59 tests). Cada fase activa metodologías coherentes con su score RICE y solo avanza cuando la anterior cumple su criterio de aceptación medible.

### MVP — Cockpit operativo (✅ mayormente construido)

**Metodologías activas:** Kanban (núcleo), Eisenhower, Riesgos, Analytics descriptivo.

**Ya entregado y verificable en el repo:**
- [x] Auth JWT, CRUD de tareas, usuarios, roles.
- [x] `task_state_transitions` + `FlowService` (lead time real, cycle time, flow efficiency, aging).
- [x] Cockpit del líder (qué está en riesgo / lento / decidir hoy).
- [x] Kanban, Mi Día, Eisenhower, Riesgos, Analytics, Equipo.
- [x] Importar CSV (diagnóstico con datos reales).
- [x] OKRs (adelanto de V2: ciclos, objetivos, KRs, alineación).
- [x] Deploy reproducible (Vercel + Supabase + Docker + CI, 59 tests).

**Criterio de aceptación de MVP:** un líder entra, importa su CSV y en 15 min entiende qué atender hoy. **Pendiente para cerrarlo del todo:** UI en Streamlit Cloud accesible al piloto + límites WIP explícitos en el tablero.

**Duración restante:** 1 sprint. **Riesgo:** que el diagnóstico no genere el "ajá" — se mitiga con las 5 entrevistas de la capa transversal.

### V2 — De descriptivo a compromiso (con 3+ pilotos activos, ~8 semanas de datos)

**Metodologías activas:** KPIs (RICE 4.0), Scrum ligero (3.7), consolidación Kanban+Lean.

- [ ] Motor de métricas/KPIs (`metric_definitions` + `metric_snapshots`) con semáforo, metas y alertas.
- [ ] Sprints ligeros estilo Linear Cycles: compromiso, velocity, burndown, cierre con carryover.
- [ ] Capa Lean sobre `task_state_transitions`: flow efficiency, desperdicio, bloqueos.
- [ ] Reporte semanal automático (estado ejecutivo + riesgos + próximos bloqueos) vía Vercel Cron.

**Criterio de aceptación:** 3-5 equipos vuelven **cada semana sin que los empujes** y al menos uno configura un KPI con meta propia. **Duración:** 3-4 sprints. **Riesgo:** meter demasiadas vistas y matar el onboarding — regla del panel: ningún módulo entra al menú hasta que Kanban+KPIs demuestren retención.

### V3 — Diferenciación y cobro (con clientes pagando o cartas de intención)

**Metodologías activas:** DORA (2.8), OKRs completo (check-ins), capa IA sobre datos propios.

- [ ] Las 4 métricas DORA con webhooks de GitHub (como providers del motor, no módulo aparte).
- [ ] OKR check-ins semanales + narrativa de progreso.
- [ ] Capa de IA: resumen semanal de riesgos y recomendaciones sobre el historial acumulado (con evals, porque aconseja sobre personas).
- [ ] Decisión Next.js: migrar solo la superficie crítica **si** un piloto prueba que la UX de Streamlit frena la compra.

**Criterio de aceptación:** 3 pilotos pagos o cartas de intención; el bloqueo deja de ser "valor" y pasa a "adopción/escala". **Duración:** 4-6 sprints. **Riesgo:** construir IA sin datos suficientes → alucina; por eso va en V3, no antes.

### V4 — Expansión de cuenta y nichos (contra demanda explícita)

**Metodologías activas (solo con contrato en mano):** Waterfall/PMBOK como capa única de "Proyectos" (SPI, baseline, EVM ligero), XP (módulo de calidad), SPACE (salud de equipo), y WSJF de SAFe como pieza suelta.

- [ ] Proyectos con fases, gates y reporte contra plan (agencias/software factories con contratos por hitos).
- [ ] Módulo XP "el tablero que entiende de calidad" (cuando haya cliente campeón con CI real).
- [ ] SPACE (cuando los equipos superen ~8 personas para anonimizar encuestas).

**Criterio de aceptación:** cada módulo se construye **solo** contra una petición pagada. **Riesgo:** sobre-ingeniería — SAFe completo, Design Thinking codificado y SPACE prematuro son las trampas identificadas en las secciones individuales.

### Vista de conjunto

| Fase | Metodologías | Señal que la habilita | Estado |
|---|---|---|---|
| MVP | Kanban, Eisenhower, Riesgos, Analytics | — (arranque) | ✅ casi completo |
| V2 | KPIs, Scrum, Lean | 3+ pilotos, 8 sem. de datos | ▶️ OKRs adelantado |
| V3 | DORA, OKRs completo, IA | Clientes pagando | ⏳ |
| V4 | Waterfall/PMBOK, XP, SPACE, WSJF | Demanda con contrato | ⏳ |

La disciplina del roadmap es negativa, no positiva: no se trata de qué construir, sino de **qué no construir todavía**. Cada fase tiene una compuerta de datos o de dinero; saltarla es la definición de sobre-ingeniería para un equipo de 1-2 personas.
