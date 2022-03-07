# Приняты некорректные данные от сокета
class IncorrectDataReceivedError(Exception):
    """
    Класс - исключение для обработки получения некорректных данных.
    """

    def __str__(self):
        return 'Принято некорректное сообщение от удаленного компьютера.'


# Аргументом функции не является словарь
class NonDictInputError(Exception):
    """
    Класс - исключение для обработки сообщения, не содержащего словарь.
    """

    def __str__(self):
        return 'Аргумент функции должен быть словарем.'


# В словаре отсутствуют обязательные поля
class ReqFieldMissingError(Exception):
    """
    Класс - исключение для обработки словарей с отсутствием необходимых полей.
    При генерации требует строку с полем, отсутствующим в словаре.
    """

    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'В принятом словаре отсутствует обязательное поле {self.missing_field}'


# Ошибка сервера
class ServerError(Exception):
    """
    Класс - исключение для обработки ошибок сервера.
    При генерации требует строку с описанием ошибки,
    полученную с сервера.
    """

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text
