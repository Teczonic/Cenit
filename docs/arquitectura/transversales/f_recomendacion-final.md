## f) Recomendación final — núcleo vs. modo avanzado

Tras las 12 secciones y la matriz RICE, la conclusión del panel es unánime en lo esencial: **Cenit no debe ser una suite de doce metodologías, sino un cockpit con cuatro capacidades núcleo y todo lo demás detrás de una señal de demanda.**

### El núcleo real (4-5 capacidades)

| # | Capacidad | Metodología | Por qué es núcleo |
|---|---|---|---|
| 1 | **Flujo visible** (tablero + WIP + lead/cycle time + aging) | Kanban | RICE 8.1, dobla al segundo. Es lo que ya existe y lo que el 100% del ICP usa a diario. Sin esto no hay producto. |
| 2 | **Foco diario** (cockpit + Eisenhower + Mi Día) | Eisenhower + síntesis propia | Es el "ajá" de la demo: qué atender hoy. El diferencial frente a Jira no es tener tablero, es decir qué decidir. |
| 3 | **Riesgo** (score, tareas estancadas, alertas) | Síntesis propia | Ya construido; es lo que un líder no ve en Trello/Jira y lo que ancla el posicionamiento "cockpit, no gestor de tareas". |
| 4 | **Compromiso medible** (motor de KPIs con semáforo) | KPIs | RICE 4.0. Convierte lo descriptivo en dirección; es la infraestructura sobre la que DORA/SPACE/OKR son solo filas de catálogo. |
| 5 | **Dirección** (OKRs con alineación tarea→resultado) | OKRs | Ya adelantado. Le habla al comprador económico (CEO/CTO) y conecta ejecución con resultado. Núcleo "blando": núcleo si el comprador es el líder, avanzado si es el equipo. |

### Modo avanzado (opcional, contra demanda)

- **Scrum ligero** — no es núcleo de producto pero es núcleo *de venta* en LatAm: nadie pide OKRs en la demo, pero todos dicen "hacemos Scrum". Se construye en V2 en su versión mínima (Linear Cycles) solo para no perder el deal por lenguaje.
- **DORA** — diferenciador fuerte para CTOs, pero solo con pilotos que desplieguen y API pública lista (V3).
- **Lean** — comparte datos con Kanban; su hook de transiciones ya está, la vista completa espera pilotos.
- **Waterfall/PMBOK** — una sola capa de "Proyectos" para agencias con contratos por hitos (V4, upsell).
- **XP** — módulo de calidad, la narrativa más defendible del fundador, pero espera cliente campeón con CI. Mientras tanto se **usa internamente** (dogfooding) a costo cero.

### Descartadas en esta etapa (justificación explícita)

- **SAFe** (RICE 0.1) — diseñado para 50-125+ personas por tren; fuera del segmento 10-50 de Cenit. Solo WSJF sería rescatable como pieza suelta futura.
- **SPACE** (0.8) — invendible hoy: con equipos <8 personas las encuestas no se anonimizan y no hay telemetría acumulada.
- **Design Thinking** (0.3) — la trazabilidad discovery→backlog es un hueco real, pero es el candidato #1 a sobre-ingeniería; practicarlo a mano con pilotos antes de codificarlo.

### Las cuatro voces del panel

- **Arquitecto:** el núcleo se sostiene sobre `task_state_transitions` + Metrics Engine; construir cualquier módulo fuera de eso antes de tiempo es deuda.
- **Head of Product:** ningún módulo nuevo entra al menú hasta que Kanban+KPIs demuestren retención semanal — doce vistas matan el onboarding.
- **QA Lead:** XP está subvalorado por RICE porque la fórmula mide mercado, no defensibilidad; se aplica ya internamente.
- **Estratega GTM LatAm:** Scrum entra por razones de venta, no de producto; sin hablar ese idioma se pierde la demo.

### Posicionamiento (2 frases)

**Cenit es el cockpit de inteligencia operacional para líderes de equipos técnicos en LatAm: observa el flujo real de trabajo, detecta qué está en riesgo o estancado, y le dice al líder qué decidir hoy.** No compite por tener más tableros que Jira o Linear — compite por convertir el trabajo que ya ocurre en decisiones, y por conectarse a las herramientas existentes en vez de exigir migrar a ellas.
