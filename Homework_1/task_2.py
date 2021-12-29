def into_bytes(items):
    for el in items:
        el = eval(f'b"{el}"')
        print(el)
        print(type(el))
        print(len(el))
        print('-' * 20)


items_list = ['class', 'function', 'method']
into_bytes(items_list)
