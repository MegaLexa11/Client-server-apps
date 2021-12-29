'''
Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие и считывание данных.
В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения каждого параметра поместить в
соответствующий список. Должно получиться четыре списка — например, os_prod_list, os_name_list, os_code_list,
os_type_list. В этой же функции создать главный список для хранения данных отчета — например, main_data — и поместить
в него названия столбцов отчета в виде списка: «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения для этих столбцов также оформить в виде списка и поместить в файл main_data (также для каждого файла);
Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой функции реализовать получение данных
через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий CSV-файл;
Проверить работу программы через вызов функции write_to_csv().
'''


import re
import csv
from find_coding import detect_encoding
# Добавить угадывание кодировки


def get_data(files):
    col_names = ['Изготовитель ОС', 'Название ОС', 'Код продукта', 'Тип системы']
    # Может не совсем так понял суть задания, но каждый список с элементами поместил в отдельный файл
    val_files_names = ['os_prod_list.csv', 'os_name_list.csv', 'os_code_list.csv', 'os_type_list.csv']

    for ind, col_el in enumerate(col_names):
        val_list = []
        for file in files:
            encoding = detect_encoding(file)
            file_read = open(file, 'r', encoding=encoding)
            file_text = file_read.read()
            # Здесь хотел также убирать неограниченное количество пробелов, но условие не позволяло это сделать
            pattern = eval(f'r"(?<={col_el}\:).*"')
            col_val = re.search(pattern, file_text)
            # В итоге, здесь убрал лишние пробелы с помощью встроенной функции
            val_list.append(col_val.group(0).strip())
            file_read.close()

        with open(val_files_names[ind], 'w', encoding='utf-8') as val_file:
            val_file_writer = csv.writer(val_file)
            val_file_writer.writerow(val_list)
        val_file.close()

    with open('col_names.csv', 'w', encoding='utf-8') as name_file:
        name_file_writer = csv.writer(name_file)
        name_file_writer.writerow(col_names)
    name_file.close()

    val_files_names.insert(0, 'col_names.csv')

    return val_files_names


# Как-то совсем запутался в форомулировках задания, поэтому сделал как ниже
def write_to_csv(files):
    filenames = get_data(files)
    result_list = []
    with open(filenames[0], 'r', encoding='utf-8') as col_name_file:
        col_name_file_reader = csv.reader(col_name_file)
        result_list.append(next(col_name_file_reader))

    for i in range(len(files)):
        val_list = []
        for file in filenames[1:]:
            with open(file, 'r', encoding='utf-8') as list_file:
                list_file_reader = csv.reader(list_file)
                val_list.append(next(list_file_reader)[i])
        result_list.append(val_list)

    with open('result_task_1.csv', 'w', encoding='utf-8') as result_file:
        result_file_writer = csv.writer(result_file)
        for row in result_list:
            result_file_writer.writerow(row)
    result_file.close()


if __name__ == '__main__':
    files_list = ['info_1.txt', 'info_2.txt', 'info_3.txt']
    print(write_to_csv(files_list))
