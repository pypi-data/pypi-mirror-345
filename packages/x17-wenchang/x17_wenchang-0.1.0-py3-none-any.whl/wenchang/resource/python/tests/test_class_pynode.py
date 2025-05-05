# test_pynode_all.py

import ast
import pytest
from wenchang.resource.python.pynode import PyNode

SAMPLE_CODE = """
@decorator
def foo(x: int, y):
    z = x + y
    return z

class Bar:
    def method(self):
        pass
"""

tree = ast.parse(SAMPLE_CODE)
func_node = tree.body[0]
class_node = tree.body[1]

def test_from_ast():
    nodes = PyNode.from_ast(func_node, source_lines=SAMPLE_CODE.splitlines())
    assert isinstance(nodes, list)
    assert isinstance(nodes[0], PyNode)
    assert nodes[0].attributes["asttype"] == "FunctionDef"

def test_code_and_snippet():
    node = PyNode(astnode=func_node)
    assert isinstance(node.code, str)
    assert isinstance(node.snippet, str)

def test_range_property():
    node = PyNode(astnode=func_node)
    r = node.range
    assert isinstance(r, tuple)
    assert len(r) == 4

def test_export():
    node = PyNode(astnode=func_node)
    result = node.export()
    assert isinstance(result, dict)
    assert "type" in result
    assert "attributes" in result

def test_unparse_methods():
    node = PyNode(astnode=func_node)
    assert isinstance(node.unparse(), str)
    assert isinstance(PyNode.unparse_from(func_node), str)

def test_get_snippet_methods():
    lines = SAMPLE_CODE.splitlines()
    snippet = PyNode.get_snippet_from(lines, 2, 4)
    assert isinstance(snippet, str)
    node = PyNode(astnode=func_node)
    assert isinstance(node.get_snippet(), str)

def test_list_node_methods():
    node = PyNode(astnode=func_node)
    assert isinstance(node.list_child_nodes(), list)
    assert isinstance(node.list_field_nodes(), list)
    assert isinstance(node.list_subnodes(), list)

def test_list_range_methods():
    node = PyNode(astnode=func_node)
    assert all(isinstance(r, tuple) and len(r) == 2 for r in node.list_child_ranges())
    assert all(isinstance(r, tuple) and len(r) == 2 for r in node.list_field_ranges())
    assert all(isinstance(r, tuple) and len(r) == 2 for r in node.list_subnode_ranges())

def test_static_node_methods():
    assert isinstance(PyNode.list_child_nodes_from(func_node), list)
    assert isinstance(PyNode.list_field_nodes_from(func_node), list)
    assert isinstance(PyNode.list_subnodes_from(func_node), list)

def test_static_range_methods():
    assert isinstance(PyNode.list_child_ranges_from(func_node), list)
    assert isinstance(PyNode.list_field_ranges_from(func_node), list)
    assert isinstance(PyNode.list_subnode_ranges_from(func_node), list)

def test_in_range_methods():
    node = PyNode(astnode=func_node)
    assert isinstance(node.in_child_range(3), bool)
    assert isinstance(node.in_field_range(3), bool)
    assert isinstance(node.in_subnode_range(3), bool)

def test_static_in_ranges():
    ranges = PyNode.list_child_ranges_from(func_node)
    if ranges:
        line = ranges[0][0]
        assert PyNode.in_ranges(line, ranges) is True
        
def test_range_property():
    node = PyNode(astnode=func_node)
    r = node.range
    assert isinstance(r, tuple)
    assert len(r) == 4
    assert all(isinstance(i, int) or i is None for i in r)

def test_get_snippet_bounds():
    node = PyNode(astnode=func_node, attributes={"source": "line1\nline2\nline3", "start_line": 1, "end_line": 3})
    assert node.get_snippet(1, 2).strip() == "line1\nline2"
    assert node.get_snippet(2, 3).strip() == "line2\nline3"

def test_list_child_nodes_with_exclude():
    node = PyNode(astnode=func_node)
    children_all = node.list_child_nodes()
    children_exclude = node.list_child_nodes(exclude=[ast.arguments])
    assert len(children_exclude) <= len(children_all)

def test_list_field_nodes_with_include():
    node = PyNode(astnode=func_node)
    included = node.list_field_nodes(include=[ast.arguments])
    assert any(isinstance(c, ast.arguments) for c in included)

def test_list_ranges():
    node = PyNode(astnode=func_node)
    child_ranges = node.list_child_ranges()
    field_ranges = node.list_field_ranges()
    subnode_ranges = node.list_subnode_ranges()
    assert all(isinstance(r, tuple) and len(r) == 2 for r in child_ranges + field_ranges + subnode_ranges)

def test_in_ranges():
    ranges = [(2, 4), (6, 8)]
    assert PyNode.in_ranges(3, ranges)
    assert not PyNode.in_ranges(5, ranges)

def test_in_range_methods():
    node = PyNode(astnode=func_node)
    # Ensure at least one line from child nodes exists
    if child_lines := node.list_child_ranges():
        line = child_lines[0][0]
        assert node.in_child_range(line)
    if field_lines := node.list_field_ranges():
        line = field_lines[0][0]
        assert node.in_field_range(line)
    if sub_lines := node.list_subnode_ranges():
        line = sub_lines[0][0]
        assert node.in_subnode_range(line)

def test_export_structure():
    node = PyNode(astnode=func_node)
    node_dict = node.export()
    assert "type" in node_dict
    assert "attributes" in node_dict
    assert isinstance(node_dict["attributes"], dict)
    
def test_get_snippet_from_errors():
    lines = ["line1", "line2", "line3"]
    assert PyNode.get_snippet_from(lines, 5, 6) == ""
    assert PyNode.get_snippet_from(lines, 3, 2) == ""
    assert PyNode.get_snippet_from(lines, -1, 2) == ""

def test_unparse_from_fallback():
    node = ast.Pass()  # cannot be unparsed to meaningful string
    result = PyNode.unparse_from(node, fallback=["value"])
    assert isinstance(result, str)

def test_list_child_nodes_consistency():
    func_ast = func_node
    raw_children = list(ast.iter_child_nodes(func_ast))
    via_method = PyNode.list_child_nodes_from(func_ast)
    assert set(raw_children) == set(via_method)

def test_list_subnodes_excludes_children():
    func_ast = func_node
    subnodes = PyNode.list_subnodes_from(func_ast)
    children = PyNode.list_child_nodes_from(func_ast)
    for s in subnodes:
        assert s not in children

def test_empty_astnode_handling():
    node = PyNode(
        astnode=ast.Pass(),
        attributes={},
    )
    exported = node.export()
    assert "attributes" in exported

def test_code_vs_unparse_consistency():
    node = PyNode(astnode=func_node)
    assert node.code == node.unparse()

def test_from_ast_generates_children():
    tree = ast.parse("def foo():\n    x = 1\n    return x\n")
    func = tree.body[0]
    node = PyNode.from_ast(func, source_lines=[""] + tree.body[0].body[0].__str__().splitlines())[0]
    assert isinstance(node.children, list)
