import sys
import os
import logging
import logging.handlers

sys.path.append('../')

# Настраиваем директорию для вывода логов
path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(path, 'client.log')

# Создаем логгер
client_log = logging.getLogger('client')

# Создаем шаблон выводимого сообщения
server_formatter = logging.Formatter('%(asctime)s %(levelname)-10s %(filename)s %(message)s')

# Создаем файл для вывода сообщений (с ротацией)
file_handler = logging.FileHandler(path, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(server_formatter)

client_log.addHandler(file_handler)
client_log.setLevel(logging.DEBUG)


if __name__ == '__main__':
    client_log.debug('Отладочное сообщение')
    client_log.info('Информационное сообщение')
    client_log.warning('Предупреждение')
    client_log.error('Ошибка')
    client_log.critical('Критическая ошибка')
