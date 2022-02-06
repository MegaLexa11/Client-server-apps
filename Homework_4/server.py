import argparse
import socket
import sys
import json
import logging
import time

import select

from custom_decorators import log
import logs.config_server_log
from errors import IncorrectDataReceivedError
from common.utils import send_message, get_message
from common.variables import ACTION, PRESENCE, USER, ACCOUNT_NAME, TIME, RESPONSE, ERROR, RESPONSE_200, RESPONSE_400,\
    RESPONDEFAULT_IP_ADDRESSES, DEFAULT_PORT, MAX_CONNECTIONS, MESSAGE, MESSAGE_TEXT, SENDER, DESTINATION, EXIT


server_logger = logging.getLogger('server')


@log
def process_client_message(message, messages_list, client, clients, names):
    server_logger.debug(f'Разбор сообщения от клиента: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message:
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Имя пользователя уже занято'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    elif ACTION in message and message[ACTION] == MESSAGE and SENDER in message and\
            DESTINATION in message and TIME in message and MESSAGE_TEXT in message:
        messages_list.append(message)
        return
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    else:
        response = RESPONSE_400
        response[ERROR] = 'Некорректный запрос!'
        send_message(client, response)
        return


@log
def process_message(message, names, listen_socks):
    message_dest = message[DESTINATION]
    message_send = message[SENDER]
    if message_dest in names and names[message_dest] in listen_socks:
        send_message(names[message_dest], message)
        server_logger.info(f'Отправлено сообщение пользователю {message_dest} '
                           f'от пользователя {message_send}.')
    elif message_dest in names and names[message_dest] not in listen_socks:
        raise ConnectionError
    else:
        server_logger.error(f'Пользователь {message_dest} не зарегистрирован на сервере, '
                            f'отправка сообщения невозможна.')


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if not 1023 < listen_port < 65536:
        server_logger.critical(f'Попытка запуска сервера с неверно указанным портом {listen_port}. '
                               f'Доступные адреса портов с 1024 по 65535')
        sys.exit(1)

    return listen_address, listen_port


def main():
    listen_address, listen_port = arg_parser()

    server_logger.info(f'Запущен сервер с портом для подключения {listen_port}, '
                       f'адрес, с которого принимаются подключения: {listen_address}, '
                       f'Если адрес не указан, прнимаются соединения с любых адресов.')

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)

    clients = []
    messages = []
    names = dict()

    transport.listen(MAX_CONNECTIONS)

    while True:
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            server_logger.info(f'Установлено соединение с ПК {client_address}.')
            clients.append(client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []

        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_message(get_message(client_with_message), messages,
                                           client_with_message, clients, names)
                except Exception:
                    server_logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                    clients.remove(client_with_message)

        for mes in messages:
            try:
                process_message(mes, names, send_data_lst)
            except Exception:
                server_logger.info(f'Связь с клиентом {mes[DESTINATION]} была потеряна.')
                clients.remove(names[mes[DESTINATION]])
                del names[mes[DESTINATION]]
        messages.clear()


if __name__ == '__main__':
    main()
