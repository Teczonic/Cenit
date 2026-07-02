# Cenit — Team Backlog Manager

App web completa para gestionar el backlog del equipo Xertify/Xertiflow.
Stack: **FastAPI + SQLite/PostgreSQL + HTML/JS puro** — sin framework frontend.

---

## Deploy en Vercel (gratis, 5 minutos)

### 1. Base de datos gratuita — Supabase
1. Ir a https://supabase.com → crear proyecto gratuito
2. Settings → Database → Connection string → URI
3. Copiar la URL (formato: `postgresql://postgres:PASSWORD@...supabase.co:5432/postgres`)

### 2. Deploy en Vercel
```bash
# Instalar Vercel CLI
npm i -g vercel

# En la carpeta del proyecto
vercel

# Seguir el wizard: Framework = Other, Root = ./
```

O importar desde GitHub en https://vercel.com/new

### 3. Variables de entorno en Vercel
En el dashboard de Vercel → Settings → Environment Variables:

```
DATABASE_URL = postgresql://postgres:PASSWORD@...supabase.co:5432/postgres
SECRET_KEY   = una-clave-secreta-larga-y-aleatoria-2026
```

### 4. Inicializar datos
Después del primer deploy, abrir en el navegador:
```
https://tu-app.vercel.app/api/seed
```
Esto crea los usuarios del equipo y tareas de ejemplo.

---

## Desarrollo local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Correr el servidor (SQLite local automático)
uvicorn api.main:app --reload --port 8000

# Abrir el frontend
open public/index.html
# O servir estático:
python -m http.server 3000 --directory public
```

Luego ir a: http://localhost:3000

---

## Credenciales del equipo (iniciales)

| Usuario   | Contraseña   | Rol    |
|-----------|-------------|--------|
| harold    | harold123   | member |
| fidel     | fidel123    | admin  |
| lorena    | lorena123   | member |
| jimmy     | jimmy123    | admin |
| jhezir    | jhezir123   | member |
| felipe    | felipe123   | member |
| luispe    | luispe123   | member |
| luispl    | luispl123   | admin |
| luisr     | luisr123    | member |
| danny     | danny123    | admin |
| moshe     | moshe123    | admin |

> ⚠️ Cambiar contraseñas después del primer login desde el panel admin.

---

## Funcionalidades

- **Kanban** — tablero con 4 columnas (No Iniciado / En Proceso / Pausado / Completado)
- **Matriz Eisenhower** — priorización automática Q1-Q4 por prioridad y estado
- **Matriz de riesgos** — Risk Score = Probabilidad × Impacto × (1 − test coverage)
- **Analytics** — throughput mensual, lead time por persona, distribución de prioridades
- **Equipo** — vista de carga activa por persona
- **Filtros** — por entidad (Xertify/Xertiflow), prioridad, responsable, búsqueda libre
- **Autenticación JWT** — token guardado en localStorage, expira en 72h

---

## Estructura del proyecto

```
cenit/
├── api/
│   ├── main.py       # FastAPI app + rutas
│   ├── models.py     # SQLAlchemy models
│   ├── schemas.py    # Pydantic schemas
│   ├── crud.py       # Operaciones DB + seed
│   ├── auth.py       # JWT + bcrypt
│   ├── database.py   # Configuración SQLAlchemy
│   └── index.py      # Entry point para Vercel
├── public/
│   └── index.html    # Frontend completo (sin dependencias)
├── requirements.txt
├── vercel.json
└── README.md
```

---

## Alternativas de deploy gratuito

| Plataforma | Backend | DB         | Notas                        |
|------------|---------|------------|------------------------------|
| **Vercel** | ✅      | Supabase   | Recomendado, más rápido      |
| Railway    | ✅      | PostgreSQL | Todo en uno, muy fácil       |
| Render     | ✅      | PostgreSQL | Free tier puede dormirse     |
| Fly.io     | ✅      | SQLite     | Más control, Docker          |
