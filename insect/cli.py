import argparse
import engine

def main():
    # 1. 파서 객체 생성
    parser = argparse.ArgumentParser(prog="insect", description="프로그램에 대한 설명")
    subparsers = parser.add_subparsers(dest="command")

    # 2. 인자 정의하기
    # 위치 인자 추가
    scan_parser = subparsers.add_parser("scan", help="주어진 경로에 해당하는 파일의 보안 취약점을 스캔합니다")
    scan_parser.add_argument("path", type=str, help="스캔할 경로")
    # 옵션 인자 추가 (True/False 플래그 형태)
    # scan_parser.add_argument("-v", "--verbose", action="store_true", help="출력을 자세하게 표시합니다")

    # 3. 명령행 인자 파싱
    args = parser.parse_args()

    # 4. 파싱된 데이터 사용
    if args.command == "scan":
        files = engine.scan(args.path)
        # for file_path, filename, file_type in files:
        #     print(f"File: {filename}, Path: {file_path}, Type: {file_type}")
        print(f"Total files scanned: {len(files)}")

if __name__ == "__main__":
    main()