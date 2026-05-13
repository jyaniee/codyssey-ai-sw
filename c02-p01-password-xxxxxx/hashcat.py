import os
import re
import shutil
import subprocess
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ZIP_FILE_NAME = os.path.join(BASE_DIR, "emergency_storage_key.zip")
PASSWORD_FILE_NAME = os.path.join(BASE_DIR, "password.txt")
HASH_FILE_NAME = os.path.join(BASE_DIR, "zip_hash.txt")


HASHCAT_PATH = r"C:\tools\hashcat-7.1.2\hashcat.exe"
ZIP2JOHN_PATH = r"C:\tools\john-1.9.0-jumbo-1-win64\run\zip2john.exe"
# HASHCAT_PATH = "hashcat"
# ZIP2JOHN_PATH = "zip2john"

# 숫자 + 소문자 알파벳, 정확히 6자리
CUSTOM_CHARSET = "?l?d"
MASK = "?1?1?1?1?1?1"

# ZIP 종류에 따라 hashcat 모드가 달라질 수 있어서 여러 모드를 순서대로 시도
# 17200: PKZIP Compressed
# 17210: PKZIP Uncompressed
# 17220: PKZIP Compressed Multi-File
# 17225: PKZIP Mixed Multi-File
# 17230: PKZIP Checksum-Only 계열
# 13600: WinZip
HASHCAT_ZIP_MODES = [17200, 17210, 17220, 17225, 17230, 13600]


def format_elapsed_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{secs:05.2f}"


def find_command(command):
    if os.path.isabs(command) and os.path.exists(command):
        return command

    found_path = shutil.which(command)
    if found_path is not None:
        return found_path

    return None

def get_hashcat_working_directory(hashcat_command):
    return os.path.dirname(hashcat_command)

def save_password(password):
    try:
        with open(PASSWORD_FILE_NAME, "w", encoding="utf-8") as file:
            file.write(password)
    except OSError as error:
        print(f"[오류] 비밀번호 저장 중 문제가 발생했습니다: {error}")


def extract_zip_hash():
    zip2john_command = find_command(ZIP2JOHN_PATH)

    if zip2john_command is None:
        print("[오류] zip2john을 찾을 수 없습니다.")
        print("PATH에 zip2john을 등록하거나 ZIP2JOHN_PATH에 직접 경로를 지정하세요.")
        return False

    if not os.path.exists(ZIP_FILE_NAME):
        print(f"[오류] {ZIP_FILE_NAME} 파일을 찾을 수 없습니다.")
        return False

    print("ZIP 해시 추출 시작")
    print(f"사용 도구: {zip2john_command}")

    try:
        result = subprocess.run(
            [zip2john_command, ZIP_FILE_NAME],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore",
            check=False
        )

        output = result.stdout.strip()

        if not output:
            print("[오류] zip2john 실행 결과가 비어 있습니다.")
            if result.stderr:
                print(result.stderr.strip())
            return False

        with open(HASH_FILE_NAME, "w", encoding="utf-8") as file:
            file.write(output + "\n")

        print(f"해시 저장 완료: {HASH_FILE_NAME}")
        return True

    except OSError as error:
        print(f"[오류] zip2john 실행 중 문제가 발생했습니다: {error}")
        return False


def run_hashcat(mode):
    hashcat_command = find_command(HASHCAT_PATH)

    if hashcat_command is None:
        print("[오류] hashcat을 찾을 수 없습니다.")
        print("PATH에 hashcat을 등록하거나 HASHCAT_PATH에 직접 경로를 지정하세요.")
        return False

    print("-" * 60)
    print(f"Hashcat 실행 시작 - 모드 {mode}")

    command = [
        hashcat_command,
        "-m", str(mode),
        "-a", "3",
        HASH_FILE_NAME,
        "-1", CUSTOM_CHARSET,
        MASK,
        "--username",
        "--status",
        "--status-timer", "10",
        "-w", "4"
    ]

    print("실행 명령:")
    print(" ".join(command))

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="ignore",
            cwd=get_hashcat_working_directory(hashcat_command)
        )

        if process.stdout is not None:
            for line in process.stdout:
                line = line.rstrip()
                if line:
                    print(line)

        process.wait()

        # hashcat은 이미 crack된 경우, 새로 crack한 경우 등에서 반환 코드가 다를 수 있으므로
        # 종료 후 --show로 실제 비밀번호 존재 여부를 확인
        return check_hashcat_result(mode)

    except OSError as error:
        print(f"[오류] hashcat 실행 중 문제가 발생했습니다: {error}")
        return False


def check_hashcat_result(mode):
    hashcat_command = find_command(HASHCAT_PATH)

    command = [
        hashcat_command,
        "-m", str(mode),
        "--show",
        HASH_FILE_NAME,
        "--username"
    ]

    try:
        result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="ignore",
        check=False,
        cwd=get_hashcat_working_directory(hashcat_command)
    )

        output = result.stdout.strip()

        if not output:
            return False

        # 출력 예시:
        # emergency_storage_key.zip:$pkzip2$...$/pkzip2$:abc123
        # 또는
        # $pkzip2$...$/pkzip2$:abc123
        lines = output.splitlines()

        for line in lines:
            password = line.split(":")[-1].strip()

            if re.fullmatch(r"[a-z0-9]{6}", password):
                print("-" * 60)
                print("비밀번호를 찾았습니다.")
                print(f"비밀번호: {password}")

                save_password(password)
                print(f"{PASSWORD_FILE_NAME} 파일에 비밀번호를 저장했습니다.")
                return True

        return False

    except OSError as error:
        print(f"[오류] hashcat 결과 확인 중 문제가 발생했습니다: {error}")
        return False


def unlock_zip_fastest():
    start_time = time.time()
    start_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("ZIP 비밀번호 GPU 기반 대입 시작")
    print(f"시작 시간: {start_datetime}")
    print(f"대상 파일: {ZIP_FILE_NAME}")
    print("비밀번호 조건: 숫자와 소문자 알파벳으로 구성된 6자리 문자")
    print("공격 방식: Hashcat GPU Mask Attack")
    print("-" * 60)

    if not extract_zip_hash():
        return None

    for mode in HASHCAT_ZIP_MODES:
        found = run_hashcat(mode)

        if found:
            elapsed_time = time.time() - start_time
            print("-" * 60)
            print(f"전체 진행 시간: {format_elapsed_time(elapsed_time)}")
            return True

    elapsed_time = time.time() - start_time
    print("-" * 60)
    print("비밀번호를 찾지 못했습니다.")
    print("ZIP 암호화 방식과 hashcat 모드가 맞지 않거나, 조건 범위 안에 비밀번호가 없을 수 있습니다.")
    print(f"전체 진행 시간: {format_elapsed_time(elapsed_time)}")

    return None


if __name__ == "__main__":
    unlock_zip_fastest()