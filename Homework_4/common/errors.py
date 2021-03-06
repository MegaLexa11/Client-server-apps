# Приняты некорректные данные от сокета
class IncorrectDataReceivedError(Exception):
    def __str__(self):
        return 'Принято некорректное сообщение от удаленного компьютера.'


# Аргументом функции не является словарь
class NonDictInputError(Exception):
    def __str__(self):
        return 'Аргумент функции должен быть словарем.'


# В словаре отсутствуют обязательные поля
class ReqFieldMissingError(Exception):
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'В принятом словаре отсутствует обязательное поле {self.missing_field}'


# Ошибка сервера
class ServerError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text
