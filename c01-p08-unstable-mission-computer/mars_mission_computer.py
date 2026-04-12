import json
import platform
import psutil   # 시스템 및 프로세스 정보, CPU 사용률, 메모리 정보를 가져오는 대표적인 파이썬 라이브러리
                # PyPl 기준 최신 안정 버전은 7.2.2

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
        self.settings = self.load_settings()    # setting.txt 읽어서 출력할 항목 목록을 변수에 저장

    def load_settings(self):    # setting.txt를 읽어서 한 줄씩 리스트에 넣음
        try:
            with open('setting.txt', 'r', encoding = 'utf-8') as file:
                lines = file.readlines()
            
            setting_list = []

            for line in lines:
                item = line.strip()
                if item != '':
                    setting_list.append(item)

            return setting_list
        
        except FileNotFoundError:
            print('setting.txt 파일을 찾을 수 없습니다.')
            return []
        except UnicodeDecodeError:
            print('setting.txt 파일의 인코딩을 읽을 수 없습니다.')
            return []
        except PermissionError:
            print('setting.txt 파일을 읽을 권한이 없습니다.')
            return []
        except OSError as error:
            print(f'setting.txt 파일을 읽는 중 오류가 발생했습니다: {error}')
            return []
        
    def filter_output(self, data):
        filtered_data = {}

        for key, value in data.items():
            if key in self.settings:
                filtered_data[key] = value

        return filtered_data

    def get_mission_computer_info(self):
        try:
            memory_info = psutil.virtual_memory()   # 메모리 정보를 여러 값과 함께 반환하는 함수
                                                    # 그중 .total은 총 메모리 크기, .percent는 메모리 사용률 %

            computer_info = {
                'operating_system': platform.system(),
                'operating_system_version': platform.version(),
                'cpu_type': platform.processor(),
                'cpu_core_count': psutil.cpu_count(logical = True),    # 논리 코어 수를 반환(문제에서 따로 코어를 언급하지 않았으니 운영체제가 실제 활용하는 기준에 가까운 논리 코어 수를 사용)
                                                                        # CPU 코어 수는 보통 두 가지: 1 - 물리코어, 2 - 논리 코어
                                                                        # 물리 코어: 진짜 코어 개수(CPU가 실제로 8코어라면 물리 코어는 8)
                                                                        # 논리 코어: 하이퍼스레딩 같은 기술까지 포함해서, 운영체제가 인식하는 실행 단위 개수
                                                                        #   -> 8코어 16스레드 CPU라면 논리 코어는 16
                'memory_size_gb': round(memory_info.total / (1024 ** 3), 3) # 소수점 3자리수까지 남기고 반올림
                # 1024 ** 3 이유
                # psutil.virtual_memory().total은 보통 메모리 크기를 바이트 단위로 줌
                # 사람이 보기엔 숫자가 너무 커져서 기가바이트(GB)로 바꾸기 위함
                # 1GB = 1024MB, 1MB = 1024KB, 1KB = 1024byte
                # 즉 byte -> GB로 바꾸려면 1024를 3번 나눠야하므로 1024^3으로 나눔
                # 예시) memory_info.total = 34359738368
                #   -> 34359738368 / (1024 ** 3) = 32.0
                #   -> 32GB
            }

            filtered_info = self.filter_output(computer_info)
            
            print('=== Mision Computer System Information ===')
            # print(json.dumps(computer_info, indent = 4))
            print(json.dumps(filtered_info, indent = 4))

        except Exception as error:
            print(f'시스템 정보를 가져오는 중 오류가 발생했습니다: {error}')

    def get_mission_computer_load(self):
        try:
            cpu_usage = psutil.cpu_percent(interval = 1)    # interval = 1: 1초 동안의 CPU 사용률을 측정
            memory_usage = psutil.virtual_memory().percent  # .percent: 사용률을 퍼센트로 제공

            computer_load = {
                'cpu_usage_percent': cpu_usage,
                'memory_usage_percent': memory_usage
            }

            filtered_load = self.filter_output(computer_load)

            print('=== Mission Computer Load Information ===')
            # print(json.dumps(computer_load, indent = 4))
            print(json.dumps(filtered_load, indent = 4))

        except Exception as error:
            print(f'시스템 부하 정보를 가져오는 중 오류가 발생했습니다: {error}')

runComputer = MissionComputer()
runComputer.get_mission_computer_info()
runComputer.get_mission_computer_load()
