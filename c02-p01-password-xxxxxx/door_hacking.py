import itertools
import os
import time
import zipfile
from datetime import datetime
import zlib
import multiprocessing

ZIP_FILE_NAME = "emergency_storage_key.zip"
PASSWORD_FILE_NAME = "password.txt"

CHARACTERS = "0123456789abcdefghijklmnopqrstuvwxyz"
PASSWORD_LENGTH = 6
TOTAL_CASES = len(CHARACTERS) ** PASSWORD_LENGTH


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

def worker(prefix):
    local_attempt_count = 0

    try:
        with zipfile.ZipFile(ZIP_FILE_NAME, "r") as zip_file:
            remaining_length = PASSWORD_LENGTH - len(prefix)

            for candidate_tuple in itertools.product(CHARACTERS, repeat=remaining_length):
                password = prefix + "".join(candidate_tuple)
                local_attempt_count += 1

                if test_zip_password(zip_file, password):
                    return password, local_attempt_count

    except zipfile.BadZipFile:
        return None, local_attempt_count
    except OSError:
        return None, local_attempt_count

    return None, local_attempt_count

def unlock_zip():
    start_time = time.time()
    start_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("ZIP 비밀번호 병렬 대입 시작")
    print(f"시작 시간: {start_datetime}")
    print(f"대상 파일: {ZIP_FILE_NAME}")
    print(f"비밀번호 조건: 숫자와 소문자 알파벳으로 구성된 {PASSWORD_LENGTH}자리 문자")
    print(f"전체 경우의 수: {TOTAL_CASES:,}")
    print(f"사용 CPU 코어 수: {multiprocessing.cpu_count()}")
    print("-" * 60)

    if not os.path.exists(ZIP_FILE_NAME):
        print(f"[오류] {ZIP_FILE_NAME} 파일을 찾을 수 없습니다.")
        return None

    PREFIX_LENGTH = 3
    prefixes = []

    for prefix_tuple in itertools.product(CHARACTERS, repeat=PREFIX_LENGTH):
        prefixes.append("".join(prefix_tuple))

    print(f"작업 분할 기준: 앞 {PREFIX_LENGTH}자리")
    print(f"전체 작업 수: {len(prefixes):,}")
    print("-" * 60)

    total_attempt_count = 0
    completed_task_count = 0
    progress_print_interval = 10

    try:
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            for result_password, attempt_count in pool.imap_unordered(worker, prefixes):
                total_attempt_count += attempt_count
                completed_task_count += 1

                elapsed_time = time.time() - start_time
                attempts_per_second = total_attempt_count / elapsed_time if elapsed_time > 0 else 0
                progress_rate = (total_attempt_count / TOTAL_CASES) * 100

                if attempts_per_second > 0:
                    remaining_count = TOTAL_CASES - total_attempt_count
                    estimated_remaining_time = remaining_count / attempts_per_second
                else:
                    estimated_remaining_time = 0

                if completed_task_count % progress_print_interval == 0:
                    print(
                        f"완료 작업 수: {completed_task_count:,}/{len(prefixes):,}, "
                        f"누적 반복 횟수: {total_attempt_count:,}, "
                        f"진행률: {progress_rate:.6f}%, "
                        f"초당 시도: {attempts_per_second:,.2f}회, "
                        f"진행 시간: {format_elapsed_time(elapsed_time)}, "
                        f"예상 남은 시간: {format_elapsed_time(estimated_remaining_time)}"
                    )

                if result_password is not None:
                    elapsed_time = time.time() - start_time

                    print("-" * 60)
                    print("비밀번호를 찾았습니다.")
                    print(f"비밀번호: {result_password}")
                    print(f"반복 횟수: {total_attempt_count:,}")
                    print(f"진행 시간: {format_elapsed_time(elapsed_time)}")

                    save_password(result_password)
                    print(f"{PASSWORD_FILE_NAME} 파일에 비밀번호를 저장했습니다.")

                    pool.terminate()
                    return result_password

    except KeyboardInterrupt:
        print("\n[중단] 사용자가 프로그램을 중단했습니다.")
        return None

    elapsed_time = time.time() - start_time

    print("-" * 60)
    print("비밀번호를 찾지 못했습니다.")
    print(f"총 반복 횟수: {total_attempt_count:,}")
    print(f"총 진행 시간: {format_elapsed_time(elapsed_time)}")

    return None


if __name__ == "__main__":
    multiprocessing.freeze_support()
    unlock_zip()


