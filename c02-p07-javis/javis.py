import os
import queue
import wave
from datetime import datetime

try:
    import sounddevice as sd
except ImportError:
    sd = None

RECORDS_DIR_NAME = 'records'
SAMPLE_RATE = 44100
CHANNELS = 1
SAMPLE_WIDTH = 2

def create_records_directory():
    try:
        os.makedirs(RECORDS_DIR_NAME, exist_ok=True)
    except OSError as error:
        print(f'[오류] records 폴더를 생성하는 중 문제가 발생했습니다: {error}')
        return False

    return True

def create_record_file_name():
    now = datetime.now()
    file_name = now.strftime('%Y%m%d-%H%M%S') + '.wav'

    return os.path.join(RECORDS_DIR_NAME, file_name)


def record_audio():
    if sd is None:
        print('[오류] sounddevice 라이브러리가 설치되어 있지 않습니다.')
        print('다음 명령어로 설치한 뒤 다시 실행하세요.')
        print('pip install sounddevice')
        return None
    
    if not create_records_directory():
        return None
    
    audio_queue = queue.Queue()
    record_file_path = create_record_file_name()

    def audio_callback(indata, frames, time_info, status):
        if status:
            print(f'[경고] 녹음 상태 메시지: {status}')

        audio_queue.put(bytes(indata))

    print('마이크 녹음을 시작합니다.')
    print('녹음을 종료하려면 Enter 키를 누르세요.')
    print(f'저장 예정 파일: {record_file_path}')

    try:
        with wave.open(record_file_path, 'wb') as wave_file:
            wave_file.setnchannels(CHANNELS)
            wave_file.setsampwidth(SAMPLE_WIDTH)
            wave_file.setframerate(SAMPLE_RATE)

            with sd.RawInputStream(
                samplerate=SAMPLE_RATE,
                blocksize=1024,
                dtype='int16',
                channels=CHANNELS,
                callback=audio_callback
            ):
                input()

                while not audio_queue.empty():
                    wave_file.writeframes(audio_queue.get())

        print('녹음이 완료되었습니다.')
        print(f'저장된 파일: {record_file_path}')

        return record_file_path
    
    except OSError as error:
        print(f'[오류] 파일을 저장하는 중 문제가 발생했습니다: {error}')
        return None
    except sd.PortAudioError as error:
        print(f'[오류] 마이크 장치를 사용하는 중 문제가 발생했습니다: {error}')
        return None
    
def main():
    record_audio

if __name__ == '__main__':
    main()