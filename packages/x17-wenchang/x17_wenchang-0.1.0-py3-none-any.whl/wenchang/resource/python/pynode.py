# -*- coding: utf-8 -*-
import ast
from typing import Optional, List, Dict, Any, Tuple, Type, Union

from wenchang.base.node import Node
from wenchang.base.nodetype import NodeType


class PyNode(Node):
    """
    A Python-specific Node extended from base Node.
    Wraps an ast.AST node and builds a tree of PyNode children.
    
    """
    @classmethod
    def from_ast(
        cls,
        astnode: ast.AST,
        type: NodeType = NodeType.UNKNOWN,
        name: Optional[str] = None,
        source_lines: Optional[List[str]] = None,
        exclude: Optional[List[Type[ast.AST]]] = None,
        include: Optional[List[Type[ast.AST]]] = None,
        **kwargs,
    ) -> List["PyNode"]:
        name = name or getattr(astnode, "name", None)
        start_line = getattr(astnode, "lineno", None)
        end_line = getattr(astnode, "end_lineno", None)
        start_col = getattr(astnode, "col_offset", None)
        end_col = getattr(astnode, "end_col_offset", None)
        if source_lines and start_line and end_line:
            source = PyNode.get_snippet_from(source_lines,  start_line, end_line)
        else:
            source = ""
            
        attributes = {
            "asttype": astnode.__class__.__name__,
            "start_line": start_line,
            "end_line": end_line,
            "start_col": start_col,
            "end_col": end_col,
            "source": source,
        }
        node = cls(
            astnode=astnode,
            name=name,
            type=type,
            attributes=attributes,
        )
        for child in cls.list_subnode_ranges_from(
            astnode,
            exclude=exclude,
            include=include,
        ):
            if isinstance(child, ast.AST):
                for child_node in cls.from_ast(astnode=child, source_lines=source_lines):
                    node.add_child(child_node)
        return [node]

    def __init__(
        self,
        astnode: ast.AST,
        type: NodeType = NodeType.UNKNOWN,
        name: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        children: Optional[List["PyNode"]] = None,
    ):
        attributes = attributes or {}
        super().__init__(
            type=type,
            name=name,
            attributes=dict(sorted(attributes.items())),
            children=children or [],
        )
        self.astnode = astnode

    @property
    def code(self) -> str:
        return PyNode.unparse_from(self.astnode) or ""
    
    @property
    def snippet(self) -> str:
        return self.attributes.get("source", "")

    @property
    def range(self) -> tuple[int, int, int, int]:
        start_line = getattr(self.astnode, "lineno", None)
        start_col = getattr(self.astnode, "col_offset", None)
        end_line = getattr(self.astnode, "end_lineno", None)
        end_col = getattr(self.astnode, "end_col_offset", None)
        return start_line, start_col, end_line, end_col

    def export(
        self,
        recursive: bool = True,
        exclude_attributes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        exclude_attributes = exclude_attributes or []
        data = {
            "type": self.type.value,
            "name": self.name,
            "attributes": {
                k: v for k, v in self.attributes.items()
                if k not in exclude_attributes
            },
        }
        if recursive and self.children:
            data["children"] = [
                child.export(
                    recursive=recursive,
                    exclude_attributes=exclude_attributes,
                ) for child in self.children
            ]
        return data

    @staticmethod
    def unparse_from(
        node: ast.AST,
        fallback: Optional[List[str]] = ["id", "name", "value"],
    ) -> Optional[str]:
        if node is None:
            return None
        try:
            return ast.unparse(node)
        except Exception:
            for attr in fallback or []:
                value = getattr(node, attr, None)
                if value is not None:
                    return str(value)
            return None
    
    def unparse(
        self,
        fallback: Optional[List[str]] = ["id", "name", "value"],
    ) -> Optional[str]:
        if self.astnode is None:
            return ''
        else:
            return PyNode.unparse_from(self.astnode, fallback=fallback)

    @staticmethod
    def get_snippet_from(
        source_lines: List[str],
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
    ) -> str:
        if (
            start_line is None or end_line is None
            or start_line <= 0
            or end_line < start_line
            or start_line > len(source_lines)
        ):
            return ""
        else:
            safe_end = min(end_line, len(source_lines))
            code = "\n".join(source_lines[start_line - 1 : safe_end])
            return code
    
    def get_snippet(
        self,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
    ) -> str:
        return PyNode.get_snippet_from(
            source_lines=self.attributes.get("source", "").splitlines(),
            start_line=start_line or self.attributes.get("start_line"),
            end_line=end_line or self.attributes.get("end_line"),
        )
    
    @staticmethod
    def list_child_nodes_from(
        node: ast.AST,
        exclude: Optional[List[Type[ast.AST]]] = None,
        include: Optional[List[Type[ast.AST]]] = None,
    ) -> List[ast.AST]:
        exclude = exclude or []
        include = include or []
        results = []
        for child in ast.iter_child_nodes(node):
            if include and not isinstance(child, tuple(include)):
                continue
            if exclude and isinstance(child, tuple(exclude)):
                continue
            results.append(child)
        return results
    
    def list_child_nodes(
        self,
        exclude: Optional[List[Type[ast.AST]]] = None,
        include: Optional[List[Type[ast.AST]]] = None,
    ) -> List[ast.AST]:
        return self.list_child_nodes_from(self.astnode, exclude=exclude, include=include)
        
    @staticmethod
    def list_field_nodes_from(
        node: ast.AST,
        exclude: Optional[List[Type[ast.AST]]] = None,
        include: Optional[List[Type[ast.AST]]] = None,
    ) -> List[ast.AST]:
        exclude = exclude or []
        include = include or []
        results = []
        for _, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if not isinstance(item, ast.AST):
                        continue
                    if include and not isinstance(item, tuple(include)):
                        continue
                    if exclude and isinstance(item, tuple(exclude)):
                        continue
                    results.append(item)
            elif isinstance(value, ast.AST):
                if include and not isinstance(value, tuple(include)):
                    continue
                if exclude and isinstance(value, tuple(exclude)):
                    continue
                results.append(value)
        return results
        
    def list_field_nodes(
        self,
        exclude: Optional[List[Type[ast.AST]]] = None,
        include: Optional[List[Type[ast.AST]]] = None,
    ) -> List[ast.AST]:
        return self.list_field_nodes_from(
            self.astnode,
            exclude=exclude,
            include=include,
        )

    @staticmethod
    def list_subnodes_from(
        node: ast.AST,
        exclude: Optional[List[Type[ast.AST]]] = None,
        include: Optional[List[Type[ast.AST]]] = None,
    ) -> List[ast.AST]:
        field_nodes = set(PyNode.list_field_nodes_from(node=node, exclude=exclude, include=include))
        child_nodes = set(PyNode.list_child_nodes_from(node=node, exclude=exclude, include=include))
        return list(field_nodes - child_nodes)

    def list_subnodes(
        self,
        exclude: Optional[List[Type[ast.AST]]] = None,
        include: Optional[List[Type[ast.AST]]] = None,
    ) -> List[ast.AST]:
        return self.list_subnodes_from(self.astnode, exclude=exclude, include=include)

    @staticmethod
    def list_child_ranges_from(
        node: ast.AST,
        exclude: Optional[List[Type[ast.AST]]] = None,
        include: Optional[List[Type[ast.AST]]] = None,
    ) -> List[Tuple[int, int]]:
        exclude = exclude or []
        include = include or []
        ranges = []
        for child in PyNode.list_child_nodes_from(node, exclude=exclude, include=include):
            start = getattr(child, "lineno", None)
            end = getattr(child, "end_lineno", None)
            if start and end:
                ranges.append((start, end))
        return ranges

    def list_child_ranges(
        self,
        exclude: Optional[List[Type[ast.AST]]] = None,
        include: Optional[List[Type[ast.AST]]] = None,
    ) -> List[Tuple[int, int]]:
        return self.list_child_ranges_from(self.astnode, exclude=exclude, include=include)
    
    @staticmethod
    def list_field_ranges_from(
        node: ast.AST,
        exclude: Optional[List[Type[ast.AST]]] = None,
        include: Optional[List[Type[ast.AST]]] = None,
    ) -> List[Tuple[int, int]]:
        exclude = exclude or []
        include = include or []
        ranges = []
        for child in PyNode.list_field_nodes_from(node, exclude=exclude, include=include):
            start = getattr(child, "lineno", None)
            end = getattr(child, "end_lineno", None)
            if start and end:
                ranges.append((start, end))
        return ranges
    
    def list_field_ranges(
        self,
        exclude: Optional[List[Type[ast.AST]]] = None,
        include: Optional[List[Type[ast.AST]]] = None,
    ) -> List[Tuple[int, int]]:
        return self.list_field_ranges_from(self.astnode, exclude=exclude, include=include)
    
    @staticmethod
    def list_subnode_ranges_from(
        node: ast.AST,
        exclude: Optional[List[Type[ast.AST]]] = None,
        include: Optional[List[Type[ast.AST]]] = None,
    ) -> List[Tuple[int, int]]:
        field_ranges = set(PyNode.list_field_ranges_from(node=node, exclude=exclude, include=include))
        child_ranges = set(PyNode.list_child_ranges_from(node=node, exclude=exclude, include=include))
        return list(field_ranges - child_ranges)
    
    def list_subnode_ranges(
        self,
        exclude: Optional[List[Type[ast.AST]]] = None,
        include: Optional[List[Type[ast.AST]]] = None,
    ) -> List[Tuple[int, int]]:
        return self.list_subnode_ranges_from(self.astnode, exclude=exclude, include=include)
        
    @staticmethod
    def in_ranges(
        line: int,
        ranges: List[Tuple[int, int]],
    ) -> bool:
        return any(start <= line <= end for start, end in ranges)
    
    def in_child_range(
        self,
        line: int,
    ) -> bool:
        return self.in_ranges(line, self.list_child_ranges())
    
    def in_field_range(
        self,
        line: int,
    ) -> bool:
        return self.in_ranges(line, self.list_field_ranges())
    
    def in_subnode_range(
        self,
        line: int,
    ) -> bool:
        return self.in_ranges(line, self.list_subnode_ranges())
    
    def get_children(
        self,
        nodetype: Optional[Union[NodeType, List[NodeType]]] = None,
        asttype: Optional[Union[Type[ast.AST], List[Type[ast.AST]]]] = None,
    ) -> List["PyNode"]:
        results = self.children or []
        if nodetype is not None:
            nodetypes = [nodetype] if isinstance(nodetype, NodeType) else nodetype
            results = [child for child in results if child.type in nodetypes]

        if asttype is not None:
            asttypes = [asttype] if isinstance(asttype, type) else asttype
            results = [
                child for child in results
                if isinstance(child.astnode, tuple(asttypes))
            ]
        return results
    
    def get_arguments(self) -> List["PyNode"]:
        return self.get_children(nodetype=NodeType.ARGUMENT)
    
    def get_statements(self) -> List["PyNode"]:
        return self.get_children(nodetype=NodeType.STATEMENT)
    
    def get_returns(self) -> List["PyNode"]:
        return self.get_children(asttype=ast.Return)
    
    def get_imports(self) -> List["PyNode"]:
        return self.get_children(nodetype=NodeType.IMPORT)
    
    def get_functions(self) -> List["PyNode"]:
        return self.get_children(nodetype=NodeType.FUNCTION)
    
    def get_classes(self) -> List["PyNode"]:
        return self.get_children(nodetype=NodeType.CLASS)
    
    def get_comments(self) -> List["PyNode"]:
        return self.get_children(nodetype=NodeType.COMMENT)
    
    