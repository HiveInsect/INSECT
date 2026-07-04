"""tests/test_cli.py

insect/cli.py의 main() 테스트.

argparse는 sys.argv를 읽으므로, monkeypatch로 sys.argv를 바꿔치기하고
capsys로 stdout 출력을 캡처해서 검증한다.
"""

import pytest
from insect.cli import main


def test_scan_command_prints_file_count(tmp_path, monkeypatch, capsys):
    (tmp_path / "docker-compose.yml").write_text("version: '3'")
    (tmp_path / "notes.txt").write_text("hello")

    monkeypatch.setattr("sys.argv", ["insect", "scan", str(tmp_path)])
    main()

    captured = capsys.readouterr()
    assert "스캔 파일 대상 개수: 2" in captured.out


def test_scan_command_empty_directory(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["insect", "scan", str(tmp_path)])
    main()

    captured = capsys.readouterr()
    assert "스캔 파일 대상 개수: 0" in captured.out


def test_scan_command_requires_path(monkeypatch, capsys):
    # 위치 인자(path) 없이 scan만 호출하면 argparse가 에러 메시지 찍고 SystemExit(2) 발생
    monkeypatch.setattr("sys.argv", ["insect", "scan"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2


def test_no_command_does_nothing(monkeypatch, capsys):
    # 서브커맨드 없이 실행하면 args.command가 None이라 아무 것도 출력 안 됨
    monkeypatch.setattr("sys.argv", ["insect"])
    main()

    captured = capsys.readouterr()
    assert captured.out == ""


def test_unknown_command_exits(monkeypatch):
    # 정의 안 된 서브커맨드 주면 argparse가 에러 내고 종료
    monkeypatch.setattr("sys.argv", ["insect", "unknown"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
