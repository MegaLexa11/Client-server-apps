
# Порт по умолчанию для сетевого взаимодействия
DEFAULT_PORT = 7777

# IP адрес по умолчанию для подключения клиента
DEFAULT_IP_ADDRESS = '127.0.0.1'

# Максимальная очередь подключений
MAX_CONNECTIONS = 5

# Максимальная длина сообщения в байтах
MAX_PACKAGE_LENGTH = 1824

# Кодировка проекта
ENCODING = 'utf-8'

# Конфигурация сервера
SERVER_CONFIG = 'server.ini'

# Основные ключи для протокола JIM:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'

# Прочее
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
RESPONDEFAULT_IP_ADDRESSES = 'respondefault_ip_addresses'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
EXIT = 'exit'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
REMOVE_CONTACT = 'remove'
ADD_CONTACT = 'add'
USERS_REQUEST = 'get_users'

# Словари - ответы
RESPONSE_200 = {RESPONSE: 200}

RESPONSE_202 = {RESPONSE: 202,
                LIST_INFO: None}

RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}

