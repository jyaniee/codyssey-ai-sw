import sys  # PyQt 프로그램 종료 처리에 필요한 sys 모듈
from PyQt5.QtCore import Qt # 정렬 옵션(오른쪽 정렬, 아래 정렬 등)을 사용하기 위함
from PyQt5.QtGui import QFont, QFontDatabase, QFontInfo # 폰트 객체 생성용 QFont, 폰트 파일 로드용 QFontDatabase, 실제 적용된 폰트 확인용 QFontInfo를 불러온다.
from PyQt5.QtWidgets import (
    QApplication, 
    QWidget,   
    QGridLayout,  
    QVBoxLayout, 
    QPushButton,   
    QLabel 
)

def load_iphone_font(point_size, src):  # 샌프란시스코 폰트 로드 함수, point_size: 폰트 크기, src는 어디서 호출한 건지 구분하기 위한 문자열
    font_path = 'SF-Pro-Display-Medium.otf' # 불러올 폰트 파일 경로 지정
    font_id = QFontDatabase.addApplicationFont(font_path)   # 지정한 폰트 파일을 현재 프로그램에 등록
    
    if font_id != -1:   # font_id가 -1이 아니면 폰트 파일 로드에 성공했다는 뜻
        font_families = QFontDatabase.applicationFontFamilies(font_id)  # 지정된 애플리케이션 글꼴에 대한 글꼴 패밀리 목록을 반환
        if font_families:   # 폰트 family 이름이 정상적으로 추출되면
            family = font_families[0]   # 첫 번째 family 이름을 family 변수에 저장(반환 값이 QStringList이라서)

            print(f'[{src}] 폰트 파일 로드 성공: {family}') # 어떤 위치(src)에서 폰트가 성공적으로 로드되었는지 출력
            
            return QFont(family, point_size)    # 로드한 family 이름과 원하는 크기로 QFont 객체를 만들어 반환
        
    print('폰트 파일 로드 실패: Arial 사용')    # 위의 과정이 실패하면 폰트 로드 실패 메시지를 출력
    return QFont('Arial', point_size)   # 실패 시 Arial 폰트로 대체한 QFont 객체를 반환

class CalculatorUI(QWidget):
    def __init__(self): # 객체가 생성될 때 자동으로 실행되는 초기화 메서드
        super().__init__()  # 부모 클래스(QWidget)의 초기화도 같이 수행
        self.current_text = '0'     # 현재 화면에 입력 중인 문자열을 저장하는 변수

        self.display_font = load_iphone_font(46, 'display') # 디스플레이용 폰트 만들고, 로그 구분을 위해 'display'도 전달
        self.button_font = load_iphone_font(20, 'button')   # 버튼용 폰트 만들고, 'button' 문자열도 전달
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('iPhone Calculator UI') # 창 제목
        self.setFixedSize(360, 640) # 창 크기 고정 360 x 640
        self.setStyleSheet('background-color: black;')  # 배경색 검정

        main_layout = QVBoxLayout() # 전체 화면은 디스플레이 영역 + 버튼 영역의 세로 구조
        main_layout.setContentsMargins(12, 20, 12, 20)  # 왼, 위, 오, 아 순으로 마진 설정
        main_layout.setSpacing(12)  # 디스플레이 영역과 버튼 영역의 간격을 12로 설정

        self.display = QLabel('0')  # 숫자를 표시할 디스플레이 라벨 만듬
        self.display.setAlignment(Qt.AlignRight | Qt.AlignBottom)   # 디스플레이 글자를 오른쪽 하단에 배치
        self.display.setStyleSheet( # 디스플레이의 글자색, 배경, 내부 여백 설정
            'color: white;'
            'background-color: black;'
            'padding: 10px 0px 0px 10px;'
        )
        self.display.setFont(self.display_font) # 디스플레이에 위에서 만들어놨던 display_font를 적용
        print('display 실제 적용 폰트:', QFontInfo(self.display.font()).family())   # 실제 적용되었는지 QFontInfo로 확인
        self.display.setFixedHeight(170)    # 디스플레이 영역의 높이를 170으로 지정

        main_layout.addWidget(self.display) # 디스플레이 라벨을 메인 레이아웃에 추가

        button_layout = QGridLayout()   # 계산기 버튼들을 격자 형태로 배치하기 위해 QGridLayout을 만듬
        button_layout.setHorizontalSpacing(10)  # 버튼들 사이의 가로 간격을 10으로 지정
        button_layout.setVerticalSpacing(12)    # 버튼들 사이의 세로 간격을 12로 지정

        # 버튼의 글자(text)와 버튼 종류(button_type)을 함께 저장한 2차원 리스트
        # function: AC, +/-, %
        # operator: +, −, ×, ÷
        # number: 일반 숫자 버튼
        # number_wide: 가로로 긴 0 버튼
        buttons = [
            [('AC', 'function'), ('+/-', 'function'), ('%', 'function'), ('÷', 'operator')],
            [('7', 'number'), ('8', 'number'), ('9', 'number'), ('×', 'operator')],
            [('4', 'number'), ('5', 'number'), ('6', 'number'), ('−', 'operator')],
            [('1', 'number'), ('2', 'number'), ('3', 'number'), ('+', 'operator')],
            [('0', 'number_wide'), ('.', 'number'), ('=', 'operator')]
        ]

        # enumerate(buttons)는 버튼 행 리스트를 돌면서
        # 몇 번째 행인지(row_index)도 같이 가져오기 위해 사용함
        for row_index, row in enumerate(buttons):
            column_index = 0    # 시작 열 번호는 0

            for text, button_type in row:   # text는 버튼의 글자, button_type은 버튼 종류
                button = QPushButton(text)  # 현재 버튼 객체 생성
                button.setFont(self.button_font)    # 버튼에 button_font 적용
                #button.setFixedHeight(70)
                #button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                button.setFixedSize(70, 70)     # 버튼 크기 70x70으로 지정
                button.clicked.connect(self.handle_button_click)    # 버튼 클릭 시 handle_button_click 함수를 호출하도록 연결

                if button_type == 'function':   # 버튼 타입이 function이면 밝은 회색 배경 스타일 지정
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
                elif button_type == 'operator': # 버튼 타입이 operator이면 주황색 계열 버튼 스타일 지정
                    button.setStyleSheet(
                        'QPushButton {'
                        'background-color: #f69906;'    # f1a33c
                        'color: white;'
                        'border: none;'
                        'border-radius: 35px;'
                        '}'
                        "QPushButton:pressed {"
                        'background-color: #ffad33;'
                        '}'
                    )
                else:
                    button.setStyleSheet(   # 그 외는 숫자 버튼이므로 어두운 회색 스타일 지정
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

                if button_type == 'number_wide':    # 버튼 타입이 number_wide이면(0버튼이면) 따로 처리
                    button.setFixedSize(160, 70)    # 0 버튼은 가로로 길기 때문에 160x70으로 지정
                    button.setStyleSheet(   # 0 버튼은 글자가 왼쪽 정렬, 나머지는 일반 숫자 스타일과 같음
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
                    button_layout.addWidget(button, row_index, column_index, 1, 2)  # 객체, 행, 열, 행으로 차지할 칸 수, 열로 차지할 칸 수
                    column_index += 2       # 0 버튼을 가로로 두 칸을 차지하게 배치하고, 두 칸을 차지했으므로 열 인덱스를 2 증가 시킴
                else:   # 0 버튼이 아닌 일반 버튼은
                    button_layout.addWidget(button, row_index, column_index)    # 0 버튼이 아닌 일반 버튼은 한 칸만 차지하도록 배치
                    column_index += 1   # 한 칸만 썻으므로 열 인덱스를 1만 증가 시킴

        main_layout.addLayout(button_layout)    # 완성된 버튼 레이아웃을 메인 레이아웃에 추가
        self.setLayout(main_layout) # 메인 레이아웃을 이 창의 최종 레이아웃으로 지정

    def format_display_text(self, text):    # 화면에 표시할 문자열을 보기 좋게 바꾸는 함수
                                            # 예) 1111111을 1,111,111로 바꿔줌
        if text == '':  # 빈 문자열 이면
            return '0'  # 0 반환
        
        if text.isdigit():  # 문자열이 숫자로만 이루어져 있다면
            return format(int(text), ',')   # format 함수로 천 단위 쉼표 넣기
        
        return text # 숫자가 아닌 문자열은 그대로 반환
    
    def handle_button_click(self):  # 모든 버튼 클릭 이벤트를 처리하는 함수
        button = self.sender()  # 이 함수를 호출하게 만든 객체, 즉 방금 눌린 버튼 객체를 반환함
        text = button.text()    # 눌린 버튼에 적힌 글자를 가져옴

        if text == 'AC':    # AC 버튼이면
            self.current_text = '0' # 현재 문자열을 0으로 초기화
        else:   # AC 버튼이 아니면
            if self.current_text == '0':    # 현재 화면 값이 0이면
                self.current_text = text    # 새 버튼 글자로 교체
            else:                           # 현재 화면 값이 0이 아니면
                self.current_text += text   # 새 버튼 글자를 뒤에 이어 붙임: 1에서 2입력시 -> 12
        
        self.display.setText(self.format_display_text(self.current_text))   # 현재 문자열을 format_display_text로 포맷한 뒤 디스플레이에 반영


if __name__ == '__main__':  # 이 파일이 직접 실행될 때만 아래 코드를 실행함
    app = QApplication(sys.argv)    # PyQt 애플리케이션 객체 생성
    calculator = CalculatorUI() # 계산기 창 객체 생성
    calculator.show()   # 계산기 창 보여줌
    sys.exit(app.exec_())   # 프로그램 종료 시 정상 종료