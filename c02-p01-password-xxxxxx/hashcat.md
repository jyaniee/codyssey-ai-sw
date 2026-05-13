# Hashcat을 이용한 ZIP 비밀번호 고속 대입 실험

## 1. 개요

기존 `door_hacking.py`는 Python의 `zipfile` 모듈과 `multiprocessing`을 이용하여 ZIP 파일의 비밀번호를 무차별 대입 방식으로 찾도록 구현하였다.

하지만 비밀번호 조건이 숫자와 소문자 알파벳으로 이루어진 6자리 문자열이기 때문에 전체 경우의 수는 다음과 같다.

```text
36^6 = 2,176,782,336
```
Python 기반 구현에서는 전체 경우의 수가 매우 크기 때문에, 병렬 처리를 적용하더라도 실행 시간이 길어질 수 있다.

따라서 별도 실험으로 GPU 기반 비밀번호 복구 도구인 Hashcat을 사용하여 같은 조건의 비밀번호를 더 빠르게 찾는 방식을 구현하였다.

---
## 2. 사용 도구
이번 실험에서는 다음 도구를 사용하였다.

| 도구                                   | 역할                             |
| ------------------------------------ | ------------------------------ |
| John the Ripper Jumbo `zip2john.exe` | ZIP 파일에서 해시 추출                 |
| Hashcat                              | 추출된 해시를 대상으로 GPU 기반 비밀번호 대입 수행 |
| Python `subprocess`                  | 외부 도구 실행 자동화                   |

`zip2john.exe`는 ZIP 파일을 Hashcat이나 John the Ripper가 처리할 수 있는 해시 문자열 형태로 변환하는 데 사용하였다.

Hashcat은 추출된 해시를 대상으로 마스크 공격을 수행하여 비밀번호 후보를 빠르게 대입하였다.

---
## 3. 전체 동작 흐름
```text
1. emergency_storage_key.zip 파일 확인
2. zip2john.exe 실행
3. ZIP 파일에서 해시 추출
4. zip_hash.txt 파일로 해시 저장
5. Hashcat 실행
6. 숫자 + 소문자 알파벳 6자리 마스크 공격 수행
7. 비밀번호 발견 여부 확인
8. 찾은 비밀번호를 password.txt에 저장
```
Python 코드가 직접 ZIP 파일을 반복해서 열어보는 것이 아니라, Python은 외부 도구 실행을 자동화하는 역할을 한다.

실제 비밀번호 대입은 Hashcat이 수행한다.

---
## 4. 마스크 공격 조건
문제에서 제시된 비밀번호 조건은 다음과 같다.
```text
특수문자 없음
숫자 사용 가능
소문자 알파벳 사용 가능
총 6자리
```
Hashcat에서는 이를 다음과 같은 마스크로 표현하였다.
```text
?1?1?1?1?1?1
```
그리고 `?1`에 들어갈 문자 집합은 다음과 같이 지정하였다.
```text
?l?d
```
의미는 다음과 같다.

| 표현             | 의미                         |
| -------------- | -------------------------- |
| `?l`           | 소문자 알파벳                    |
| `?d`           | 숫자                         |
| `?1`           | 사용자 정의 문자 집합               |
| `?1?1?1?1?1?1` | 사용자 정의 문자 집합으로 구성된 6자리 문자열 |

즉, 최종적으로 다음 조건의 모든 문자열을 검사한다.
```text
[a-z0-9]{6}
```

---

## 5. 주요 코드 설명
### 5.1 도구 경로 설정
Hashcat과 zip2john을 실행하기 위해 각 실행 파일의 경로를 지정하였다.
```python
HASHCAT_PATH = r"C:\tools\hashcat-7.1.2\hashcat.exe"
ZIP2JOHN_PATH = r"C:\tools\john-1.9.0-jumbo-1-win64\run\zip2john.exe"
```
환경 변수에 등록하지 않아도 Python 코드에서 직접 실행할 수 있도록 절대경로를 사용하였다.

---
### 5.2 파일 경로 설정
Hashcat 실행 시 작업 디렉터리가 달라져도 파일을 안정적으로 찾을 수 있도록, 현재 Python 파일 위치를 기준으로 경로를 생성하였다.
```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ZIP_FILE_NAME = os.path.join(BASE_DIR, "emergency_storage_key.zip")
PASSWORD_FILE_NAME = os.path.join(BASE_DIR, "password.txt")
HASH_FILE_NAME = os.path.join(BASE_DIR, "zip_hash.txt")
```
이를 통해 어느 위치에서 Python 파일을 실행하더라도 같은 폴더에 있는 ZIP 파일과 결과 파일을 사용할 수 있다.
---
### 5.3 ZIP 해시 추출
`extract_zip_hash()` 함수는 `zip2john.exe`를 실행하여 ZIP 파일의 해시를 추출한다.
```python
result = subprocess.run(
    [zip2john_command, ZIP_FILE_NAME],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding="utf-8",
    errors="ignore",
    check=False
)
```
실행 결과로 출력된 해시는 `zip_hash.txt` 파일에 저장된다.
```python
with open(HASH_FILE_NAME, "w", encoding="utf-8") as file:
    file.write(output + "\n")
```
---
### 5.4 Hashcat 실행
`run_hashcat()` 함수는 Hashcat을 실행하여 마스크 공격을 수행한다.
```python
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
```
각 옵션의 의미는 다음과 같다.
| 옵션                  | 의미                          |
| ------------------- | --------------------------- |
| `-m`                | 해시 타입 지정                    |
| `-a 3`              | 마스크 공격 모드                   |
| `-1 ?l?d`           | 사용자 정의 문자 집합 설정             |
| `?1?1?1?1?1?1`      | 6자리 비밀번호 후보 생성              |
| `--username`        | 해시 파일 앞쪽의 파일명 부분을 사용자명처럼 무시 |
| `--status`          | 진행 상태 출력                    |
| `--status-timer 10` | 10초마다 상태 출력                 |
| `-w 4`              | 높은 성능 우선 설정                 |

---
### 5.5 Hashcat 작업 디렉터리 설정
처음에는 Hashcat 실행 시 다음 오류가 발생하였다.
```text
./OpenCL/: No such file or directory
```
이는 `hashcat.exe`만 절대경로로 실행하고, 작업 디렉터리는 과제 폴더로 유지되었기 때문에 발생한 문제였다.

Hashcat은 실행 시 자기 폴더 안의 `OpenCL` 디렉터리 등을 참조하므로, 실행 작업 디렉터리를 Hashcat 폴더로 지정해야 한다.

이를 위해 다음 함수를 추가하였다.
```python
def get_hashcat_working_directory(hashcat_command):
    return os.path.dirname(hashcat_command)
```
그리고 `subprocess.Popen()` 실행 시 `cwd`를 지정하였다.
```python
process = subprocess.Popen(
    command,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding="utf-8",
    errors="ignore",
    cwd=get_hashcat_working_directory(hashcat_command)
)
```
이후 Hashcat이 정상적으로 GPU 장치를 인식하였다.

---
## 6. Hashcat 모드
ZIP 파일의 암호화 방식에 따라 Hashcat의 모드 번호가 달라질 수 있다.

따라서 코드에서는 여러 ZIP 관련 모드를 순서대로 시도하도록 작성하였다.
```python
HASHCAT_ZIP_MODES = [17200, 17210, 17220, 17225, 17230, 13600]
```
각 모드는 ZIP 파일의 압축 방식이나 암호화 방식에 따라 다르게 적용될 수 있다.

하나의 모드에서 비밀번호를 찾으면 나머지 모드는 실행하지 않고 종료한다.

---

## 7. 실행 결과
Hashcat 실행 중 GPU 장치가 정상적으로 인식되었다.
```text
OpenCL API (OpenCL 3.0 CUDA 13.2.73) - Platform #1 [NVIDIA Corporation]
Device #01: NVIDIA GeForce RTX 4060
```
초기에는 CUDA 관련 경고가 출력되었지만, OpenCL 런타임으로 전환되어 GPU를 정상적으로 사용할 수 있었다.
```text
Falling back to OpenCL runtime.
```
이후 Hashcat이 ZIP 해시를 정상적으로 읽고 마스크 공격을 수행하였다.
```text
Parsed Hashes: 1/1 (100.00%)
Hashes: 1 digests; 1 unique digests, 1 unique salts
Optimizers applied:
* Not-Iterated
* Single-Hash
* Single-Salt
* Brute-Force
```
실행 결과, 기존 Python 기반 방식보다 훨씬 빠르게 비밀번호를 찾을 수 있었다.

---

## 8. 기존 Python 방식과의 차이
| 구분       | Python 방식            | Hashcat 방식           |
| -------- | -------------------- | -------------------- |
| 실행 방식    | Python이 직접 ZIP 파일 열기 | Hashcat이 해시 기반 대입 수행 |
| 병렬화      | CPU 멀티프로세싱           | GPU 병렬 연산            |
| 속도       | 상대적으로 느림             | 매우 빠름                |
| 과제 조건 충족 | 충족                   | 외부 도구 사용으로 제출용에는 부적합 |
| 목적       | 과제 제출용 구현            | 성능 비교 및 실험용 구현       |

Python 방식은 과제 조건을 만족하는 구현이지만, 모든 후보 비밀번호마다 ZIP 파일을 직접 열고 읽어야 하므로 실행 시간이 길다.

반면 Hashcat 방식은 ZIP 파일에서 추출한 해시를 대상으로 GPU 기반 대입을 수행하므로 훨씬 빠르게 탐색할 수 있다.

---

## 9. 주의사항
이 방식은 외부 도구인 John the Ripper와 Hashcat을 사용한다.

따라서 문제의 제약사항인 “Python 기본 제공 명령어 이외의 별도 라이브러리나 패키지를 사용하지 않는다”는 조건에는 맞지 않을 수 있다.

그러므로 이 코드는 과제 제출용 핵심 구현이 아니라, 비밀번호 대입 작업의 성능 차이를 비교하기 위한 추가 실험 코드로 분리하였다.

제출용 핵심 코드는 `door_hacking.py`이며, 이 문서에서 설명한 Hashcat 기반 코드는 `hashcat.py`에서 별도로 관리한다.

---

## 10. 느낀점
이번 실험을 통해 같은 무차별 대입 방식이라도 구현 방식과 실행 환경에 따라 성능 차이가 매우 크다는 것을 확인할 수 있었다.

Python으로 직접 ZIP 파일을 반복해서 검사하는 방식은 구현이 쉽고 과제 조건에 적합하지만, 전체 경우의 수가 커질수록 실행 시간이 급격히 증가한다.

반면 Hashcat은 GPU의 병렬 연산 능력을 활용하여 매우 빠른 속도로 후보 비밀번호를 검사할 수 있었다. 실제 실행 결과, Python 기반 방식에서는 수 시간이 예상되던 작업을 Hashcat 기반 방식에서는 약 1분 내외로 완료할 수 있었다.

이를 통해 비밀번호 보안에서 단순히 “길이가 짧은 비밀번호”는 GPU 기반 대입 공격에 매우 취약할 수 있다는 점도 확인할 수 있었다.
