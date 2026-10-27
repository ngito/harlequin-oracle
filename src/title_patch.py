# Monkey-patch panel titles to show keyboard shortcut hints.
# Zero changes to Harlequin base code.
from __future__ import annotations

from harlequin.components.data_catalog import DataCatalog
from harlequin.components.code_editor import EditorCollection
from harlequin.components.results_viewer import ResultsViewer

DataCatalog.BORDER_TITLE = "Data Catalog (F6)"
EditorCollection.BORDER_TITLE = "Query Editor (F2)"


# Harlequin.app imports DataCatalog/EditorCollection at module load time,
# so class-attr patching happens before the widget instances are created.
# However, the Harlequin IDE also creates a Lazy editor_placeholder widget
# and assigns its border_title from editor_collection.border_title.  We
# patch the Harlequin compose method to ensure the shortcut hints appear
# on the placeholder too.
_harlequin_app_patch = None


def _patch_harlequin_app():
    """Monkey-patch the Harlequin app to add shortcut hints to panel titles."""
    global _harlequin_app_patch
    if _harlequin_app_patch:
        return
    try:
        from harlequin.app import Harlequin
    except ImportError:
        return

    _orig_compose = Harlequin.compose

    def _patched_compose(self):
        yield from _orig_compose(self)
        # Set border titles on widget instances after they are created.
        # Class-attr patching happens at import time (before instances
        # exist), but Textual's Widget.__init__ copies BORDER_TITLE into
        # the instance's border_title reactive at construction.  Setting
        # the instance attribute after compose ensures the value is
        # updated.
        if hasattr(self, "data_catalog"):
            self.data_catalog.border_title = "Data Catalog (F6)"
        if hasattr(self, "editor_collection"):
            self.editor_collection.border_title = "Query Editor (F2)"
        if hasattr(self, "editor") and self.editor is not None:
            self.editor.border_title = self.editor_collection.border_title

    Harlequin.compose = _patched_compose
    _harlequin_app_patch = True


def _append_f5(fn):
    """Wrap a method so its border_title assignments get (F5) appended."""
    def wrapped(self, *args, **kwargs):
        fn(self, *args, **kwargs)
        title = self.border_title
        if isinstance(title, str) and not title.endswith(" (F5)"):
            self.border_title = title + " (F5)"
    return wrapped


ResultsViewer.show_loading = _append_f5(ResultsViewer.show_loading)
ResultsViewer.show_table = _append_f5(ResultsViewer.show_table)

_orig_tab_activated = ResultsViewer.on_tabbed_content_tab_activated


def _new_tab_activated(self, message):
    _orig_tab_activated(self, message)
    title = self.border_title
    if isinstance(title, str) and not title.endswith(" (F5)"):
        self.border_title = title + " (F5)"


ResultsViewer.on_tabbed_content_tab_activated = _new_tab_activated

# Run the app-level patch (safe to call even if Harlequin isn't loaded yet)
_patch_harlequin_app()
