# -*- coding: utf-8 -*-
from typing import List, Optional, Dict, Any, Union
import ast

from wenchang.resource.python.pynode import PyNode
from wenchang.base.nodetype import NodeType

class PyImport(PyNode):
    """
    A Python-specific Import Node. 
    Extends the generic Import particle,
    adding parsing capability from AST, 
    and collects detailed information.
    
    """
    @classmethod
    def from_ast(
        cls, 
        astnode: ast.ImportFrom | ast.Import,
        name: Optional[str] = None,
        source_lines: Optional[List[str]] = None,
        **kwargs,
    ) -> List["PyImport"]:
        imports = []
        module = getattr(astnode, "module", None)
        level = getattr(astnode, "level", None)
        start_line = getattr(astnode, "lineno", None)
        end_line = getattr(astnode, "end_lineno", None)
        start_col = getattr(astnode, "col_offset", None)
        end_col = getattr(astnode, "end_col_offset", None)
        if source_lines and start_line and end_line:
            source = cls.get_snippet_from(source_lines, start_line, end_line)
        else:
            source = ''
        
        for subnode in getattr(astnode, "names", []):
            subname = getattr(subnode, "name", name)
            alias = getattr(subnode, "asname", None)
            imports.append(
                PyImport(
                    astnode = astnode,
                    name = subname or getattr(astnode, "name", None) or name,
                    attributes={
                        "asttype": astnode.__class__.__name__,
                        "alias": alias,
                        "module": module,
                        "level": level,
                        "source": source,
                        "start_line": start_line,
                        "end_line": end_line,
                        "start_col": start_col,
                        "end_col": end_col,
                    },
                )
            )
        return imports
    
    def __init__(
        self,
        astnode: ast.ImportFrom | ast.Import,
        name: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = {},
    ):
        super().__init__(
            astnode=astnode,
            type=NodeType.IMPORT,
            name=name,
            attributes=attributes,
        )
        self.astnode = astnode
    