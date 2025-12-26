import numpy as np

def comupte_plane_and_marker_height3(
    Z,
    plane_percentile=60,
    marker_percentile=60
):
    """
    基于分位数的平面 / 标记带高度计算

    返回：
    z_plane       : 平面平均高度
    z_marker      : 标记带平均高度
    delta_z       : 高度差
    plane_mask    : 平面区域 mask (bool, same shape as Z)
    marker_mask   : 标记区域 mask (bool, same shape as Z)
    """

    # 1. 展平并去 NaN（只用于阈值计算）
    z_flat = Z.flatten()
    z_valid = z_flat[~np.isnan(z_flat)]

    if z_valid.size == 0:
        return np.nan, np.nan, np.nan, None, None

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

    return z_plane, z_marker, delta_z, plane_mask, marker_mask
