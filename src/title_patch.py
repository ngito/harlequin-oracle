# Monkey-patch panel titles to show keyboard shortcut hints.
# Zero changes to Harlequin base code.
from __future__ import annotations

from harlequin.components.data_catalog import DataCatalog
from harlequin.components.code_editor import EditorCollection
from harlequin.components.results_viewer import ResultsViewer

DataCatalog.BORDER_TITLE = "Data Catalog [F6]"
EditorCollection.BORDER_TITLE = "Query Editor [F2]"


def _append_f5(fn):
    """Wrap a method so its border_title assignments get [F5] appended."""
    def wrapped(self, *args, **kwargs):
        fn(self, *args, **kwargs)
        title = self.border_title
        if isinstance(title, str) and not title.endswith(" [F5]"):
            self.border_title = title + " [F5]"
    return wrapped


ResultsViewer.show_loading = _append_f5(ResultsViewer.show_loading)
ResultsViewer.show_table = _append_f5(ResultsViewer.show_table)

_orig_tab_activated = ResultsViewer.on_tabbed_content_tab_activated


def _new_tab_activated(self, message):
    _orig_tab_activated(self, message)
    title = self.border_title
    if isinstance(title, str) and not title.endswith(" [F5]"):
        self.border_title = title + " [F5]"


ResultsViewer.on_tabbed_content_tab_activated = _new_tab_activated
