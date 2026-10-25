from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from harlequin.catalog import CatalogItem, InteractiveCatalogItem

if TYPE_CHECKING:
    from schema import OracleSchemaCatalogItem
    from connection import OracleHarlequinConnection


@dataclass
class OracleTableGroupItem(InteractiveCatalogItem["OracleHarlequinConnection"]):
    """Group item for tables under a schema."""
    qualified_identifier: str = "Tables"
    query_name: str = "Tables"
    label: str = "Tables"
    type_label: str = "t"
    type_name: str | None = None
    INTERACTIONS = None
    parent: "OracleSchemaCatalogItem" | None = None

    def fetch_children(self) -> list[CatalogItem]:
        from table import OracleTableCatalogItem
        if self.connection is None:
            return []
        conn = self.connection.conn
        cur = conn.cursor()
        children: list[CatalogItem] = []
        try:
            for row in cur.execute(
                "SELECT table_name FROM user_tables ORDER BY table_name"
            ).fetchall():
                children.append(
                    OracleTableCatalogItem.from_schema(
                        self.parent or self, row[0], "TABLE", self.connection
                    )
                )
        except Exception:
            pass
        finally:
            cur.close()
        return children


@dataclass
class OracleViewGroupItem(InteractiveCatalogItem["OracleHarlequinConnection"]):
    """Group item for views under a schema."""
    qualified_identifier: str = "Views"
    query_name: str = "Views"
    label: str = "Views"
    type_label: str = "v"
    type_name: str | None = None
    INTERACTIONS = None
    parent: "OracleSchemaCatalogItem" | None = None

    def fetch_children(self) -> list[CatalogItem]:
        from view import OracleViewCatalogItem
        if self.connection is None:
            return []
        conn = self.connection.conn
        cur = conn.cursor()
        children: list[CatalogItem] = []
        try:
            for row in cur.execute(
                "SELECT view_name FROM user_views ORDER BY view_name"
            ).fetchall():
                children.append(
                    OracleViewCatalogItem.from_schema(
                        self.parent or self, row[0], "VIEW", self.connection
                    )
                )
        except Exception:
            pass
        finally:
            cur.close()
        return children


@dataclass
class OracleFunctionGroupItem(InteractiveCatalogItem["OracleHarlequinConnection"]):
    """Group item for functions under a schema."""
    qualified_identifier: str = "Functions"
    query_name: str = "Functions"
    label: str = "Functions"
    type_label: str = "fn"
    type_name: str | None = None
    INTERACTIONS = None
    parent: "OracleSchemaCatalogItem" | None = None

    def fetch_children(self) -> list[CatalogItem]:
        from function import OracleFunctionCatalogItem
        if self.connection is None:
            return []
        conn = self.connection.conn
        cur = conn.cursor()
        children: list[CatalogItem] = []
        try:
            for row in cur.execute(
                "SELECT object_name FROM user_objects "
                "WHERE object_type = 'FUNCTION' ORDER BY object_name"
            ).fetchall():
                children.append(
                    OracleFunctionCatalogItem.from_schema(
                        self.parent or self, row[0], self.connection
                    )
                )
        except Exception:
            pass
        finally:
            cur.close()
        return children


@dataclass
class OracleProcedureGroupItem(InteractiveCatalogItem["OracleHarlequinConnection"]):
    """Group item for standalone procedures under a schema."""
    qualified_identifier: str = "Procedures"
    query_name: str = "Procedures"
    label: str = "Procedures"
    type_label: str = "pr"
    type_name: str | None = None
    INTERACTIONS = None
    parent: "OracleSchemaCatalogItem" | None = None

    def fetch_children(self) -> list[CatalogItem]:
        from procedure import OracleProcedureCatalogItem
        if self.connection is None:
            return []
        conn = self.connection.conn
        cur = conn.cursor()
        children: list[CatalogItem] = []
        try:
            for row in cur.execute(
                "SELECT object_name FROM user_objects "
                "WHERE object_type = 'PROCEDURE' ORDER BY object_name"
            ).fetchall():
                children.append(
                    OracleProcedureCatalogItem.from_schema(
                        self.parent or self, row[0], self.connection
                    )
                )
        except Exception:
            pass
        finally:
            cur.close()
        return children


@dataclass
class OracleIndexGroupItem(InteractiveCatalogItem["OracleHarlequinConnection"]):
    """Group item for indexes under a schema."""
    qualified_identifier: str = "Indexes"
    query_name: str = "Indexes"
    label: str = "Indexes"
    type_label: str = "ix"
    type_name: str | None = None
    INTERACTIONS = None
    parent: "OracleSchemaCatalogItem" | None = None

    def fetch_children(self) -> list[CatalogItem]:
        from index import OracleIndexCatalogItem
        if self.connection is None:
            return []
        conn = self.connection.conn
        cur = conn.cursor()
        children: list[CatalogItem] = []
        try:
            for row in cur.execute(
                "SELECT index_name FROM user_indexes ORDER BY index_name"
            ).fetchall():
                children.append(
                    OracleIndexCatalogItem.from_schema(
                        self.parent or self, row[0], self.connection
                    )
                )
        except Exception:
            pass
        finally:
            cur.close()
        return children


@dataclass
class OracleSynonymGroupItem(InteractiveCatalogItem["OracleHarlequinConnection"]):
    """Group item for synonyms under a schema."""
    qualified_identifier: str = "Synonyms"
    query_name: str = "Synonyms"
    label: str = "Synonyms"
    type_label: str = "sn"
    type_name: str | None = None
    INTERACTIONS = None
    parent: "OracleSchemaCatalogItem" | None = None

    def fetch_children(self) -> list[CatalogItem]:
        from synonym import OracleSynonymCatalogItem
        if self.connection is None:
            return []
        conn = self.connection.conn
        cur = conn.cursor()
        children: list[CatalogItem] = []
        try:
            for row in cur.execute(
                "SELECT synonym_name FROM user_synonyms ORDER BY synonym_name"
            ).fetchall():
                children.append(
                    OracleSynonymCatalogItem.from_schema(
                        self.parent or self, row[0], self.connection
                    )
                )
        except Exception:
            pass
        finally:
            cur.close()
        return children


@dataclass
class OracleSequenceGroupItem(InteractiveCatalogItem["OracleHarlequinConnection"]):
    """Group item for sequences under a schema."""
    qualified_identifier: str = "Sequences"
    query_name: str = "Sequences"
    label: str = "Sequences"
    type_label: str = "sq"
    type_name: str | None = None
    INTERACTIONS = None
    parent: "OracleSchemaCatalogItem" | None = None

    def fetch_children(self) -> list[CatalogItem]:
        from sequence import OracleSequenceCatalogItem
        if self.connection is None:
            return []
        conn = self.connection.conn
        cur = conn.cursor()
        children: list[CatalogItem] = []
        try:
            for row in cur.execute(
                "SELECT sequence_name FROM user_sequences ORDER BY sequence_name"
            ).fetchall():
                children.append(
                    OracleSequenceCatalogItem.from_schema(
                        self.parent or self, row[0], self.connection
                    )
                )
        except Exception:
            pass
        finally:
            cur.close()
        return children


@dataclass
class OraclePackageGroupItem(InteractiveCatalogItem["OracleHarlequinConnection"]):
    """Group item for packages under a schema."""
    qualified_identifier: str = "Packages"
    query_name: str = "Packages"
    label: str = "Packages"
    type_label: str = "pk"
    type_name: str | None = None
    INTERACTIONS = None
    parent: "OracleSchemaCatalogItem" | None = None

    def fetch_children(self) -> list[CatalogItem]:
        from package import OraclePackageCatalogItem
        if self.connection is None:
            return []
        conn = self.connection.conn
        cur = conn.cursor()
        children: list[CatalogItem] = []
        try:
            for row in cur.execute(
                "SELECT object_name FROM user_objects "
                "WHERE object_type = 'PACKAGE' ORDER BY object_name"
            ).fetchall():
                children.append(
                    OraclePackageCatalogItem.from_schema(
                        self.parent or self, row[0], self.connection
                    )
                )
        except Exception:
            pass
        finally:
            cur.close()
        return children
