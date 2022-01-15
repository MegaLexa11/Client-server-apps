from chardet import detect


def detect_encoding(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    encoding = detect(content)['encoding']
    return encoding
