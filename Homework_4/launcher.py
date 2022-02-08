import subprocess

PROCESS = []
client_names = ['John', 'Ann', 'Bob', 'Alice']

while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, x - закрыть все окна: ')

    if ACTION == 'q':
        break

    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()

    elif ACTION == 's':
        PROCESS.append(subprocess.Popen('python server.py',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE))

        for name in client_names:
            PROCESS.append(subprocess.Popen(f'python client.py -n {name}',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE))
