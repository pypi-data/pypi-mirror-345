

def load_config(path='config', encoding='utf-8'):
    def __tryformat(s):
        try:
            return int(s)
        except:
            try:
                return float(s)
            except:
                return s

    config = {}
    with open(path, 'r', encoding=encoding) as f:
        for l in f.readlines():
            if l.startswith('==='):
                continue
            else:
                newl = l
                if '&&&' in l:
                    newl = l.split('&&&')[0].strip()
                if '=' in newl:
                    keyvalue = newl.split('=')
                    keyvalue = [x.strip() for x in keyvalue]
                    if len(keyvalue) != 2:
                        print(f'WARNING: config file {path} has line {l} with invalid format')
                    config[keyvalue[0]] = __tryformat(keyvalue[1])
                else:
                    print(f'WARNING: config file {path} has line {l} with invalid format')
    return config