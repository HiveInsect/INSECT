"""컨테이너가 root 권한으로 실행되는지 탐지하는 룰 (CWE-250).

컨테이너 탈출(escape) 발생 시 호스트에서 root 권한을 얻을 수 있으므로,
USER 지시어가 없거나 명시적으로 root(uid 0)로 지정된 경우를 탐지한다.
"미설정 = 안전하지 않은 기본값" 원칙: USER 미지정은 root 실행으로 간주한다.
"""

from insect.facts import Fact, Finding, Severity

ROOT_IDENTIFIERS = {"root", "0"}


class ContainerRootRule:
    id = "CONTAINER_ROOT"
    severity = Severity.HIGH
    cwe = "CWE-250"

    def detect(self, facts: list[Fact]) -> list[Finding]:
        out = []
        for f in facts:
            if f.kind != "run_as":
                continue
            user = f.attrs.get("user")
            if user is None or str(user) in ROOT_IDENTIFIERS:
                out.append(Finding(
                    rule_id=self.id,
                    severity=self.severity,
                    cwe=self.cwe,
                    subject=f.subject,
                    file=f.file,
                    line=f.line,
                    message=f"{f.subject} 컨테이너가 root 권한으로 실행됨 (USER 미지정 또는 root 명시)",
                    lesson_id="CWE-250_container_root",
                    evidence=[f],
                ))
        return out