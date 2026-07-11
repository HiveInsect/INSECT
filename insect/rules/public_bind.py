from insect.facts import Finding, Severity, Fact
from insect.fact_kinds import FactKind
from insect.rule_kinds import RuleKind


# ---------------------분류별 메타데이터 (테이블)--------------------------------
EXPOSURE_TYPES = {
    "db": {
        "id": RuleKind.DB_EXPOSED,
        "severity": Severity.HIGH,
        "label": "DB 포트",
        "lesson_id": "CWE-1327_db_exposed",
    },
    "generic": {
        "id": RuleKind.PORT_EXPOSED,
        "severity": Severity.LOW,
        "label": "포트",
        "lesson_id": "CWE-1327_port_exposed",
    },
}

# ---------------------DB 룰 상수--------------------------------
DB_PORTS = {
    5432,   # PostgreSQL
    3306,   # MySQL / MariaDB (동일 포트)
    27017,  # MongoDB
    6379,   # Redis
    5984,   # CouchDB
    1433,   # SQL Server
    1521,   # Oracle
    9042,   # Cassandra
    11211,  # Memcached
    7687,   # Neo4j (bolt)
    8123,   # ClickHouse (HTTP)
}

DB_IMAGES = {
    "postgres", "postgresql",           # PostgreSQL
    "mysql", "mariadb",                 # MySQL 계열
    "mongo", "mongodb",                 # MongoDB
    "redis",                            # Redis
    "couchdb",                          # CouchDB
    "mssql", "sqlserver",               # SQL Server (mcr.microsoft.com/mssql/server)
    "oracle", "oracledb",               # Oracle
    "cassandra",                        # Cassandra
    "memcached",                        # Memcached
    "neo4j",                            # Neo4j
    "clickhouse",                       # ClickHouse
}

class PublicBindRule:
    id = "PORT_EXPOSED"
    cwe = "CWE-1327"
    def detect(self, facts: list[Fact]) -> list[Finding]:
        findings = []
        images_by_subject = {}

        for f in facts:
            if f.kind == FactKind.IMAGE:
                images_by_subject[f.subject] = f
        for f in facts:
            if f.kind == FactKind.BIND:
                # TODO: 네 조건 (host_port 매핑됨 / host==0.0.0.0 / target_port in DB_PORTS / tcp)
                # 하나라도 안 맞으면 continue
                if (f.attrs["host_port"] is None            # 매핑 없음 = 외부 노출 안 됨
                    or f.attrs["host"] != "0.0.0.0"):     # 모든 인터페이스 바인딩 아님
                    continue
                image_fact = images_by_subject.get(f.subject)
                kind = self._classify(f, image_fact)      # "db" / "docker_api" / "generic"
                meta = EXPOSURE_TYPES[kind]                # 테이블에서 꺼냄
                evidence = [f]
                if image_fact is not None:
                    evidence.append(image_fact)
                # TODO: 다 통과하면 Finding 생성
                #   evidence=[f], subject/file/line은 f에서 가져오기
                #   severity, cwe, message, lesson_id 채우기
                findings.append(Finding(
                    rule_id=meta["id"],
                    severity=meta["severity"],
                    cwe=self.cwe,
                    subject=f.subject,      # ← 여기서 채워짐 (Fact에서 가져옴)
                    file=f.file,
                    line=f.line,
                    message=f"{f.subject}의 {meta['label']} {f.attrs['target_port']}가 모든 인터페이스(0.0.0.0)에 바인딩됨",
                    lesson_id=meta["lesson_id"],
                    evidence=evidence,
                ))

        
        return findings
    
    def _classify(self, bind_fact: Fact, image_fact: Fact | None) -> str:
        """어느 분류인지 문자열로 리턴"""
        if self._is_db(bind_fact, image_fact):
            return "db"
        return "generic"
    
    def _is_db(self, bind_fact: Fact, image_fact: Fact | None) -> bool:
        if (bind_fact.attrs["target_port"] in DB_PORTS
                and bind_fact.attrs["protocol"] == "tcp"):
            return True

        if image_fact is not None:
            name = image_fact.attrs["name"].lower()
            if any(kw in name for kw in DB_IMAGES):
                return True

        return False