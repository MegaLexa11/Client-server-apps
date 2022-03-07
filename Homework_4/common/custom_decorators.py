import logging
import inspect
import socket
import sys
import logging
import logs.config_server_log
import logs.config_client_log

if sys.argv[0].find('client') == -1:
    func_logger = logging.getLogger('server')
else:
    func_logger = logging.getLogger('client')


def log(func):
    """
    Декоратор, выполняющий логирование вызовов функций.
    Сохраняет события типа debug, содержащие
    информацию об имени вызываемой функиции, параметры, с которыми
    вызывается функция, и модуль, вызывающий функцию.
    """
    def wrapper(*args, **kwargs):
        func_result = func(*args, **kwargs)
        func_name = func.__name__
        func_module = func.__module__
        if args or kwargs:
            param_text = f'с параметрами {args}, {kwargs} '
        else:
            param_text = ''
        text_to_log = f'Функция {func_name} {param_text}' \
                      f'из модуля {func_module} была вызвана из функции {inspect.stack()[1][3]}'

        func_logger.debug(text_to_log)
        return func_result
    return wrapper
