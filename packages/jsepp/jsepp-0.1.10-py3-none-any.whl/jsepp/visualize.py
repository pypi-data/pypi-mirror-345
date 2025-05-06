import os
import numpy as np
from haversine import haversine
import matplotlib
import matplotlib.pyplot as plt
import pickle

matplotlib.use('Agg')

class SimpleDisWeightModel(object):
    def __init__(self, x, y, z, e=0.2):
        self.x = x
        self.y = y
        self.z = z
        self.e = e

    def excute(self, gridx, gridy):
        X, Y = np.meshgrid(gridx, gridy)
        total_weight = np.zeros_like(X)
        total_value = np.zeros_like(X)
        for i in range(len(self)):
            w = 1 / np.power(np.power(X - self.x[i], 2) + np.power(Y - self.y[i], 2), self.e)
            total_weight += w
            total_value += w * self.z[i]
        return np.divide(total_value, total_weight)

    def __len__(self):
        return len(self.x)

def rgba_to_hex(rgba):
    r, g, b, a = rgba
    return "#{:02x}{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255), int(a * 255))

def heatmap(X:np.ndarray, Y:np.ndarray, Q:np.ndarray, combine=None, combine_method='sum', imgpath=None, resolution=512,
            offset=0.1, levels=None, cache=None, cmap='rainbow')->str:
    def __get_nearest_points(X: np.ndarray, Y:np.ndarray):
        n = len(X)
        mini = 0
        minj = 1
        minV = 1e10
        for i in range(n - 1):
            for j in range(i + 1, n):
                dist = haversine((Y[i], X[i]), (Y[j], X[j])) * 1000
                if dist < minV:
                    mini, minj = i, j
                    minV = dist
        return mini, minj, minV

    def __combine_points(i, j, X, Y, Q, method):
        X[i] = (X[i] + X[j])/2
        Y[i] = (Y[i] + Y[j])/2
        if method == 'sum':
            Q[i] = Q[i] + Q[j]
        elif method == 'avg':
            Q[i] = (Q[i] + Q[j])/2
        else:
            raise ValueError(f'only accept method sum and avg, given {method}')
        return np.delete(X, j), np.delete(Y, j), np.delete(Q, j)

    def __save_cache(path, X, Y, Q):
        with open(path, 'wb') as f:
            pickle.dump({'X': X, 'Y': Y, 'Q': Q}, f)

    def __load_cache(path):
        with open(path, 'rb') as f:
            r = pickle.load(f)
        return r['X'], r['Y'], r['Q']

    if combine is not None:
        mini, minj, minV = __get_nearest_points(X, Y)
        while(minV <= combine):
            X, Y, Q = __combine_points(mini, minj, X, Y, Q, combine_method)
            print(minV, len(X))
            mini, minj, minV = __get_nearest_points(X, Y)
    # print('s')
    if cache is not None:
        if os.path.exists(cache):
            X, Y, Q = __load_cache(cache)
        else:
            __save_cache(cache, X, Y, Q)

    xstart, xend = min(X)-offset, max(X)+offset
    ystart, yend = min(Y)-offset, max(Y)+offset
    gridx = np.arange(xstart, xend, (xend - xstart) / resolution)
    gridy = np.arange(ystart, yend, (yend - ystart) / resolution)
    m = SimpleDisWeightModel(X, Y, Q, e=1.0)
    z = m.excute(gridx, gridy)
    plt.figure(figsize=(10, 10 * (yend - ystart) / (yend - ystart)))
    # info = plt.contourf(gridx, gridy, z, cmap='rainbow', extend='both')
    print(f'{z.max():.4f}, {z.min():.4f}')
    # info = plt.contourf(gridx, gridy, z, levels=np.linspace(info.levels[0], info.levels[-1], 8), cmap='rainbow',
    #                     extend='both')
    if levels is None:
        info = plt.contourf(gridx, gridy, z, levels=np.percentile(z.flatten(), np.linspace(100/8, 700/8, num=8)), cmap=cmap,
                            extend='both')
    else:
        info = plt.contourf(gridx, gridy, z, levels=levels, cmap=cmap, extend='both')
    # plt.colorbar(info)
    # plt.show()
    plt.axis('off')
    if imgpath is None:
        imgpath = 'heatmap.png'
    plt.savefig(imgpath, bbox_inches='tight', pad_inches=0, transparent=True)  # https://www.zhihu.com/question/506015285/answer/2270700851
    plt.close()
    hexcode = [rgba_to_hex(x) for x in info.get_cmap()(np.linspace(0, 1, len(info.levels)))]
    return imgpath, [xstart, ystart], [xend, yend], info.levels.tolist(), hexcode