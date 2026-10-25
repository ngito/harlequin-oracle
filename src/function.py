from __future__ import annotations

from typing import TYPE_CHECKING

from object import OracleObjectCatalogItem

if TYPE_CHECKING:
    from schema import OracleSchemaCatalogItem
    from connection import OracleHarlequinConnection


class OracleFunctionCatalogItem(OracleObjectCatalogItem):
    type_label = "fn"

    @staticmethod
    def from_schema(
        parent: "OracleSchemaCatalogItem",
        label: str,
        connection: "OracleHarlequinConnection",
    ) -> "OracleFunctionCatalogItem":
        return OracleFunctionCatalogItem(
            qualified_identifier=f'"{label}"',
            query_name=f'"{label}"',
            label=label,
            type_label="fn",
            type_name="FUNCTION",
            connection=connection,
            parent=parent,
            loaded=False,
        )
