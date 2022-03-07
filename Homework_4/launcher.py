if __name__ == '__main__':
    import subprocess

    PROCESS = []
    client_names = ['Nick', 'Ann', 'Bob', 'Alice']

    while True:
        ACTION = input('Выберите действие: q - выход, '
                       's - запустить сервер, c - запустить клиенты x - закрыть все окна: ')

        if ACTION == 'q':
            break

        elif ACTION == 'x':
            while PROCESS:
                VICTIM = PROCESS.pop()
                VICTIM.kill()

        elif ACTION == 's':
            PROCESS.append(subprocess.Popen('python server.py',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE))

        elif ACTION == 'c':
            for name in client_names:
                PROCESS.append(subprocess.Popen(f'python client.py -n {name} -p 123456',
                                                creationflags=subprocess.CREATE_NEW_CONSOLE))
