import random

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
    
    def get_env(self):  # 저장된 env_values 딕셔너리 반환
        return self.env_values
    
ds = DummySensor()  # 클래스 인스턴스화
ds.set_env()
env_data = ds.get_env()

for key, value in env_data.items():
    print(f'{key}: {value}')
