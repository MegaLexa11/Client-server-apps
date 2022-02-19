import logging

server_logger = logging.getLogger('Server')


class Port:
    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            server_logger.critical(f'Попытка запуска сервера с неверно указанным портом {value}. '
                                   f'Доступные адреса портов с 1024 по 65535')
            exit(1)

        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
