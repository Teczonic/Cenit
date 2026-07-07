## j) Plan de datos semilla para demos

El objetivo: que un piloto abra Cenit y vea **todas las vistas pobladas y creíbles** sin exponer datos reales de nadie. Hoy el repo ya siembra 34 tareas + OKRs vía `crud.py::seed_initial_data` con el equipo real de Xertify. Este plan propone un seed **de demo genérico** (empresa ficticia) que no filtra datos internos y que hace lucir cada métrica.

### Empresa ficticia coherente

**"Nimbus Labs"** — software factory ficticia de 9 personas. Roles que hacen creíbles las vistas de Equipo y OKR:

| Nombre | Rol | Usuario |
|---|---|---|
| Elena Ríos | Engineering Lead (admin) | elena |
| Marco Díaz | Backend | marco |
| Sofía Peña | Backend | sofia |
| Diego Luna | Frontend | diego |
| Camila Ортiz | Frontend | camila |
| Andrés Gil | QA | andres |
| Lucía Mora | Producto | lucia |
| Pablo Vega | DevOps | pablo |
| Renata Sол | Diseño | renata |

### Distribución de ~60 tareas para poblar cada vista

El seed actual da 34; subir a ~60 con distribución deliberada para que ninguna vista se vea vacía o plana:

| Vista | Qué necesita | Cómo sembrarlo |
|---|---|---|
| Kanban | Columnas balanceadas | ~15 No Iniciado, ~18 En Proceso, ~7 Pausado, ~20 Completado |
| Eisenhower | Los 4 cuadrantes con casos claros | Mezclar prioridad (Urgente/Alta/Media/Baja) × proyecto importante/no |
| Riesgos | Críticos y altos visibles, no solo bajos | Algunas tareas Urgentes en proyectos clave, sin fecha o vencidas → score alto |
| Analytics / Flow | 3+ meses de throughput, lead times variados | Completadas con `fecha_completado` repartida en 12-14 semanas; lead times de 1 a 30 días |
| Cockpit | Tareas estancadas y en riesgo hoy | Varias En Proceso/Pausado con `fecha_inicio` de hace 10-20 días (aging alto) |
| OKRs | 2-3 objetivos con KRs en distinto progreso | 1 objetivo casi logrado, 1 a medias, 1 rezagado; tareas vinculadas para alignment ~40% |
| Equipo | Carga desigual entre personas | Repartir `responsable` con sesgo (algunos sobrecargados, otros libres) |

### Esqueleto de función

```python
def seed_demo_data(db: Session):
    """Datos de demo para pilotos — empresa ficticia, ninguna dato real.
    Espejo de seed_initial_data pero con Nimbus Labs y ~60 tareas balanceadas."""
    if db.query(models.User).filter_by(username="elena").first():
        return  # ya sembrado

    equipo = [
        ("elena", "Elena Ríos", "demo1234", "admin",  "#2563EB"),
        ("marco", "Marco Díaz", "demo1234", "member", "#0F766E"),
        # … resto del equipo
    ]
    for u in equipo:
        db.add(models.User(username=u[0], name=u[1],
                           hashed_password=hash_password(u[2]), role=u[3], color=u[4]))
    db.commit()

    now = datetime.utcnow()
    # (entidad, proyecto, cliente, desc, prioridad, estado, responsable, fecha_inicio, fecha_fin)
    tareas = _demo_task_matrix(now)   # ~60 tuplas con la distribución de la tabla de arriba
    for t in tareas:
        db.add(models.Task(**_row_to_task(t)))
    db.commit()

    # Historia de estados para que flujo/aging luzcan (reusa el backfill existente)
    for task in db.query(models.Task).all():
        _backfill_transitions(db, task)
    db.commit()

    _seed_demo_okrs(db)   # 3 objetivos, KRs en distinto progreso, tareas vinculadas
    db.commit()
```

### Cómo exponerlo

- Endpoint `POST /api/seed/demo` (distinto de `/api/seed`), protegido por token de admin, que puebla Nimbus Labs — para levantar un ambiente de demo limpio en segundos antes de una llamada de ventas.
- **Nunca mezclar** demo y datos reales en la misma base: usar un proyecto Supabase aparte para el ambiente de demo, o un flag de entorno que elija el seed.
- **Reproducibilidad:** el seed usa fechas relativas a `now` (como el actual), así la demo siempre se ve "reciente" sin importar cuándo se ejecute.

### Regla

El seed de demo es una herramienta de **ventas**, no de desarrollo: su criterio de éxito no es "tiene datos" sino "en la primera pantalla, el líder ve algo en riesgo, algo estancado y un OKR rezagado que le da ganas de preguntar cómo arreglarlo". Si el cockpit sembrado no genera esa conversación, el seed está mal calibrado, no el producto.
