import argparse
import socket
import sys
import json
import logging

from custom_decorators import log
import logs.config_server_log
from errors import IncorrectDataReceivedError
from common.utils import send_message, get_message
from common.variables import ACTION, PRESENCE, USER, ACCOUNT_NAME, \
    TIME, RESPONSE, RESPONDEFAULT_IP_ADDRESSES, ERROR, DEFAULT_PORT, MAX_CONNECTIONS


server_logger = logging.getLogger('server')

@log
def process_client_message(message):
    server_logger.debug(f'Разбор сообщения от клиента: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONDEFAULT_IP_ADDRESSES: 400,
        ERROR: 'Bad Request'
    }

@log
def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    return parser


def main():

    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if not 1023 < listen_port < 65536:
        server_logger.critical(f'Попытка запуска сервера с неверно указанным портом {listen_port}. '
                               f'Доступные адреса портов с 1024 по 65535')
        sys.exit(1)

    server_logger.info(f'Запущен сервер с портом для подключения {listen_port}, '
                       f'адрес, с которого принимаются подключения: {listen_address}, '
                       f'Если адрес не указан, прнимаются соединения с любых адресов.')

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        server_logger.info(f'Установлено соединение с ПК {client_address}.')

        try:
            message_from_client = get_message(client)
            server_logger.info(f'Получено ообщение от клиента: {message_from_client}.')
            response = process_client_message(message_from_client)
            server_logger.info(f'Сформирован ответ для клиента: {response}.')
            send_message(client, response)
            server_logger.debug(f'Соединение с клиентом {client_address} закрыто.')
            client.close()
        except json.JSONDecodeError:
            server_logger.error(f'Строку, полученную от клиента {client_address}, не удалось декодировать. '
                                f'Соединение закрыто.')
            client.close()
        except IncorrectDataReceivedError:
            server_logger.error(f'От клиента {client_address} приняты некорректные данные. Соединение закрыто.')
            client.close()


if __name__ == '__main__':
    main()
