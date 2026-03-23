def read_csv_file(filename):
    inventory_list = []

    try:
        with open(filename, 'r', encoding = 'utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f'{filename} 파일을 찾을 수 없습니다.')
        return None
    except UnicodeDecodeError:
        print(f'{filename} 파일의 인코딩을 읽을 수 없습니다.')
        return None
    except PermissionError:
        print(f'{filename} 파일을 읽을 권한이 없습니다.')
        return None
    except OSError as error:
        print(f'파일을 읽는 중 오류가 발생했습니다: {error}')
        return None

    if not lines:
        print('파일 내용이 비어 있습니다.')
        return None

    header = lines[0].strip().split(',')

    for line in lines[1:]:
        values = line.strip().split(',')

        if len(values) != len(header):
            continue

        item = {}
        for index in range(len(header)):
            item[header[index]] = values[index]

        try:
            item['Flammability'] = float(item['Flammability'])
        except ValueError:
            continue

        inventory_list.append(item)

    return inventory_list


def sort_by_flammability(inventory_list):
    return sorted(
        inventory_list,
        key = lambda item: item['Flammability'],
        reverse = True
    )


def convert_list_to_text(inventory_list):
    lines = []
    header = 'Substance,Weight (g/cm³),Specific Gravity,Strength,Flammability'
    lines.append(header)

    for item in inventory_list:
        line = (
            f"{item['Substance']},"
            f"{item['Weight (g/cm³)']},"
            f"{item['Specific Gravity']},"
            f"{item['Strength']},"
            f"{item['Flammability']}"
        )
        lines.append(line)

    return '\n'.join(lines)


def save_binary_file(filename, text):
    try:
        with open(filename, 'wb') as file:  # wb : write binary(이진 파일 쓰기 모드)
            file.write(text.encode('utf-8'))    # 문자열을 바이트로 변환
        print(f'{filename} 파일로 이진 저장했습니다.')
    except PermissionError:
        print(f'{filename} 파일을 저장할 권한이 없습니다.')
    except OSError as error:
        print(f'이진 파일 저장 중 오류가 발생했습니다: {error}')


def read_binary_file(filename):
    try:
        with open(filename, 'rb') as file:  # rb : read binary(이진 파일 읽기 모드)
            data = file.read()
        # print(data)
        return data
    except FileNotFoundError:
        print(f'{filename} 파일을 찾을 수 없습니다.')
        return None
    except PermissionError:
        print(f'{filename} 파일을 읽을 권한이 없습니다.')
        return None
    except OSError as error:
        print(f'이진 파일 읽기 중 오류가 발생했습니다: {error}')
        return None


def print_binary_content(binary_data):
    if binary_data is None:
        return

    try:
        text = binary_data.decode('utf-8')
        print('\n=== 이진 파일에서 다시 읽은 내용 ===')
        print(text)
    except UnicodeDecodeError:
        print('이진 데이터를 utf-8로 디코딩할 수 없습니다.')

def main():
    source_file = 'Mars_Base_Inventory_List.csv'
    binary_file = 'Mars_Base_Inventory_List.bin'

    inventory_list = read_csv_file(source_file)

    if inventory_list is None:
        return
    
    sorted_inventory_list = sort_by_flammability(inventory_list)

    text_data = convert_list_to_text(sorted_inventory_list)
    save_binary_file(binary_file, text_data)

    binary_data = read_binary_file(binary_file)
    print_binary_content(binary_data)

if __name__ == '__main__':
    main()