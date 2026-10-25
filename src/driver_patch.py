# Monkey-patch HarlequinDriver to add run_query() for direct query execution
# and patch Harlequin app to handle the RunQuery message.
from __future__ import annotations

from textual.message import Message

from harlequin.app import QuerySubmitted


class _RunQuery(Message):
    """Message for executing a query directly from a catalog interaction."""
    def __init__(self, query: str, title: str = "Preview") -> None:
        super().__init__()
        self.query = query
        self.title = title


def _patch_driver(drv_cls):
    def run_query(self, query: str, title: str = "Preview") -> None:
        """Execute a query directly and show results in the query results panel."""
        self.app.post_message(_RunQuery(query=query, title=title))
    drv_cls.run_query = run_query


def _patch_harlequin_app(app_cls):
    """Register a handler for _RunQuery on the Harlequin app by patching _on_message."""
    _orig_on_message = app_cls._on_message

    async def _patched_on_message(self, message: Message) -> None:
        if isinstance(message, _RunQuery):
            if self.connection is None:
                return
            self.full_screen = False
            self.run_query_bar.set_not_responsive()
            self.results_viewer.show_loading()
            self.post_message(QuerySubmitted(queries=[message.query], limit=500))
            return
        await _orig_on_message(self, message)

    app_cls._on_message = _patched_on_message


# Apply patches
from harlequin.driver import HarlequinDriver
from harlequin.app import Harlequin

_patch_driver(HarlequinDriver)
_patch_harlequin_app(Harlequin)
