# insect/fact_kinds.py
from enum import Enum

class RuleKind(str, Enum):
    """rule id Enum. 룰 추가 시 여기에도 추가"""
    DB_EXPOSED = "DB_EXPOSED"
    PORT_EXPOSED = "PORT_EXPOSED"