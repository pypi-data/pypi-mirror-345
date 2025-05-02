import pandas as pd
import numpy as np
import math as ma
from sklearn.preprocessing import MinMaxScaler
import operator


def load_and_preprocess_data(file_path, attri):

    origin_data = pd.read_csv(file_path, index_col=0)
    y_true = origin_data.iloc[:, -1]

    origin_data = origin_data.iloc[:, :-1].values
    origin_data = pd.DataFrame(origin_data, index=y_true.index,
                               columns=list(range(1, attri + 1)))
    statistic = list(
        origin_data.describe().loc['std', :] / abs(
            origin_data.describe().loc['mean', :]))
    return origin_data, y_true, statistic


def distance(i, j, statistic, origin_data, n):
    result = 0
    for d in range(1, n + 1):
        pre1 = statistic[d - 1] * (origin_data.loc[i, d] - origin_data.loc[
            j, d]) ** 2
        result += pre1
    return ma.sqrt(result)


def distance_workout(n, dem, statistic, origin_data):
    distance_in_total = pd.DataFrame(index=range(1, n + 1),
                                     columns=range(1, n + 1))
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            distance_in_total.loc[i, j] = distance(i, j, statistic,
                                                   origin_data, dem)
    return distance_in_total


def density(d_i, d_c1):
    list1 = []
    for i in range(len(d_i)):
        list1.append(d_c1)
    d_c = np.array(list1)
    a = -(d_i.astype(float) ** 2) / (d_c.astype(float) ** 2)
    answer = sum(np.exp(a))
    return answer


def density_workout(distance_in_total, n, dc1):
    density_local = pd.DataFrame(index=range(1, n + 1), columns=['ρ'])
    dc = dc1
    for i in range(1, n + 1):
        array_distance = np.array(distance_in_total.loc[i, :])
        den = density(array_distance, dc)
        density_local.loc[i, 'ρ'] = den
    return density_local


def high_denworkout(density_local, distance_in_total, n):
    click = 0
    core = []
    high_den = pd.DataFrame(index=range(1, n + 1), columns=['δ'])
    for i in range(1, n + 1):
        middle = []
        for j in range(1, n + 1):
            if i == j:
                continue
            if density_local.loc[i, 'ρ'] < density_local.loc[j, 'ρ'] or (
                    density_local.loc[i, 'ρ'] <= density_local.loc[j, 'ρ'] and
                    click == 1):
                dis = distance_in_total.loc[i, j]
                middle.append(dis)
        if middle == [] and click == 0:
            core.append(i)
            max1 = max(distance_in_total.loc[i, :])
            high_den.loc[i, 'δ'] = max1
            click = 1
            continue
        min1 = min(middle)
        high_den.loc[i, 'δ'] = min1
    return high_den, core


def cluster_density_core(n, density_local, high_den, y_true, k):
    array_den = np.array(density_local.loc[:, 'ρ'])
    array_high = np.array(high_den.loc[:, 'δ'])
    array_score = array_den * array_high
    sort_array = np.sort(array_score)
    list_core = []
    label = []
    for j in range(10000):
        for i in range(0, n):
            if array_score[i] == sort_array[n - 1 - j] and y_true[
                i + 1] not in set(label):
                list_core.append(i + 1)
                label.append(y_true[i + 1])
        if len(label) == k:
            break
    return list_core, sort_array


def cluster_result(n, core, den1, k, ditance_in_total):
    result = pd.DataFrame(index=den1.index, columns=['result'])
    class_end = []
    distance1 = []
    for i in range(k):
        class_end.append([])
        distance1.append([])
    den_cluster = []
    for i in range(1, n + 1):
        den_cluster.append([i, den1.loc[i, 'ρ']])
    for i in range(k):
        class_end[i].append(core[i])
    den_cluster.sort(key=operator.itemgetter(1), reverse=True)
    for i in range(0, n):
        if den_cluster[i][0] in core:
            continue
        for b in range(k):
            for j in range(len(class_end[b])):
                distance1[b].append(
                    ditance_in_total.loc[den_cluster[i][0], class_end[b][j]])
            distance1[b] = [min(distance1[b])]
        for m in range(k):
            if min(distance1) == distance1[m]:
                class_end[m].append(den_cluster[i][0])
        for g in range(k):
            distance1[g].clear()
    for i in range(k):
        for j in class_end[i]:
            result.loc[j, 'result'] = i + 1
    return result


def average(class1, attri, origin_data):
    avg_total1 = []
    total = 0
    for j in range(1, attri + 1):
        for i in class1:
            total += origin_data.loc[i, j]
        avg_total1.append(total / len(class1))
        total = 0
    return avg_total1


def OKMD(center, class1, attri, origin_data):
    statistic = list(
        origin_data.describe().loc['std', :] / origin_data.describe().loc[
            'mean', :])
    class1_distance = pd.DataFrame(index=class1.index, columns=['distance'])
    d = []
    for i in class1.index:
        for j in range(1, attri + 1):
            d.append(statistic[j - 1] * (origin_data.loc[i, j] - center[
                j - 1]) ** 2)
        dis = ma.sqrt(sum(d))
        d.clear()
        class1_distance.loc[i, 'distance'] = dis
    return class1_distance


def overlap_values(class_total, ditance_in_total):
    count = 0
    list_middle = []
    list_outclass = []
    for i in range(len(class_total)):
        for ii in class_total[i]:
            for j in range(len(class_total)):
                if i == j:
                    continue
                else:
                    for jj in class_total[j]:
                        list_middle.append(ditance_in_total.loc[ii, jj])
            min_distance = min(list_middle)
            list_outclass.append(min_distance)
            list_middle.clear()
    d0 = sum(list_outclass) / len(list_outclass)
    for dist in list_outclass:
        if dist < d0:
            count += 1
    return count


def KMDPC(class_result, k, attri, origin_data, ditance_in_total, density_local):
    result = class_result
    columns_name = []
    class_total = []
    avg_class = []
    for i in range(1, k + 1):
        columns_name.append(str(i))
    columns_name.append('label0')    
    distance_matrix = pd.DataFrame(index=result.index, columns=columns_name)
    distance_matrix.loc[:, 'label0'] = result.values.flatten()
    result_group = result.groupby(['result'])
    for i in range(k):
        class_total.append(list(result_group.get_group(i + 1).index))
    for i in range(k):
        avg_class.append(average(class_total[i], attri, origin_data))
    for i in range(k):
        class1 = origin_data.loc[class_total[i]]
        # 计算当前类簇的距离
        class1_distance = OKMD(avg_class[i], class1, attri, origin_data)
        # 创建一个和 distance_matrix 列长度相同的数组
        full_distance = pd.Series(index=distance_matrix.index, dtype=float)
        # 将当前类簇的距离填充到对应位置
        full_distance.loc[class_total[i]] = class1_distance.values.flatten()
        # 将填充好的数组赋值给 distance_matrix 的列
        distance_matrix.iloc[:, i] = full_distance
    list_judge = []
    for i in range(len(origin_data)):
        for j in range(k):
            if min(distance_matrix.iloc[i, :k]) != distance_matrix.iloc[i, j]:
                continue
            if min(distance_matrix.iloc[i, :k]) == distance_matrix.iloc[
                i, j] and distance_matrix.iloc[i, k] == j + 1:
                continue
            list_judge.append(i + 1)
    if list_judge == []:
        return class_result
    R = overlap_values(class_total, ditance_in_total)
    balance_matrix = distance_matrix.describe()
    balance_value = (sum(balance_matrix.iloc[1, :k]) / k) / (
            sum(ditance_in_total.mean()) / len(ditance_in_total.mean()))
    weight_origin = [balance_value * (1 - R / len(result.index)),
                     R / len(result.index)]
    result_KMDPC = pd.DataFrame(index=list_judge, columns=['result'])
    columns_name.remove('label0')
    distance_DPC = pd.DataFrame(index=list_judge, columns=columns_name)
    distance_middle = []
    min2 = 0
    for k1 in range(k):
        for i in list_judge:
            for j in class_total[k1]:
                if density_local.loc[i, 'ρ'] < density_local.loc[j, 'ρ']:
                    distance_middle.append(ditance_in_total.loc[i, j])
            if distance_middle == []:
                distance_middle.append(6500)
            min2 = min(distance_middle)
            distance_DPC.loc[i, str(k1 + 1)] = min2
            distance_middle.clear()
    distance_judge = pd.DataFrame(index=distance_DPC.index,
                                  columns=columns_name)
    for k2 in range(k):
        for i in distance_DPC.index:
            distance_judge.loc[i, str(k2 + 1)] = weight_origin[0] * \
                                                 distance_DPC.loc[
                                                     i, str(k2 + 1)] + \
                                                 weight_origin[1] * \
                                                 distance_matrix.loc[
                                                     i, str(k2 + 1)]
    for i in range(len(distance_judge.index)):
        for k3 in range(k):
            if min(distance_judge.iloc[i, :k]) == distance_judge.iloc[i, k3]:
                result_KMDPC.iloc[i, 0] = k3 + 1
    for i in class_result.index:
        if i in result_KMDPC.index:
            class_result.loc[i, 'result'] = result_KMDPC.loc[i, 'result']
    return class_result
    