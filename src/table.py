from __future__ import annotations

from typing import TYPE_CHECKING

from relation import OracleRelationCatalogItem

if TYPE_CHECKING:
    from schema import OracleSchemaCatalogItem
    from connection import OracleHarlequinConnection


class OracleTableCatalogItem(OracleRelationCatalogItem):
    type_label = "t"

    @staticmethod
    def from_schema(
        parent: "OracleSchemaCatalogItem",
        label: str,
        type_name: str,
        connection: "OracleHarlequinConnection",
    ) -> "OracleTableCatalogItem":
        return OracleTableCatalogItem(
            qualified_identifier=f'"{label}"',
            query_name=f'"{label}"',
            label=label,
            type_label="t",
            type_name=type_name,
            connection=connection,
            parent=parent,
            loaded=False,
        )
