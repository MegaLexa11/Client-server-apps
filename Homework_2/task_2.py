'''
Создать функцию write_order_to_json(), в которую передается 5 параметров — товар (item), количество (quantity),
цена (price), покупатель (buyer), дата (date). В это словаре параметров обязательно должны присутствовать юникод-символы,
отсутствующие в кодировке ASCII. Функция должна предусматривать запись данных в виде словаря в файл orders.json.
При записи данных указать величину отступа в 4 пробельных символа;
Необходимо также установить возможность отображения символов юникода: ensure_ascii=False;
Проверить работу программы через вызов функции write_order_to_json() с передачей в нее значений каждого параметра.
'''


import json


def write_order_to_json(item, quantity, price, buyer, date):
    with open('result_task_2.json', 'r', encoding='utf-8') as file:
        order_dict = json.load(file)

    dict_to_write = {
        'item': item,
        'quantity': quantity,
        'price': price,
        'buyer': buyer,
        'date': date,
    }

    order_dict['orders'].append(dict_to_write)

    with open('result_task_2.json', 'w', encoding='utf-8') as file:
        json.dump(order_dict, file, indent=4, ensure_ascii=False)
    file.close()


if __name__ == '__main__':
    write_order_to_json('Стол', 22, 11999.99, 'Andrew', '11-12-2021')
