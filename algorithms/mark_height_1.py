import numpy as np

def compute_plane_marker_height1(
    Z,
    plane_percentile=60,
    marker_percentile=80
):
    """
    方法一：计算平面 / 标记带高度，同时输出提及去除率（delta_z * marker_mask）

    返回：
    z_plane       : 平面平均高度
    z_marker      : 标记带平均高度
    delta_z       : 高度差
    plane_mask    : 平面区域 mask (bool, same shape as Z)
    marker_mask   : 标记区域 mask (bool, same shape as Z)
    removal_map   : 提及去除率 map (float, same shape as Z)
    """

    # 1. 展平并去 NaN（只用于阈值计算）
    z_flat = Z.flatten()
    z_valid = z_flat[~np.isnan(z_flat)]

    if z_valid.size == 0:
        shape = Z.shape
        return np.nan, np.nan, np.nan, None, None, np.full(shape, np.nan)

    # 2. 计算阈值
    plane_th = np.percentile(z_valid, plane_percentile)
    marker_th = np.percentile(z_valid, marker_percentile)

    # 3. mask（保持 Z 的二维结构）
    plane_mask = (Z <= plane_th) & np.isfinite(Z)
    marker_mask = (Z >= marker_th) & np.isfinite(Z)

    # 4. 高度
    z_plane = np.mean(Z[plane_mask]) if np.any(plane_mask) else np.nan
    z_marker = np.mean(Z[marker_mask]) if np.any(marker_mask) else np.nan
    delta_z = z_marker - z_plane

    # 5. 提及去除率
    removal_map = delta_z * marker_mask.astype(float)  # 非标记区域为0，标记区域为delta_z

    return z_plane, z_marker, delta_z, plane_mask, marker_mask, removal_map
