import subprocess

PROCESS = []

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

        for i in range(3):
            PROCESS.append(subprocess.Popen('python client.py',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE))

        for i in range(3):
            PROCESS.append(subprocess.Popen('python client_send.py',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE))
