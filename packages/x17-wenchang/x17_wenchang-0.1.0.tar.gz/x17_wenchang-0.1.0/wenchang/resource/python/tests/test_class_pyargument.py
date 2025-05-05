# test_pyargument.py
import ast
from wenchang.resource.python.pyargument import PyArgument

test_cases = [
    (
    """
def f7(x: "Quoted"): pass
    """,
    [("x", "'Quoted'", False, False, False, True)],
    ),
    (
    """
def f8(x: list[int] = [1, 2]): pass
    """,
    [("x", "list[int]", False, False, False, True)],
    ),
    (
    """
def f9(x, /, y=42, *, z='ok', **kwargs): pass
    """,
    [
        ("x", None, False, False, False, True),
        ("y", None, False, False, False, True),
        ("z", None, False, False, True, False),
        ("kwargs", None, False, True, False, False),
    ],
    ),
    (
        """
def f1(x): pass
        """,
        [("x", None, False, False, False, True)],
    ),
    (
        """
def f2(x: int, y='a'): pass
        """,
        [("x", "int", False, False, False, True), ("y", None, False, False, False, True)],
    ),
    (
        """
def f3(*args): pass
        """,
        [("args", None, True, False, False, False)],
    ),
    (
        """
def f4(**kwargs): pass
        """,
        [("kwargs", None, False, True, False, False)],
    ),
    (
        """
def f5(x, *, y=42): pass
        """,
        [("x", None, False, False, False, True), ("y", None, False, False, True, False)],
    ),
    (
        """
def f6(x, /, y): pass
        """,
        [("x", None, False, False, False, True), ("y", None, False, False, False, True)],
    ),
]

def test_pyargument_from_ast_variants_with_source():
    for code, expected_args in test_cases:
        source = code.strip()
        tree = ast.parse(source)
        funcdef = tree.body[0]
        source_lines = source.splitlines()

        arguments = PyArgument.from_ast(funcdef.args, source_lines=source_lines)
        assert len(arguments) == len(expected_args)

        for arg, expected in zip(arguments, expected_args):
            expected_name, expected_annotation, is_vararg, is_kwarg, is_kwonly, is_posonly = expected
            assert arg.name == expected_name
            assert arg.attributes["annotation"] == expected_annotation
            assert arg.attributes["is_vararg"] == is_vararg
            assert arg.attributes["is_kwarg"] == is_kwarg
            assert arg.attributes["is_kwonly"] == is_kwonly
            assert arg.attributes["is_posonly"] == is_posonly
            assert expected_name in arg.snippet or arg.snippet != ""