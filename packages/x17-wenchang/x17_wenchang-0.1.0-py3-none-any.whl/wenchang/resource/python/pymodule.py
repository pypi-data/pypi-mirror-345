# -*- coding: utf-8 -*-
import ast
from typing import Optional, List, Dict, Any

from wenchang.base.nodetype import NodeType
from wenchang.resource.python.pynode import PyNode
from wenchang.resource.python.pyclass import PyClass
from wenchang.resource.python.pyfunction import PyFunction
from wenchang.resource.python.pyimport import PyImport
from wenchang.resource.python.pycomment import PyComment
from wenchang.resource.python.pystatement import PyStatement


class PyModule(PyNode):
    """
    A Python-specific Module Node.
    Represents the root of a Python file, handling:
    - Module-level docstring and comments
    - Top-level imports, classes, functions, and statements
    """

    @classmethod
    def from_ast(
        cls,
        astnode: ast.Module,
        name: Optional[str] = None,
        source_lines: Optional[List[str]] = None,
    ) -> List["PyModule"]:
        docstring = ast.get_docstring(astnode, clean=True)
        source = "\n".join(source_lines).strip() if source_lines else ""
        children = []
        children.extend(
            PyComment.from_ast(astnode, source_lines=source_lines),
        )
        for stmt in astnode.body:
            if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                children.extend(
                    PyImport.from_ast(stmt, source_lines=source_lines),
                )
            elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                children.extend(
                    PyFunction.from_ast(stmt, source_lines=source_lines),
                )
            elif isinstance(stmt, ast.ClassDef):
                children.extend(
                    PyClass.from_ast(stmt, source_lines=source_lines),
                )
            else:
                children.extend(
                    PyStatement.from_ast(stmt, source_lines=source_lines),
                )
        return [
            cls(
                astnode=astnode,
                name=name,
                attributes={
                    "docstring": docstring,
                    "source": source,
                },
                children=children,
            )
        ]

    def __init__(
        self,
        astnode: ast.Module,
        name: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        children: Optional[List["PyNode"]] = None,
    ):
        super().__init__(
            astnode=astnode,
            name=name,
            type=NodeType.MODULE,
            attributes=attributes or {},
            children=children or [],
        )
        self.astnode = astnode
    
    