def _map_oracle_type(data_type, precision, scale, nullable):
    """Map Oracle data type to (type_name, type_label)."""
    if data_type == 'NUMBER':
        short_type = "NUMBER"
        type_label = "num"
        if precision is not None or scale is not None:
            if precision is not None and scale is not None:
                short_type = f"NUMBER({precision},{scale})"
            elif precision is not None:
                short_type = f"NUMBER({precision})"
    elif data_type == 'VARCHAR2':
        short_type = "VARCHAR2"
        type_label = "str"
    elif data_type == 'VARCHAR':
        short_type = "VARCHAR"
        type_label = "str"
    elif data_type in ('CHAR', 'NCHAR', 'NVARCHAR2'):
        short_type = data_type
        type_label = "str"
    elif data_type == 'DATE':
        short_type = "DATE"
        type_label = "date"
    elif data_type == 'TIMESTAMP':
        short_type = "TIMESTAMP"
        type_label = "time"
    elif data_type in ('TIMESTAMP WITH TIME ZONE', 'TIMESTAMP_WITH_TIMEZONE'):
        short_type = "TIMESTAMPTZ"
        type_label = "tstz"
    elif data_type in ('TIMESTAMP WITH LOCAL TIME ZONE',):
        short_type = "TIMESTAMPLTZ"
        type_label = "tstz"
    elif data_type in ('RAW', 'BLOB', 'CLOB', 'BFILE'):
        short_type = data_type
        type_label = "lob"
    elif data_type == 'LONG':
        short_type = "LONG"
        type_label = "str"
    elif data_type == 'ROWID':
        short_type = "ROWID"
        type_label = "rid"
    elif data_type in ('BINARY_DOUBLE', 'BINARY_FLOAT'):
        short_type = data_type
        type_label = "flt"
    elif data_type == 'INTEGER':
        short_type = "INTEGER"
        type_label = "int"
    elif data_type == 'FLOAT':
        short_type = "FLOAT"
        type_label = "flt"
    else:
        short_type = data_type
        type_label = "???"

    if nullable == 'N':
        type_label += " NN"

    return short_type, type_label


def _get_schema_name(connection_conn) -> str:
    """Get current schema name from Oracle connection."""
    try:
        cur = connection_conn.cursor()
        row = cur.execute("SELECT USER FROM DUAL").fetchone()
        return row[0] if row else "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def _get_ddl(connection_conn, object_type, name):
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
