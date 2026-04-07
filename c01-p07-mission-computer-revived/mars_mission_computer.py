import random
import json
import time
import msvcrt

class DummySensor:
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }

    def set_env(self):
        self.env_values['mars_base_internal_temperature'] = round(
            random.uniform(18, 30), 2
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

    def get_env(self):
        return self.env_values

ds = DummySensor()

class MissionComputer:
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }
        self.env_history = []   # 5분 동안 측정된 환경값들을 저장하는 리스트, 5초에 1번 -> 5분: 60개

    def print_average(self):    # env_history에 5분 동안 쌓인 환경값들의 평균을 항목별로 계산해서 JSON 형태로 출력하기 위한 함수
        if not self.env_history:
            return
        
        average_values = {}
        keys = self.env_history[0].keys()   # 첫 번째(0) 측정값 딕셔너리에서 키 목록을 가져옴. (값을 제외한 'mars_base...'와 같은 텍스트 필드/이름들)

        for key in keys:    # key = 'mars-base..1' -> key = 'mars-base..2' -> .. 반복
            total = 0.0
            for item in self.env_history:   # 저장된 측정값 딕셔너리들을 하나식 꺼내면서 반복
                total += item[key]  # 현재 항목값 누적
            average_values[key] = round(total / len(self.env_history), 4)   # 합계를 개수로 나눠 평균을 구하고, 소수점 4자리수까지 반올림해서 저장
            # ex) average_values['mars_base_internal_temperature'] = 22.0
            
        print('=== 5분 평균 환경값 ===')
        print(json.dumps(average_values, indent = 4))

    def get_sensor_data(self):  # self: 이 메서드를 호출한 객체 자기 자신 RunComputer.get_sensonr_data() << self는 RunComputer 객체 자신
        start_time = time.time()
        
        while True:        
            if msvcrt.kbhit():  # 키보드 입력이 들어왔는지 확인
                key = msvcrt.getch().decode('utf-8').lower()    # getch: 입력된 키를 1글자 읽음
                if key == 'q':  # q 입력 시
                    print('System stopped....')
                    break
            
            ds.set_env()
            self.env_values = ds.get_env().copy()  # 62줄에서 self.env_values가 RunComputer.env_values 같은 의미
            self.env_history.append(self.env_values.copy()) # copy를 안 쓰면 같은 딕셔너리를 같이 바라보는 문제가 생겨, 
                                                            # 결과적으로 전부 마지막 값만 바라보면 평균 계산이 의미가 없어짐.
            
            print(json.dumps(self.env_values, indent = 4))  # dumps: 파이썬 객체 -> JSON 문자열로 바꾸는 함수, dump() = 파일에 저장, dumps() = 문자열로 반환(dump+string)
                                                            # indent: 들여쓰기를 공백 N칸 기준으로 해서 JSON을 깔끔하게 출력
            
            current_time = time.time()
            if current_time - start_time >= 300:
                self.print_average()
                self.env_history = []
                start_time = current_time

            time.sleep(5)

RunComputer = MissionComputer()
RunComputer.get_sensor_data()
