# test_node.py

# -*- coding: utf-8 -*-
import pytest
from wenchang.base.node import Node, NodeType

def test_node_init_with_all_params():
    node = Node(
        type=NodeType.CLASS,
        name="TestNode",
        attributes={"docstring": "This is a class"},
        children=[]
    )
    assert node.type == NodeType.CLASS
    assert node.name == "TestNode"
    assert node.docstring == "This is a class"
    assert node.children == []
    assert node.parent is None

def test_node_add_child_sets_parent():
    parent = Node(type=NodeType.CLASS, name="Parent")
    child = Node(type=NodeType.FUNCTION, name="Child")
    parent.add_child(child)
    assert child in parent.children
    assert child.parent == parent

def test_node_init_sets_parents_on_children():
    child1 = Node(type=NodeType.IMPORT, name="os")
    child2 = Node(type=NodeType.COMMENT, attributes={"content": "hi"})
    parent = Node(type=NodeType.MODULE, name="mod", children=[child1, child2])
    assert child1.parent == parent
    assert child2.parent == parent
    assert len(parent.children) == 2

def test_node_dict_contains_type_name_and_attributes():
    node = Node(
        type=NodeType.FUNCTION,
        name="process_data",
        attributes={"return_type": "str", "doc": "test"}
    )
    d = node.dict
    assert d["type"] == "function"
    assert d["name"] == "process_data"
    assert d["attributes"]["return_type"] == "str"
    assert d["attributes"]["doc"] == "test"

def test_node_repr_contains_core_fields():
    node = Node(type=NodeType.IMPORT, name="os")
    rep = repr(node)
    assert "type=import" in rep
    assert "name=os" in rep

def test_node_is_leaf_and_composite_behavior():
    leaf = Node(type=NodeType.IMPORT, name="sys")
    assert leaf.is_leaf is True
    assert leaf.is_composite is False

    parent = Node(type=NodeType.CLASS, name="Cls", children=[leaf])
    assert parent.is_leaf is False
    assert parent.is_composite is True

def test_add_child_multiple():
    parent = Node(type=NodeType.MODULE, name="mod")
    for i in range(3):
        child = Node(type=NodeType.FUNCTION, name=f"f{i}")
        parent.add_child(child)
        assert child.parent == parent
    assert len(parent.children) == 3