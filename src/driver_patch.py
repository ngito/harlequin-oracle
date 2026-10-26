# Monkey-patch HarlequinDriver to add run_query() for direct query execution.
# Uses Harlequin's message handling infrastructure (not _on_message monkey-patch).
from __future__ import annotations

from textual.message import Message
from harlequin.app import QuerySubmitted


class RunQuery(Message):
    """Message for executing a query directly from a catalog interaction."""
    def __init__(self, query: str, title: str = "Preview") -> None:
        super().__init__()
        self.query = query
        self.title = title


def _patch_driver(drv_cls):
    def run_query(self, query: str, title: str = "Preview") -> None:
        """Execute a query directly and show results in the query results panel."""
        self.app.post_message(RunQuery(query=query, title=title))
    drv_cls.run_query = run_query


def _patch_harlequin_app(app_cls):
    """Register a RunQuery handler on the Harlequin app via _decorated_handlers."""
    async def _handle_run_query(self, message: RunQuery) -> None:
        if self.connection is None:
            return
        self.full_screen = False
        self.run_query_bar.set_not_responsive()
        self.results_viewer.show_loading()
        self.post_message(QuerySubmitted(queries=[message.query], limit=500))
    
    # Register via the @on decorator mechanism
    handlers = app_cls.__dict__.get("_decorated_handlers", {})
    if handlers is None:
        handlers = {}
    handlers.setdefault(RunQuery, []).append((_handle_run_query, ()))
    app_cls._decorated_handlers = handlers


# Apply patches
from harlequin.driver import HarlequinDriver
from harlequin.app import Harlequin

_patch_driver(HarlequinDriver)
_patch_harlequin_app(Harlequin)
