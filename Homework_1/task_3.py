def check_bytes(items):
    for el in items:
        try:
            eval_el = eval(f'b"{el}"')
            print(f'{el}: {eval_el}')
        except SyntaxError:
            print(f'{el}: тип bytes может содержать только элементы ASCII!')


items_list = ['attribute', 'функция', 'type', 'класс']
check_bytes(items_list)
