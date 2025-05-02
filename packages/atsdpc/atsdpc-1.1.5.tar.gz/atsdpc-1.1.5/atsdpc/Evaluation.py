import numpy as np
from sklearn import metrics
from sklearn.metrics import adjusted_rand_score
from sklearn import metrics
from sklearn.metrics import fowlkes_mallows_score
import numpy as np
from scipy.optimize import linear_sum_assignment

def acc(y_true, y_pred):
    y_true = y_true.astype(np.int64)
    assert y_pred.size == y_true.size
    D = max(y_pred.max(), y_true.max()) + 1
    w = np.zeros((D, D), dtype=np.int64)
    for i in range(y_pred.size):
        w[y_pred[i], y_true[i]] += 1
    # 使用 linear_sum_assignment 计算最优匹配
    row_ind, col_ind = linear_sum_assignment(w.max() - w)
    # 计算准确率
    return sum([w[row, col] for row, col in zip(row_ind, col_ind)]) * 1.0 / y_pred.size
def ari(list1,list2):
    return adjusted_rand_score(list1,list2 )
def nmi(list1,list2):
    return metrics.normalized_mutual_info_score(list1, list2)
def fmi(list1,list2):
    return fowlkes_mallows_score(list1,list2)