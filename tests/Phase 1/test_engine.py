"""tests/test_engine.py

insect/engine.py의 scan() 테스트.

주의: 현재 scan()은 detect_files 호출까지만 구현돼 있고
parse_all, run_rules는 주석 처리된 stub 상태.
파싱/룰실행이 연결되면 이 테스트도 확장해야 함.
"""

from insect.engine import scan


def test_scan_returns_list(tmp_path):
    (tmp_path / "sample.txt").write_text("hello")
    result = scan(str(tmp_path))
    assert isinstance(result, list)


def test_scan_empty_directory_returns_empty_list(tmp_path):
    result = scan(str(tmp_path))
    assert result == []
