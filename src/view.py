from __future__ import annotations

from typing import TYPE_CHECKING

from relation import OracleRelationCatalogItem

if TYPE_CHECKING:
    from schema import OracleSchemaCatalogItem
    from connection import OracleHarlequinConnection


class OracleViewCatalogItem(OracleRelationCatalogItem):
    type_label = "v"

    @staticmethod
    def from_schema(
        parent: "OracleSchemaCatalogItem",
        label: str,
        type_name: str,
        connection: "OracleHarlequinConnection",
    ) -> "OracleViewCatalogItem":
        return OracleViewCatalogItem(
            qualified_identifier=f'"{label}"',
            query_name=f'"{label}"',
            label=label,
            type_label="v",
            type_name=type_name,
            connection=connection,
            parent=parent,
            loaded=False,
        )
