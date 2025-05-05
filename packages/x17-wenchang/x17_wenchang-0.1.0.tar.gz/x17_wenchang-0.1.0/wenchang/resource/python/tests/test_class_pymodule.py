# test_pymodule.py
import ast
import textwrap
from wenchang.resource.python.pymodule import PyModule
from wenchang.base.nodetype import NodeType
from wenchang.resource.python.pyfunction import PyFunction
from wenchang.resource.python.pyclass import PyClass
from wenchang.resource.python.pyimport import PyImport
from wenchang.resource.python.pystatement import PyStatement
from wenchang.resource.python.pycomment import PyComment

def test_pymodule_from_ast_full_structure():
    raw_code = '''
    """
    This is the module docstring.
    """

    # Module-level comment

    import os
    from typing import List

    class MyClass(BaseClass):
        """A sample class"""
        def method(self): pass

    def my_function(x: int) -> int:
        return x + 1

    y = 42  # A statement
    '''
    code = textwrap.dedent(raw_code).strip()
    lines = code.splitlines()
    tree = ast.parse(code)
    module_nodes = PyModule.from_ast(tree, name="example.py", source_lines=lines)
    
    assert len(module_nodes) == 1
    mod = module_nodes[0]

    assert mod.name == "example.py"
    assert mod.type == NodeType.MODULE
    assert "module docstring" in mod.attributes["docstring"]

    imports = mod.get_children(nodetype=NodeType.IMPORT)
    assert len(imports) == 2
    assert all(isinstance(i, PyImport) for i in imports)

    classes = mod.get_children(nodetype=NodeType.CLASS)
    assert len(classes) == 1
    assert classes[0].name == "MyClass"
    assert isinstance(classes[0], PyClass)

    functions = mod.get_children(nodetype=NodeType.FUNCTION)
    assert len(functions) == 1
    assert functions[0].name == "my_function"
    assert isinstance(functions[0], PyFunction)

    statements = mod.get_children(nodetype=NodeType.STATEMENT)
    assert len(statements) == 2
    assert isinstance(statements[0], PyStatement)

    comments = mod.get_children(nodetype=NodeType.COMMENT)
    assert any("Module-level comment" in c.attributes["content"] for c in comments)
    

def test_recursive_structure():
    raw_code = '''
def outer():
    def inner():
        class InnerClass:
            def inner_method(self): pass
        return InnerClass
    return inner

class OuterClass:
    def method(self):
        def nested_function():
            return 42
        return nested_function
    '''

    code = textwrap.dedent(raw_code).strip()
    lines = code.splitlines()
    tree = ast.parse(code)
    mod = PyModule.from_ast(tree, name="recursion_test.py", source_lines=lines)[0]

    # Step 1: top level
    top_funcs = mod.get_functions()
    top_classes = mod.get_classes()

    assert [f.name for f in top_funcs] == ["outer"]
    assert [c.name for c in top_classes] == ["OuterClass"]

    # Step 2: inner of outer()
    inner_func = top_funcs[0].get_functions()
    assert [f.name for f in inner_func] == ["inner"]

    # Step 3: inner of inner()
    inner_class = inner_func[0].get_classes()
    assert [c.name for c in inner_class] == ["InnerClass"]

    # Step 4: inner_method of InnerClass
    inner_method = inner_class[0].get_functions()
    assert [f.name for f in inner_method] == ["inner_method"]

    # Step 5: method of OuterClass
    outer_method = top_classes[0].get_functions()
    assert [f.name for f in outer_method] == ["method"]

    # Step 6: nested_function in method()
    nested = outer_method[0].get_functions()
    assert [f.name for f in nested] == ["nested_function"]
    
    
    
    