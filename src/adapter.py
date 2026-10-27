from __future__ import annotations

import oracledb
from harlequin import HarlequinAdapter
from harlequin.autocomplete.completion import HarlequinCompletion
from harlequin.catalog import Catalog, InteractiveCatalogItem
from harlequin.exception import HarlequinConnectionError
import os as _os
import os.path as _path

from options import (
    ORACLE_OPTIONS,
    ORACLE_KEYWORDS,
    ORACLE_FUNCTIONS,
)
from connection import OracleHarlequinConnection


class OracleHarlequinAdapter(HarlequinAdapter):

    ADAPTER_OPTIONS = ORACLE_OPTIONS
    IMPLEMENTS_CATALOG_SEARCH = True
    IMPLEMENTS_CANCEL = True
    ADAPTER_DETAILS = "Oracle database adapter using oracledb"
    IMPLEMENTS_VALIDATE_SQL = True

    def __init__(self, conn_str=None, read_only: bool = False, **options):
        self._conn_str = conn_str or []
        self._options = options
        self._conn_info = None
        super().__init__(conn_str, read_only=read_only, **options)

    @property
    def connection_id(self):
        if self._conn_info is None:
            try:
                tns = self._options.get("tns", "")
                host = self._options.get("host", "")
                port = self._options.get("port", "")
                svc = self._options.get("service_name", "")
                user = self._options.get("username", "")
                if tns:
                    self._conn_info = f"{tns}@{user}"
                elif host:
                    self._conn_info = f"{host}:{port}/{svc}@{user}"
                else:
                    self._conn_info = f"{svc}@{user}" if svc else "oracle"
            except Exception:
                self._conn_info = "oracle"
        return self._conn_info

    @staticmethod
    def _parse_tnses():
        """Parse tnsnames.ora and return list of alias names."""
        tns_admin = _os.environ.get("TNS_ADMIN")
        oracle_home = _os.environ.get("ORACLE_HOME", "")
        tns_paths = []
        if tns_admin:
            tns_paths.append(tns_admin)
        if oracle_home:
            tns_paths.append(_path.join(oracle_home, "network", "admin"))

        for tns_dir in tns_paths:
            fpath = _path.join(tns_dir, "tnsnames.ora") if tns_dir else ""
            if tns_dir and _path.isfile(fpath):
                try:
                    with open(fpath) as f:
                        content = f.read()
                    aliases = []
                    in_alias = False
                    current_alias = None
                    for line in content.splitlines():
                        stripped = line.strip()
                        if stripped and not stripped.startswith('#'):
                            if not in_alias and '(' not in stripped and stripped.endswith('='):
                                alias = stripped[:-1].strip()
                                if alias and alias not in aliases and not alias.startswith('('):
                                    aliases.append(alias)
                                    in_alias = True
                                    current_alias = alias
                            elif stripped.startswith(')'):
                                in_alias = False
                                current_alias = None
                    return aliases
                except Exception:
                    continue
        return []

    def _ensure_thick_mode(self, strict: bool = False):
        """Initialize oracledb thick mode. Raises HarlequinConnectionError
        in strict=True mode if thick mode cannot be initialized."""
        try:
            lib_dir = _os.environ.get("ORACLE_CLIENT_LIB")
            if lib_dir is None:
                _oracle_home = _os.environ.get("ORACLE_HOME", "")
                if _oracle_home:
                    lib_dir = _path.join(_oracle_home, "lib")

            config_dir = _os.environ.get("TNS_ADMIN")
            if config_dir is None:
                _oracle_home = _os.environ.get("ORACLE_HOME", "")
                if _oracle_home:
                    config_dir = _path.join(_oracle_home, "network", "admin")

            if lib_dir:
                old_ld = _os.environ.get("LD_LIBRARY_PATH", "")
                if lib_dir not in old_ld:
                    _os.environ["LD_LIBRARY_PATH"] = (
                        f"{lib_dir}:{old_ld}" if old_ld else lib_dir
                    )
                oracledb.init_oracle_client(lib_dir=lib_dir, config_dir=config_dir)
            elif strict:
                raise HarlequinConnectionError(
                    msg=(
                        "TNS alias resolution requires Oracle thick mode (libclntsh).\n\n"
                        "Please set ORACLE_HOME to your Oracle client installation:\n"
                        "  export ORACLE_HOME=/path/to/oracle_home\n\n"
                        "Then run:\n"
                        "  harlequin oracle --tns " + self._options.get("tns", "") + "\n\n"
                        "Alternatively, create ~/.harlequin.toml with explicit host/port:\n\n"
                        "  [profiles.oracle]\n"
                        "  adapter = \"oracle\"\n"
                        "  username = \"scott\"\n"
                        "  password = \"tiger\"\n"
                        "  host = \"db.example.com\"\n"
                        "  port = \"1521\"\n"
                        "  service_name = \"pdb1\""
                    ),
                    title="Could not connect to Oracle"
                )
        except HarlequinConnectionError:
            raise
        except Exception:
            if strict:
                raise HarlequinConnectionError(
                    msg=(
                        "TNS alias resolution requires Oracle thick mode (libclntsh),\n"
                        "but init_oracle_client() failed.\n\n"
                        "Ensure ORACLE_HOME is set and libclntsh is available:\n"
                        "  export ORACLE_HOME=/oracle12cR2/app/oracle/product/19.0.0/dbhome_1\n\n"
                        "Alternatively, create ~/.harlequin.toml with explicit host/port:\n\n"
                        "  [profiles.oracle]\n"
                        "  adapter = \"oracle\"\n"
                        "  username = \"scott\"\n"
                        "  password = \"tiger\"\n"
                        "  host = \"db.example.com\"\n"
                        "  port = \"1521\"\n"
                        "  service_name = \"pdb1\""
                    ),
                    title="Could not connect to Oracle"
                ) from None

    def _get_connection_target(self):
        """Return the TNS alias to use for connection, following priority:
        1. --tns option (explicit)
        2. TWO_TASK env var (auto)
        3. First alias from tnsnames.ora (auto-detect)
        
        Returns (alias, source) tuple or (None, 'none')."""
        tns = self._options.get("tns", "")
        if tns:
            return (tns, "tns_option")
        two_task = _os.environ.get("TWO_TASK", "")
        if two_task:
            return (two_task, "TWO_TASK")
        aliases = self._parse_tnses()
        if aliases:
            return (aliases[0], "tnsnames.ora")
        return (None, "none")

    def connect(self) -> OracleHarlequinConnection:
        try:
            all_options = {**self._options}
            username = all_options.get("username", "")
            password = all_options.get("password", "")

            is_os_auth = username == "os" or (not username and not password)
            auth_kwargs = {"externalauth": True} if is_os_auth else {}

            # --- Resolve connection target ---
            tns, source = self._get_connection_target()

            if tns is None:
                tns_admin = _os.environ.get("TNS_ADMIN")
                oracle_home = _os.environ.get("ORACLE_HOME", "")
                tns_paths = []
                if tns_admin:
                    tns_paths.append(tns_admin)
                if oracle_home:
                    tns_paths.append(_path.join(oracle_home, "network", "admin"))

                tns_found = any(
                    p and _path.isfile(_path.join(p, "tnsnames.ora")) for p in tns_paths
                )

                if tns_found:
                    aliases = self._parse_tnses()
                    alias_list = ", ".join(aliases[:20])
                    if len(aliases) > 20:
                        alias_list += f", ... and {len(aliases) - 20} more"

                    raise HarlequinConnectionError(
                        msg=(
                            f"Auto-detection found no target. Available tnsnames.ora aliases:\n"
                            f"  {alias_list}\n\n"
                            "To connect with a specific alias:\n"
                            "  harlequin oracle --tns mydb\n\n"
                            "Or set the TWO_TASK environment variable:\n"
                            "  export TWO_TASK=mydb\n"
                            "  harlequin oracle\n\n"
                            "Alternatively, create ~/.harlequin.toml:\n\n"
                            "  [profiles.oracle]\n"
                            "  adapter = \"oracle\"\n"
                            "  tns = \"mydb\"\n\n"
                            "# or explicit connection (no tnsnames.ora):\n\n"
                            "  [profiles.oracle]\n"
                            "  adapter = \"oracle\"\n"
                            "  username = \"scott\"\n"
                            "  password = \"tiger\"\n"
                            "  host = \"db.example.com\"\n"
                            "  port = \"1521\"\n"
                            "  service_name = \"pdb1\"\n\n"
                            "# Or if tnsnames.ora exists but thick mode unavailable:\n"
                            "#   export ORACLE_HOME=/path/to/oracle_home\n"
                            "#   harlequin oracle"
                        ),
                        title="Could not connect to Oracle"
                    )
                else:
                    raise HarlequinConnectionError(
                        msg=(
                            "No tnsnames.ora found and no connection target available.\n\n"
                            "Set TWO_TASK or TNS_ADMIN environment variables, or:\n\n"
                            "  harlequin oracle --tns mydb\n\n"
                            "Alternatively, create ~/.harlequin.toml:\n\n"
                            "  [profiles.oracle]\n"
                            "  adapter = \"oracle\"\n"
                            "  tns = \"mydb\"\n\n"
                            "# or explicit connection (no tnsnames.ora):\n\n"
                            "  [profiles.oracle]\n"
                            "  adapter = \"oracle\"\n"
                            "  username = \"scott\"\n"
                            "  password = \"tiger\"\n"
                            "  host = \"db.example.com\"\n"
                            "  port = \"1521\"\n"
                            "  service_name = \"pdb1\""
                        ),
                        title="Could not connect to Oracle"
                    )

            # --- Force thick mode for TNS resolution ---
            self._ensure_thick_mode(strict=True)

            # --- Connect ---
            if username and not is_os_auth:
                conn = oracledb.connect(dsn=tns, user=username, password=password)
            else:
                conn = oracledb.connect(dsn=tns, **auth_kwargs)

            user_display = username if (username and not is_os_auth) else "os"
            init_msg = f"Connected to Oracle {tns} as {user_display} ({source})"
            self._conn_info = f"{tns}@{user_display}"
            return OracleHarlequinConnection(conn, init_message=init_msg)

        except HarlequinConnectionError:
            raise
        except Exception as e:
            raise HarlequinConnectionError(msg=str(e), title="Could not connect to Oracle") from e

    def get_catalog(self, connection):
        catalog = connection.get_catalog()
        for item in catalog.items:
            if isinstance(item, InteractiveCatalogItem):
                item.connection = connection
        return catalog

    def get_completions(self) -> list[HarlequinCompletion]:
        return [
            HarlequinCompletion(
                label=kw,
                type_label="",
                value=kw,
                priority=100,
            )
            for kw in ORACLE_KEYWORDS
        ] + [
            HarlequinCompletion(
                label=fn,
                type_label="func",
                value=fn,
                priority=1000,
                context="function",
            )
            for fn in ORACLE_FUNCTIONS
        ]

    def get_schema(self, connection):
        return None
