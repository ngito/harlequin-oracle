from __future__ import annotations

from typing import TYPE_CHECKING

from object import OracleObjectCatalogItem

if TYPE_CHECKING:
    from schema import OracleSchemaCatalogItem
    from connection import OracleHarlequinConnection


class OracleProcedureCatalogItem(OracleObjectCatalogItem):
    type_label = "pr"

    @staticmethod
    def from_schema(
        parent: "OracleSchemaCatalogItem",
        label: str,
        connection: "OracleHarlequinConnection",
    ) -> "OracleProcedureCatalogItem":
        return OracleProcedureCatalogItem(
            qualified_identifier=f'"{label}"',
            query_name=f'"{label}"',
            label=label,
            type_label="pr",
            type_name="PROCEDURE",
            connection=connection,
            parent=parent,
            loaded=False,
        )
