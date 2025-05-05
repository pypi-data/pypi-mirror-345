# -*- coding: utf-8 -*-
from typing import Optional, Dict, Any, List
import ast

from wenchang.resource.python.pynode import PyNode
from wenchang.base.nodetype import NodeType

class PyStatement(PyNode):
    """
    A Python-specific CodeBlock Node.
    Captures all AST statement types that are not handled
    by specialized nodes like PyFunction, PyClass, PyImport, PyArgument, or PyComment.
    """
    @classmethod
    def from_ast(
        cls,
        astnode: ast.AST,
        source_lines: Optional[List[str]] = None,
        **kwargs,
    ) -> List["PyStatement"]:
        start_line = getattr(astnode, "lineno", None)
        end_line = getattr(astnode, "end_lineno", None)
        start_col = getattr(astnode, "col_offset", None)
        end_col = getattr(astnode, "end_col_offset", None)

        if source_lines and start_line and end_line:
            source = cls.get_snippet_from(source_lines, start_line, end_line)
        else:
            source = ""

        return [
            cls(
                astnode=astnode,
                name=None,
                attributes={
                    "asttype": astnode.__class__.__name__,
                    "start_line": start_line,
                    "end_line": end_line,
                    "start_col": start_col,
                    "end_col": end_col,
                    "source": source,
                },
            )
        ]

    def __init__(
        self,
        astnode: ast.stmt,
        name: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            astnode=astnode,
            type=NodeType.STATEMENT,
            name=name,
            attributes=attributes or {},
        )
        self.astnode = astnode