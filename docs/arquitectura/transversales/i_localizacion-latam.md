## i) Consideraciones de localización LatAm

Cenit apunta a equipos de 10-50 personas en LatAm (arranque Colombia/México). La localización no es "traducir botones" — es lenguaje, moneda, zona horaria y, para la capa de billing futura, facturación electrónica obligatoria.

### Idioma

- **Español es la lengua base del producto** (ya lo es: toda la UI y el dominio están en español). Es un diferencial real frente a Jira/Linear, cuyos productos y docs son primariamente en inglés.
- **pt-BR como segunda ola** si se entra a Brasil — el mercado dev más grande de la región, pero con idioma y facturación (NF-e) propios que justifican tratarlo como fase aparte, no como un locale más.
- **Estrategia i18n:** hoy los textos están embebidos. Antes de pt-BR, extraer a un diccionario (`domain/i18n.py` o JSON por locale) y servir el idioma según preferencia del usuario. No invertir en i18n hasta tener señal de un cliente no hispanohablante — sería sobre-ingeniería.
- **Términos técnicos:** el glosario (transversal g) resuelve que muchos líderes del ICP no dominan "flow efficiency" o "WSJF" — el modo aprendizaje en español es parte de la localización, no un extra.

### Moneda y pricing

- **Mostrar precios en moneda local** (COP, MXN) genera más conversión que USD en LatAm B2B, pero **facturar/cobrar puede ser en USD** vía Stripe/Paddle para evitar la complejidad cambiaria al inicio.
- **Anclar el precio a valor, no a tipo de cambio:** un plan por equipo/mes con tiers por número de usuarios activos. Evitar el error de convertir un precio USD a COP con la tasa del día (se ve arbitrario y cambia solo).
- **Realidad de pago LatAm:** tarjeta corporativa no siempre disponible en equipos pequeños; contemplar transferencia/PSE (Colombia) y SPEI (México) como métodos, aunque sea manual al principio.

### Zona horaria

- **Almacenar todo en UTC, mostrar en local.** ⚠️ Riesgo activo detectado en el código: `api/crud.py` usa `datetime.utcnow()` (naive) en varios puntos, y `FlowService` normaliza `changed_at` a naive para comparar. Funciona hoy porque todo es UTC implícito, pero al mostrar fechas al usuario hay que convertir a su zona (COT = UTC-5, CDMX = UTC-6) en la capa de presentación.
- **Acción concreta:** migrar `datetime.utcnow()` → `datetime.now(timezone.utc)` (aware) para evitar bugs de comparación cuando la DB devuelva timestamps con zona (Postgres `TIMESTAMPTZ`), y formatear a la zona del usuario solo en `ui/`.
- **Cadencias sensibles a zona:** el reporte semanal y los check-ins de OKR deben dispararse en la mañana local del equipo, no a medianoche UTC (que en LatAm es tarde-noche del día anterior).

### Facturación electrónica (solo capa de billing futura — V3+)

No es necesaria para el producto ni los pilotos; se vuelve obligatoria al **facturar formalmente** a un cliente.

- **Colombia (DIAN):** factura electrónica obligatoria vía un proveedor tecnológico autorizado. No se construye desde cero — se integra un proveedor como **Siigo, Alegra o Factus** que expone API y maneja la validación con la DIAN (CUFE, XML UBL). Cenit solo dispara la emisión.
- **México (CFDI 4.0):** factura via un **PAC** (Proveedor Autorizado de Certificación) que timbra el CFDI. Igual que en Colombia: integrar, no reimplementar.
- **Regla:** la facturación electrónica es un módulo de integración detrás de un `feature_flag`, activado por país, y **solo cuando haya ingresos que facturar**. Antes de eso, un recibo simple basta.

### Prioridad de localización

1. **Ahora:** español nativo (✅ hecho) + zona horaria correcta al mostrar fechas.
2. **Con pilotos pagos:** pricing en moneda local + cobro USD vía Stripe.
3. **Con clientes formales:** facturación electrónica DIAN/CFDI vía proveedor.
4. **Con demanda de Brasil:** i18n real + pt-BR + NF-e.

Lo caro (i18n, facturación) espera señal; lo barato y de alto impacto (español, zona horaria) es prioridad inmediata.
