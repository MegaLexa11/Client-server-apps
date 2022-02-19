import argparse
import socket
import sys
import json
import logging
import time
from threading import Thread
import select

from descriptors import Port
from custom_decorators import log
import logs.config_server_log
from errors import IncorrectDataReceivedError
from metaclasses import ServerVerifier
from common.utils import send_message, get_message
from common.variables import ACTION, PRESENCE, USER, ACCOUNT_NAME, TIME, RESPONSE, ERROR, RESPONSE_200, RESPONSE_400,\
    RESPONDEFAULT_IP_ADDRESSES, DEFAULT_PORT, MAX_CONNECTIONS, MESSAGE, MESSAGE_TEXT, SENDER, DESTINATION, EXIT
from server_database import ServerDataBase


server_logger = logging.getLogger('server')


class Server(metaclass=ServerVerifier):
    port = Port()

    def __init__(self, listen_address, listen_port, database):
        self.addr = listen_address
        self.port = listen_port
        self.clients = []
        self.messages = []
        self.names = dict()
        self.database = database
        super().__init__()

    def init_socket(self):
        server_logger.info(f'Запущен сервер с портом для подключения {self.port}, '
                           f'адрес, с которого принимаются подключения: {self.addr}, '
                           f'Если адрес не указан, прнимаются соединения с любых адресов.')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)

        self.sock = transport
        self.sock.listen()

    def process_message(self, message, listen_socks):
        message_dest = message[DESTINATION]
        message_send = message[SENDER]
        if message_dest in self.names and self.names[message_dest] in listen_socks:
            send_message(self.names[message_dest], message)
            server_logger.info(f'Отправлено сообщение пользователю {message_dest} '
                               f'от пользователя {message_send}.')
        elif message_dest in self.names and self.names[message_dest] not in listen_socks:
            raise ConnectionError
        else:
            server_logger.error(f'Пользователь {message_dest} не зарегистрирован на сервере, '
                                f'отправка сообщения невозможна.')

    def process_client_message(self, message, client):
        server_logger.debug(f'Разбор сообщения от клиента: {message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message:
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port)
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        elif ACTION in message and message[ACTION] == MESSAGE and SENDER in message and \
                DESTINATION in message and TIME in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.database.user_logout(message[USER][ACCOUNT_NAME])
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            return
        else:
            response = RESPONSE_400
            response[ERROR] = 'Некорректный запрос!'
            send_message(client, response)
            return

    def main_loop(self):
        self.init_socket()

        while True:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                server_logger.info(f'Установлено соединение с ПК {client_address}.')
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []

            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    server_logger.info(client_with_message)
                    try:
                        self.process_client_message(get_message(client_with_message), client_with_message)
                    except:
                        server_logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        self.clients.remove(client_with_message)

            for mes in self.messages:
                try:
                    self.process_message(mes, send_data_lst)
                except:
                    server_logger.info(f'Связь с клиентом {mes[DESTINATION]} была потеряна.')
                    self.clients.remove(self.names[mes[DESTINATION]])
                    del self.names[mes[DESTINATION]]
            self.messages.clear()


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port


def print_help():
    print('Поддерживаемые комманды:')
    print('users - список известных пользователей')
    print('connected - список подключённых пользователей')
    print('loghist - история входов пользователя')
    print('exit - завершение работы сервера.')
    print('help - вывод справки по поддерживаемым командам')


def server_func(listen_address, listen_port, database):
    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.main_loop()


def user_interactions(database):
    print_help()
    while True:
        server_input = input('Введите команду: ')
        if server_input == 'help':
            print_help()
        elif server_input == 'exit':
            break
        elif server_input == 'users':
            for user in sorted(database.users_list()):
                print(f'Пользователь: {user[0]}, последний вход: {user[1]}')
        elif server_input == 'connected':
            for user in sorted(database.active_users_list()):
                print(f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
        elif server_input == 'loghist':
            name = input('Введите имя пользователя для просмотра истории. '
                         'Для вывода всей истории, просто нажмите Enter: ')
            for user in sorted(database.login_history(name)):
                print(f'Пользователь: {user[0]} время входа: {user[1]}. Вход с: {user[2]}:{user[3]}')
        else:
            print('Такой команды не существует!\nСписок существующих команд:')
            print_help()


def main():
    listen_address, listen_port = arg_parser()
    database = ServerDataBase()
    thr_runserver = Thread(target=server_func, args=(listen_address, listen_port, database))
    thr_userinteract = Thread(target=user_interactions, args=(database, ))

    thr_runserver.start()
    thr_userinteract.start()


if __name__ == '__main__':
    main()
