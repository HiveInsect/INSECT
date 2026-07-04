from pathlib import Path
import os, re




def detect_files(path: str) -> list[tuple[str, str]]:
    """주어진 경로에서 모든 파일을 재귀적으로 탐색하고, 각 파일의 경로와 제목을 반환한다.

    Args:
        path (str): 탐색할 디렉토리 경로
    Returns:
        list[tuple[str, str]]: 파일 경로와 제목의 튜플 리스트
    """
    EXCLUDED_DIRS = {
            ".git", # Git 저장소 디렉토리 제외
            "__pycache__", # Python 캐시 디렉토리 제외
            "node_modules", # Node.js 패키지 디렉토리 제외
            "venv", # Python 가상환경 디렉토리 제외
            ".venv", # Python 가상환경 디렉토리 제외
            ".idea", # JetBrains IDE 설정 디렉토리 제외
            ".vscode", # Visual Studio Code 설정 디렉토리 제외
            ".next", # Next.js 빌드 디렉토리 제외
            "dist", # 빌드 결과물 디렉토리 제외
            "build", # 빌드 결과물 디렉토리 제외
            "out", # 빌드 결과물 디렉토리 제외
            ".parcel-cache", # Parcel 빌드 캐시 디렉토리 제외
            ".cache", # 일반적인 캐시 디렉토리 제외
            "logs", # 로그 디렉토리 제외
            "tmp", # 임시 파일 디렉토리 제외
            "temp" # 임시 파일 디렉토리 제외
        }
    USER_EXCLUDED_DIRS = set()  # 사용자 정의 제외 디렉토리 (추후 확장 가능)
    files = []
    for root, dirs, filenames in os.walk(path):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and d not in USER_EXCLUDED_DIRS]
        for filename in filenames:
            # file_path = os.path.join(root, filename)
            # with open(file_path, 'r', encoding='utf-8') as f:
            #     content = f.read()
            files.append((root, filename, classify_file(filename, root)))  # 파일 타입 판별
    return files

def classify_file(filename: str, dir: str) -> str | None:
    """파일명 하나 보고 타입 판별만 담당"""
    if(not filename):
        raise ValueError(f"설정 파일 없음: {filename}")
    dir = Path(dir) if dir else None
    if re.match(r"^.*\b(docker-compose|compose)\b.*\.(yml|yaml)$", filename): # 컴포즈 파일 판별
        return "compose"
    elif re.match(r"^Dockerfile(\..+)?$", filename): # 도커 파일 판별
        return "dockerfile"
    elif dir and dir.name == "migrations" and dir.parent.name == "supabase" and re.match(r"\d{14}_.+\.sql", filename): # SUPABASE 마이그레이션 파일 판별
        return "migration_sql"
    elif dir and dir.name == "supabase" and re.match(r"^seed\.sql$", filename): # SUPABASE 시드 파일 판별
        return "seed_sql"
    elif dir and dir.name == "schemas" and dir.parent.name == "supabase" and re.match(r".+\.sql$", filename): # SUPABASE 스키마 파일 판별
        return "schema_sql"
    # TODO: .env 파일 위험성 판별
    elif re.match(r"^\.env(\..+)?$", filename, re.IGNORECASE): # ENV 파일 판별
        return "env"
    elif re.match(r"^vercel\.json$", filename): # VERCEL 파일 판별
        return "vercel"
    elif dir and dir.name == "workflows" and dir.parent.name == ".github" and re.match(r"(.+).*\.(yml|yaml)$", filename): # GITHUB 워크플로우 파일 판별
        return "github_workflow"
    elif re.match(r"^next\.config\.(js|mjs|ts)$", filename): # NEXT.js 설정 파일 판별
        return "next_config"
    return None

# print(detect_files(input("Enter the path to scan for files: ")))