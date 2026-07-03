from domain.csv_import import (
    detect_mapping,
    normalize_estado,
    normalize_prioridad,
    parse_date,
    parse_tasks,
)


class TestNormalizacion:
    def test_estado_reconoce_sinonimos_de_tableros(self):
        assert normalize_estado("In Progress") == "En Proceso"
        assert normalize_estado("Done") == "Completado"
        assert normalize_estado("To Do") == "No Iniciado"
        assert normalize_estado("Blocked") == "Pausado"
        assert normalize_estado("basura") == "No Iniciado"

    def test_prioridad_invalida_cae_en_media(self):
        assert normalize_prioridad("alta") == "Alta"
        assert normalize_prioridad("") == "Media"
        assert normalize_prioridad("P1") == "Media"

    def test_parse_date_soporta_varios_formatos(self):
        assert parse_date("15/03/2026").year == 2026
        assert parse_date("2026-03-15").month == 3
        assert parse_date("pendiente") is None
        assert parse_date("") is None
        assert parse_date("31/12/1999") is None  # descarta años pre-2000


class TestDetectMapping:
    def test_detecta_encabezados_estilo_jira(self):
        headers = ["Summary", "Status", "Priority", "Assignee", "Due Date"]
        m = detect_mapping(headers)
        assert m["descripcion"] == "Summary"
        assert m["estado"] == "Status"
        assert m["responsable"] == "Assignee"
        assert m["fecha_fin"] == "Due Date"

    def test_detecta_encabezados_en_espanol(self):
        headers = ["Descripcion", "Estado", "Responsable", "Cliente"]
        m = detect_mapping(headers)
        assert m["descripcion"] == "Descripcion"
        assert m["cliente"] == "Cliente"


class TestParseTasks:
    def test_convierte_filas_a_tareas_normalizadas(self):
        rows = [
            {"Summary": "Arreglar login", "Status": "In Progress",
             "Priority": "High", "Assignee": "Ana", "Due Date": "20/03/2026"},
            {"Summary": "Migrar API", "Status": "Done",
             "Priority": "Alta", "Assignee": "unassigned", "Due Date": "10/03/2026"},
        ]
        r = parse_tasks(rows)
        assert len(r.tasks) == 2
        assert r.skipped == 0
        t0 = r.tasks[0]
        assert t0["descripcion"] == "Arreglar login"
        assert t0["estado"] == "En Proceso"
        assert t0["prioridad"] == "Media"       # "High" no es prioridad válida → Media
        assert t0["responsable"] == "Ana"
        t1 = r.tasks[1]
        assert t1["estado"] == "Completado"
        assert t1["responsable"] is None         # "unassigned" → None
        assert t1["fecha_completado"] is not None # completada con fecha → se fija

    def test_omite_filas_sin_descripcion(self):
        rows = [{"Summary": "Válida", "Status": "To Do"},
                {"Summary": "", "Status": "To Do"}]
        r = parse_tasks(rows)
        assert len(r.tasks) == 1
        assert r.skipped == 1

    def test_sin_columna_descripcion_avisa_y_no_importa(self):
        rows = [{"Foo": "bar", "Baz": "qux"}]
        r = parse_tasks(rows)
        assert r.tasks == []
        assert r.skipped == 1
        assert any("descripción" in w.lower() for w in r.warnings)

    def test_archivo_vacio_devuelve_warning(self):
        r = parse_tasks([])
        assert r.tasks == []
        assert r.warnings
