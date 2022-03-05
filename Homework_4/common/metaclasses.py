import dis


# Метакласс для проверки сервера:
class ServerVerifier(type):
    def __init__(cls, cls_name, bases, cls_dict):
        methods = []
        attrs = []
        for func in cls_dict:
            try:
                ret = dis.get_instructions(cls_dict[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    # print(i)
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            attrs.append(i.argval)
        # print(methods)
        # print(attrs)

        if 'connect' in methods:
            raise TypeError('Исползование метода connect недопустимо в серверном классе')
        if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
            raise TypeError('Некорректная инициализация сокета.')
        super().__init__(cls_name, bases, cls_dict)


# Метакласс для проверки клиентов
class ClientVerifier(type):
    def __init__(cls, cls_name, bases, cls_dict):
        methods = []
        for func in cls_dict:
            try:
                ret = dis.get_instructions(cls_dict[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    # print(i)
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
        # print(methods)

        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('В классе обнаружено использование запрещенного метода')
        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')
        super().__init__(cls_name, bases, cls_dict)
