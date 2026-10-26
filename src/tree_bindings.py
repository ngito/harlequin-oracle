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
from textual.events import Click

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


_group_expanded: ClassVar[bool] = False


def _schedule_schema_expand(tree: DatabaseTree, schema_node: TreeNode) -> None:
    """Queue schema for loading and expand the node."""
    tree._add_to_load_queue(schema_node.data, priority=0)
    schema_node.expand()


def _schedule_group_expand(tree: DatabaseTree, schema_node: TreeNode) -> None:
    """Find Tables group under schema, queue it, and expand."""
    for gchild in schema_node.children:
        if gchild.data and isinstance(gchild.data, CatalogItem):
            if gchild.data.label == "Tables":
                if gchild.data.loaded:
                    gchild.expand()
                    for t in gchild.children:
                        if t.data:
                            tree.move_cursor(t)
                            _group_expanded = True
                            return
                    tree.move_cursor(gchild)
                    _group_expanded = True
                    return
                else:
                    tree._add_to_load_queue(gchild.data, priority=0)
                    gchild.expand()
                    return


def _schedule_auto_expand_groups(self: DatabaseTree) -> None:
    """Poll until schema children are populated, then expand groups."""
    def _tick(tree: DatabaseTree) -> None:
        if _group_expanded:
            return
        for child in tree.root.children:
            if child.data and isinstance(child.data, CatalogItem):
                if child.data.type_name == "schema":
                    if child.children or getattr(child.data, "children", None):
                        _schedule_schema_expand(tree, child)
                        # After schema is queued, schedule group expansion check
                        tree.set_timer(0.3, lambda c=child, t=tree: _schedule_group_expand_if_ready(t, c))
                        return
        tree.set_timer(0.2, lambda t=tree: _tick(t))
    _tick(self)


def _schedule_group_expand_if_ready(tree: DatabaseTree, schema_node: TreeNode) -> None:
    """Check if schema children loaded, then expand Groups."""
    if _group_expanded:
        return
    if schema_node.children or getattr(schema_node.data, "children", None):
        _schedule_group_expand(tree, schema_node)
    else:
        tree.set_timer(0.3, lambda s=schema_node, t=tree: _schedule_group_expand_if_ready(t, s))


_database_tree_watch_catalog = DatabaseTree.watch_catalog


async def _new_watch_catalog(self: DatabaseTree, catalog: CatalogItem | None) -> None:
    global _group_expanded
    _group_expanded = False
    await _database_tree_watch_catalog(self, catalog)
    if catalog is not None:
        self.set_timer(0.05, lambda s=self: _schedule_auto_expand_groups(s))


DatabaseTree.watch_catalog = _new_watch_catalog


# ---------------------------------------------------------------------------
# Type-ahead search on the tree
# ---------------------------------------------------------------------------


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


def _handle_typeahead(self: HarlequinTree, event: events.Key) -> None:
    if not isinstance(event, events.Key):
        return
    key = event.key
    if len(key) == 1 and key.isalnum():
        event.stop()
        HarlequinTree._typeahead_buffer += key
        self._find_and_cursor_to_label_start(HarlequinTree._typeahead_buffer)
    else:
        HarlequinTree._typeahead_buffer = ""


HarlequinTree.on_key = _handle_typeahead
HarlequinTree._is_group_header = _is_group_header
HarlequinTree._find_and_cursor_to_label_start = _find_and_cursor_to_label_start
HarlequinTree._find_first_node_by_label = _find_first_node_by_label
HarlequinTree._typeahead_buffer = ""


def _handle_key_left(self: HarlequinTree, event: events.Key) -> None:
    """Handle left arrow: collapse or move to parent."""
    cursor_node = self.cursor_node
    if cursor_node is not None:
        if cursor_node.is_expanded and cursor_node.allow_expand:
            cursor_node.collapse()
        elif cursor_node.parent is not None:
            self.move_cursor(cursor_node.parent)
        return
    event.stop()


HarlequinTree.key_left = _handle_key_left


# ---------------------------------------------------------------------------
# Page / Home / End navigation
# ---------------------------------------------------------------------------

DatabaseTree.BINDINGS = list(DatabaseTree.BINDINGS) + [
    Binding("pageup", "page_up", "Page Up", show=False),
    Binding("pagedown", "page_down", "Page Down", show=False),
    Binding("home", "scroll_home", "Scroll Home", show=False),
    Binding("end", "scroll_end", "Scroll End", show=False),
    Binding("right", "select_cursor", "Select", show=False),
]

DatabaseTree._merged_bindings = DatabaseTree._merge_bindings()


# ---------------------------------------------------------------------------
# Single-click moves cursor to clicked node
# ---------------------------------------------------------------------------

_database_tree_on_click = HarlequinTree.on_click


async def _new_on_click(self: DatabaseTree, event: Click) -> None:
    await _database_tree_on_click(self, event)
    meta = event.style.meta
    click_line = meta.get("line", None)
    if event.button == 1 and click_line is not None and event.chain != 2:
        node = self.get_node_at_line(click_line)
        if node is not None and node.data is not None:
            self.move_cursor(node)


DatabaseTree.on_click = _new_on_click
