import itertools
import os
import time
import zipfile
from datetime import datetime
import zlib

ZIP_FILE_NAME = "emergency_storage_key.zip"
PASSWORD_FILE_NAME = "password.txt"

CHARACTERS = "0123456789abcdefghijklmnopqrstuvwxyz"
PASSWORD_LENGTH = 6

def format_elapsed_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{secs:05.2f}"

def save_password(password):
    try:
        with open(PASSWORD_FILE_NAME, "w", encoding="utf-8") as file:
            file.write(password)
    except OSError as error:
        print(f"[오류] 비밀번호 저장 중 문제가 발생했습니다: {error}")


def test_zip_password(zip_file, password):
    try:
        password_bytes = password.encode("utf-8")

        for file_info in zip_file.infolist():
            if file_info.is_dir():
                continue

            with zip_file.open(file_info, pwd=password_bytes) as file:
                file.read()

            return True
        return False
    
    except (RuntimeError, zlib.error, zipfile.BadZipFile):
        return False
        
    except OSError as error:
        print(f"[오류] ZIP 파일을 읽는 중 문제가 발생했습니다: {error}")
        raise

def unlock_zip():
    start_time = time.time()
    start_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    attempt_count = 0
    print_interval = 10000

    print("ZIP 비밀번호 대입 시작")
    print(f"시작 시간: {start_datetime}")
    print(f"대상 파일: {ZIP_FILE_NAME}")
    print(f"비밀번호 조건: 숫자와 소문자 알파벳으로 구성된 {PASSWORD_LENGTH}자리 문자")
    print("-" * 60)

    if not os.path.exists(ZIP_FILE_NAME):
        print(f"[오류] {ZIP_FILE_NAME} 파일을 찾을 수 없습니다.")
        return None
    
    try:
        with zipfile.ZipFile(ZIP_FILE_NAME, "r") as zip_file:
            file_list = zip_file.infolist()

            if len(file_list) == 0:
                print("[오류] ZIP 파일 안에 검사할 파일이 없습니다.")
                return None
            
            for candidate_tuple in itertools.product(CHARACTERS, repeat=PASSWORD_LENGTH):
                attempt_count += 1
                candidate_password = "".join(candidate_tuple)

                if test_zip_password(zip_file, candidate_password):
                    elapsed_time = time.time() - start_time

                    print("-" * 60)
                    print("비밀번호를 찾았습니다.")
                    print(f"비밀번호: {candidate_password}")
                    print(f"반복 횟수: {attempt_count}")
                    print(f"진행 시간: {format_elapsed_time(elapsed_time)}")

                    save_password(candidate_password)
                    print(f"{PASSWORD_FILE_NAME} 파일에 비밀번호를 저장했습니다.")

                    return candidate_password
                
                if attempt_count % print_interval == 0:
                    elapsed_time = time.time() - start_time
                    print(
                        f"반복 횟수: {attempt_count}, "
                        f"현재 시도: {candidate_password}, "
                        f"진행 시간: {format_elapsed_time(elapsed_time)}"
                    )

    except zipfile.BadZipFile:
        print("[오류] ZIP 파일 형식이 올바르지 않습니다.")
    except OSError as error:
        print(f"[오류] 파일 처리 중 문제가 발생했습니다: {error}")

    elapsed_time = time.time() - start_time
    print("-" * 60)
    print("비밀번호를 찾지 못했습니다.")
    print(f"총 반복 횟수: {attempt_count}")
    print(f"총 진행 시간: {format_elapsed_time(elapsed_time)}")

    return None

if __name__ == "__main__":
    unlock_zip()


