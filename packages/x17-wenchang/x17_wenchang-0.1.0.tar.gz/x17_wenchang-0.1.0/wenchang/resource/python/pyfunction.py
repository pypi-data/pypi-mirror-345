# -*- coding: utf-8 -*-
import ast
from typing import Optional, List, Dict, Any, Type, Union

from wenchang.base.nodetype import NodeType
from wenchang.resource.python.pynode import PyNode
from wenchang.resource.python.pyargument import PyArgument
from wenchang.resource.python.pycomment import PyComment
from wenchang.resource.python.pystatement import PyStatement
from wenchang.resource.python.pyimport import PyImport


class PyFunction(PyNode):
    """
    A Python-specific Function Node.
    Supports both `FunctionDef` and `AsyncFunctionDef`, and parses:
    
    """
    @classmethod
    def from_ast(
        cls,
        astnode: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        name: Optional[str] = None,
        source_lines: Optional[List[str]] = None,
        **kwargs,
    ) -> List["PyFunction"]:
        name = astnode.name or name
        start_line = getattr(astnode, "lineno", None)
        end_line = getattr(astnode, "end_lineno", None)
        start_col = getattr(astnode, "col_offset", None)
        end_col = getattr(astnode, "end_col_offset", None)
        if source_lines and start_line and end_line:
            source = cls.get_snippet_from(source_lines, start_line, end_line)
        else:
            source = ''
            
        return_annotation = PyNode.unparse_from(
            getattr(astnode, "returns", None),
        )
        type_comment = PyNode.unparse_from(
            getattr(astnode, "type_comment", None),
        )
        is_async = isinstance(astnode, ast.AsyncFunctionDef)
        decorators = [PyNode.unparse_from(deco) for deco in astnode.decorator_list]
        
        children =[]
        children.extend(
            PyComment.from_ast(
                astnode,
                source_lines=source_lines,
                exclude=[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef],
            )
        )
        children.extend(
            PyArgument.from_ast(astnode.args, source_lines=source_lines)
        )
        for stmt in astnode.body:
            if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                children.extend(
                    PyImport.from_ast(stmt, source_lines=source_lines)
                )
            elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                children.extend(
                    PyFunction.from_ast(stmt, source_lines=source_lines)
                )
            elif isinstance(stmt, ast.ClassDef):
                from wenchang.resource.python.pyclass import PyClass
                children.extend(
                    PyClass.from_ast(stmt, source_lines=source_lines)
                ) 
            else:
                children.extend(
                    PyStatement.from_ast(stmt, source_lines=source_lines)
                )
        
        node = cls(
            astnode=astnode,
            name=name,
            attributes={
                "is_async": is_async,
                "decorators": decorators,
                "type_comment": type_comment,
                "docstring": ast.get_docstring(astnode, clean=True),
                "return_annotation": return_annotation,
                "start_line": start_line,
                "end_line": end_line,
                "start_col": start_col,
                "end_col": end_col,
                "source": source,
            },
            children=children,
        )

        return [node]

    def __init__(
        self,
        astnode: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        name: Optional[str],
        attributes: Optional[Dict[str, Any]] = None,
        children: Optional[List["PyNode"]] = None,
    ):
        super().__init__(
            astnode=astnode,
            name=name,
            type=NodeType.FUNCTION,
            attributes=attributes or {},
            children=children or [],
        )
        self.astnode = astnode
        
    
        
    

        
    