from __future__ import annotations

from typing import TYPE_CHECKING

from object import OracleObjectCatalogItem

if TYPE_CHECKING:
    from schema import OracleSchemaCatalogItem
    from connection import OracleHarlequinConnection


class OracleSynonymCatalogItem(OracleObjectCatalogItem):
    type_label = "sn"

    @staticmethod
    def from_schema(
        parent: "OracleSchemaCatalogItem",
        label: str,
        connection: "OracleHarlequinConnection",
    ) -> "OracleSynonymCatalogItem":
        return OracleSynonymCatalogItem(
            qualified_identifier=f'"{label}"',
            query_name=f'"{label}"',
            label=label,
            type_label="sn",
            type_name="SYNONYM",
            connection=connection,
            parent=parent,
            loaded=False,
        )
