# 参照地表水GB3838-2002
CLASS_LIMITS = {
    1: {
        'DO': 7.5,  # 溶解氧，mg/L
        'CODMn': 2.0,  # 高锰酸盐指数，mg/L
        'NH3_N': 0.15,  # 氨氮，mg/L
        'TN': 0.2,  # 总氮，mg/L
        'TP': 0.02,  # 总磷，mg/L。湖、库I-V限值0.01/0.025/0.05/0.1/0.2
    },
    2: {
        'DO': 6.0,
        'CODMn': 4.0,
        'NH3_N': 0.5,
        'TN': 0.5,
        'TP': 0.1,
    },
    3: {
        'DO': 5.0,
        'CODMn': 6.0,
        'NH3_N': 1.0,
        'TN': 1.0,
        'TP': 0.2,
    },
    4: {
        'DO': 3.0,
        'CODMn': 10.0,
        'NH3_N': 1.5,
        'TN': 1.5,
        'TP': 0.3,
    },
    5: {
        'DO': 2.0,
        'CODMn': 15.0,
        'NH3_N': 2.0,
        'TN': 2.0,
        'TP': 0.4,
    },
}

def classify_water_quality(v: list or float, species:str or list = ['DO','CODMn', 'NH3_N', 'TN', 'TP']):
    def __class2str(c):
        if c <= 3:
            return "优良（I~III），水源地、自然保护区、水产养殖区等"
        elif c==4:
            return "四类，工业用水区及人体非直接接触娱乐用水区"
        elif c==5:
            return "五类，农业用水及一般景观用水"
        else:
            return "劣五类，污染水域"
    if isinstance(v, float):
        if species in CLASS_LIMITS[5].keys():
            if species != "DO":
                for i in range(5):
                    if v <= CLASS_LIMITS[i+1][species]:
                        return i+1, __class2str(i+1)
                return 6, __class2str(6)
            else:
                for i in range(5):
                    if v >= CLASS_LIMITS[i+1][species]:
                        return i+1, __class2str(i+1)
                return 6, __class2str(6)
        else:
            raise Exception(f'species should be set properly, accept: DO, CODMn, NH3_N, TN, TP, given {species}')
    elif isinstance(v, list) and len(v) == 5:
        classes = []
        for x, s in zip(v,species):
            classes.append(classify_water_quality(x, s)[0])
        return min(classes), __class2str(min(classes))
    else:
        raise Exception(f'cannot resolve input value: {v}')
