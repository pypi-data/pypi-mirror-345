# test_pyfunction.py
# -*- coding: utf-8 -*-
import ast
import textwrap
from wenchang.resource.python.pyfunction import PyFunction
from wenchang.base.nodetype import NodeType
from wenchang.resource.python.pyargument import PyArgument
from wenchang.resource.python.pycomment import PyComment
from wenchang.resource.python.pystatement import PyStatement
from wenchang.resource.python.pyimport import PyImport

def test_pyfunction_from_ast_full_structure():
    raw_code = '''
@decorator1
@decorator2(param=1)
async def foo(x: int, y="bar") -> str:
    """
    This is a docstring.
    """
    # function comment
    import os
    z = x + 1
    return z
    '''

    code = textwrap.dedent(raw_code).strip()
    lines = code.splitlines()
    tree = ast.parse(code)
    func_node = tree.body[0]

    results = PyFunction.from_ast(func_node, source_lines=lines)
    assert len(results) == 1
    func = results[0]

    assert func.name == "foo"
    assert func.type == NodeType.FUNCTION
    assert func.attributes["is_async"] is True
    assert func.attributes["docstring"] == "This is a docstring."
    assert func.attributes["return_annotation"] == "str"
    assert "decorator1" in func.attributes["decorators"][0]
    assert isinstance(func.export(), dict)

    args = func.get_arguments()
    assert len(args) == 2
    assert isinstance(args[0], PyArgument)
    assert args[0].name == "x"
    assert args[0].attributes["annotation"] == "int"

    comments = func.get_comments()
    assert len(comments) == 1
    assert isinstance(comments[0], PyComment)
    assert "function comment" in comments[0].attributes["content"]

    statements = func.get_statements()
    assert any("return" in stmt.snippet for stmt in statements)
    assert any("z = x + 1" in stmt.snippet for stmt in statements)

    imports = func.get_imports()
    assert len(imports) == 1
    assert isinstance(imports[0], PyImport)
    assert imports[0].name == "os"
    
def test_function_no_args():
    code = '''def no_args(): pass'''
    func_node = ast.parse(code).body[0]
    func = PyFunction.from_ast(func_node, source_lines=code.splitlines())[0]
    assert func.name == "no_args"
    assert func.get_arguments() == []
    

def test_nested_function_is_composite():
    code = '''
def outer():
    def inner(): pass
    return 1
'''
    lines = textwrap.dedent(code).strip().splitlines()
    func = PyFunction.from_ast(ast.parse("\n".join(lines)).body[0], source_lines=lines)[0]
    nested_funcs = func.get_functions()
    assert len(nested_funcs) == 1
    assert nested_funcs[0].name == "inner"
    
def test_inner_class_skipped():
    code = '''
def f():
    class Inner: pass
    return 1
'''
    lines = textwrap.dedent(code).strip().splitlines()
    func = PyFunction.from_ast(ast.parse("\n".join(lines)).body[0], source_lines=lines)[0]
    classes = func.get_children(asttype=ast.ClassDef)
    assert len(classes) == 1
    
def test_multiple_decorators():
    code = '''
@a
@b
def f(): pass
'''
    lines = textwrap.dedent(code).strip().splitlines()
    func = PyFunction.from_ast(ast.parse("\n".join(lines)).body[0], source_lines=lines)[0]
    assert func.attributes["decorators"] == ["a", "b"]
    
def test_argument_with_annotation_and_default():
    code = '''def f(x: int = 10): pass'''
    func = PyFunction.from_ast(ast.parse(code).body[0], source_lines=code.splitlines())[0]
    arg = func.get_arguments()[0]
    assert arg.name == "x"
    assert arg.attributes["annotation"] == "int"
    assert arg.attributes["default"] == "10"
    
    
