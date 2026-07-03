# Deploy reproducible de Cenit

Arquitectura del despliegue: **la API va en Vercel** (función serverless Python) y
**la UI Streamlit va en otro host** (Streamlit Community Cloud). Vercel no ejecuta
Streamlit —es un servidor de larga duración, no serverless— así que la interfaz
vive aparte y apunta a la API por HTTP.

```
Navegador ──▶ Streamlit (Streamlit Cloud)  ──HTTP──▶  API FastAPI (Vercel)  ──▶  Postgres (Supabase)
```

## 1. Base de datos — Supabase (5 min)

1. Crea un proyecto gratis en https://supabase.com
2. Settings → Database → Connection string → **URI**
3. Copia la URL (`postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:5432/postgres`)

Sin esto la API cae a SQLite en `/tmp`, que **se borra en cada cold start y diverge
entre instancias serverless** — cualquier dato que cree el piloto se pierde.

## 2. API en Vercel

Ya está conectado a GitHub. Solo falta configurar el entorno:

1. Vercel → tu proyecto `cenit` → Settings → Environment Variables:
   - `DATABASE_URL` = la URI de Supabase del paso 1
   - `SECRET_KEY` = una clave larga y aleatoria
2. Redespliega (Deployments → Redeploy, o haz `git push` a `main`).
3. Siembra los datos una vez: abre `https://<tu-app>.vercel.app/api/seed`
   (o `curl -X POST .../api/seed`).

Verifica:
- `https://<tu-app>.vercel.app/`            → JSON de estado
- `https://<tu-app>.vercel.app/docs`        → Swagger navegable
- `https://<tu-app>.vercel.app/api/health`  → `{"status":"ok","db":"up"}`
- `https://<tu-app>.vercel.app/api/tasks`   → lista de tareas

> El `vercel.json` enruta **todo** el tráfico a la función (`/(.*)`), por eso
> funcionan la raíz, `/docs` y `/api/*`. La API instala desde `api/requirements.txt`
> (mantenlo en sync con la sección "# API" del `requirements.txt` raíz).

## 3. UI en Streamlit Community Cloud

1. https://share.streamlit.io → New app → repo de GitHub, rama `main`
2. Main file path: `ui/app.py`
3. Advanced → Secrets:
   ```toml
   CENIT_API_URL = "https://<tu-app>.vercel.app"
   ```
   (la UI lee `CENIT_API_URL`; por defecto usa `http://localhost:8000`)
4. Deploy. El login de prueba es `fidel` / `fidel123` (cámbialo en producción).

La API ya permite CORS desde cualquier origen, así que la UI en otro host puede
llamarla sin configuración extra.

## Alternativas para la UI
Cualquier host que corra el `Dockerfile.ui` sirve: Railway, Render o Fly.io.
Pasa `CENIT_API_URL` como variable de entorno apuntando a la API de Vercel.

## Checklist de piloto
- [ ] `DATABASE_URL` (Supabase) y `SECRET_KEY` configurados en Vercel
- [ ] `/api/health` responde `db: up`
- [ ] `/api/seed` ejecutado una vez
- [ ] UI desplegada con `CENIT_API_URL` correcto
- [ ] Cambiadas las contraseñas del seed antes de dar acceso externo
