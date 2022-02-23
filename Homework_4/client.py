import argparse
import socket
import sys
import time
import json
import logging
import threading

from custom_decorators import log
import logs.config_client_log
from errors import ReqFieldMissingError, ServerError, IncorrectDataReceivedError
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, \
    DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, MESSAGE_TEXT, SENDER, DESTINATION, EXIT, GET_CONTACTS, \
    ADD_CONTACT, USERS_REQUEST, REMOVE_CONTACT, LIST_INFO
from common.utils import send_message, get_message
from metaclasses import ClientVerifier
from client_database import ClientDatabase


client_logger = logging.getLogger('client')

sock_lock = threading.Lock()
database_lock = threading.Lock()


class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock, database):
        self.account_name = account_name,
        self.sock = sock
        self.database = database
        super().__init__()

    @staticmethod
    def print_help():
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Получатель и текст будут запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    def create_exit_message(self):
        return {
            ACTION: EXIT,
            ACCOUNT_NAME: self.account_name[0],
            TIME: time.time()
        }

    def create_message(self):
        to_user = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')

        with database_lock:
            if not self.database.check_user(to_user):
                client_logger.error(f'Попытка отправить сообщение незарегистрированному пользователю.')

        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        client_logger.debug(f'Сформирован словарь сообщения: {message_dict}')

        with database_lock:
            self.database.save_message(self.account_name, to_user, message)

        with sock_lock:
            try:
                send_message(self.sock, message_dict)
                client_logger.info(f'Отправлено сообщение пользователю {to_user}')
            except OSError as err:
                if err.errno:
                    client_logger.critical('Потеряно соединение с сервером.')
                    sys.exit(1)
                else:
                    client_logger.error('Не удалось передать сообщение. Время ожидания истекло.')

    def print_history(self):
        user_choice = input('Возможные действия:\n"in" - Показать входящие сообщения;\n'
                            '"out" - Показать исходящие сообщения;\n"" - Показать все сообщения;\n'
                            'Введите одну из команд: ')
        with database_lock:
            if user_choice == 'in':
                message_history = self.database.get_history(to_user=self.account_name)
                for message in message_history:
                    print(f'\nСообщение от пользователя: {message[0]} от {message[3]}:\n{message[2]}')
            elif user_choice == 'out':
                message_history = self.database.get_history(from_user=self.account_name)
                for message in message_history:
                    print(f'\nСообщение пользователю: {message[1]} от {message[3]}:\n{message[2]}')
            else:
                message_history = self.database.get_history()
                for message in message_history:
                    print(f'\nСообщение от пользователя {message[0]} пользователю {message[1]} '
                          f'от {message[3]}:\n{message[2]}')

    def edit_contacts(self):
        user_choice = input('Возможные действия:\n"del" - Удаление пользователя;'
                            '\n"add" - Добавление пользователя;\nВведите команду: ')
        if user_choice == 'del':
            edit_user = input('Введите имя контакта для удаления: ')
            with database_lock:
                if self.database.check_contact(edit_user):
                    self.database.del_contact(edit_user)
                else:
                    client_logger.error('Попытка удаления несуществующего контакта.')
        elif user_choice == 'add':
            edit_user = input('Введите имя контакта для добавления: ')
            if self.database.check_user(edit_user):
                with database_lock:
                    self.database.add_contact(edit_user)
                with sock_lock:
                    try:
                        add_contact(self.sock, self.account_name, edit_user)
                    except ServerError:
                        client_logger.error('Не удалось отправить информацию на сервер.')

    def run(self):
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message()

            elif command == 'help':
                self.print_help()

            elif command == 'exit':
                with sock_lock:
                    try:
                        send_message(self.sock, self.create_exit_message())
                    except Exception as e:
                        print(e)
                        pass
                    print('Завершение соединения...')
                    client_logger.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break

            elif command == 'contacts':
                with database_lock:
                    contacts_list = self.database.get_contacts()
                for contact in contacts_list:
                    print(contact)

            elif command == 'edit':
                self.edit_contacts()

            elif command == 'history':
                self.print_history()

            else:
                print('Команда не распознана, попробуйте снова.\nhelp - вывести возможные команды.')


class ClientReader(threading.Thread):
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock = sock
        self.database = database
        super().__init__()

    def run(self):
        while True:
            time.sleep(1)
            with sock_lock:
                try:
                    message = get_message(self.sock)
                except IncorrectDataReceivedError:
                    client_logger.error(f'Не удалось декодировать полученное сообщение.')
                except (OSError, ConnectionError, ConnectionAbortedError,
                        ConnectionResetError, json.JSONDecodeError):
                    client_logger.critical(f'Потеряно соединение с сервером.')
                    break
                else:
                    if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and MESSAGE_TEXT \
                            in message and DESTINATION in message and message[DESTINATION] == self.account_name:
                        print(f'\nСообщение от пользователя {message[SENDER][0]}: {message[MESSAGE_TEXT]}')
                        with database_lock:
                            try:
                                self.database.save_message(message[SENDER], self.account_name, message[MESSAGE_TEXT])
                            except Exception as e:
                                print(e)
                                client_logger.error('Ошибка взаимодействия с базой данных.')
                        client_logger.info(f'\nПолучено сообщение от пользователя {message[SENDER][0]}: '
                                           f'{message[MESSAGE_TEXT]}')
                    else:
                        client_logger.error(f'Получено некорректное сообщение с сервера: {message}')


@log
def create_presence(account_name):
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
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        client_logger.critical(f'Попытка запуска клиента с неверно указанного номера порта: {server_port},'
                               f'Доступные адреса портов с 1024 по 65535')
        sys.exit(1)

    return server_address, server_port, client_name


def contacts_list_request(sock, name):
    client_logger.debug(f'Запрос списка контактов для пользователя {name}')
    request = {
        ACTION: GET_CONTACTS,
        TIME: time.time(),
        USER: name
    }
    client_logger.debug(f'Сформирован запрос {request}')
    send_message(sock, request)
    answer = get_message(sock)
    client_logger.debug(f'Получен ответ: {answer}')
    if RESPONSE in answer and answer[RESPONSE] == 202:
        return answer[LIST_INFO]
    else:
        raise ServerError


def add_contact(sock, username, contact):
    client_logger.debug(f'Создание контакта {contact}')
    request = {
        ACTION: ADD_CONTACT,
        TIME: time.time(),
        USER: username,
        ACCOUNT_NAME: contact
    }
    send_message(sock, request)
    answer = get_message(sock)
    if RESPONSE in answer and answer[RESPONSE] == 200:
        print('Контак успешно создан.')
    else:
        raise ServerError('Ошибка создания контакта.')


def user_list_request(sock, username):
    client_logger.debug(f'Запрос списка существующих пользователей {username}')
    request = {
        ACTION: USERS_REQUEST,
        TIME: time.time(),
        ACCOUNT_NAME: username
    }
    send_message(sock, request)
    answer = get_message(sock)
    if RESPONSE in answer and answer[RESPONSE] == 202:
        return answer[LIST_INFO]
    else:
        raise ServerError


def remove_contact(sock, username, contact):
    client_logger.debug(f'Удаление контакта {contact}')
    req = {
        ACTION: REMOVE_CONTACT,
        TIME: time.time(),
        USER: username,
        ACCOUNT_NAME: contact
    }
    send_message(sock, req)
    answer = get_message(sock)
    if RESPONSE in answer and answer[RESPONSE] == 200:
        print('Контакт успешно удален')
    else:
        raise ServerError('Ошибка удаления контакта')


def database_load(sock, database, username):
    try:
        users_list = user_list_request(sock, username)
    except ServerError:
        client_logger.error('Ошибка запроса списка существующих пользователей')
    else:
        database.add_users(users_list)

    try:
        contacts_list = contacts_list_request(sock, username)
    except ServerError:
        client_logger.error('Ошибка запроса списка контактов')
    else:
        for contact in contacts_list:
            database.add_contact(contact)


def main():
    server_address, server_port, client_name = arg_parser()
    if not client_name:
        client_name = input('Введите имя пользователя: ')

    print(f'Добро пожаловать в консольный мессенджер. \nИмя пользователя: {client_name}')

    client_logger.info(f'Запущен клиент с параметрами: адрес сервера: {server_address}, '
                       f'порт: {server_port}, имя пользователя: {client_name}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.settimeout(1)

        transport.connect((server_address, server_port))
        message_to_server = create_presence(client_name)
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
    except (ConnectionRefusedError, ConnectionError):
        client_logger.critical(f'Не удалось подключиться к серверу {server_port}:{server_address}, '
                               f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        client_logger.error(f'В ответе сервера отсутствует необходимое поле: '
                            f'{missing_error.missing_field}')
        sys.exit(1)
    else:

        database = ClientDatabase(client_name)
        database_load(transport, database, client_name)

        sender = ClientSender(client_name, transport, database)
        sender.daemon = True
        sender.start()

        receiver = ClientReader(client_name, transport, database)
        receiver.daemon = True
        receiver.start()

        client_logger.debug('Процессы запущены.')

        while True:
            time.sleep(1)
            if receiver.is_alive() and sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
