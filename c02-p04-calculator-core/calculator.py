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


def load_iphone_font(point_size, src):
    font_path = 'SF-Pro-Display-Medium.otf'
    font_id = QFontDatabase.addApplicationFont(font_path)

    if font_id != -1:
        font_families = QFontDatabase.applicationFontFamilies(font_id)

        if font_families:
            family = font_families[0]
            database = QFontDatabase()

            print(f'[{src}] 폰트 파일 로드 성공: {family}')
            print(f'[{src}] 사용 가능한 스타일: {database.styles(family)}')
            return QFont(family, point_size)

    print(f'[{src}] 폰트 파일 로드 실패: Arial 사용')
    return QFont('Arial', point_size)


class Calculator:
    def __init__(self):
        self.max_value = 999999999999
        self.reset()

    def reset(self):
        self.current_input = '0'
        self.stored_value = None
        self.pending_operator = None
        self.waiting_for_new_input = False

    def add(self, left, right):
        return left + right

    def subtract(self, left, right):
        return left - right

    def multiply(self, left, right):
        return left * right

    def divide(self, left, right):
        if right == 0:
            return 'Error'
        return left / right

    def negative_positive(self):
        if self.current_input == 'Error':
            return

        if self.current_input.startswith('-'):
            self.current_input = self.current_input[1:]
        elif self.current_input != '0':
            self.current_input = '-' + self.current_input

    def percent(self):
        if self.current_input == 'Error':
            return

        value = self.get_current_value() / 100

        if not self.is_valid_range(value):
            self.current_input = 'Error'
            return

        self.current_input = self.format_result_value(value)

    def input_digit(self, digit):
        if self.current_input == 'Error':
            self.current_input = digit
            self.waiting_for_new_input = False
            return

        if self.waiting_for_new_input:
            self.current_input = digit
            self.waiting_for_new_input = False
        elif self.current_input == '0':
            self.current_input = digit
        else:
            self.current_input += digit

    def input_decimal(self):
        if self.current_input == 'Error':
            self.current_input = '0.'
            self.waiting_for_new_input = False
            return

        if self.waiting_for_new_input:
            self.current_input = '0.'
            self.waiting_for_new_input = False
        elif '.' not in self.current_input:
            self.current_input += '.'

    def get_current_value(self):
        if self.current_input in ('', '-', 'Error'):
            return 0.0
        return float(self.current_input)

    def is_valid_range(self, value):
        return abs(value) <= self.max_value

    def calculate_result(self, left, operator, right):
        if operator == '+':
            return self.add(left, right)
        if operator == '−':
            return self.subtract(left, right)
        if operator == '×':
            return self.multiply(left, right)
        if operator == '÷':
            return self.divide(left, right)
        return right

    def handle_operator(self, operator):
        if self.current_input == 'Error':
            return

        current_value = self.get_current_value()

        if not self.is_valid_range(current_value):
            self.current_input = 'Error'
            return

        if self.stored_value is None:
            self.stored_value = current_value
        elif self.pending_operator is not None and not self.waiting_for_new_input:
            result = self.calculate_result(
                self.stored_value,
                self.pending_operator,
                current_value
            )

            if result == 'Error' or not self.is_valid_range(result):
                self.current_input = 'Error'
                self.stored_value = None
                self.pending_operator = None
                self.waiting_for_new_input = True
                return

            self.stored_value = result
            self.current_input = self.format_result_value(result)

        self.pending_operator = operator
        self.waiting_for_new_input = True

    def equal(self):
        if self.current_input == 'Error':
            return

        if self.stored_value is None or self.pending_operator is None:
            return

        current_value = self.get_current_value()

        result = self.calculate_result(
            self.stored_value,
            self.pending_operator,
            current_value
        )

        if result == 'Error' or not self.is_valid_range(result):
            self.current_input = 'Error'
        else:
            self.current_input = self.format_result_value(result)

        self.stored_value = None
        self.pending_operator = None
        self.waiting_for_new_input = True

    def format_result_value(self, value):
        if value == 'Error':
            return 'Error'

        if float(value).is_integer():
            return str(int(value))

        text = str(round(value, 10)).rstrip('0').rstrip('.')
        return text

    def format_display_text(self):
        text = self.current_input

        if text in ('', 'Error'):
            return text if text else '0'

        if '.' in text:
            integer_part, decimal_part = text.split('.', 1)

            if integer_part in ('', '-'):
                formatted_integer = integer_part + '0' if integer_part == '-' else '0'
            else:
                formatted_integer = format(int(integer_part), ',')

            return f'{formatted_integer}.{decimal_part}'

        if text in ('-',):
            return text

        return format(int(text), ',')

    def get_display_text(self):
        return self.format_display_text()


class CalculatorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.calculator = Calculator()
        self.operator_buttons = {}

        self.display_font = load_iphone_font(46, 'display')
        self.button_font = load_iphone_font(20, 'button')
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
        print('[display] 폰트 적용 확인:', QFontInfo(self.display.font()).family())
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
                button.setFixedSize(70, 70)
                button.clicked.connect(self.handle_button_click)

                if button_type == 'function':
                    button.setStyleSheet(
                        'QPushButton {'
                        'background-color: #a0a0a0;'
                        'color: black;'
                        'border: none;'
                        'border-radius: 35px;'
                        '}'
                        'QPushButton:pressed {'
                        'background-color: #bdbdbd;'
                        '}'
                    )
                elif button_type == 'operator':
                    button.setStyleSheet(self.get_operator_button_style(False))
                    self.operator_buttons[text] = button
                else:
                    button.setStyleSheet(
                        'QPushButton {'
                        'background-color: #313131;'
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
        self.update_operator_button_styles()
        self.update_display()

    def get_operator_button_style(self, is_active=False):
        if is_active:
            return (
                'QPushButton {'
                'background-color: white;'
                'color: #f69906;'
                'border: none;'
                'border-radius: 35px;'
                '}'
                'QPushButton:pressed {'
                'background-color: #e6e6e6;'
                'color: #f69906;'
                '}'
            )

        return (
            'QPushButton {'
            'background-color: #f69906;'
            'color: white;'
            'border: none;'
            'border-radius: 35px;'
            '}'
            'QPushButton:pressed {'
            'background-color: #ffad33;'
            'color: white;'
            '}'
        )

    def update_operator_button_styles(self):
        for operator, button in self.operator_buttons.items():
            is_active = operator == self.calculator.pending_operator
            button.setStyleSheet(self.get_operator_button_style(is_active))

    def update_display(self):
        self.display.setText(self.calculator.get_display_text())

    def handle_button_click(self):
        button = self.sender()
        text = button.text()

        if text.isdigit():
            self.calculator.input_digit(text)
        elif text == '.':
            self.calculator.input_decimal()
        elif text == 'AC':
            self.calculator.reset()
        elif text == '+/-':
            self.calculator.negative_positive()
        elif text == '%':
            self.calculator.percent()
        elif text in ('+', '−', '×', '÷'):
            self.calculator.handle_operator(text)
        elif text == '=':
            self.calculator.equal()

        self.update_operator_button_styles()
        self.update_display()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calculator = CalculatorUI()
    calculator.show()
    sys.exit(app.exec_())