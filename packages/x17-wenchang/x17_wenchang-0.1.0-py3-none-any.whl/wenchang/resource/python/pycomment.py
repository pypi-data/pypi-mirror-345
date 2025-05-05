# -*- coding: utf-8 -*-
from typing import Optional, Dict, Any, List, Union, Type, Tuple
import ast
import tokenize
from io import StringIO

from wenchang.resource.python.pynode import PyNode
from wenchang.base.nodetype import NodeType

class PyComment(PyNode):
    """
    Python-specific Comment node.
    Supports both `ast-comments` and `tokenize` extraction.
    
    """
    @classmethod
    def from_ast(
        cls,
        astnode: ast.AST,
        source_lines: Optional[List[str]] = None,
        exclude: Optional[List[Type[ast.AST]]] = [],
        include: Optional[List[Type[ast.AST]]] = [],
        **kwargs,
    ) -> List["PyComment"]:
        if not source_lines: 
            return []
        
        start_line = getattr(astnode, "lineno", 1)
        end_line = getattr(astnode, "end_lineno", len(source_lines))
        
        # 反转视角：我们关心的是被“子节点占据”的范围（即 should include into exclusion）
        internal_include = exclude or []
        internal_exclude = include or []
        child_ranges = PyNode.list_field_ranges_from(
            astnode,
            include=internal_include,
            exclude=internal_exclude,
        )
        return cls.from_lines(
            source_lines, 
            (start_line, end_line), 
            child_ranges=child_ranges,
        )
    
    @classmethod
    def from_lines(
        cls,
        lines: List[str],
        line_range: Tuple[int, int],
        child_ranges: Optional[List[Tuple[int, int]]] = None,
        check: bool = False,
    ) -> List["PyComment"]:
        comments = []
        start_line, end_line = line_range
        snippet = "\n".join(lines[start_line - 1:end_line])
        
        try:
            tokens = tokenize.generate_tokens(StringIO(snippet).readline)
        except tokenize.TokenError as e:
            if check:
                raise ValueError(f"Tokenization error: {e}")
            else:
                return []
        
        for token in tokens:
            if token.type != tokenize.COMMENT:
                continue
            abs_line = start_line + token.start[0] - 1
            if child_ranges and PyNode.in_ranges(abs_line, child_ranges):
                continue
            comments.append(
                cls(
                    name=None,
                    attributes={
                        "asttype": "Comment",
                        "content": token.string.lstrip("# ").rstrip(),
                        "start_line": abs_line,
                        "end_line": abs_line,
                        "start_col": token.start[1],
                        "end_col": token.end[1],
                        "source": lines[abs_line - 1].strip(),
                    },
                )
            )
        
        return comments
    
    
    
    # @classmethod
    # def from_ast(
    #     cls,
    #     astnode: ast.AST,
    #     source_lines: Optional[List[str]] = None,
    #     exclude: Optional[List[Union[ast.AST]]] = [ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef],
    #     include: Optional[List[Union[ast.AST]]] = [],
    #     **kwargs,
    # ) -> List["PyComment"]:
    #     if not source_lines:
    #         return []
    
    #     if isinstance(astnode, ast.Module):
    #         start_line = 1
    #         end_line = len(source_lines)
    #     else:
    #         start_line = getattr(astnode, "lineno", None)
    #         end_line = getattr(astnode, "end_lineno", None)
            
    #     if not start_line or not end_line:
    #         return []
        
    #     comments = []
    #     child_ranges = PyNode.get_child_ranges(
    #         astnode,
    #         exclude = exclude,
    #         include = include,
    #     )
    #     full_snippet = cls.extract_snippet(source_lines, start_line, end_line)
    #     tokens = tokenize.generate_tokens(StringIO(full_snippet).readline)
    #     for token in tokens:
    #         if token.type != tokenize.COMMENT: 
    #             continue
            
    #         rel_line = token.start[0]
    #         abs_line = start_line + rel_line - 1
    #         if PyNode.in_child_ranges(abs_line, child_ranges): 
    #             continue
            
    #         comment_text = PyNode.extract_snippet(
    #             source_lines,
    #             start_line=abs_line,
    #             end_line=abs_line,
    #         )
    #         comments.append(
    #             cls(
    #                 attributes={
    #                     "asttype": "Comment",
    #                     "token_type": token.type,
    #                     "content": token.string.lstrip("# ").rstrip(),
    #                     "start_line": abs_line,
    #                     "end_line": abs_line,
    #                     "start_col": token.start[1],
    #                     "end_col": token.end[1],
    #                     "source": comment_text,
    #                 }
    #             )
    #         )
    #     return comments

    def __init__(
        self,
        name: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            astnode=None,
            type=NodeType.COMMENT,
            name=name,
            attributes=attributes or {},
        )
        self.astnode = None
    
    