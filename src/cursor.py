from __future__ import annotations

import oracledb


class OracleHarlequinCursor:
    def __init__(self, cursor):
        self.cursor = cursor
        self._limit = None

    def columns(self):
        desc = self.cursor.description
        if desc is None:
            return []
        return [(col[0], self._get_short_type(col[1])) for col in desc]

    def set_limit(self, limit):
        self._limit = limit
        return self

    def fetchall(self):
        try:
            if self._limit is not None:
                return self.cursor.fetchmany(self._limit)
            return self.cursor.fetchall()
        except Exception as e:
            from harlequin.exception import HarlequinQueryError
            raise HarlequinQueryError(msg=str(e), title="Error executing query") from e

    def fetchone(self):
        return self.cursor.fetchone()

    def execute(self, sql, params=None):
        if params:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)

    def cancel(self):
        try:
            self.cursor.connection.cancel()
        except Exception:
            pass

    @staticmethod
    def _get_short_type(pytype_id):
        mapping = {
            oracledb.DB_TYPE_VARCHAR: "string",
            oracledb.DB_TYPE_CHAR: "string",
            oracledb.DB_TYPE_LONG: "string",
            oracledb.DB_TYPE_NVARCHAR: "string",
            oracledb.DB_TYPE_NCHAR: "string",
            oracledb.DB_TYPE_NUMBER: "number",
            oracledb.DB_TYPE_BINARY_DOUBLE: "float",
            oracledb.DB_TYPE_BINARY_FLOAT: "float",
            oracledb.DB_TYPE_BINARY_INTEGER: "integer",
            oracledb.DB_TYPE_DATE: "date",
            oracledb.DB_TYPE_TIMESTAMP: "timestamp",
            oracledb.DB_TYPE_TIMESTAMP_TZ: "timestamptz",
            oracledb.DB_TYPE_TIMESTAMP_LTZ: "timestamp",
            oracledb.DB_TYPE_INTERVAL_DS: "interval",
            oracledb.DB_TYPE_INTERVAL_YM: "interval",
            oracledb.DB_TYPE_RAW: "raw",
            oracledb.DB_TYPE_BLOB: "blob",
            oracledb.DB_TYPE_CLOB: "clob",
            oracledb.DB_TYPE_BFILE: "bfile",
            oracledb.DB_TYPE_ROWID: "rowid",
            oracledb.DB_TYPE_UROWID: "rowid",
            oracledb.DB_TYPE_BOOLEAN: "boolean",
            oracledb.DB_TYPE_JSON: "json",
            oracledb.DB_TYPE_XMLTYPE: "xml",
        }
        return mapping.get(pytype_id, str(pytype_id))
