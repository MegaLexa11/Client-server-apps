import argparse
import socket
import sys
import time
import json
import logging

from custom_decorators import log
import logs.config_client_log
from errors import ReqFieldMissingError, ServerError
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, \
    DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, MESSAGE_TEXT, SENDER
from common.utils import send_message, get_message


client_logger = logging.getLogger('client')


@log
def message_from_server(message):
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        user_message = f'Получено сообщение от пользователя {message[SENDER]}: {message[MESSAGE_TEXT]}'
        print(user_message)
        client_logger.info(user_message)
    else:
        client_logger.error(f'Получено некорректное сообщение с сервера: {message}')

@log
def create_message(sock, account_name = 'Guest'):
    message = input('Введите сообщение для отправки или "!!!" для завершения работы: ')
    if message == '!!!':
        sock.close()
        client_logger.info('Завершение работы по команде пользователя.')
        print('Завершение работы.')
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    client_logger.debug(f'Сформирован словарь сообщения: {message_dict}')
    return message_dict

@log
def create_presence(account_name='Guest'):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }

    client_logger.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


@log
def process_ans(message):
    client_logger.debug(f'Получен ответ от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400: {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='send', nargs='?')

    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    if not 1023 < server_port < 65536:
        client_logger.critical(f'Попытка запуска клиента с неверно указанного номера порта: {server_port},'
                               f'Доступные адреса портов с 1024 по 65535')
        sys.exit(1)

    if client_mode not in ('listen', 'send'):
        client_logger.critical(f'Указан недопкстимый режим работы: {client_mode}.'
                               f'Допустимые режимы: listen, send')
        sys.exit(1)

    return server_address, server_port, client_mode


def main():
    server_address, server_port, client_mode = arg_parser()

    client_logger.info(f'Запущен клиент с параметрами: '
                       f'адрес сервера: {server_address}, порт: {server_port}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        message_to_server = create_presence()
        send_message(transport, message_to_server)
        answer = process_ans(get_message(transport))
        client_logger.info(f'Принят ответ от сервера: {answer}')
        print('Установлено соединение с сервером.')
    except json.JSONDecodeError:
        client_logger.error(f'Строку, полученную от сервера, не удалось декодировать.')
        sys.exit(1)
    except ServerError as error:
        client_logger.error(f'При установке соединения возникла ошибка: {error.text}')
        sys.exit(1)
    except ConnectionRefusedError:
        client_logger.critical(f'Не удалось подключиться к серверу {server_port}:{server_address}, '
                               f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        client_logger.error(f'В ответе сервера отсутствует необходимое поле: '
                            f'{missing_error.missing_field}')
        sys.exit(1)
    else:
        if client_mode == 'send':
            print('Режим работы - отправка сообщений.')
        else:
            print('Режим работы - прием сообщений.')
        while True:
            if client_mode == 'send':
                try:
                    send_message(transport, create_message(transport))
                except (ConnectionRefusedError, ConnectionError, ConnectionAbortedError):
                    client_logger.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)

            if client_mode == 'listen':
                try:
                    message_from_server(get_message(transport))
                except (ConnectionRefusedError, ConnectionError, ConnectionAbortedError):
                    client_logger.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)


if __name__ == '__main__':
    main()
