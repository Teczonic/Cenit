## Cierre — las 3 decisiones más importantes

De las doce metodologías, los once entregables y el análisis del panel, tres decisiones concentran casi todo el valor. El fundador debe tomarlas ahora; el resto se deriva de ellas.

### 1. Núcleo de 4-5 capacidades, no una suite de 12 metodologías

**La decisión:** comprometerse a que Cenit sea Kanban + foco diario + riesgo + KPIs (+ OKR según comprador), y que todo lo demás espere una señal de demanda explícita.

**Por qué es la más importante ahora:** es la que determina si el producto envía o se ahoga. Un equipo de 1-2 personas que intente las doce muere de deuda y de un onboarding ilegible. La matriz RICE ya dio el veredicto (Kanban 8.1 vs. SAFe 0.1); la única forma de perder es ignorarla y construir por completitud.

**Recomendación del panel:** aplicar la regla dura — ningún módulo nuevo entra al menú de navegación hasta que Kanban+KPIs demuestren retención semanal. Construir el Metrics Engine para que las metodologías futuras sean filas de catálogo, no módulos.

### 2. Validar con pilotos antes de sofisticar la UI (Streamlit ahora, Next.js solo con señal)

**La decisión:** no migrar a Next.js por ansiedad estética; mantener Streamlit hasta que un piloto real pruebe que la UX frena la adopción o la compra.

**Por qué es la más importante ahora:** es el mayor sumidero potencial de tiempo. La arquitectura ya está diseñada para que la UI sea desechable (`ui/` solo habla HTTP con la API), así que migrar cuando llegue la señal no cuesta reescribir el cerebro. Gastar semanas en Next.js antes de validar valor es optimizar la parte equivocada.

**Recomendación del panel:** desplegar la UI de Streamlit ya, conseguir 3-5 equipos que vuelvan cada semana, y dejar la migración de una sola superficie crítica para cuando haya un piloto diciendo textualmente que la interfaz lo limita.

### 3. Capturar la memoria histórica desde el primer día

**La decisión:** priorizar la captura de datos irrecuperables — `task_state_transitions` (ya construido) y los snapshots de métricas — por encima de cualquier feature vistosa.

**Por qué es la más importante ahora:** es la única de las tres que tiene costo de oportunidad **irreversible**. Cada semana sin capturar transiciones es historia que no se recupera, y el foso de Cenit no es el código (que es público) ni la UI (que es desechable) — es la memoria histórica que permite diagnóstico e IA. Sin ese dato acumulado, las métricas y la IA de V3 solo maquillan opiniones.

**Recomendación del panel:** el hook de transiciones ya está vivo; mantenerlo, sumarle snapshots append-only vía cron en cuanto haya el motor de KPIs, y no borrar ni sobrescribir jamás una serie temporal.

---

Las tres decisiones comparten una misma raíz: **Cenit gana por foco, evidencia y memoria — no por completitud, apariencia ni velocidad de construcción.** El producto ya está vivo y desplegado; el trabajo de aquí en adelante es resistir la tentación de construir de más y dejar que los pilotos dicten qué merece existir.
