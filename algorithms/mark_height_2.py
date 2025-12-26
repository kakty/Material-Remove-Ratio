import numpy as np
from scipy import ndimage

def compute_plane_and_mark_height2(Z, delta=5):
    """
    Z: 2D numpy array, 高度矩阵
    delta: 超过平面平均高度 delta µm 的部分视为标记
    返回：
      plane_mean: 平面平均高度
      mark_mean: 标记带平均高度
      delta_h: 高度差
      mark_mask: 标记带布尔掩码
    """
    Z_valid = Z[np.isfinite(Z)]

    # 1. 平面平均高度
    plane_mean = np.mean(Z_valid)

    # 2. 标记带掩码
    mark_mask = Z > (plane_mean + delta)

    # 3. 可选：只取最大连通区域（防止孤立高点干扰）
    labeled, num_features = ndimage.label(mark_mask)
    if num_features > 1:
        # 取面积最大的连通区域
        sizes = ndimage.sum(mark_mask, labeled, range(1, num_features + 1))
        largest_label = np.argmax(sizes) + 1
        mark_mask = labeled == largest_label

    # 4. 标记带平均高度
    if np.sum(mark_mask) > 0:
        mark_mean = np.mean(Z[mark_mask])
    else:
        mark_mean = np.nan

    delta_h = mark_mean - plane_mean

    return plane_mean, mark_mean, delta_h