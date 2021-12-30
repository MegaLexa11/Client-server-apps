import socket
import sys

from common.utils import *


def process_client_message(message):
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONDEFAULT_IP_ADDRESSES: 400,
        ERROR: 'Bad Request'
    }


def main():
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        print('после параметра -\'p\' необходимо указать номер порта.')
        sys.exit(1)
    except ValueError:
        print('В качестве порта может быть указано число в интервале от 1024 до 65535!')
        sys.exit(1)

    try:
        if '-p' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''
    except IndexError:
        # Нижк добавить штукенцию
        print('После порта \'a\'- необходимо указать адрес, который будет слушать с порта')
        sys.exit(1)

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()

        try:
            message_from_client = get_message(client)
            print(message_from_client)
            responce = process_client_message(message_from_client)
            send_message(client, responce)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print('Принято некорректное сообщение от клиента.')
            client.close()


if __name__ == '__main__':
    main()
