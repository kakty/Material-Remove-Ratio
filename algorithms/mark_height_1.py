import numpy as np

def compute_plane_and_marker_height1(Z, plane_percentile=60, marker_percentile=70):
    Z_valid = np.copy(Z)
    Z_valid[~np.isfinite(Z_valid)] = np.nan

    # 阈值
    plane_th = np.nanpercentile(Z_valid, plane_percentile)
    marker_th = np.nanpercentile(Z_valid, marker_percentile)

    # mask 保持 Z 形状
    plane_mask = (Z_valid <= plane_th) & np.isfinite(Z_valid)
    marker_mask = (Z_valid >= marker_th) & np.isfinite(Z_valid)

    # 平均高度
    z_plane = np.mean(Z_valid[plane_mask]) if np.any(plane_mask) else np.nan
    z_marker = np.mean(Z_valid[marker_mask]) if np.any(marker_mask) else np.nan
    delta_z = z_marker - z_plane

    # 体积去除率（整体数值）
    mrr = delta_z * np.sum(marker_mask)

    return mrr, marker_mask, plane_mask
