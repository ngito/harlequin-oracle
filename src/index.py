from __future__ import annotations

from typing import TYPE_CHECKING

from object import OracleObjectCatalogItem

if TYPE_CHECKING:
    from schema import OracleSchemaCatalogItem
    from connection import OracleHarlequinConnection


class OracleIndexCatalogItem(OracleObjectCatalogItem):
    type_label = "ix"

    @staticmethod
    def from_schema(
        parent: "OracleSchemaCatalogItem",
        label: str,
        connection: "OracleHarlequinConnection",
    ) -> "OracleIndexCatalogItem":
        return OracleIndexCatalogItem(
            qualified_identifier=f'"{label}"',
            query_name=f'"{label}"',
            label=label,
            type_label="ix",
            type_name="INDEX",
            connection=connection,
            parent=parent,
            loaded=False,
        )
