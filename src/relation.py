from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from harlequin.catalog import CatalogItem, InteractiveCatalogItem
from ddl import _map_oracle_type

if TYPE_CHECKING:
    from schema import OracleSchemaCatalogItem
    from connection import OracleHarlequinConnection
    from column import OracleColumnCatalogItem


@dataclass
class OracleRelationCatalogItem(InteractiveCatalogItem["OracleHarlequinConnection"]):
    """Base for tables and views. Bare qualified_identifier."""
    parent: "OracleSchemaCatalogItem" | None = None
    INTERACTIONS: ClassVar[list | None] = None

    @staticmethod
    def from_schema(
        parent: "OracleSchemaCatalogItem",
        label: str,
        type_name: str,
        connection: "OracleHarlequinConnection",
    ) -> "OracleRelationCatalogItem":
        from table import OracleTableCatalogItem
        item = OracleTableCatalogItem(
            qualified_identifier=f'"{label}"',
            query_name=f'"{label}"',
            label=label,
            type_label="t",
            type_name=type_name,
            connection=connection,
            loaded=False,
        )
        item.parent = parent
        return item

    def fetch_children(self) -> list[CatalogItem]:
        if self.connection is None:
            return []
        from column import OracleColumnCatalogItem
        conn = self.connection.conn
        cur = conn.cursor()
        children: list[CatalogItem] = []
        try:
            for row in cur.execute(
                "SELECT column_name, data_type, nullable, data_length, data_precision, data_scale "
                "FROM user_tab_columns WHERE table_name = :1 ORDER BY column_id",
                [self.label]
            ).fetchall():
                col_name, data_type, nullable, data_length, precision, scale = row
                short_type, type_label = _map_oracle_type(data_type, precision, scale, nullable)
                children.append(
                    OracleColumnCatalogItem(
                        qualified_identifier=f'{self.qualified_identifier}."{col_name}"',
                        query_name=f'"{col_name}"',
                        label=col_name,
                        type_label=type_label,
                        type_name=short_type,
                    )
                )
        finally:
            cur.close()
        return children
