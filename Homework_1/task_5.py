import chardet
import subprocess
import platform


def get_ping_result(amount, host):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    args = ['ping', param, str(amount), host]
    result = subprocess.Popen(args, stdout=subprocess.PIPE)
    for line in result.stdout:
        result = chardet.detect(line)
        line = line.decode(result['encoding']).encode('utf-8')
        print(line.decode('utf-8'))


get_ping_result(2, 'youtube.com')
