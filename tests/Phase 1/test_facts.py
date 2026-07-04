"""tests/test_facts.py

insect/facts.py의 Fact, Finding, Severity 테스트.
"""

import pytest
from dataclasses import FrozenInstanceError
from insect.facts import Fact, Finding, Severity


@pytest.fixture
def sample_fact():
    return Fact(
        kind="port_exposure",
        subject="web-container",
        attrs={"port": 22},
        file="docker-compose.yml",
        line=12,
        source_format="compose",
    )


def test_fact_is_frozen(sample_fact):
    with pytest.raises(FrozenInstanceError):
        sample_fact.line = 99


def test_fact_holds_correct_values(sample_fact):
    assert sample_fact.kind == "port_exposure"
    assert sample_fact.subject == "web-container"
    assert sample_fact.attrs == {"port": 22}
    assert sample_fact.file == "docker-compose.yml"
    assert sample_fact.line == 12
    assert sample_fact.source_format == "compose"


def test_finding_evidence_is_list_of_facts(sample_fact):
    finding = Finding(
        rule_id="R001",
        severity=Severity.HIGH,
        cwe="CWE-284",
        subject="web-container",
        file="docker-compose.yml",
        line=12,
        message="SSH 포트가 외부에 노출됨",
        lesson_id="L001",
        evidence=[sample_fact],
    )
    assert isinstance(finding.evidence, list)
    assert all(isinstance(f, Fact) for f in finding.evidence)
    assert finding.evidence[0] is sample_fact


def test_finding_evidence_defaults_to_empty_list():
    finding = Finding(
        rule_id="R002",
        severity=Severity.LOW,
        cwe="CWE-000",
        subject="db-container",
        file="docker-compose.yml",
        line=5,
        message="테스트용",
        lesson_id="L002",
    )
    assert finding.evidence == []
