from __future__ import annotations

from typing import TYPE_CHECKING

from object import OracleObjectCatalogItem

if TYPE_CHECKING:
    from schema import OracleSchemaCatalogItem
    from connection import OracleHarlequinConnection


class OracleSequenceCatalogItem(OracleObjectCatalogItem):
    type_label = "sq"

    @staticmethod
    def from_schema(
        parent: "OracleSchemaCatalogItem",
        label: str,
        connection: "OracleHarlequinConnection",
    ) -> "OracleSequenceCatalogItem":
        return OracleSequenceCatalogItem(
            qualified_identifier=f'"{label}"',
            query_name=f'"{label}"',
            label=label,
            type_label="sq",
            type_name="SEQUENCE",
            connection=connection,
            parent=parent,
            loaded=False,
        )
