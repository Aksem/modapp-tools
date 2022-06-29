from __future__ import annotations

from typing import Sequence

from .visitor import Visitor


class CstNode:
    def visit(self, visitor: Visitor) -> CstNode:
        # visit self
        should_visit_children = visitor.on_visit(self)

        if should_visit_children:
            for child in self.children:
                child.visit(visitor)

        leave_result = visitor.on_leave(self)
        # TODO: validate return type
        return leave_result

    @property
    def children(self) -> Sequence[CstNode]:
        return []
