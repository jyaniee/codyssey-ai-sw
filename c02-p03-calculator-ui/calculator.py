import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase, QFontInfo
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QSizePolicy
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
        self.current_text = '0'
        self.display_font = load_iphone_font(46)
        self.button_font = load_iphone_font(20)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('iPhone Calculator UI')
        self.setFixedSize(360, 640)
        self.setStyleSheet('background-color: black;')

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 20, 12, 20)
        main_layout.setSpacing(12)

        self.display = QLabel('0')
        self.display.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.display.setStyleSheet(
            'color: white;'
            'background-color: black;'
            'padding: 10px 0px 0px 10px;'
        )
        self.display.setFont(self.display_font)
        print('display 실제 적용 폰트:', QFontInfo(self.display.font()).family())
        self.display.setFixedHeight(170)

        main_layout.addWidget(self.display)

        button_layout = QGridLayout()
        button_layout.setHorizontalSpacing(10)
        button_layout.setVerticalSpacing(12)


        buttons = [
            [('AC', 'function'), ('+/-', 'function'), ('%', 'function'), ('÷', 'operator')],
            [('7', 'number'), ('8', 'number'), ('9', 'number'), ('×', 'operator')],
            [('4', 'number'), ('5', 'number'), ('6', 'number'), ('−', 'operator')],
            [('1', 'number'), ('2', 'number'), ('3', 'number'), ('+', 'operator')],
            [('0', 'number_wide'), ('.', 'number'), ('=', 'operator')]
        ]

        for row_index, row in enumerate(buttons):
            column_index = 0

            for text, button_type in row:
                button = QPushButton(text)
                button.setFont(self.button_font)
                #button.setFixedHeight(70)
                #button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                button.setFixedSize(70, 70)
                button.clicked.connect(self.handle_button_click)

                if button_type == 'function':
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
                elif button_type == 'operator':
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
                    button.setStyleSheet(
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

                if button_type == 'number_wide':
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
                    button_layout.addWidget(button, row_index, column_index, 1, 2)
                    column_index += 2
                else:
                    button_layout.addWidget(button, row_index, column_index)
                    column_index += 1

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def format_display_text(self, text):
        if text == '':
            return '0'
        
        if text.isdigit():
            return format(int(text), ',')
        
        return text
    
    def handle_button_click(self):
        button = self.sender()
        text = button.text()

        if text == 'AC':
            self.current_text = '0'
        else:
            if self.current_text == '0':
                self.current_text = text
            else:
                self.current_text += text
        
        self.display.setText(self.format_display_text(self.current_text))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calculator = CalculatorUI()
    calculator.show()
    sys.exit(app.exec_())