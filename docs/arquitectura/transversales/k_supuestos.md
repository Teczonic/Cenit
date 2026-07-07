## k) Supuestos y preguntas abiertas

Declarados explícitamente en vez de asumidos en silencio. Se dividen en supuestos (afirmaciones que damos por ciertas y su riesgo si son falsas) y preguntas abiertas priorizadas.

### Supuestos

| # | Supuesto | Riesgo si es falso | Cómo validarlo |
|---|---|---|---|
| 1 | **El stack real es 100% Python** (FastAPI + Streamlit), no Next.js | El brief original describía Next.js; todo este documento se mapeó al stack actual del repo. Si alguien espera el stack viejo, hay desalineación de expectativas | Ya validado: el repo, los tests y el deploy en Vercel confirman FastAPI + Streamlit. Documento alineado a esa realidad |
| 2 | **Streamlit aguanta hasta pilotos pagos** como UI | Si la UX frena la adopción antes de validar valor, se pierde tiempo en Streamlit que debió ir a Next.js | Señales de disparo: piloto dice "lento/limitado/no puedo colaborar"; entonces migrar solo una superficie a Next.js (la arquitectura ya lo permite sin tocar API/dominio) |
| 3 | **El líder de equipo es el comprador y el usuario** | Si quien paga (CTO/CEO) no es quien usa a diario, el cockpit le habla a la persona equivocada | Las 5 entrevistas de discovery: confirmar quién siente el dolor y quién firma el cheque |
| 4 | **Hay disposición a pagar por "inteligencia sobre el flujo"** en LatAm | Todo el modelo de negocio depende de esto y no está validado | Pilotos: medir si vuelven cada semana y si al menos uno acepta hablar de precio |
| 5 | **El diferencial es la memoria histórica + diagnóstico, no el código** | Si el foso fuera el código, hacer el repo público (para desplegar gratis en Vercel) lo regalaría | Coherente con hacer build-in-public; el foso son los datos acumulados por cliente y la ejecución, no el fuente |
| 6 | **Un equipo de 1-2 personas puede sostener el ritmo** | Sobrecarga → releases que se detienen → pilotos que se enfrían | Cadencia semanal con artefacto visible; decir NO al 80% de metodologías; Codex/IA como apoyo |
| 7 | **Los pilotos meten sus tareas** (manual o CSV) para que haya datos | Sin datos, el cockpit está vacío y no hay "ajá"; el modelo "observa, no reemplaza" exige ingesta | CSV import ya construido (Fase 1.5); validar en la primera demo que el líder logra importar su export real |
| 8 | **`create_all` basta para el esquema** mientras no haya que alterar tablas con datos | Un `ALTER` manual en prod con datos de piloto puede corromper o divergir | Introducir Alembic en cuanto haya la primera migración destructiva sobre datos reales |

### Preguntas abiertas (priorizadas)

1. **¿Manual-first o import-first para los pilotos?** El posicionamiento "cockpit que observa" empuja a import-first (CSV/Jira), pero eso adelanta la ingesta a Fase 1.5. Decisión pendiente que define el siguiente sprint. *(Recomendación del panel: import-first, ya hay CSV.)*
2. **¿Quién es el ICP exacto?** "Equipos dev 10-50 en LatAm" es amplio. ¿Software factories/agencias (que necesitan reporte a cliente → Waterfall/PMBOK) o product teams internos (que viven en Kanban+OKR)? El nicho cambia qué módulos de V4 importan.
3. **¿Cofundador técnico?** El plan asume que el fundador sostiene el desarrollo con IA. ¿Buscar cofundador cambia la velocidad y qué se puede construir en V3/V4?
4. **¿Pricing?** Sin hipótesis explícita de precio/tier/canal. ¿Por usuario activo, por equipo, freemium? Bloquea el diseño de la capa de billing.
5. **¿Integración Jira/Linear read-only en V3 o antes?** Si "no migres, conectamos tus datos" es el pitch, la ingesta profunda (no solo CSV) podría necesitarse antes de lo planeado.
6. **¿Rotó/borró el Supabase viejo?** El proyecto `liwpsnbpghontykngznn` tiene su password en el historial de git público — acción de seguridad pendiente de confirmar.
7. **¿Cadencia del reporte semanal?** ¿Lunes en la mañana local? ¿Push a Slack o solo in-app? Define el diseño del cron y la integración.

### Nota de método

Este documento describe un **espacio de diseño** (12 metodologías analizadas a fondo), no un mandato de construcción. La recomendación (transversal f) y el roadmap (transversal e) son opinables y dependen de que las preguntas 1-4 se respondan con pilotos reales. La disciplina que atraviesa todo el documento es la misma: **construir contra evidencia, no contra completitud**.
