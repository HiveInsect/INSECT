from importlib.metadata import files
from importlib.resources import path
from pathlib import Path
import os, re

def detect_files(path: str) -> list[tuple[str, str]]:
    """주어진 경로에서 모든 파일을 재귀적으로 탐색하고, 각 파일의 경로와 제목을 반환한다.

    Args:
        path (str): 탐색할 디렉토리 경로
    Returns:
        list[tuple[str, str]]: 파일 경로와 제목의 튜플 리스트
    """
    files = []
    for root, dirs, filenames in os.walk(path):
        for filename in filenames:
            # file_path = os.path.join(root, filename)
            # with open(file_path, 'r', encoding='utf-8') as f:
            #     content = f.read()
            files.append((root, filename, classify_file(filename, root)))  # 파일 타입 판별
    return files

def classify_file(filename: str, dir: str) -> str | None:
    """파일명 하나 보고 타입 판별만 담당"""
    dir = Path(dir) if dir else None
    if filename.startswith(("compose", "docker-compose")) and filename.endswith((".yml", ".yaml")): # 컴포즈 파일 판별
        return "compose"
    elif filename == "Dockerfile": # 도커 파일 판별
        return "dockerfile"
    elif dir.name == "migrations" and dir.parent.name == "supabase" and re.match(r"\d{14}_.+\.sql", filename): # SUPABASE 마이그레이션 파일 판별
        return "migration_sql"
    elif dir.name == "supabase" and filename == "seed.sql": # SUPABASE 시드 파일 판별
        return "seed_sql"
    elif dir.name == "schemas" and dir.parent.name == "supabase" and filename.endswith(".sql"): # SUPABASE 스키마 파일 판별
        return "schema_sql"
    elif filename.startswith(".env"): # ENV 파일 판별
        return "env"
    elif filename == "vercel.json": # VERCEL 파일 판별
        return "vercel"
    elif dir.name == "workflows" and dir.parent.name == ".github" and filename.endswith(".yml"): # GITHUB 워크플로우 파일 판별
        return "github_workflow"
    elif filename.startswith("next.config.") and filename.endswith((".js", ".mjs", ".ts")): # NEXT.js 설정 파일 판별
        return "next_config"
    return None

# print(detect_files(input("Enter the path to scan for files: ")))