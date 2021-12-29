from chardet import detect


def read_file(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    encoding = detect(content)['encoding']

    with open(filename, 'r', encoding=encoding) as f:
        for el_str in f:
            print(el_str)
    f.close()


f_name = 'test.txt'

# Создание и заполнение файла текстом
with open(f_name, 'w', encoding='utf-8') as file:
    file.write('сетевое программирование\nсокет\nдекоратор')
file.close()

read_file(f_name)
