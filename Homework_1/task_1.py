def get_items_info(items):
    for el in items:
        print(f'Значение: {el}')
        print(f'Тип: {type(el)}')
        print('-' * 20)


string_els = ['Разработка', 'Сокет', 'Декоратор']
unicode_els = ['\u0420\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
               '\u0421\u043e\u043a\u0435\u0442\u000a',
               '\u0414\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440\u000a']

get_items_info(string_els)
get_items_info(unicode_els)

# Все данные элементы, не смотря на различия в записи, являются строками, причем эквивалентными
