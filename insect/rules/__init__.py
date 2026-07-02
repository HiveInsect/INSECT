from insect.facts import Fact, Finding, Severity
from typing import Protocol

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
    def register(cls, rule: Rule):
        cls._rules[rule.id] = rule

    @classmethod
    def get_rule(cls, rule_id: str) -> Rule:
        return cls._rules[rule_id]

    @classmethod
    def all_rules(cls) -> list[Rule]:
        return list(cls._rules.values())

    @classmethod
    def clear(cls):
        cls._rules = {}