from insect.facts import Fact, Finding, Severity
from typing import Protocol
from insect.rules import public_bind

class Rule(Protocol):
    id: str
    severity: Severity
    cwe: str
    def detect(self, facts: list[Fact]) -> list[Finding]: ...

class RuleRegistry:
    """룰을 등록하고, 룰 ID로 룰을 조회하는 레지스트리.

    RuleRegistry는 싱글톤으로 동작한다.
    """
    _rules: dict[str, Rule] = {}

    @classmethod
    def register(cls, rule: Rule): # 룰 등록
        cls._rules[rule.id] = rule

    @classmethod
    def get_rule(cls, rule_id: str) -> Rule: # 룰 id로 룰 조회
        return cls._rules[rule_id]

    @classmethod
    def all_rules(cls) -> list[Rule]: # 전체 룰 조회
        return list(cls._rules.values())

    @classmethod
    def clear(cls): # 룰 목록 초기화
        cls._rules = {}

# -------------------------------- 룰 등록 --------------------------------------
RuleRegistry.register(public_bind.PublicBindRule)