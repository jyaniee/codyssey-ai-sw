import random
from datetime import datetime   # 파이썬 기본 라이브러리

class DummySensor:  # 클래스 정의
    def __init__(self): # 객체가 생성될 때 실행되는 초기화 메서드. env_values 딕셔너리를 멤버로 만듬.
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }
    
    def set_env(self):  # 센서값들을 랜덤으로 채움
        self.env_values['mars_base_internal_temperature'] = round(  # round - 소수점 n자리까지 반올림
            random.uniform(18, 30), 2   # uniform - 두 수 사이의 랜덤한 소수를 리턴시켜주는 함수
        )
        self.env_values['mars_base_external_temperature'] = round(
            random.uniform(0, 21), 2
        )
        self.env_values['mars_base_internal_humidity'] = round(
            random.uniform(50, 60), 2
        )
        self.env_values['mars_base_external_illuminance'] = round(
            random.uniform(500, 715), 2
        )
        self.env_values['mars_base_internal_co2'] = round(
            random.uniform(0.02, 0.1), 4
        )
        self.env_values['mars_base_internal_oxygen'] = round(
            random.uniform(4, 7), 2
        )
    
    def get_env(self):  # 저장된 env_values 딕셔너리 반환 + 보너스 과제
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # 현재 시간 가져오기, str(ing)f(ormat)time (시간을 문자열 형식으로)
                                                # 2026-03-31 00:15:22
        log_line = (    # 로그 한 줄 만들기
      f'datetime: {current_time}\n'
        f'mars_base_internal_temperature: '
        f'{self.env_values["mars_base_internal_temperature"]}\n'
        f'mars_base_external_temperature: '
        f'{self.env_values["mars_base_external_temperature"]}\n'
        f'mars_base_internal_humidity: '
        f'{self.env_values["mars_base_internal_humidity"]}\n'
        f'mars_base_external_illuminance: '
        f'{self.env_values["mars_base_external_illuminance"]}\n'
        f'mars_base_internal_co2: '
        f'{self.env_values["mars_base_internal_co2"]}\n'
        f'mars_base_internal_oxygen: '
        f'{self.env_values["mars_base_internal_oxygen"]}\n'
        f'----------------------------------------\n'
        )
        # 2026-03-31 00:15:22, 24.31, 7.52, 55.81, 601.42, 0.0834, 5.62
        # datetime: 2026-03-30 23:29:14, mars_base_internal_temperature: 27.61, mars_base_external_temperature: 5.34, mars_base_internal_humidity: 52.91, mars_base_external_illuminance: 589.89, mars_base_internal_co2: 0.0952, mars_base_internal_oxygen: 4.91
        
        # datetime: 2026-03-30 23:31:06
        # mars_base_internal_temperature: 29.55
        # mars_base_external_temperature: 14.84
        # mars_base_internal_humidity: 51.14
        # mars_base_external_illuminance: 595.15
        # mars_base_internal_co2: 0.0211
        # mars_base_internal_oxygen: 6.5
        # ----------------------------------------

        try:
            with open('mars_env_log.txt', 'a', encoding = 'utf-8') as file: # a는 append 모드, 기존 내용을 지우지 않고 뒤에 계속 추가
                file.write(log_line)
        except PermissionError:
            print('mars_env_log.txt 파일에 로그를 저장할 권한이 없습니다.')
        except OSError as error:
            print(f'로그 파일 저장 중 오류가 발생했습니다: {error}')

        return self.env_values
    
ds = DummySensor()  # 클래스 인스턴스화
ds.set_env()
env_data = ds.get_env()

for key, value in env_data.items():
    print(f'{key}: {value}')
