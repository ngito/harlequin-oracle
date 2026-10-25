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
                host = self._options.get("host", "")
                port = self._options.get("port", "")
                svc = self._options.get("service_name", "")
                user = self._options.get("username", "")
                self._conn_info = f"{host}:{port}/{svc}@{user}" if host else f"{svc}@{user}"
            except Exception:
                self._conn_info = "oracle"
        return self._conn_info

    def connect(self) -> OracleHarlequinConnection:
        try:
            all_options = {**self._options}
            username = all_options.get("username", "")
            password = all_options.get("password", "")
            service_name = all_options.get("service_name", "")

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
            except Exception:
                pass

            if username == "os" or (not username and not password):
                auth_kwargs = (
                    {"auth_mode": oracledb.AUTH_MODE_OS}
                    if hasattr(oracledb, 'AUTH_MODE_OS')
                    else {}
                )
                conn = oracledb.connect(service_name=service_name, **auth_kwargs)
            else:
                host = all_options.get("host", "localhost")
                port = all_options.get("port", "1521")
                dsn = oracledb.makedsn(host, port, service_name=service_name)
                conn = oracledb.connect(user=username, password=password, dsn=dsn)

            if username == "os" or (not username and not password):
                init_msg = f"Connected to Oracle {service_name} as OS authenticated user"
            else:
                host = all_options.get("host", "")
                port = all_options.get("port", "")
                init_msg = f"Connected to Oracle {host}:{port}/{service_name} as {username}"

            conn_obj = OracleHarlequinConnection(conn, init_message=init_msg)
            return conn_obj
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
