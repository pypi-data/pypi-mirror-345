# -*- coding: utf-8 -*-
import ast
import textwrap

from wenchang.resource.python.pycomment import PyComment


test_cases = [
    (
        '''
# Module-level comment

def foo():
    # Inner comment
    x = 1  # Trailing comment
''',
        [
            ("Module", ["Module-level comment"]),
            ("foo", ["Inner comment", "Trailing comment"]),
        ],
    ),
    (
        '''
def outer():
    # Outer comment
    def inner():
        # Inner comment
        pass
    return 1  # Outer trailing
''',
        [
            ("outer", ["Outer comment", "Outer trailing"]),
            ("inner", ["Inner comment"]),
        ],
    ),
    (
        '''
def lonely():
    pass
''',
        [
            ("lonely", []),
        ],
    ),
    (
        '''
# One
# Two
class C:
    # Three
    def m(self):
        # Four
        pass
''',
        [
            ("Module", ["One", "Two"]),
            ("C", ["Three"]),
            ("m", ["Four"]),
        ],
    ),
]


def test_pycomment_from_ast_comprehensive():
    for raw_code, expected_pairs in test_cases:
        code = textwrap.dedent(raw_code).strip()
        lines = code.splitlines()
        tree = ast.parse(code)

        for node_type, expected_comments in expected_pairs:
            if node_type == "Module":
                target = tree
            else:
                target = next(
                    n for n in ast.walk(tree)
                    if isinstance(n, (ast.FunctionDef, ast.ClassDef))
                    and getattr(n, "name", None) == node_type
                )
            comments = PyComment.from_ast(
                target, source_lines=lines, exclude=[ast.FunctionDef, ast.ClassDef]
            )
            contents = [c.attributes["content"] for c in comments]
            for expected in expected_comments:
                assert expected in contents, f"Missing comment: {expected}"
            assert len(contents) == len(expected_comments), f"Unexpected comments for {node_type}: {contents}"
            
def test_pycomment_class_and_function_levels():
    code = '''
# Module-level comment

class MyClass:
    # Class-level comment
    def method(self):
        # Method comment
        x = 1  # trailing

def top_level():
    # Top-level function comment
    return 42  # top trailing
    '''
    source_lines = code.strip().splitlines()
    tree = ast.parse(code)

    # 提取 Class 节点
    cls_node = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
    class_comments = PyComment.from_ast(cls_node, source_lines=source_lines, exclude=[ast.FunctionDef])
    class_contents = [c.attributes["content"] for c in class_comments]
    assert "Class-level comment" in class_contents
    assert "Method comment" not in class_contents  # method 被排除
    assert len(class_contents) == 1

    # 提取 Function 节点（method）
    func_node = next(n for n in ast.walk(cls_node) if isinstance(n, ast.FunctionDef) and n.name == "method")
    func_comments = PyComment.from_ast(func_node, source_lines=source_lines)
    func_contents = [c.attributes["content"] for c in func_comments]
    assert "Method comment" in func_contents
    assert "trailing" in func_contents
    assert len(func_contents) == 2

    # 提取 top-level function
    top_node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "top_level")
    top_comments = PyComment.from_ast(top_node, source_lines=source_lines)
    top_contents = [c.attributes["content"] for c in top_comments]
    assert "Top-level function comment" in top_contents
    assert "top trailing" in top_contents
    assert len(top_contents) == 2
    