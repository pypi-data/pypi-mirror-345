# -*- coding: utf-8 -*-
from enum import Enum
from typing import Any, Dict, List, Optional


class NodeType(Enum):
    # Common
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    IMPORT = "import"
    COMMENT = "comment"
    STATEMENT = "statement"
    ARGUMENT = "argument"
    
    
    # Safenet
    OTHERS = "others" # Other types not specified or not supported
    UNKNOWN = "unknown" # Unknown type, used for error handling or unrecognized nodes
