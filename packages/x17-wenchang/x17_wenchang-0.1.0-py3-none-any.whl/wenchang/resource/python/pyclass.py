# -*- coding: utf-8 -*-
import ast
from typing import Optional, List, Dict, Any, Type, Union

from wenchang.base.nodetype import NodeType
from wenchang.resource.python.pynode import PyNode
from wenchang.resource.python.pyfunction import PyFunction
from wenchang.resource.python.pycomment import PyComment
from wenchang.resource.python.pystatement import PyStatement
from wenchang.resource.python.pyimport import PyImport


class PyClass(PyNode):
    """
    A Python-specific Class Node.
    Supports `ClassDef`, and extracts:
    
    """
    @classmethod
    def from_ast(
        cls,
        astnode: ast.ClassDef,
        name: Optional[str] = None,
        source_lines: Optional[List[str]] = None,
        **kwargs,
    ) -> List["PyClass"]:
        name = astnode.name or name
        start_line = getattr(astnode, "lineno", None)
        end_line = getattr(astnode, "end_lineno", None)
        start_col = getattr(astnode, "col_offset", None)
        end_col = getattr(astnode, "end_col_offset", None)
        if source_lines and start_line and end_line:
            source = cls.get_snippet_from(source_lines, start_line, end_line)
        else:
            source = ''

        decorators = [PyNode.unparse_from(deco) for deco in astnode.decorator_list]
        bases = [PyNode.unparse_from(base) for base in astnode.bases]
        keywords = {
            k.arg: PyNode.unparse_from(k.value)
            for k in astnode.keywords if k.arg is not None
        }
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
                    "decorators": decorators,
                    "bases": bases,
                    "keywords": keywords,
                    "docstring": ast.get_docstring(astnode, clean=True),
                    "start_line": start_line,
                    "end_line": end_line,
                    "start_col": start_col,
                    "end_col": end_col,
                    "source": source,
                },
                children=children,
            )
        ]

    def __init__(
        self,
        astnode: ast.ClassDef,
        name: Optional[str],
        attributes: Optional[Dict[str, Any]] = None,
        children: Optional[List["PyNode"]] = None,
    ):
        super().__init__(
            astnode=astnode,
            name=name,
            type=NodeType.CLASS,
            attributes=attributes or {},
            children=children or [],
        )
        self.astnode = astnode
        
    def get_init_function(self) -> Optional[PyFunction]:
        for function in self.get_functions():
            if function.name == "__init__":
                return function
        return None
    