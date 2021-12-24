def word_encoding(items):
    for ind, el in enumerate(items):
        items[ind] = el.encode('utf-8')
    print(items)

    for ind, el in enumerate(items):
        items[ind] = el.decode('utf-8')
    print(items)


item_list = ['администрирование', 'разработка', 'protocol', 'standard']
word_encoding(item_list)
