from insect.detector import detect_files
from insect.facts import Finding

def scan(path: str) -> list[Finding]:
    files = detect_files(path)      # 1. 파일 목록 수집
    # facts = parse_all(files)        # 2. 파싱 → Fact[]
    # findings = run_rules(facts)     # 3. 룰 실행 → Finding[]
    return files # 테스트