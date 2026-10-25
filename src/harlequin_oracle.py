# Re-export everything from the src/ flat layout so that
# `import harlequin_oracle` still works (entry point compat)
#
import tree_bindings  # noqa: F401 - monkey-patches catalog tree navigation
import driver_patch  # noqa: F401 - monkey-patches driver run_query for preview

from options import (
    username,
    password,
    host,
    port,
    service_name,
    ORACLE_OPTIONS,
    ORACLE_KEYWORDS,
    ORACLE_FUNCTIONS,
)
from cursor import OracleHarlequinCursor
from connection import OracleHarlequinConnection
from adapter import OracleHarlequinAdapter
from schema import OracleSchemaCatalogItem, InteractiveCatalogItem
from table import OracleTableCatalogItem
from view import OracleViewCatalogItem
from column import OracleColumnCatalogItem
from function import OracleFunctionCatalogItem
from procedure import OracleProcedureCatalogItem
from package import OraclePackageCatalogItem, OraclePackageSubProgram
from index import OracleIndexCatalogItem
from synonym import OracleSynonymCatalogItem
from sequence import OracleSequenceCatalogItem
from catalog_groups import (
    OracleTableGroupItem,
    OracleViewGroupItem,
    OracleFunctionGroupItem,
    OracleProcedureGroupItem,
    OracleIndexGroupItem,
    OracleSynonymGroupItem,
    OracleSequenceGroupItem,
    OraclePackageGroupItem,
)

# Configure INTERACTIONS after everything is loaded
import interactions
interactions.configure_interactions({
    "OracleRelationCatalogItem": OracleTableCatalogItem.__bases__[0],
    "OracleTableCatalogItem": OracleTableCatalogItem,
    "OracleViewCatalogItem": OracleViewCatalogItem,
    "OracleFunctionCatalogItem": OracleFunctionCatalogItem,
    "OracleProcedureCatalogItem": OracleProcedureCatalogItem,
    "OraclePackageCatalogItem": OraclePackageCatalogItem,
    "OraclePackageSubProgram": OraclePackageSubProgram,
    "OracleIndexCatalogItem": OracleIndexCatalogItem,
    "OracleSynonymCatalogItem": OracleSynonymCatalogItem,
    "OracleSequenceCatalogItem": OracleSequenceCatalogItem,
})
