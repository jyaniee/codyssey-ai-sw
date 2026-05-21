import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PASSWORD_FILE_NAME = os.path.join(
    BASE_DIR,
    "..",
    "c02-p01-password-xxxxxx",
    "password.txt"
)

RESULT_FILE_NAME = os.path.join(BASE_DIR, "result.txt")

ALPHABET_COUNT = 26

def read_password_file():
    try:
        if not os.path.exists(PASSWORD_FILE_NAME):
            print(f"[오류] {PASSWORD_FILE_NAME} 파일을 찾을 수 없습니다.")
            return None
        
        with open(PASSWORD_FILE_NAME, "r", encoding="utf-8") as file:
            content = file.read().strip()

        if content == "":
            print(f"[오류] {PASSWORD_FILE_NAME} 파일이 비어 있습니다.")
            return None
        
        return content
    
    except OSError as error:
        print(f"[오류] 파일을 읽는 중 문제가 발생했습니다 : {error}")
        return None
    

def save_result(decoded_text):
    try:
        with open(RESULT_FILE_NAME, "w", encoding="utf-8") as file:
            file.write(decoded_text)

        print(f"{RESULT_FILE_NAME} 파일에 해독 결과를 저장했습니다.")

    except OSError as error:
        print(f"[오류] 결과 파일을 저장하는 중 문제가 발생했습니다.")


def shift_character(character, shift_count):
    if "a" <= character <= "z":
        base = ord("a")
        return chr((ord(character) - base - shift_count) % ALPHABET_COUNT + base)
    
    if "A" <= character <= "Z":
        base = ord("A")
        return chr((ord(character) - base - shift_count) % ALPHABET_COUNT + base)
    
    return character

def caesar_cipher_decode(target_text):
    decoded_results = []

    print("카이사르 암호 해독을 시작합니다.")
    print(f"대상 문자열: {target_text}")
    print("-" * 60)

    for shift_count in range(ALPHABET_COUNT):
        decoded_text = ""

        for character in target_text:
            decoded_text += shift_character(character, shift_count)
        
        decoded_results.append(decoded_text)

        print(f"[{shift_count:02d}] {decoded_text}")

    print("-" * 60)

    return decoded_results


def select_decoded_result(decoded_results):
    while True:
        selected_shift = input("해독된 것으로 보이는 자리수를 입력하세요. (0~25): ")
        
        try:
            selected_shift = int(selected_shift)

            if 0 <= selected_shift < ALPHABET_COUNT:
                return selected_shift
            
            print("[오류] 0부터 25 상잉의 숫자를 입력해야 합니다.")

        except ValueError:
            print("[오류] 숫자만 입력해야 합니다.")

def main():
    target_text = read_password_file()

    if target_text is None:
        return
    
    decoded_results = caesar_cipher_decode(target_text)

    selected_shift = select_decoded_result(decoded_results)
    final_result = decoded_results[selected_shift]

    print("-" * 60)
    print(f"선택한 자리수: {selected_shift}")
    print(f"최종 해독 결과: {final_result}")

    save_result(final_result)

if __name__ == "__main__":
    main()


