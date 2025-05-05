# test_pyclass.py
# -*- coding: utf-8 -*-
import ast
import textwrap
import pytest

from wenchang.resource.python.pyclass import PyClass
from wenchang.base.nodetype import NodeType

@pytest.mark.parametrize("code, expected", [
    (
        '''
@decorator1
@decorator2(param=1)
class MyClass(Base1, Base2, metaclass=Meta):
    """
    This is a class docstring.
    """
    # class-level comment
    class_attr = 123

    def method(self, x: int) -> int:
        # method comment
        return x + self.class_attr

    class InnerClass:
        pass

    import os
        ''',
        {
            "name": "MyClass",
            "decorators": ["decorator1", "decorator2(param=1)"],
            "bases": ["Base1", "Base2"],
            "keywords": {"metaclass": "Meta"},
            "docstring": "This is a class docstring.",
            "comments": ["class-level comment"],
            "statements": ["class_attr = 123"],
            "functions": ["method"],
            "inner_classes": ["InnerClass"],
            "imports": ["os"],
        }
    )
])
def test_pyclass_from_ast_full(code, expected):
    code = textwrap.dedent(code).strip()
    lines = code.splitlines()
    tree = ast.parse(code)
    class_node = next(n for n in tree.body if isinstance(n, ast.ClassDef))
    results = PyClass.from_ast(class_node, source_lines=lines)
    assert len(results) == 1
    cls = results[0]

    assert cls.name == expected["name"]
    assert cls.type == NodeType.CLASS
    assert cls.attributes["docstring"] == expected["docstring"]
    for deco in expected["decorators"]:
        assert deco in cls.attributes["decorators"]
    for base in expected["bases"]:
        assert base in cls.attributes["bases"]
    for k, v in expected["keywords"].items():
        assert cls.attributes["keywords"].get(k) == v

    comments = cls.get_children(NodeType.COMMENT)
    assert [c.attributes["content"] for c in comments] == expected["comments"]

    functions = cls.get_children(NodeType.FUNCTION)
    assert [f.name for f in functions] == expected["functions"]

    statements = cls.get_children(NodeType.STATEMENT)
    assert any(expected["statements"][0] in s.snippet for s in statements)

    inner_classes = cls.get_children(NodeType.CLASS)
    assert [c.name for c in inner_classes] == expected["inner_classes"]

    imports = cls.get_children(NodeType.IMPORT)
    assert [i.name for i in imports] == expected["imports"]
    
def test_pyclass_from_ast_comprehensive():
    raw_code = '''
@decorator1
@decorator2(param=2)
class MyClass(Base1, Base2, metaclass=MetaBase):
    """
    This is a docstring.
    """

    # Class-level comment
    import os

    class_attr = 42

    def method1(self):
        # Method1 comment
        return self.class_attr

    async def method2(self, x: int) -> str:
        return str(x)

    class Nested:
        pass
    '''

    code = textwrap.dedent(raw_code).strip()
    lines = code.splitlines()
    tree = ast.parse(code)
    cls_node = next(n for n in tree.body if isinstance(n, ast.ClassDef))

    results = PyClass.from_ast(cls_node, source_lines=lines)
    assert len(results) == 1
    cls = results[0]

    # Check class meta
    assert cls.name == "MyClass"
    assert cls.type == NodeType.CLASS
    assert "decorator1" in cls.attributes["decorators"][0]
    assert "Base1" in cls.attributes["bases"]
    assert cls.attributes["keywords"]["metaclass"] == "MetaBase"
    assert "docstring" in cls.attributes
    assert "This is a docstring." in cls.attributes["docstring"]
    assert "source" in cls.attributes
    assert isinstance(cls.export(), dict)

    # Check children
    comments = cls.get_comments()
    assert any("Class-level comment" in c.attributes["content"] for c in comments)

    imports = cls.get_imports()
    assert len(imports) == 1
    assert imports[0].name == "os"

    functions = cls.get_functions()
    assert len(functions) == 2
    assert any(f.name == "method1" for f in functions)
    assert any(f.name == "method2" for f in functions)

    statements = cls.get_statements()
    assert any("class_attr" in stmt.snippet for stmt in statements)

    nested_classes = cls.get_classes()
    assert len(nested_classes) == 1
    assert nested_classes[0].name == "Nested"
    
def test_pyclass_get_init_function():
    raw_code = '''
class MyClass:
    def __init__(self, x):
        self.x = x

    def method(self):
        return self.x
    '''
    code = textwrap.dedent(raw_code).strip()
    lines = code.splitlines()
    tree = ast.parse(code)
    cls_node = next(n for n in tree.body if isinstance(n, ast.ClassDef))

    results = PyClass.from_ast(cls_node, source_lines=lines)
    assert len(results) == 1
    cls = results[0]

    init_func = cls.get_init_function()
    assert init_func is not None
    assert init_func.name == "__init__"
    assert "x" in [arg.name for arg in init_func.get_arguments()]