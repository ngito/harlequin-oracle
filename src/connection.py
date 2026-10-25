from __future__ import annotations

import os
import oracledb
from harlequin import HarlequinConnection
from harlequin.autocomplete.completion import HarlequinCompletion
from harlequin.catalog import Catalog, CatalogSearchResult
from harlequin.exception import (
    HarlequinConnectionError,
    HarlequinQueryError,
    HarlequinCopyError,
)
from harlequin.transaction_mode import HarlequinTransactionMode

from cursor import OracleHarlequinCursor
from schema import OracleSchemaCatalogItem
from table import OracleTableCatalogItem
from view import OracleViewCatalogItem
from column import OracleColumnCatalogItem
from function import OracleFunctionCatalogItem
from procedure import OracleProcedureCatalogItem
from package import OraclePackageCatalogItem
from package import OraclePackageSubProgram
from index import OracleIndexCatalogItem
from synonym import OracleSynonymCatalogItem
from sequence import OracleSequenceCatalogItem
from ddl import _map_oracle_type


class OracleHarlequinConnection(HarlequinConnection):
    def __init__(self, conn_oracledb, init_message=""):
        self.conn = conn_oracledb
        self._cursor = None
        self.init_message = init_message
        self._transaction_mode = HarlequinTransactionMode(label="Autocommit")

    def execute(self, query: str) -> OracleHarlequinCursor:
        self._cursor = OracleHarlequinCursor(self.conn.cursor())
        try:
            self._cursor.cursor.execute(query)
        except Exception as e:
            raise HarlequinQueryError(msg=str(e), title="Error executing query") from e
        return self._cursor

    def get_catalog(self) -> Catalog:
        return Catalog(
            items=[
                OracleSchemaCatalogItem.from_connection(self),
            ]
        )

    def get_completions(self) -> list[HarlequinCompletion]:
        from options import ORACLE_KEYWORDS, ORACLE_FUNCTIONS
        return [
            HarlequinCompletion(
                label=kw,
                type_label="",
                value=kw,
                priority=100,
            )
            for kw in ORACLE_KEYWORDS
        ] + [
            HarlequinCompletion(
                label=fn,
                type_label="func",
                value=fn,
                priority=1000,
                context="function",
            )
            for fn in ORACLE_FUNCTIONS
        ]

    @property
    def transaction_mode(self) -> HarlequinTransactionMode | None:
        if self.conn.autocommit:
            return HarlequinTransactionMode(label="Autocommit")
        return HarlequinTransactionMode(
            label="Manual",
            commit=self._commit,
            rollback=self._rollback,
        )

    def _commit(self):
        try:
            self.conn.commit()
        except Exception as e:
            raise HarlequinQueryError(msg=str(e), title="Error committing transaction") from e

    def _rollback(self):
        try:
            self.conn.rollback()
        except Exception as e:
            raise HarlequinQueryError(msg=str(e), title="Error rolling back transaction") from e

    def toggle_transaction_mode(self) -> HarlequinTransactionMode:
        self.conn.autocommit = not self.conn.autocommit
        return self.transaction_mode

    def get_schema(self):
        return None

    def cancel(self):
        if self._cursor:
            self._cursor.cancel()

    def search_catalog(self, term: str, kind: str = "all"):
        results = []
        try:
            cur = self.conn.cursor()
            schema = OracleSchemaCatalogItem.get_schema_name(self.conn)

            if kind in ("all", "relations"):
                for row in cur.execute(
                    "SELECT table_name FROM user_tables WHERE UPPER(table_name) LIKE :1 ORDER BY table_name",
                    [f"%{term}%"]
                ).fetchall():
                    results.append(CatalogSearchResult(
                        item=OracleTableCatalogItem.from_schema(
                            parent=None, label=row[0], type_name="TABLE", connection=self
                        ),
                        parents=(schema,),
                    ))
                for row in cur.execute(
                    "SELECT view_name FROM user_views WHERE UPPER(view_name) LIKE :1 ORDER BY view_name",
                    [f"%{term}%"]
                ).fetchall():
                    results.append(CatalogSearchResult(
                        item=OracleViewCatalogItem.from_schema(
                            parent=None, label=row[0], type_name="VIEW", connection=self
                        ),
                        parents=(schema,),
                    ))

            if kind in ("all", "columns"):
                for row in cur.execute(
                    "SELECT table_name, column_name, data_type, nullable, data_precision, data_scale "
                    "FROM user_tab_columns WHERE UPPER(column_name) LIKE :1 ORDER BY table_name, column_id",
                    [f"%{term}%"]
                ).fetchall():
                    table_name, col_name, data_type, nullable, precision, scale = row
                    short_type, type_label = _map_oracle_type(data_type, precision, scale, nullable)
                    results.append(CatalogSearchResult(
                        item=OracleColumnCatalogItem(
                            qualified_identifier=f'"{table_name}"."{col_name}"',
                            query_name=f'"{col_name}"',
                            label=col_name,
                            type_label=type_label,
                            type_name=short_type,
                        ),
                        parents=(schema, table_name),
                    ))

            if kind in ("all",):
                try:
                    for row in cur.execute(
                        "SELECT object_name FROM user_objects "
                        "WHERE object_type = 'FUNCTION' AND UPPER(object_name) LIKE :1",
                        [f"%{term}%"]
                    ).fetchall():
                        results.append(CatalogSearchResult(
                            item=OracleFunctionCatalogItem.from_schema(
                                label=row[0], connection=self
                            ),
                            parents=(schema,),
                        ))
                except Exception:
                    pass

                try:
                    for row in cur.execute(
                        "SELECT object_name FROM user_objects "
                        "WHERE object_type = 'PROCEDURE' AND UPPER(object_name) LIKE :1",
                        [f"%{term}%"]
                    ).fetchall():
                        results.append(CatalogSearchResult(
                            item=OracleProcedureCatalogItem.from_schema(
                                label=row[0], connection=self
                            ),
                            parents=(schema,),
                        ))
                except Exception:
                    pass

                try:
                    for row in cur.execute(
                        "SELECT index_name FROM user_indexes WHERE UPPER(index_name) LIKE :1",
                        [f"%{term}%"]
                    ).fetchall():
                        results.append(CatalogSearchResult(
                            item=OracleIndexCatalogItem.from_schema(
                                label=row[0], connection=self
                            ),
                            parents=(schema,),
                        ))
                except Exception:
                    pass

                for row in cur.execute(
                    "SELECT synonym_name FROM user_synonyms WHERE UPPER(synonym_name) LIKE :1",
                    [f"%{term}%"]
                ).fetchall():
                    results.append(CatalogSearchResult(
                        item=OracleSynonymCatalogItem.from_schema(
                            parent=None, label=row[0], connection=self
                        ),
                        parents=(schema,),
                    ))

                for row in cur.execute(
                    "SELECT sequence_name FROM user_sequences WHERE UPPER(sequence_name) LIKE :1",
                    [f"%{term}%"]
                ).fetchall():
                    results.append(CatalogSearchResult(
                        item=OracleSequenceCatalogItem.from_schema(
                            parent=None, label=row[0], connection=self
                        ),
                        parents=(schema,),
                    ))
        except Exception:
            pass
        return results

    def copy(self, query: str, path, format_name: str, options: dict) -> None:
        raise HarlequinCopyError(
            "Oracle adapter does not support exporting data. Use SQL*Plus or Oracle SQL Developer.",
            title="Copy not implemented",
        )

    def validate_sql(self, sql: str) -> str:
        if not sql or not sql.strip():
            return ""
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        for stmt in statements:
            cur = self.conn.cursor()
            try:
                cur.execute(f"EXPLAIN PLAN FOR {stmt}")
                cur.close()
            except Exception:
                return ""
        return sql

    def cursor(self):
        return OracleHarlequinCursor(self.conn.cursor())

    def close(self):
        self.conn.close()
