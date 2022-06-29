from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cst import CstNode


class Visitor:
    def on_visit(self, node: CstNode) -> bool:
        visit_func = getattr(self, f"visit_{type(node).__name__}", None)
        if visit_func is not None:
            retval = visit_func(node)
        else:
            retval = True
        # Don't visit children IFF the visit function returned False.
        return False if retval is False else True

    def on_leave(self, original_node: CstNode) -> CstNode:
        leave_func = getattr(self, f"leave_{type(original_node).__name__}", None)
        if leave_func is not None:
            leave_func(original_node)
        return original_node

    # TODO: on_visit_attribute
    # TODO: on_leave_attribute
