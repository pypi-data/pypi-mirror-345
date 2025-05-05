# test_pystatement.py
# -*- coding: utf-8 -*-
import ast
import textwrap
import pytest
from wenchang.resource.python.pystatement import PyStatement

@pytest.mark.parametrize("code, expected_types", [
    ("x = 1", ["Assign"]),
    ("x, y = 1, 2", ["Assign"]),
    ("del x", ["Delete"]),
    ("print('hello')", ["Expr"]),
    ("return x", ["Return"]),
    ("raise ValueError('err')", ["Raise"]),
    ("assert x > 0", ["Assert"]),
    ("pass", ["Pass"]),
    ("break", ["Break"]),
    ("continue", ["Continue"]),
    ("yield x", ["Expr"]),
    ("yield from some_gen()", ["Expr"]),
    ("global x", ["Global"]),
    ("nonlocal y", ["Nonlocal"]),
])
def test_single_statements(code, expected_types):
    tree = ast.parse(code)
    stmt = tree.body[0]
    source_lines = code.strip().splitlines()
    results = PyStatement.from_ast(stmt, source_lines=source_lines)

    assert len(results) == 1
    result = results[0]
    assert result.attributes["asttype"] in expected_types
    assert result.type.value == "statement"
    assert result.snippet.strip() != ""
    assert isinstance(result.export(), dict)


@pytest.mark.parametrize("code, expected_types", [
    ("""
if x > 0:
    y = 1
""", ["If"]),
    ("""
for i in range(3):
    print(i)
""", ["For"]),
    ("""
while True:
    break
""", ["While"]),
    ("""
try:
    x = 1
except Exception:
    x = 2
finally:
    x = 3
""", ["Try"]),
    ("""
with open('f') as f:
    data = f.read()
""", ["With"]),
    ("""
match value:
    case 1: pass
""", ["Match"]),
])
def test_compound_statements(code, expected_types):
    tree = ast.parse(textwrap.dedent(code))
    stmt = tree.body[0]
    lines = textwrap.dedent(code).strip().splitlines()
    results = PyStatement.from_ast(stmt, source_lines=lines)

    assert len(results) == 1
    result = results[0]
    assert result.attributes["asttype"] in expected_types
    assert result.type.value == "statement"
    assert result.snippet.strip() != ""
    assert isinstance(result.export(), dict)
    
    