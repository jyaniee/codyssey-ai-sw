import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase, QFontInfo
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QPushButton,
    QLabel
)

def load_iphone_font(point_size, src):  # 샌프란시스코 폰트 로드 함수, point_size: 폰트 크기, src는 어디서 호출한 건지 구분하기 위한 문자열
    font_path = 'SF-Pro-Display-Medium.otf'
    font_id = QFontDatabase.addApplicationFont(font_path)

    if font_id != -1:   # 폰트 파일 로드 성공 시
        font_families = QFontDatabase.applicationFontFamilies(font_id)

        if font_families:   # 폰트 family 이름이 정상적으로 추출되면
            family = font_families[0]
            database = QFontDatabase()

            print(f'[{src}] 폰트 파일 로드 성공: {family}')
            print(f'[{src}] 사용 가능한 스타일: {database.styles(family)}')
            
            return QFont(family, point_size)    # 해당 family와 point_size로 폰트 객체 생성 후 반환
        
    print('폰트 파일 로드 실패: Arial 사용')
    return QFont('Arial', point_size)

class CalculatorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.current_input = '0'    # 현재 화면에 입력 중인 문자열
        self.stored_value = None    # 이전 숫자를 저장하는 변수: 12 + 3을 할 때 12는 stored_value에, 3은 current_input에, +는 pending_operator에
        self.pending_operator = None    #  현재 대기 중인 연산자, 사용자가 + 버튼을 누른 상태라면 pending_operator = '+'
        self.waiting_for_new_input = False  # 다음 숫자 입력을 새로 시작해야 하는지 여부: 12 입력 후 +를 눌렀을 때
                                            # 다음 숫자 입력을 이어 붙이는게 아니라 새로 시작해야함. 그것을 구분하는 플래그
        self.operator_buttons = {}  # 연산자 버튼들을 따로 저장하는 딕셔너리, 현재 선택된 연산자 버튼만 색을 반전시켜, 활성화되있는지 아닌지 구분하는 용도

        self.display_font = load_iphone_font(46, 'display')
        self.button_font = load_iphone_font(20, 'button')
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('iPhone Calculator UI')     # 창 제목
        self.setFixedSize(360, 640)                     # 창 크기
        self.setStyleSheet('background-color: black;')  # 전체 배경색

        main_layout = QVBoxLayout()                     # 전체 화면은 크게 두 덩어리, 1. 디스플레이 영역 2. 버튼 영역, 이걸 세로로 쌓기 위함
        main_layout.setContentsMargins(12, 20, 12, 20)  # 레이아웃 바깥 여백
        main_layout.setSpacing(12)                      # 디스플레이 영역과 버튼 영역 사이 간격

        self.display = QLabel('0')                                     # 디스플레이 라벨, 처음엔 0
        self.display.setAlignment(Qt.AlignRight | Qt.AlignBottom)      # 디스플레이 라벨 위치를 오른쪽 아래로 위치
        self.display.setStyleSheet(                                    # 디스플레이 스타일 지정
            'color: white;'
            'background-color: black;'
            'padding: 10px 0px 0px 10px;'
        )
        self.display.setFont(self.display_font)     # 폰트 지정
        print('폰트 적용 확인:', QFontInfo(self.display.font()).family())
        self.display.setFixedHeight(170)       # 디스플레이 영역 높이 지정 170px

        main_layout.addWidget(self.display)

        button_layout = QGridLayout()   # 계산기 버튼은 격자 구조라서 그리드 레이아웃이 적합
        button_layout.setHorizontalSpacing(10)  # 가로 간격 10
        button_layout.setVerticalSpacing(12)    # 세로 간격 12


        buttons = [
            [('AC', 'function'), ('+/-', 'function'), ('%', 'function'), ('÷', 'operator')],
            [('7', 'number'), ('8', 'number'), ('9', 'number'), ('×', 'operator')],
            [('4', 'number'), ('5', 'number'), ('6', 'number'), ('−', 'operator')],
            [('1', 'number'), ('2', 'number'), ('3', 'number'), ('+', 'operator')],
            [('0', 'number_wide'), ('.', 'number'), ('=', 'operator')]
        ]
        # 버튼 텍스트 + 버튼 타입을 같이 저장한 2차원 구조 리스트
        # 타입이 다른 버튼들은 서로 다른 스타일을 지정해줘야 하기 때문에 반복문에 조건부로 사용하기 위해 구분

        for row_index, row in enumerate(buttons):   # enumerate(buttons)는 행 번호와 행 데이터(row)를 같이 꺼내기 위해 사용
            column_index = 0

            for text, button_type in row:   # 각 행 안의 버튼을 하나씩 생성
                button = QPushButton(text)
                button.setFont(self.button_font)    # 폰트 지정
                #button.setFixedHeight(70)
                #button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                button.setFixedSize(70, 70)     # 70x70 가로세로 지정
                button.clicked.connect(self.handle_button_click)    # 클릭했을 때 실행되는 함수 지정: handle_button_click()

                if button_type == 'function':   # 타입이 function 이면 밝은 회색 배경의 버튼으로
                    button.setStyleSheet(
                        'QPushButton {'
                        'background-color: #a0a0a0;'    # a5a5a5
                        'color: black;'
                        'border: none;'
                        'border-radius: 35px;'
                        '}'
                        'QPushButton:pressed {'
                        'background-color: #bdbdbd;'
                        '}'
                    )
                elif button_type == 'operator':     # 타입이 연산자면, 주황 배경 버튼
                    button.setStyleSheet(self.get_operator_button_style(False))
                    self.operator_buttons[text] = button    # 아까 위에서 만들어 둔 빈 딕셔너리에 연산자들 저장
                                                            # (연산자 버튼의 글자text를 key로, 그 버튼의 객체button을 value로 저장)
                else:
                    button.setStyleSheet(   # 나머지 숫자 버튼들은 어두운 회색 버튼으로
                        'QPushButton {'
                        'background-color: #313131;'    # 333333
                        'color: white;'
                        'border: none;'
                        'border-radius: 35px;'
                        '}'
                        'QPushButton:pressed {'
                        'background-color: #4a4a4a;'
                        '}'
                    )

                if button_type == 'number_wide':    # 0 버튼은 가로 크기가 혼자 다르기 때문에 따로 number_wide 타입으로 지정 후 스타일도 따로 지정
                    button.setFixedSize(160, 70)
                    button.setStyleSheet(
                        'QPushButton {'
                        'background-color: #313131;'
                        'color: white;'
                        'border: none;'
                        'border-radius: 35px;'
                        'text-align: left;'
                        'padding-left: 28px;'
                        '}'
                        'QPushButton:pressed {'
                        'background-color: #4a4a4a;'
                        '}'
                    )
                    button_layout.addWidget(button, row_index, column_index, 1, 2)  # 위젯, 행, 열, 행으로 차지할 칸 수, 열로 차지할 칸 수
                    column_index += 2                                               # 0 버튼 혼자 가로로 두 칸 먹게끔
                else:
                    button_layout.addWidget(button, row_index, column_index)        # 나머지는 그대로 한 칸씩
                    column_index += 1                               

        main_layout.addLayout(button_layout)    # 만든 버튼 레이아웃 배치
        self.setLayout(main_layout)
        self.update_operator_button_styles()
        self.update_display()

    def get_operator_button_style(self, is_active = False):     # 연산자 활성화 표시용 함수
        if is_active:   # 활성화 시
            return (
            'QPushButton {'
            'background-color: white;'  # 배경 흰색
            'color: #f69906;'           # 글자 주황색
            'border: none;'
            'border-radius: 35px;'
            '}'
            'QPushButton:pressed {'
            'background-color: #e6e6e6;'
            'color: #f69906;'
            '}'
            )
        
        return (    # 활성화 X
            'QPushButton {'
            'background-color: #f69906;'    # 배경 주황
            'color: white;'                 # 글자 흰색
            'border: none;'
            'border-radius: 35px;'
            '}'
            'QPushButton:pressed {'
            'background-color: #ffad33;'
            'color: white;'
            '}'
        )
    
    def update_operator_button_styles(self):    # self.operator_buttons에 저장된 연산자 버튼들을 전부 순회하면서
                                                # 현재 self.pending_operator와 같은 버튼만 활성 스타일로 변경
        for operator, button in self.operator_buttons.items():
            is_active = operator == self.pending_operator
            button.setStyleSheet(self.get_operator_button_style(is_active))


    def format_display_text(self, text):    # 화면 표시용 포맷 함수
                                            # 1111111 입력 시 -> 1,111,111로 표기하기 위함
        if text in ('', 'Error'):       
            return text if text else '0'    # 빈 문자열이면 0, Error면 Error로 표시
        
        if '.' in text:     # 소수점이 있는 경우
            integer_part, decimal_part = text.split('.', 1)     # 정수 부분과 소수 부분을 나눔, 정수 부분에만 쉼표를 넣기 위함

            if integer_part in ('', '-'):   # 정수 부분이 비어있거나, 부호(-)만 있는 경우: .5, -.5 << 이런 경우 0.5, -0.5로 바꿔야함
                formatted_integer = integer_part + '0' if integer_part == '-' else '0'  # integer_part가 -이면 -0으로, 아니면 0 으로
            else:   # 정수 부분이 정상 숫자면
                formatted_integer = format(int(integer_part), ',')  # int로 바꾼 뒤 format 함수로 쉼표 넣기

            return f'{formatted_integer}.{decimal_part}'
        
        if text in ('-',):  # 부호만 있는 경우는 그대로 반환
            return text
        
        return format(int(text), ',')   # 일반 정수는 천 단위 쉼표 적용
        
        # if text.isdigit():
        #     return format(int(text), ',')
        
        # return text
    
    def update_display(self):   # 디스플레이 갱신
        self.display.setText(self.format_display_text(self.current_input))  # 현재 current_input 값을 화면에 다시 표시

    def get_current_value(self):        # 현재 입력 문자열을 실제 계산용 숫자(float)으로 바꾸는 함수
        if self.current_input in ('', '-', 'Error'):
            return 0.0
        
        return float(self.current_input)    # -> 그냥 float으로 리턴해주는 함수
    
    def calculate_result(self, left, operator, right):      # 계산 담당
        if operator == '+':
            return left + right
        if operator == '−':
            return left - right
        if operator == '×':
            return left * right
        if operator == '÷':
            if right == 0:      # 오른쪽 피연산자가 0이면 Error 반환
                return 'Error'
            return left / right
        return right
    
    def format_result_value(self, value):   # 계산 결과를 다시 문자열로 바꾸는 함수, 정수면 소수점 제거, 소수면 불필요한 0을 제거하기 위함
        if value == 'Error':
            return 'Error'
        
        if float(value).is_integer():   # 정수면
            return str(int(value))  # 문자열로 바꿔서 리턴
        
        # 소수면
        text = str(round(value, 10)).rstrip('0').rstrip('.')    # 소수점 10자리까지 반올림하고, 숫자를 문자열로 바꾸고,
                                                                # 문자열 오른쪽 끝에서 0제거하고, 마지막에 .만 남으면 그것도 지움
        return text
    
    def input_digit(self, digit):       # 숫자 버튼 처리, 0에서 7 -> 7, 12에서 3 -> 123, + 누른 직후 4 -> 새입력 4
                                        # digit은 눌린 숫자 문자열
        if self.current_input == 'Error':       # 현재 숫자가 Error면
            self.current_input = digit      # 새 숫자(digit)를 현재 입력값으로 넣고
            self.waiting_for_new_input = False  # 새 입력 대기 상태 해제
            self.update_display()       # 화면 갱신
            return
        
        if self.waiting_for_new_input:  # 새 입력 대기 상태일 때(연산자를 누른 직후)
            self.current_input = digit      # 현재 입력을 새 숫자(digit)으로 교체
            self.waiting_for_new_input = False  # 새 입력 대기 상태 해제
        elif self.current_input == '0':     # 현재 값이 0이면
            self.current_input = digit      # 0뒤에 숫자 붙이지 않고 그 숫자(digit)으로 교체
        else:
            self.current_input += digit     # 이미 정상 숫자이고 새 숫자를 누른 경우에는 그냥 뒤에 이어 붙임: 12에서 3 -> 123

        self.update_display()

    def input_decimal(self):    # 소수점 버튼 처리
        if self.current_input == 'Error':   # Error면 0. 부터 시작
            self.current_input = '0.'
            self.waiting_for_new_input = False
            self.update_display()
            return
        
        if self.waiting_for_new_input:  # 새 입력 대기 중이면 0. 시작
            self.current_input = '0.'
            self.waiting_for_new_input = False
        elif '.' not in self.current_input:     # .이 없으면
            self.current_input += '.'           # . 추가 (소수점 중복 입력 방지)

        self.update_display()

    def clear_all(self):    # AC 버튼
        self.current_input = '0'    # 현재 입력 중인 값
        self.stored_value = None    # 이전에 입력한 값
        self.pending_operator = None    # 현재 대기중인 연산자
        self.waiting_for_new_input = False  # 새 입력 대기 플래그
        self.update_operator_button_styles()    # 연산자 활성화 스타일 지정 
        self.update_display()

    def toggle_sign(self):  # 부호 반전 버튼 처리(+/- 버튼 동작)
        if self.current_input == 'Error':
            return
        
        if self.current_input.startswith('-'):  # 문자열이 특정 문자열로 시작하는지 확인하는 함수(-로 시작하는지 확인/ 음수인지)
            self.current_input = self.current_input[1:] # -(0번째 인덱스)를 제외한 그 이후 문자 모두: -1234 -> 1234
        elif self.current_input != '0':     # 음수가 아니면서 0이 아닐 때(양수 일 때), 0을 제외하는 이유는 0은 부호를 바꿔도 의미 없으니 -0 방지
            self.current_input = '-' + self.current_input # 맨 앞에 -붙이기

        self.update_display()

    def apply_percent(self):    # % 버튼 처리
        if self.current_input == 'Error':
            return
        
        value = self.get_current_value() / 100  # 계산해야하니까 문자열을 float으로 바꾸고 현재 값을 100으로 나눔
        self.current_input = self.format_result_value(value)    # 그 나눈 값을 다시 문자열로 보기좋게 바꿔줌
        self.update_display()

    def handle_operator(self, operator):    # +, −, ×, ÷ 눌렀을 때 처리
        if self.current_input == 'Error':
            return
        
        current_value = self.get_current_value()    # 현재 입력 값을 실수형으로 가져오고

        if self.stored_value is None:       # 아직 이전 값이 없으면
            self.stored_value = current_value   # 현재 입력 값을 저장
        elif self.pending_operator is not None and not self.waiting_for_new_input:  # 이미 이전값(저장값)이 있으면서, 연산자도 있고, 새 입력도 있으면
            # 예) 10 + 10 상태에서 = 말고 +(연산자)를 한 번 더 누른 상태
            result = self.calculate_result(self.stored_value, self.pending_operator, current_value)
            # 중간 계산 수행

            if result == 'Error':       # 계산 결과가 Error라면 상태 초기화
                self.current_input = 'Error'
                self.stored_value = None
                self.pending_operator = None
                self.waiting_for_new_input = True
                self.update_operator_button_styles()
                self.update_display()
                return
            
            self.stored_value = result      # 그 계산 결과를 다시 저장값(이전값)으로 넣어서 다음 계산에 활용되도록 함
            self.current_input = self.format_result_value(result)
            self.update_display()

        self.pending_operator = operator    # 새로 누른 연산자를 pending_operator에 저장
        self.waiting_for_new_input = True   # 이제 다음 숫자는 새로 입력받아야 하므로 True
        self.update_operator_button_styles()    # 연산자 버튼 색 반전 업데이트

    def handle_equal(self): # = 버튼 처리
        if self.current_input == 'Error':
            return
        
        if self.stored_value is None or self.pending_operator is None:  # 계산할 연산자가 없으면 아무 것도 하지 않음
            return
        
        # stored_value 와 pending_operator 가 있으면
        
        current_value = self.get_current_value()    # 입력되있는 문자열을 실수형으로 가져오고
        result = self.calculate_result(
            self.stored_value, 
            self.pending_operator, 
            current_value
        )
        # 계산해줌

        if result == "Error":   # 결과가 에러면
            self.current_input = 'Error'    # 표기도 Error로
        else:
            self.current_input = self.format_result_value(result)   # format_result_value로 정리(문자열로 변환)함

        self.stored_value = None    # 계산이 끝났으니 왼쪽 피연산자값 초기화
        self.pending_operator = None    # 연산자도 초기화
        self.waiting_for_new_input = True   # 새 입력 해야하니 True
        self.update_operator_button_styles()    # 연산자 버튼 색 반전 상태도 갱신
        self.update_display()

    def handle_button_click(self):  # 모든 버튼 클릭 이벤트 처리
        button = self.sender()  # 이 함수를 호출하게 만든 객체, 즉 방금 눌린 버튼 객체 반환
        text = button.text()    # 방금 눌린 버튼에 적혀있는 글자를 가져옴

        if text.isdigit():  # 문자열이 숫자로만 이루어져있는지 확인함(숫자면)
            self.input_digit(text)  # 숫자면 input_digit() 호출
        elif text == '.':   # .이면
            self.input_decimal()    # input_decimal() 호출
        elif text == 'AC':      # AC이면
            self.clear_all()    # clear_all() 호출
        elif text == '+/-':     # +/-면
            self.toggle_sign()  # toggle_sign() 호출
        elif text == '%':       # %면
            self.apply_percent()    # apply_percent() 호출
        elif text in ('+', '−', '×', '÷'):  # '+', '−', '×', '÷' 중 하나이면
            self.handle_operator(text)  # handle_operator() 호출
        elif text == '=':       # = 이면
            self.handle_equal() # handle_equal() 호출

        # if text == 'AC':
        #    self.current_text = '0'
        # else:
        #     if self.current_text == '0':
        #         self.current_text = text
        #     else:
        #         self.current_text += text
        
        # self.display.setText(self.format_display_text(self.current_text))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calculator = CalculatorUI()
    calculator.show()
    sys.exit(app.exec_())