'''
Подготовить данные для записи в виде словаря, в котором первому ключу соответствует список, второму — целое число,
третьему — вложенный словарь, где значение каждого ключа — это целое число с юникод-символом, отсутствующим в кодировке
ASCII (например, €);
Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml.
При этом обеспечить стилизацию файла с помощью параметра default_flow_style, а также установить возможность работы с
юникодом: allow_unicode = True;
Реализовать считывание данных из созданного файла и проверить, совпадают ли они с исходными.
'''


import yaml


def write_to_yaml(models: list, quantity: int, price_models: dict):
    dict_to_write = {
        'models': models,
        'quantity': quantity,
        'price_models': price_models,
    }

    with open('result_task_3.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(dict_to_write, file, default_flow_style=False, allow_unicode=True)


if __name__ == '__main__':
    _list = ['e123', 'е125', 't€11']
    _num = 11
    _dict = {el: (ind * 100 + 999) for ind, el in enumerate(_list)}

    write_to_yaml(_list, _num, _dict)

'''
Так как вы говорили не создавать самому структуру yaml файла, то здесь идет исключительно запись в него одного объекта.
И вот еще один момент:
Не понял смысла в строке: 'значение каждого ключа — это целое число с юникод-символом': нужно было представлять
это в виде строки? Я представил в виде целого числа, а unicode символ добавил в другом месте
'''
