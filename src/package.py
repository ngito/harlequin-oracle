from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from harlequin.catalog import CatalogItem, InteractiveCatalogItem
from object import OracleObjectCatalogItem

if TYPE_CHECKING:
    from schema import OracleSchemaCatalogItem
    from connection import OracleHarlequinConnection


class OraclePackageCatalogItem(OracleObjectCatalogItem):
    type_label = "pk"

    @staticmethod
    def from_schema(
        parent: "OracleSchemaCatalogItem",
        label: str,
        connection: "OracleHarlequinConnection",
    ) -> "OraclePackageCatalogItem":
        return OraclePackageCatalogItem(
            qualified_identifier=f'"{label}"',
            query_name=f'"{label}"',
            label=label,
            type_label="pk",
            type_name="PACKAGE",
            connection=connection,
            parent=parent,
            loaded=False,
        )

    def fetch_children(self) -> list[CatalogItem]:
        if self.connection is None:
            return []
        from package_subprogram import OraclePackageSubProgram
        conn = self.connection.conn
        cur = conn.cursor()
        children: list[CatalogItem] = []
        try:
            for row in cur.execute(
                "SELECT name, procedure_name FROM user_procedures "
                "WHERE object_name = :1 AND procedure_name IS NOT NULL "
                "ORDER BY procedure_name",
                [self.label]
            ).fetchall():
                children.append(
                    OraclePackageSubProgram(
                        qualified_identifier=f'"{self.label}"."{row[1]}"',
                        query_name=f'"{self.label}"."{row[1]}"',
                        label=row[1],
                        type_label="sub",
                        type_name="SUBPROGRAM",
                        connection=self.connection,
                        parent=self,
                        loaded=False,
                    )
                )
        except Exception:
            try:
                for row in cur.execute(
                    "SELECT name, procedure_name FROM all_procedures "
                    "WHERE object_name = :1 AND owner = USER "
                    "AND procedure_name IS NOT NULL "
                    "ORDER BY procedure_name",
                    [self.label]
                ).fetchall():
                    children.append(
                        OraclePackageSubProgram(
                            qualified_identifier=f'"{self.label}"."{row[1]}"',
                            query_name=f'"{self.label}"."{row[1]}"',
                            label=row[1],
                            type_label="sub",
                            type_name="SUBPROGRAM",
                            connection=self.connection,
                            parent=self,
                            loaded=False,
                        )
                    )
            except Exception:
                pass
        finally:
            cur.close()
        return children


@dataclass
class OraclePackageSubProgram(InteractiveCatalogItem["OracleHarlequinConnection"]):
    """Nested under OraclePackageCatalogItem."""
    parent: "OraclePackageCatalogItem" | None = None
    INTERACTIONS: ClassVar[list | None] = None

    @staticmethod
    def from_parent(
        parent: "OraclePackageCatalogItem",
        label: str,
        connection: "OracleHarlequinConnection",
    ) -> "OraclePackageSubProgram":
        return OraclePackageSubProgram(
            qualified_identifier=f'"{parent.label}"."{label}"',
            query_name=f'"{parent.label}"."{label}"',
            label=label,
            type_label="sub",
            type_name="SUBPROGRAM",
            connection=connection,
            parent=parent,
            loaded=False,
        )
