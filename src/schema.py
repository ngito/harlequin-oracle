from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from harlequin.catalog import CatalogItem, InteractiveCatalogItem
from ddl import _get_schema_name

if TYPE_CHECKING:
    from connection import OracleHarlequinConnection


@dataclass
class OracleSchemaCatalogItem(InteractiveCatalogItem["OracleHarlequinConnection"]):
    """Top-level schema node. Type label 'sch'."""
    INTERACTIONS: ClassVar[list | None] = None

    @classmethod
    def from_connection(
        cls, connection: "OracleHarlequinConnection"
    ) -> "OracleSchemaCatalogItem":
        schema_name = _get_schema_name(connection.conn)
        return cls(
            qualified_identifier=f'"{schema_name}"',
            query_name=f'"{schema_name}"',
            label=schema_name,
            type_label="sch",
            type_name="schema",
            connection=connection,
            loaded=False,
        )

    @staticmethod
    def get_schema_name(connection_conn) -> str:
        return _get_schema_name(connection_conn)

    def fetch_children(self) -> list[CatalogItem]:
        if self.connection is None:
            return []
        from table import OracleTableCatalogItem
        from view import OracleViewCatalogItem
        from index import OracleIndexCatalogItem
        from synonym import OracleSynonymCatalogItem
        from sequence import OracleSequenceCatalogItem

        conn = self.connection.conn
        cur = conn.cursor()
        children: list[CatalogItem] = []

        try:
            try:
                for row in cur.execute(
                    "SELECT table_name FROM user_tables ORDER BY table_name"
                ).fetchall():
                    children.append(
                        OracleTableCatalogItem.from_schema(
                            self, row[0], "TABLE", self.connection
                        )
                    )
            except Exception:
                pass

            try:
                for row in cur.execute(
                    "SELECT view_name FROM user_views ORDER BY view_name"
                ).fetchall():
                    children.append(
                        OracleViewCatalogItem.from_schema(
                            self, row[0], "VIEW", self.connection
                        )
                    )
            except Exception:
                pass

            try:
                for row in cur.execute(
                    "SELECT index_name FROM user_indexes ORDER BY index_name"
                ).fetchall():
                    children.append(
                        OracleIndexCatalogItem.from_schema(
                            self, row[0], self.connection
                        )
                    )
            except Exception:
                pass

            try:
                for row in cur.execute(
                    "SELECT synonym_name FROM user_synonyms ORDER BY synonym_name"
                ).fetchall():
                    children.append(
                        OracleSynonymCatalogItem.from_schema(
                            self, row[0], self.connection
                        )
                    )
            except Exception:
                pass

            try:
                for row in cur.execute(
                    "SELECT sequence_name FROM user_sequences ORDER BY sequence_name"
                ).fetchall():
                    children.append(
                        OracleSequenceCatalogItem.from_schema(
                            self, row[0], self.connection
                        )
                    )
            except Exception:
                pass
        finally:
            cur.close()

        return children
