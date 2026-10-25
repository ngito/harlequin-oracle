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
        from catalog_groups import (
            OracleTableGroupItem,
            OracleViewGroupItem,
            OracleFunctionGroupItem,
            OracleProcedureGroupItem,
            OracleIndexGroupItem,
            OracleSynonymGroupItem,
            OracleSequenceGroupItem,
            OraclePackageGroupItem,
        )

        children: list[CatalogItem] = []

        try:
            # Check if tables exist before adding the group
            try:
                conn = self.connection.conn
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM user_tables")
                if cur.fetchone()[0] > 0:
                    children.append(OracleTableGroupItem(parent=self, connection=self.connection))
                cur.close()
            except Exception:
                pass

            try:
                conn = self.connection.conn
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM user_views")
                if cur.fetchone()[0] > 0:
                    children.append(OracleViewGroupItem(parent=self, connection=self.connection))
                cur.close()
            except Exception:
                pass

            try:
                conn = self.connection.conn
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM user_objects WHERE object_type = 'FUNCTION'")
                if cur.fetchone()[0] > 0:
                    children.append(OracleFunctionGroupItem(parent=self, connection=self.connection))
                cur.close()
            except Exception:
                pass

            try:
                conn = self.connection.conn
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM user_objects WHERE object_type = 'PROCEDURE'")
                if cur.fetchone()[0] > 0:
                    children.append(OracleProcedureGroupItem(parent=self, connection=self.connection))
                cur.close()
            except Exception:
                pass

            try:
                conn = self.connection.conn
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM user_indexes")
                if cur.fetchone()[0] > 0:
                    children.append(OracleIndexGroupItem(parent=self, connection=self.connection))
                cur.close()
            except Exception:
                pass

            try:
                conn = self.connection.conn
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM user_synonyms")
                if cur.fetchone()[0] > 0:
                    children.append(OracleSynonymGroupItem(parent=self, connection=self.connection))
                cur.close()
            except Exception:
                pass

            try:
                conn = self.connection.conn
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM user_sequences")
                if cur.fetchone()[0] > 0:
                    children.append(OracleSequenceGroupItem(parent=self, connection=self.connection))
                cur.close()
            except Exception:
                pass

            try:
                conn = self.connection.conn
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM user_objects WHERE object_type = 'PACKAGE'")
                if cur.fetchone()[0] > 0:
                    children.append(OraclePackageGroupItem(parent=self, connection=self.connection))
                cur.close()
            except Exception:
                pass

        except Exception:
            pass

        return children
