"""tests/test_detector.py

insect/detector.py의 classify_file, detect_files 테스트.

- 정상 케이스: 현재 구현이 의도대로 잘 분류하는지 확인
- 경계 케이스: 애매한 입력에서 None을 정확히 리턴하는지 확인
- 알려진 버그 케이스: 현재 구현의 한계를 xfail로 문서화
  (고쳐지면 xfail을 지우고 정상 assert로 바꾸면 됨)
"""

import pytest
from insect.detector import classify_file, detect_files


# ─────────────────────────────────────────────────────────
# classify_file — compose
# ─────────────────────────────────────────────────────────

def test_classify_docker_compose_yml():
    assert classify_file("docker-compose.yml", "/project") == "compose"


def test_classify_docker_compose_yaml():
    assert classify_file("docker-compose.yaml", "/project") == "compose"


def test_classify_compose_yml():
    assert classify_file("compose.yml", "/project") == "compose"


def test_classify_docker_compose_prod_yml():
    assert classify_file("docker-compose.prod.yml", "/project") == "compose"


def test_classify_compose_override_yaml():
    assert classify_file("compose.override.yaml", "/project") == "compose"


def test_classify_compose_wrong_extension_returns_none():
    assert classify_file("docker-compose.txt", "/project") is None


# startswith 매칭이라 접두사가 붙은 compose 파일명은 인식 못함 (알려진 한계)
def test_classify_prefixed_compose_file():
    assert classify_file("my-docker-compose.yml", "/project") == "compose"


# ─────────────────────────────────────────────────────────
# classify_file — dockerfile
# ─────────────────────────────────────────────────────────

def test_classify_dockerfile_exact():
    assert classify_file("Dockerfile", "/project") == "dockerfile"


def test_classify_dockerfile_lowercase_not_matched():
    # 완전 일치(==)라서 대소문자 다르면 안 잡힘 (현재 동작)
    assert classify_file("dockerfile", "/project") is None


# 완전일치(==)라서 Dockerfile.dev 같은 변형을 놓침 (알려진 한계)
def test_classify_dockerfile_variant():
    assert classify_file("Dockerfile.dev", "/project") == "dockerfile"


# ─────────────────────────────────────────────────────────
# classify_file — supabase migration
# ─────────────────────────────────────────────────────────

MIGRATIONS_DIR = "/project/supabase/migrations"


def test_classify_migration_sql_valid():
    assert classify_file("20260703120000_init.sql", MIGRATIONS_DIR) == "migration_sql"


def test_classify_migration_sql_missing_timestamp():
    assert classify_file("init.sql", MIGRATIONS_DIR) is None


def test_classify_migration_sql_short_timestamp():
    # 14자리가 아니라 10자리 → 패턴 불일치
    assert classify_file("2026070312_init.sql", MIGRATIONS_DIR) is None


def test_classify_migration_sql_wrong_parent_dir():
    assert classify_file("20260703120000_init.sql", "/project/migrations") is None


def test_classify_migration_sql_wrong_dir_name():
    assert classify_file("20260703120000_init.sql", "/project/supabase/other") is None


# ─────────────────────────────────────────────────────────
# classify_file — supabase seed
# ─────────────────────────────────────────────────────────

def test_classify_seed_sql_valid():
    assert classify_file("seed.sql", "/project/supabase") == "seed_sql"


def test_classify_seed_sql_wrong_dir():
    assert classify_file("seed.sql", "/project/other") is None


def test_classify_seed_sql_wrong_filename():
    assert classify_file("seeds.sql", "/project/supabase") is None


# ─────────────────────────────────────────────────────────
# classify_file — supabase schema
# ─────────────────────────────────────────────────────────

def test_classify_schema_sql_valid():
    assert classify_file("public.sql", "/project/supabase/schemas") == "schema_sql"


def test_classify_schema_sql_wrong_parent_dir():
    assert classify_file("public.sql", "/project/schemas") is None


def test_classify_schema_sql_wrong_extension():
    assert classify_file("public.txt", "/project/supabase/schemas") is None


# ─────────────────────────────────────────────────────────
# classify_file — env
# ─────────────────────────────────────────────────────────

def test_classify_env_plain():
    assert classify_file(".env", "/project") == "env"


def test_classify_env_local():
    assert classify_file(".env.local", "/project") == "env"


def test_classify_env_production():
    assert classify_file(".env.production", "/project") == "env"


def test_classify_env_wrong_prefix_returns_none():
    assert classify_file("env.txt", "/project") is None


# ─────────────────────────────────────────────────────────
# classify_file — vercel
# ─────────────────────────────────────────────────────────

def test_classify_vercel_json():
    assert classify_file("vercel.json", "/project") == "vercel"


def test_classify_vercel_json5_not_matched():
    # 완전 일치라서 vercel.json5는 안 잡힘 (현재 동작)
    assert classify_file("vercel.json5", "/project") is None


# ─────────────────────────────────────────────────────────
# classify_file — github workflow
# ─────────────────────────────────────────────────────────

WORKFLOWS_DIR = "/project/.github/workflows"


def test_classify_github_workflow_yml():
    assert classify_file("ci.yml", WORKFLOWS_DIR) == "github_workflow"


# yaml 확장자는 체크 안 함 — GitHub Actions는 .yml/.yaml 둘 다 허용 (알려진 한계)
def test_classify_github_workflow_yaml():
    assert classify_file("ci.yaml", WORKFLOWS_DIR) == "github_workflow"


def test_classify_github_workflow_wrong_dir():
    assert classify_file("ci.yml", "/project/workflows") is None


# ─────────────────────────────────────────────────────────
# classify_file — next config
# ─────────────────────────────────────────────────────────

def test_classify_next_config_js():
    assert classify_file("next.config.js", "/project") == "next_config"


def test_classify_next_config_mjs():
    assert classify_file("next.config.mjs", "/project") == "next_config"


def test_classify_next_config_ts():
    assert classify_file("next.config.ts", "/project") == "next_config"


def test_classify_next_config_unsupported_extension():
    assert classify_file("next.config.json", "/project") is None


# ─────────────────────────────────────────────────────────
# classify_file — 알 수 없는 파일 / 방어 케이스
# ─────────────────────────────────────────────────────────

def test_classify_unknown_file_returns_none():
    assert classify_file("random.txt", "/project") is None


def test_classify_empty_filename_returns_none():
    # startswith("")는 항상 True지만 endswith 검사에서 걸러져 결국 None
    assert classify_file("", "/project") is None


# filename=None이면 .startswith() 호출에서 AttributeError 발생 (방어 로직 없음)
def test_classify_none_filename_does_not_crash():
    assert classify_file(None, "/project") is None


# dir=''이면 None으로 변환되고 dir.name 접근 시 AttributeError 발생 (방어 로직 없음)
def test_classify_empty_dir_does_not_crash():
    assert classify_file("public.sql", "") is None


# dir=None이면 dir.name 접근 시 AttributeError 발생 (방어 로직 없음)
def test_classify_none_dir_does_not_crash():
    assert classify_file("public.sql", None) is None


# ─────────────────────────────────────────────────────────
# detect_files — 통합 테스트 (실제 파일시스템 사용, tmp_path fixture)
# ─────────────────────────────────────────────────────────

def test_detect_files_empty_directory_returns_empty_list(tmp_path):
    result = detect_files(str(tmp_path))
    assert result == []


def test_detect_files_finds_all_files(tmp_path):
    (tmp_path / "docker-compose.yml").write_text("version: '3'")
    (tmp_path / "notes.txt").write_text("hello")

    result = detect_files(str(tmp_path))

    assert len(result) == 2
    filenames = {name for _, name, _ in result}
    assert filenames == {"docker-compose.yml", "notes.txt"}


def test_detect_files_classifies_correctly(tmp_path):
    (tmp_path / "docker-compose.yml").write_text("version: '3'")
    (tmp_path / "unknown.txt").write_text("hello")

    result = detect_files(str(tmp_path))
    result_by_name = {name: kind for _, name, kind in result}

    assert result_by_name["docker-compose.yml"] == "compose"
    assert result_by_name["unknown.txt"] is None


def test_detect_files_recurses_into_subdirectories(tmp_path):
    subdir = tmp_path / "supabase" / "migrations"
    subdir.mkdir(parents=True)
    (subdir / "20260703120000_init.sql").write_text("CREATE TABLE x();")

    result = detect_files(str(tmp_path))

    assert len(result) == 1
    root, name, kind = result[0]
    assert name == "20260703120000_init.sql"
    assert kind == "migration_sql"


def test_detect_files_multiple_nested_dirs(tmp_path):
    (tmp_path / ".env").write_text("SECRET=1")
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text("name: CI")
    schemas = tmp_path / "supabase" / "schemas"
    schemas.mkdir(parents=True)
    (schemas / "public.sql").write_text("CREATE TABLE t();")

    result = detect_files(str(tmp_path))
    result_by_name = {name: kind for _, name, kind in result}

    assert result_by_name[".env"] == "env"
    assert result_by_name["ci.yml"] == "github_workflow"
    assert result_by_name["public.sql"] == "schema_sql"


def test_detect_files_nonexistent_path_returns_empty_list(tmp_path):
    # os.walk는 존재하지 않는 경로에 예외를 던지지 않고 그냥 빈 결과를 리턴함
    fake_path = tmp_path / "does_not_exist"
    result = detect_files(str(fake_path))
    assert result == []


# .git/.venv/node_modules 등 대형 디렉토리를 걸러내는 로직이 없음 (알려진 한계)
def test_detect_files_excludes_git_directory(tmp_path):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("[core]")
    (tmp_path / "docker-compose.yml").write_text("version: '3'")

    result = detect_files(str(tmp_path))
    filenames = {name for _, name, _ in result}

    assert "config" not in filenames
    assert "docker-compose.yml" in filenames
