from __future__ import annotations

import os
import oracledb
from harlequin import (
    HarlequinAdapter,
    HarlequinConnection,
    HarlequinCursor,
    HarlequinAdapterOption,
)
from harlequin.autocomplete.completion import HarlequinCompletion
from harlequin.catalog import Catalog, CatalogSearchResult
from harlequin.exception import (
    HarlequinConnectionError,
    HarlequinQueryError,
    HarlequinCopyError,
)
from harlequin.options import TextOption
from harlequin.transaction_mode import HarlequinTransactionMode


# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------

tns = TextOption(
    name="tns",
    description="TNS alias from tnsnames.ora (like sqlplus). Overrides host/port/service_name.",
    default="",
)

username = TextOption(
    name="username",
    description="Database username. Use 'os' for OS authentication (like sqlplus /).",
    default="os",
)

password = TextOption(
    name="password",
    description="Database password (not used with OS authentication).",
    default="",
)

host = TextOption(
    name="host",
    description="Oracle server hostname or IP.",
    default="localhost",
)

port = TextOption(
    name="port",
    description="Oracle server port.",
    default="1521",
)

service_name = TextOption(
    name="service_name",
    description="Oracle service name or SID.",
    default="pdb1",
)

ORACLE_OPTIONS = [tns, username, password, host, port, service_name]

ORACLE_KEYWORDS = [
    "AND", "AS", "BETWEEN", "BY", "CASE", "CREATE", "SELECT", "FROM",
    "WHERE", "INSERT", "UPDATE", "DELETE", "TABLE", "INDEX", "ALTER",
    "DROP", "INTO", "VALUES", "SET", "NULL", "NOT", "OR", "IN", "LIKE",
    "ORDER", "GROUP", "HAVING", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER",
    "ON", "UNION", "ALL", "DISTINCT", "COUNT", "SUM", "AVG", "MIN", "MAX",
    "VARCHAR2", "NUMBER", "DATE", "INTEGER", "CHAR", "LONG", "ROWNUM",
    "TRUNCATE", "COMMIT", "ROLLBACK", "GRANT", "REVOKE", "WITH",
]

ORACLE_FUNCTIONS = [
    "ABS", "ACOS", "ADD_MONTHS", "ASCII", "ASIN", "ATAN", "AVG", "CEIL",
    "CHR", "CONCAT", "COS", "COSH", "COUNT", "DECODE", "DUAL", "EXP",
    "FLOOR", "INITCAP", "LENGTH", "LN", "LOWER", "LPAD", "LTRIM",
    "MAX", "MIN", "MOD", "NVL", "POWER", "REPLACE", "ROUND", "RPAD",
    "RTRIM", "SIGN", "SIN", "SINH", "SQRT", "SUBSTR", "SUM", "SYSDATE",
    "TAN", "TANH", "TO_CHAR", "TO_DATE", "TO_NUMBER", "TO_TIMESTAMP",
    "TRUNC", "UPPER", "WMSYS.WM_CONCAT", "SYS_GUID",
]
