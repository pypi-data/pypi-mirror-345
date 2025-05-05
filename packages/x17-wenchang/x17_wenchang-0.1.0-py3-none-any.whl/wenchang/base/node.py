# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Optional

from wenchang.base.nodetype import NodeType


class Node:
    """
    A generic Node that represents any code structure element.
    In Node Tree, each Node can be either a composite or a leaf node.
    Composite Node can have children (e.g., MODULE, CLASS, FUNCTION)
    Leaf Node cannot have children (e.g., IMPORT, COMMENT, CODEBLOCK, ARGUMENT)
    Node can loop through its children and export itself as a dictionary.

    """
    def __init__(
        self,
        type: NodeType = NodeType.UNKNOWN,
        name: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        children: Optional[List["Node"]] = None,
    ):
        self.type = type
        self.name = name
        self.attributes = attributes or {}
        for key, value in self.attributes.items():
            setattr(self, key, value)

        self.children = []
        self.parent = None
        for child in children or []:
            self.add_child(child)

    # --- Properties ---

    @property
    def is_composite(self) -> bool:
        return True if self.children else False

    @property
    def is_leaf(self) -> bool:
        return not self.is_composite

    # --- Methods ---
    
    def add_child(self, child: "Node") -> None:
        child.add_parent(self)
        self.children.append(child)

    def add_parent(self, parent: "Node") -> None:
        self.parent = parent

    @property
    def dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "name": self.name,
            "attributes": self.attributes,
        }

    def __repr__(self) -> str:
        attributes = []
        for key, value in self.dict.items():
            if isinstance(value, list):
                value = f"[{len(value)}]"
            if value:
                attributes.append(f"{key}={value}")
        return f"{self.__class__.__name__}({', '.join(attributes)})"

