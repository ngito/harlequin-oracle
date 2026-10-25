# Monkey-patch Harlequin's DatabaseTree to add navigation key bindings.
# DatabaseTree has inherit_bindings=False, so it needs its own BINDINGS class
# attribute for Textual's binding system to pick them up. We extend the existing
# bindings from HarlequinTree (which already has cursor_up/down, enter, space, etc.)
# and add page_up, page_down, home, end, and type-ahead search.
#
# Textual caches _merged_bindings at class creation time (in __new__). Since
# DatabaseTree has inherit_bindings=False, _merged_bindings was computed as an
# empty map. We must recompute it after assigning a new BINDINGS list.

from __future__ import annotations

from typing import ClassVar

from textual import events, on
from textual.binding import Binding
from textual.widgets._tree import TreeNode

from harlequin.catalog import CatalogItem, InteractiveCatalogItem
from harlequin.components.data_catalog.database_tree import DatabaseTree
from harlequin.components.data_catalog.tree import HarlequinTree


# ---------------------------------------------------------------------------
# Auto-expand group headers & highlight Tables on first catalog load
# ---------------------------------------------------------------------------

_EXPANDED_GROUP_NAMES = {
    "Tables", "Views", "Functions", "Procedures",
    "Indexes", "Synonyms", "Sequences", "Packages",
}


def _auto_expand_groups(self: DatabaseTree, catalog_items: list[CatalogItem]) -> None:
    """Expand group-header children and highlight the Tables group."""
    if self.cursor_line >= 0:
        return  # already expanded something
    for child in self.root.children:
        data = child.data
        if data and isinstance(data, CatalogItem):
            if data.label in _EXPANDED_GROUP_NAMES:
                child.expand()
                if data.label == "Tables":
                    for gchild in child.children:
                        if gchild.data:
                            self.move_cursor(gchild)
                            break
                break


_database_tree_watch_catalog = DatabaseTree.watch_catalog


async def _new_watch_catalog(self: DatabaseTree, catalog: CatalogItem | None) -> None:
    await _database_tree_watch_catalog(self, catalog)
    if catalog is not None and self.root.children:
        self.set_timer(0.1, lambda: _auto_expand_groups(self, catalog.items))


DatabaseTree.watch_catalog = _new_watch_catalog


# ---------------------------------------------------------------------------
# Type-ahead search on the tree
# ---------------------------------------------------------------------------

HarlequinTree._typeahead_buffer: ClassVar[str] = ""


def _typeahead_on_key(self: HarlequinTree, event: events.Key) -> None:
    if isinstance(event, events.Key):
        key = event.key
        if len(key) == 1 and key.isalnum():
            event.stop()
            HarlequinTree._typeahead_buffer = (
                HarlequinTree._typeahead_buffer + key
            ).lower()
            self._find_and_cursor_to_label_start(HarlequinTree._typeahead_buffer)
            return
        else:
            HarlequinTree._typeahead_buffer = ""


def _find_and_cursor_to_label_start(self: HarlequinTree, label_prefix: str) -> None:
    def _walk(node: TreeNode) -> bool:
        if node.data and isinstance(node.data, CatalogItem):
            lbl = node.data.label.lower()
            if lbl.startswith(label_prefix) and not self._is_group_header(node):
                self.move_cursor(node)
                return True
        if node.is_expanded:
            for child in node.children:
                if _walk(child):
                    return True
        return False

    if label_prefix and len(label_prefix) == 1:
        if self._find_first_node_by_label(label_prefix):
            return

    _walk(self.root)


def _is_group_header(self: HarlequinTree, node: TreeNode) -> bool:
    data = node.data
    if data is None:
        return False
    if not isinstance(data, CatalogItem):
        return False
    if data.type_name is None and data.label in (
        "Tables", "Views", "Functions", "Procedures",
        "Indexes", "Synonyms", "Sequences", "Packages",
    ):
        return True
    return False


def _find_first_node_by_label(self: HarlequinTree, first_char: str) -> bool:
    """Find the first node whose label starts with first_char."""
    def _walk(node: TreeNode) -> bool:
        if node.data and isinstance(node.data, CatalogItem):
            lbl = node.data.label.lower()
            if lbl.startswith(first_char) and not _is_group_header(self, node):
                self.move_cursor(node)
                return True
        if node.is_expanded:
            for child in node.children:
                if _walk(child):
                    return True
        return False
    return _walk(self.root)


HarlequinTree.on_key = _typeahead_on_key
HarlequinTree._is_group_header = _is_group_header
HarlequinTree._find_and_cursor_to_label_start = _find_and_cursor_to_label_start
HarlequinTree._find_first_node_by_label = _find_first_node_by_label


# ---------------------------------------------------------------------------
# Page / Home / End navigation
# ---------------------------------------------------------------------------

DatabaseTree.BINDINGS = list(DatabaseTree.BINDINGS) + [
    Binding("pageup", "page_up", "Page Up", show=False),
    Binding("pagedown", "page_down", "Page Down", show=False),
    Binding("home", "scroll_home", "Scroll Home", show=False),
    Binding("end", "scroll_end", "Scroll End", show=False),
]

DatabaseTree._merged_bindings = DatabaseTree._merge_bindings()
