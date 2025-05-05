# -*- coding: utf-8 -*-
import pytest

from wenchang.base.nodetype import NodeType


def test_nodetype_enum_values():
    assert NodeType.MODULE.value == "module"
    assert NodeType.CLASS.value == "class"
    assert NodeType.FUNCTION.value == "function"
    assert NodeType.IMPORT.value == "import"
    assert NodeType.COMMENT.value == "comment"
    assert NodeType.ARGUMENT.value == "argument"
    assert NodeType.OTHERS.value == "others"
