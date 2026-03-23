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
        print(f'파일을 읽는 도중 오류가 발생했습니다: {error}')
        return None
    
    if not lines:
        print('파일 내용이 비어 있습니다.')
        return None
    
    print('=== CSV 원본 내용 출력 ===')

    for line in lines:
        print(line.strip())

    header = lines[0].strip().split(',') # ['Substance', 'Weight (g/cm³)', 'Specific Gravity', 'Strength', 'Flammability']
    # print(header)

    for line in lines[1:]:
        values = line.strip().split(',') # ['Ethanol', '0.789', '0.789', '40', '0.9']
        # print(values)

        if len(values) != len(header):
            continue

        item = {}
        for index in range(len(header)):
            item[header[index]] = values[index] # index 0 -> item['Substance'] = 'Ethanol'

        # {
        #     'Substance': 'Ethanol',
        #     'Weight (g/cm³)': '0.789',
        #     'Specific Gravity': '0.789',
        #     'Strength': '40',
        #     'Flammability': '0.9'
        # }
        
        try:
            item['Flammability'] = float(item['Flammability'])
        except ValueError:
            continue
    
        inventory_list.append(item)
        # print(len(inventory_list))

    return inventory_list

def print_inventory_list(inventory_list):
    print('\n=== 리스트 객체 변환 결과 ===')
    for item in inventory_list:
        print(item)

def sort_by_flammability(inventory_list):
    return sorted(
        inventory_list,
        key = lambda item: item['Flammability'], # lambda 매개변수: 반환값
        reverse = True
    )
    # sorted 함수 사용해서 정렬

def filter_danger_items(inventory_list, threshold):
    danger_list = []

    for item in inventory_list:
        if item['Flammability'] >= threshold:
            danger_list.append(item)
    
    return danger_list

def print_danger_items(danger_list):
    print('\n=== 인화성 지수 0.7 이상 목록 ===')
    for item in danger_list:
        print(item)

def save_danger_csv(filename, danger_list):
    try:
        with open(filename, 'w', encoding = 'utf-8') as file:
            file.write('Substance,Weight (g/cm³),Specific Gravity,Strength,Flammability\n')

            for item in danger_list:
                line = (
                    f"{item['Substance']},"
                    f"{item['Weight (g/cm³)']},"
                    f"{item['Specific Gravity']},"
                    f"{item['Strength']},"
                    f"{item['Flammability']}\n"
                )
                file.write(line)
        print(f'\n{filename} 파일로 저장했습니다.')

    except PermissionError:
        print(f'{filename} 파일을 저장할 권한이 없습니다.')
    except OSError as error:
        print(f'파일을 저장하는 중 오류가 발생했습니다: {error}')


def main():
    source_file = 'Mars_Base_Inventory_List.csv'
    danger_file = 'Mars_Base_Inventory_danger.csv'
    threshold = 0.7

    inventory_list = read_csv_file(source_file)

    if inventory_list is None:
        return
    
    print_inventory_list(inventory_list)

    sorted_inventory_list = sort_by_flammability(inventory_list)

    print('\n=== 인화성 지수 기준 내림차순 정렬 결과 ===')
    for item in sorted_inventory_list:
        print(item)

    danger_list = filter_danger_items(sorted_inventory_list, threshold)

    print_danger_items(danger_list)

    save_danger_csv(danger_file, danger_list)

if __name__ == '__main__':
    main()
        
