# atsdpc/atsdpc/main.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .clustering_utils import *
from .metrics import purity_score
import Evaluation as Ev


def run_clustering(attri=7, k=3, file_path='Wine_opt.csv'):
    origin_data, y_true, statistic = load_and_preprocess_data(file_path, attri)
    ditance_in_total = distance_workout(len(origin_data), attri, statistic,
                                        origin_data)
    arr1 = np.array(ditance_in_total.loc[:, :].values)
    arr2 = arr1.reshape((len(origin_data) * len(origin_data),))
    list1 = list(arr2)
    list1.sort()
    dc = list1[int(len(origin_data) * len(origin_data) * 0.02 + len(
        origin_data)) - 1]
    density_local = density_workout(ditance_in_total, len(origin_data), dc)
    high_den, core = high_denworkout(density_local, ditance_in_total,
                                    len(origin_data))
    core, sort_array = cluster_density_core(len(origin_data), density_local,
                                            high_den, y_true, k)
    x = density_local.loc[:, 'ρ']
    y = high_den.loc[:, 'δ']
    plt.scatter(x, y)
    plt.xlabel('density')
    plt.ylabel('high density of distance')
    plt.title('Result')
    plt.show()
    class_result = cluster_result(len(origin_data), core, density_local, k,
                                  ditance_in_total)
    purity = purity_score(y_true.values, class_result.iloc[:, 0].values)
    acc_value = Ev.acc(y_true.values, class_result.iloc[:, 0].values)
    nmi = Ev.nmi(class_result.iloc[:, 0].tolist(), y_true.values.tolist())
    ari = Ev.ari(class_result.iloc[:, 0].tolist(), y_true.values.tolist())
    fmi = Ev.fmi(class_result.iloc[:, 0].tolist(), y_true.values.tolist())
    best_acc = acc_value
    best_metrics = {}
    best_metrics = {
        'Purity': purity,
        'ACC': acc_value,
         'NMI': nmi,
         'ARI': ari,
         'FMI': fmi
            }

    for miu in range(10):
        class_result = KMDPC(class_result, k, attri, origin_data,
                             ditance_in_total, density_local)
        purity = purity_score(y_true.values, class_result.iloc[:, 0].values)
        acc_value = Ev.acc(y_true.values, class_result.iloc[:, 0].values)
        nmi = Ev.nmi(class_result.iloc[:, 0].tolist(), y_true.values.tolist())
        ari = Ev.ari(class_result.iloc[:, 0].tolist(), y_true.values.tolist())
        fmi = Ev.fmi(class_result.iloc[:, 0].tolist(), y_true.values.tolist())

        if acc_value > best_acc:
            best_acc = acc_value
            best_metrics = {
                'Purity': purity,
                'ACC': acc_value,
                'NMI': nmi,
                'ARI': ari,
                'FMI': fmi
            }

    return best_metrics