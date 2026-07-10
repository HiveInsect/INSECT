r"""
C:\dev\INSECT\tests\fixtures\ 폴더 안의 모든 .yml/.yaml 파일을 파싱해서
각 파일 옆에 <파일명>.facts.txt로 저장합니다.

사용법:
    python dump_facts.py
"""

import sys
from collections import defaultdict
from pathlib import Path

from insect.parsers.compose import parse


FIXTURES_DIR = Path(r"C:\dev\INSECT\tests\fixtures")


def dump_facts(input_path: Path) -> None:
    facts = parse(str(input_path))

    by_subject = defaultdict(list)
    for f in facts:
        by_subject[f.subject].append(f)

    kind_counter = defaultdict(int)
    for f in facts:
        kind_counter[str(f.kind)] += 1

    lines = []
    lines.append("=" * 70)
    lines.append(f"INSECT compose 파서 Fact 리포트")
    lines.append("=" * 70)
    lines.append(f"입력 파일 : {input_path.name}")
    lines.append(f"총 Fact  : {len(facts)}개")
    lines.append(f"서비스 수 : {len(by_subject)}개")
    lines.append("")

    lines.append("-" * 70)
    lines.append("Fact 종류별 개수")
    lines.append("-" * 70)
    for kind, cnt in sorted(kind_counter.items(), key=lambda x: -x[1]):
        lines.append(f"  {kind:35} {cnt}")
    lines.append("")

    lines.append("-" * 70)
    lines.append("Subject별 상세")
    lines.append("-" * 70)
    for subject in sorted(by_subject.keys()):
        subject_facts = by_subject[subject]
        lines.append(f"\n[{subject}] ({len(subject_facts)}개)")
        for f in subject_facts:
            lines.append(f"  L{f.line:>4}  {str(f.kind):30} {f.attrs}")

    lines.append("")
    lines.append("=" * 70)

    output_path = input_path.with_name(input_path.name + ".facts.txt")
    output_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"  OK {input_path.name} -> {output_path.name} ({len(facts)} facts)")


def main():
    if not FIXTURES_DIR.exists():
        print(f"folder not found: {FIXTURES_DIR}")
        sys.exit(1)

    # .yml, .yaml 둘 다 처리 (단, .facts.txt로 끝나는 리포트 파일은 제외)
    targets = [
        p for p in FIXTURES_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in (".yml", ".yaml")
        and not p.name.endswith(".facts.txt")
    ]

    if not targets:
        print(f"no .yml/.yaml files in {FIXTURES_DIR}")
        sys.exit(0)

    print(f"processing: {FIXTURES_DIR}\n")
    success = 0
    failed = 0
    for path in sorted(targets):
        try:
            dump_facts(path)
            success += 1
        except Exception as e:
            print(f"  FAIL {path.name} - {type(e).__name__}: {e}")
            failed += 1

    print(f"\ntotal: {success} success, {failed} failed")


if __name__ == "__main__":
    main()