"""tests/test_rules.py

insect/rules/__init__.py의 RuleRegistry 테스트.
"""

import pytest
from insect.rules import RuleRegistry
from insect.facts import Severity


class DummyRule:
    """테스트용 가짜 룰 — Rule Protocol을 만족시킴"""
    id = "R999"
    severity = Severity.LOW
    cwe = "CWE-000"

    def detect(self, facts):
        return []


@pytest.fixture(autouse=True)
def clear_registry():
    """각 테스트 전후로 레지스트리 초기화 (클래스 변수라 상태가 테스트 간 공유됨)"""
    RuleRegistry.clear()
    yield
    RuleRegistry.clear()


def test_register_and_get_rule():
    rule = DummyRule()
    RuleRegistry.register(rule)
    assert RuleRegistry.get_rule("R999") is rule


def test_get_unregistered_rule_raises():
    with pytest.raises(KeyError):
        RuleRegistry.get_rule("NOT_EXIST")


def test_all_rules_returns_registered():
    rule = DummyRule()
    RuleRegistry.register(rule)
    assert RuleRegistry.all_rules() == [rule]


def test_clear_empties_registry():
    RuleRegistry.register(DummyRule())
    RuleRegistry.clear()
    assert RuleRegistry.all_rules() == []
