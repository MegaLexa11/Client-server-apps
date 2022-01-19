import sys
import os
import logging
import logging.handlers

sys.path.append('../')

# Настраиваем директорию для вывода логов
path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(path, 'server.log')

# Создаем логгер
server_log = logging.getLogger('server')

# Создаем шаблон выводимого сообщения
server_formatter = logging.Formatter('%(asctime)s %(levelname)-10s %(filename)s %(message)s')

# Создаем файл для вывода сообщений (с ротацией)
file_handler = logging.handlers.TimedRotatingFileHandler(path, encoding='utf-8', interval=1, when='D')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(server_formatter)

server_log.addHandler(file_handler)
server_log.setLevel(logging.DEBUG)


if __name__ == '__main__':
    server_log.debug('Отладочное сообщение')
    server_log.info('Информационное сообщение')
    server_log.warning('Предупреждение')
    server_log.error('Ошибка')
    server_log.critical('Критическая ошибка')

