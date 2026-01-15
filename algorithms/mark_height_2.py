import numpy as np


def compute_groove_depth_method2(
        Z,
        plane_top_percent=50,  # 平面取值范围：最高的 50%
        groove_bottom_percent=20  # 槽取值范围：最低的 20%
):
    """
    方法2：基于分位数的凹槽深度计算 (Groove Depth Analysis)

    参数:
    plane_top_percent: 取最高的多少比例作为平面 (例如 50 代表取 Top 50%)
    groove_bottom_percent: 取最低的多少比例作为槽底 (例如 20 代表取 Bottom 20%)

    返回:
    z_plane       : 平面平均高度
    z_groove      : 槽底平均高度
    depth         : 槽深 (平面 - 槽底)
    plane_mask    : 平面区域 mask
    groove_mask   : 槽区域 mask
    """

    # 1. 展平并去 NaN
    z_flat = Z.flatten()
    z_valid = z_flat[~np.isnan(z_flat)]

    if z_valid.size == 0:
        return np.nan, np.nan, np.nan, None, None

    # 2. 计算阈值
    # 平面阈值：如果是取 Top 50%，则分位点是 100 - 50 = 50
    # 如果平面取 Top 30%，则分位点是 70
    p_threshold_val = np.percentile(z_valid, 100 - plane_top_percent)

    # 槽阈值：取 Bottom 20%，分位点就是 20
    g_threshold_val = np.percentile(z_valid, groove_bottom_percent)

    # 3. 生成 Mask
    # 平面是高于阈值的部分
    plane_mask = (Z >= p_threshold_val) & np.isfinite(Z)
    # 槽是低于阈值的部分
    groove_mask = (Z <= g_threshold_val) & np.isfinite(Z)

    # 4. 计算平均高度
    z_plane = np.mean(Z[plane_mask]) if np.any(plane_mask) else np.nan
    z_groove = np.mean(Z[groove_mask]) if np.any(groove_mask) else np.nan

    # 5. 槽深 = 平面 - 槽底 (正值代表深度)
    depth = z_plane - z_groove

    return z_plane, z_groove, depth, plane_mask, groove_mask