# -*- coding: utf-8 -*-
import ast
import pytest
from wenchang.resource.python.pyimport import PyImport

@pytest.mark.parametrize("code, expected", [
    ("import os", [("os", None, None, None, "import os")]),
    ("import os, sys", [("os", None, None, None, "import os, sys"), ("sys", None, None, None, "import os, sys")]),
    ("import pandas as pd", [("pandas", "pd", None, None, "import pandas as pd")]),
    ("from typing import List", [("List", None, "typing", 0, "from typing import List")]),
    ("from typing import Dict as D", [("Dict", "D", "typing", 0, "from typing import Dict as D")]),
    ("from typing import List, Dict", [
        ("List", None, "typing", 0, "from typing import List, Dict"),
        ("Dict", None, "typing", 0, "from typing import List, Dict"),
    ]),
    ("from . import something", [("something", None, None, 1, "from . import something")]),
    ("from ..module.sub import A as Alias", [("A", "Alias", "module.sub", 2, "from ..module.sub import A as Alias")]),
])
def test_pyimport_from_ast_variants_with_source_lines(code, expected):
    tree = ast.parse(code)
    node = tree.body[0]
    source_lines = code.splitlines()
    results = PyImport.from_ast(node, source_lines=source_lines)

    assert len(results) == len(expected), f"Mismatch on number of imports for: {code}"

    for imp, (name, alias, module, level, expected_source) in zip(results, expected):
        assert imp.name == name
        assert imp.attributes["alias"] == alias
        assert imp.attributes["module"] == module
        assert imp.attributes["level"] == level
        assert imp.attributes["source"].strip() == expected_source.strip()
        assert imp.type.value == "import"
        assert isinstance(imp.export(), dict)