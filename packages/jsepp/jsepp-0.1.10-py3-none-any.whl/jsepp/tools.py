import numpy as np

def gen_rand(n:int)->str:
    return ''.join(np.random.choice(list('abcdefghijklmnopqrstuvwxzy01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'), size=n, replace=True))