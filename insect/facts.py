from dataclasses import dataclass, field
from enum import Enum

@dataclass
class Fact:
    """설정 파일에서 발견한 사실 하나.

    여러 포맷(compose/sql/env)을 이 공통 형식으로 통일한다.
    이렇게 하면 룰이 원본 포맷 문법을 몰라도 된다.
    """
    kind: str # 종류
    subject: str # 대상 리소스
    attrs: dict # 세부 내용
    file: str # 나온 파일
    line: int # 몇 번째 줄
    source_format: str # 출처 포맷

class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class Finding:
    """룰이 판정한 취약점 하나.

    Fact를 근거로 룰이 '이건 취약하다'고 판단한 결과.
    심각도·CWE·교육 연결 정보가 붙는다.
    """
    rule_id: str # 해당 보안 룰 ID
    severity: Severity # 지정 Enum 클래스
    cwe: str # CWE 번호
    subject: str # 대상 리소스
    file: str # 나온 파일
    line: int # 몇 번째 줄
    message: str # 사용자에게 보여줄 설명
    lesson_id: str # 교육 레슨 연결
    evidence: list = field(default_factory=list)  # ← 이 Finding을 만든 근거 Fact들