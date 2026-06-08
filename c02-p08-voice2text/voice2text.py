import csv
import os
import wave

try:
    import speech_recognition as sr
except ImportError:
    sr = None


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RECORDS_DIR_NAME = os.path.abspath(
    os.path.join(
        BASE_DIR,
        '..',
        'c02-p07-javis',
        'records'
    )
)

STT_CHUNK_SECONDS = 10


def get_record_files():
    try:
        if not os.path.exists(RECORDS_DIR_NAME):
            print(f'[오류] records 폴더를 찾을 수 없습니다: {RECORDS_DIR_NAME}')
            return []

        file_names = os.listdir(RECORDS_DIR_NAME)
        wav_files = []

        for file_name in file_names:
            if file_name.lower().endswith('.wav'):
                wav_files.append(os.path.join(RECORDS_DIR_NAME, file_name))

        wav_files.sort()

        return wav_files

    except OSError as error:
        print(f'[오류] 녹음 파일 목록을 불러오는 중 문제가 발생했습니다: {error}')
        return []


def print_record_files(record_files):
    if len(record_files) == 0:
        print('녹음된 음성 파일이 없습니다.')
        return

    print('녹음 파일 목록')
    print('-' * 60)

    for index, file_path in enumerate(record_files, start=1):
        print(f'{index}. {file_path}')

    print('-' * 60)


def select_record_file(record_files):
    while True:
        selected_number = input('텍스트로 변환할 음성 파일 번호를 입력하세요: ')

        try:
            selected_number = int(selected_number)

            if 1 <= selected_number <= len(record_files):
                return record_files[selected_number - 1]

            print('[오류] 목록에 있는 번호를 입력해야 합니다.')

        except ValueError:
            print('[오류] 숫자만 입력해야 합니다.')


def create_csv_file_name(audio_file_path):
    file_name_without_extension = os.path.splitext(audio_file_path)[0]

    return file_name_without_extension + '.csv'


def get_audio_duration(audio_file_path):
    try:
        with wave.open(audio_file_path, 'rb') as wave_file:
            frame_count = wave_file.getnframes()
            frame_rate = wave_file.getframerate()

            if frame_rate == 0:
                return 0

            return frame_count / frame_rate

    except wave.Error as error:
        print(f'[오류] WAV 파일 정보를 읽는 중 문제가 발생했습니다: {error}')
        return 0
    except OSError as error:
        print(f'[오류] 음성 파일을 읽는 중 문제가 발생했습니다: {error}')
        return 0


def format_audio_time(seconds):
    minutes = int(seconds // 60)
    remain_seconds = int(seconds % 60)

    return f'{minutes:02d}:{remain_seconds:02d}'


def speech_to_text(audio_file_path):
    if sr is None:
        print('[오류] SpeechRecognition 라이브러리가 설치되어 있지 않습니다.')
        print('다음 명령어로 설치한 뒤 다시 실행하세요.')
        print('pip install SpeechRecognition')
        return []

    recognizer = sr.Recognizer()
    duration = get_audio_duration(audio_file_path)
    stt_results = []

    if duration <= 0:
        print('[오류] 음성 파일의 길이를 확인할 수 없습니다.')
        return []

    print(f'STT 변환 시작: {audio_file_path}')
    print(f'음성 파일 길이: {duration:.2f}초')
    print('-' * 60)

    try:
        with sr.AudioFile(audio_file_path) as source:
            start_time = 0

            while start_time < duration:
                audio_data = recognizer.record(
                    source,
                    duration=STT_CHUNK_SECONDS
                )

                time_text = format_audio_time(start_time)

                try:
                    recognized_text = recognizer.recognize_google(
                        audio_data,
                        language='ko-KR'
                    )

                    stt_results.append({
                        'time': time_text,
                        'text': recognized_text
                    })

                    print(f'[{time_text}] {recognized_text}')

                except sr.UnknownValueError:
                    stt_results.append({
                        'time': time_text,
                        'text': ''
                    })

                    print(f'[{time_text}] 인식된 텍스트 없음')

                except sr.RequestError as error:
                    print(f'[오류] STT 요청 중 문제가 발생했습니다: {error}')
                    return stt_results

                start_time += STT_CHUNK_SECONDS

    except OSError as error:
        print(f'[오류] 음성 파일을 처리하는 중 문제가 발생했습니다: {error}')
        return []
    except ValueError as error:
        print(f'[오류] 음성 파일 형식이 올바르지 않습니다: {error}')
        return []

    return stt_results


def save_stt_result_to_csv(csv_file_path, stt_results):
    try:
        with open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['time', 'text'])

            for result in stt_results:
                writer.writerow([result['time'], result['text']])

        print(f'CSV 파일 저장 완료: {csv_file_path}')

    except OSError as error:
        print(f'[오류] CSV 파일을 저장하는 중 문제가 발생했습니다: {error}')


def convert_audio_to_text():
    record_files = get_record_files()
    print_record_files(record_files)

    if len(record_files) == 0:
        return

    selected_file = select_record_file(record_files)
    stt_results = speech_to_text(selected_file)

    if len(stt_results) == 0:
        print('[오류] 저장할 STT 결과가 없습니다.')
        return

    csv_file_path = create_csv_file_name(selected_file)
    save_stt_result_to_csv(csv_file_path, stt_results)


def main():
    convert_audio_to_text()


if __name__ == '__main__':
    main()