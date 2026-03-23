def main():
    try:
        with open('mission_computer_main.log', 'r', encoding='utf-8') as file:
            # content = file.read()
            # print(content)
            lines = file.readlines()

        header = lines[0]   # timestamp,event,message
        logs = lines[1:]

        logs.reverse()  # 역순 정렬

        print(header.strip())
        for line in logs:
            print(line.strip())

        problem_logs = []

        for line in logs:
            if 'unstable' in line or 'explosion' in line:   # 문제 로그 기준
                problem_logs.append(line)
        
        with open('problem_log.log', 'w', encoding= 'utf-8') as file:
            for line in problem_logs:
                file.write(line)

    except FileNotFoundError:
        print('mission_computer_main.log 파일을 찾을 수 없습니다.')
    except UnicodeDecodeError:
        print('파일 인코딩을 읽을 수 없습니다.')
    except PermissionError:
        print('파일을 읽을 권한이 없습니다.')
    except OSError as error:
        print(f'파일 처리 중 오류가 발생했습니다: {error}')

if __name__ == '__main__':
    main()