from statsmodels.tsa.ar_model import AutoReg
import numpy as np

def autoreg_fill(x:np.ndarray, rank:int) -> np.ndarray:
    for i in range(len(x)):
        if np.isnan(x[i]):
            if i > 10:
                model = AutoReg(x[:i], rank)
                r = model.fit()
                x[i] = r.predict(i, i)[0]
            elif i == 0:
                for j in range(len(x)):
                    if not np.isnan(x[j]):
                        x[0] = x[j]
                        break
            else:
                x[i] = x[i - 1]
    return x