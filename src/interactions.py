from __future__ import annotations

from harlequin.catalog import CatalogItem, InteractiveCatalogItem
from harlequin.exception import HarlequinQueryError


def _get_label(item):
    """Get bare label from catalog item."""
    label = getattr(item, 'label', None)
    if label:
        return label
    qi = getattr(item, 'qualified_identifier', '')
    if qi and qi.startswith('"') and qi.endswith('"'):
        return qi[1:-1]
    return qi


def _get_connection(item):
    """Get Oracle connection from catalog item."""
    return getattr(item, 'connection', None)


# ---------------------------------------------------------------------------
# Table/View interactions
# ---------------------------------------------------------------------------

def _insert_columns_at_cursor(item, driver) -> None:
    conn = _get_connection(item)
    if conn is None:
        return
    label = _get_label(item)
    cur = conn.conn.cursor()
    try:
        rows = cur.execute(
            "SELECT column_name FROM user_tab_columns "
            "WHERE table_name = :1 ORDER BY column_id",
            [label]
        ).fetchall()
        cols = [row[0] for row in rows]
        if cols:
            driver.insert_text_at_selection(text=", ".join(cols))
        else:
            driver.notify(f"No columns found for {label}", severity="warning")
    except Exception as e:
        driver.notify(str(e), severity="error")
    finally:
        cur.close()


def _show_select_star(item, driver) -> None:
    """Execute SELECT * directly and show results in the query results panel."""
    conn = _get_connection(item)
    if conn is None:
        driver.notify("No connection available", severity="error")
        return
    label = _get_label(item)
    # Build fully qualified name: schema.table or just table
    parents = getattr(item, 'parents', ())
    if parents:
        qualified_name = f'"{parents[0]}".{item.query_name}'
    else:
        qualified_name = item.query_name
    query = f'SELECT * FROM {qualified_name} WHERE rownum <= 100'
    driver.run_query(query, title=f"Preview: {label}")


def _show_describe(item, driver) -> None:
    """Execute DESCRIBE query and show results in the query results panel."""
    conn = _get_connection(item)
    if conn is None:
        driver.notify("No connection available", severity="error")
        return
    label = _get_label(item)
    parents = getattr(item, 'parents', ())
    if parents:
        qualified_name = f'"{parents[0]}".{item.query_name}'
    else:
        qualified_name = item.query_name
    query = (
        f"SELECT column_name, data_type, nullable, data_length, "
        f"data_precision, data_scale FROM user_tab_columns "
        f"WHERE table_name = '{label}' ORDER BY column_id"
    )
    driver.run_query(query, title=f"Describe: {label}")


def _show_ddl(item, driver) -> None:
    conn = _get_connection(item)
    if conn is None:
        return
    label = _get_label(item)

    type_label = getattr(item, 'type_label', '')
    type_map = {
        "t": ("TABLE",),
        "v": ("VIEW",),
        "fn": ("FUNCTION",),
        "pr": ("PROCEDURE",),
        "pk": ("PACKAGE",),
        "sub": ("PROCEDURE",),
        "ix": ("INDEX",),
        "sn": ("SYNONYM",),
        "sq": ("SEQUENCE",),
    }
    ddl_type = type_map.get(type_label, ("TABLE",))

    for dt in ddl_type:
        ddl = _get_ddl_for_type(conn.conn, dt, label)
        if ddl:
            driver.insert_text_at_selection(text=ddl)
            return

    driver.notify(f"No DDL found for {label}", severity="warning")


def _get_ddl_for_type(connection_conn, object_type, name):
    """Get DDL via DBMS_METADATA.GET_DDL."""
    cur = connection_conn.cursor()
    try:
        row = cur.execute(
            "SELECT DBMS_METADATA.GET_DDL(:1, :2) FROM DUAL",
            [object_type, name]
        ).fetchone()
        if row and row[0]:
            return str(row[0])
        return None
    except Exception:
        return None


def _execute_drop_table_statement(item, driver) -> None:
    label = _get_label(item)
    conn = _get_connection(item)
    if conn is None:
        return

    def _do_drop():
        cur = conn.conn.cursor()
        try:
            cur.execute(f'DROP TABLE "{label}"')
            conn.conn.commit()
            driver.notify(f"Table {label} dropped", severity="information")
            driver.refresh_catalog()
        except Exception as e:
            driver.notify(str(e), severity="error")
        finally:
            cur.close()

    driver.confirm_and_execute(callback=_do_drop, instructions=f"Drop table {label}?")


def _execute_drop_view_statement(item, driver) -> None:
    label = _get_label(item)
    conn = _get_connection(item)
    if conn is None:
        return

    def _do_drop():
        cur = conn.conn.cursor()
        try:
            cur.execute(f'DROP VIEW "{label}"')
            conn.conn.commit()
            driver.notify(f"View {label} dropped", severity="information")
            driver.refresh_catalog()
        except Exception as e:
            driver.notify(str(e), severity="error")
        finally:
            cur.close()

    driver.confirm_and_execute(callback=_do_drop, instructions=f"Drop view {label}?")


def _count_rows(item, driver) -> None:
    label = _get_label(item)
    conn = _get_connection(item)
    if conn is None:
        driver.notify("No connection available", severity="error")
        return
    parents = getattr(item, 'parents', ())
    if parents:
        qualified_name = f'"{parents[0]}".{item.query_name}'
    else:
        qualified_name = item.query_name
    query = f"SELECT COUNT(*) FROM {qualified_name}"
    driver.run_query(query, title=f"Count: {label}")


# ---------------------------------------------------------------------------
# Function interaction
# ---------------------------------------------------------------------------

def _show_function_preview(item, driver) -> None:
    """Run the function and show result in the query results panel."""
    label = _get_label(item)
    conn = _get_connection(item)
    if conn is None:
        driver.notify("No connection available", severity="error")
        return
    query = f'SELECT "{label}" FROM DUAL'
    driver.run_query(query, title=f"Preview: {label}")


# ---------------------------------------------------------------------------
# Sequence interaction
# ---------------------------------------------------------------------------

def _get_sequence_nextval(item, driver) -> None:
    label = _get_label(item)
    conn = _get_connection(item)
    if conn is None:
        driver.notify("No connection available", severity="error")
        return
    query = f'SELECT "{label}".NEXTVAL FROM DUAL'
    driver.run_query(query, title=f"Next Val: {label}")


# ---------------------------------------------------------------------------
# Copy / name helpers
# ---------------------------------------------------------------------------

def _copy_qualified_name(item, driver) -> None:
    label = _get_label(item)
    driver.insert_text_at_selection(text=f'"{label}"')



# ---------------------------------------------------------------------------
# Configure INTERACTIONS on catalog item classes
# ---------------------------------------------------------------------------

def configure_interactions(catalog_items):
    """Set up INTERACTIONS on catalog item classes.

    catalog_items: dict mapping class names to classes from harlequin_oracle package.
    """
    OracleRelationCatalogItem = catalog_items["OracleRelationCatalogItem"]
    OracleTableCatalogItem = catalog_items["OracleTableCatalogItem"]
    OracleViewCatalogItem = catalog_items["OracleViewCatalogItem"]
    OracleFunctionCatalogItem = catalog_items["OracleFunctionCatalogItem"]
    OracleProcedureCatalogItem = catalog_items["OracleProcedureCatalogItem"]
    OraclePackageCatalogItem = catalog_items["OraclePackageCatalogItem"]
    OraclePackageSubProgram = catalog_items["OraclePackageSubProgram"]
    OracleIndexCatalogItem = catalog_items["OracleIndexCatalogItem"]
    OracleSynonymCatalogItem = catalog_items["OracleSynonymCatalogItem"]
    OracleSequenceCatalogItem = catalog_items["OracleSequenceCatalogItem"]

    OracleRelationCatalogItem.INTERACTIONS = [
        ("Insert Columns at Cursor", _insert_columns_at_cursor),
        ("Preview Data", _show_select_star),
        ("Describe", _show_describe),
        ("Show DDL", _show_ddl),
    ]

    OracleTableCatalogItem.INTERACTIONS = (
        list(OracleRelationCatalogItem.INTERACTIONS) +
        [
            ("Count Rows", _count_rows),
            ("Drop Table", _execute_drop_table_statement),
        ]
    )

    OracleViewCatalogItem.INTERACTIONS = (
        list(OracleRelationCatalogItem.INTERACTIONS) +
        [
            ("Count Rows", _count_rows),
            ("Drop View", _execute_drop_view_statement),
        ]
    )

    OracleFunctionCatalogItem.INTERACTIONS = [
        ("Preview Data", _show_function_preview),
        ("Show DDL", _show_ddl),
        ("Copy Qualified Name", _copy_qualified_name),
    ]

    OracleProcedureCatalogItem.INTERACTIONS = [
        ("Show DDL", _show_ddl),
        ("Copy Qualified Name", _copy_qualified_name),
    ]

    OraclePackageCatalogItem.INTERACTIONS = [
        ("Show DDL", _show_ddl),
        ("Copy Qualified Name", _copy_qualified_name),
    ]

    OraclePackageSubProgram.INTERACTIONS = [
        ("Show DDL", _show_ddl),
        ("Copy Qualified Name", _copy_qualified_name),
    ]

    OracleIndexCatalogItem.INTERACTIONS = [
        ("Show DDL", _show_ddl),
        ("Copy Qualified Name", _copy_qualified_name),
    ]

    OracleSynonymCatalogItem.INTERACTIONS = [
        ("Preview Data", _show_select_star),
        ("Show DDL", _show_ddl),
        ("Copy Qualified Name", _copy_qualified_name),
    ]

    OracleSequenceCatalogItem.INTERACTIONS = [
        ("Next Value", _get_sequence_nextval),
        ("Show DDL", _show_ddl),
        ("Copy Qualified Name", _copy_qualified_name),
    ]
