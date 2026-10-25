from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from harlequin.catalog import CatalogItem, InteractiveCatalogItem

if TYPE_CHECKING:
    from schema import OracleSchemaCatalogItem
    from connection import OracleHarlequinConnection


@dataclass
class OracleObjectCatalogItem(InteractiveCatalogItem["OracleHarlequinConnection"]):
    """Base for functions, procedures, packages, indexes, synonyms, sequences."""
    parent: "OracleSchemaCatalogItem" | None = None
    INTERACTIONS: ClassVar[list | None] = None

    @staticmethod
    def from_schema(
        parent: "OracleSchemaCatalogItem",
        label: str,
        connection: "OracleHarlequinConnection",
    ) -> "OracleObjectCatalogItem":
        return OracleObjectCatalogItem(
            qualified_identifier=f'"{label}"',
            query_name=f'"{label}"',
            label=label,
            type_label="?",
            type_name=None,
            connection=connection,
            parent=parent,
            loaded=False,
        )
