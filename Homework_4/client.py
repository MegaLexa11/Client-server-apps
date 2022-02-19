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
    DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, MESSAGE_TEXT, SENDER, DESTINATION, EXIT
from common.utils import send_message, get_message
from metaclasses import ClientVerifier


client_logger = logging.getLogger('client')


class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name,
        self.sock = sock
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
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        client_logger.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            send_message(self.sock, message_dict)
            client_logger.info(f'Отправлено сообщение пользователю {to_user}')
        except:
            client_logger.critical('Потеряно соединение с сервером.')
            sys.exit(1)

    def run(self):
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                try:
                    send_message(self.sock, self.create_exit_message())
                except:
                    pass
                print('Завершение соединения...')
                client_logger.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробуйте снова.\nhelp - вывести возможные команды.')


class ClientReader(threading.Thread):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def run(self):
        while True:
            try:
                message = get_message(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and MESSAGE_TEXT in message\
                    and DESTINATION in message and message[DESTINATION] == self.account_name:
                    print(f'\nСообщение от пользователя {message[SENDER][0]}: {message[MESSAGE_TEXT]}')
                    client_logger.info(f'\nПолучено сообщение от пользователя {message[SENDER][0]}: '
                                       f'{message[MESSAGE_TEXT]}')
                else:
                    client_logger.error(f'Получено некорректное сообщение с сервера: {message}')
            except IncorrectDataReceivedError:
                client_logger.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                client_logger.critical(f'Потеряно соединение с сервером.')
                break


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


def main():
    server_address, server_port, client_name = arg_parser()

    if not client_name:
        client_name = input('Введите имя пользователя: ')

    print(f'Добро пожаловать в консольный мессенджер. \nИмя пользователя: {client_name}')

    client_logger.info(f'Запущен клиент с параметрами: адрес сервера: {server_address}, '
                       f'порт: {server_port}, имя пользователя: {client_name}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        receiver = ClientReader(client_name, transport)
        receiver.daemon = True
        receiver.start()

        sender = ClientSender(client_name, transport)
        sender.daemon = True
        sender.start()

        client_logger.debug('Процессы запущены.')

        while True:
            time.sleep(1)
            if receiver.is_alive() and sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
