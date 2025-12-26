import numpy as np

def comupte_plane_and_marker_height1(Z,
                            plane_percentile=60,
                            marker_percentile=70):
    z = Z.flatten()
    z = z[~np.isnan(z)]

    # 平面：较低分位数
    plane_mask = z <= np.percentile(z, plane_percentile)

    # 标记条：较高分位数
    marker_mask = z >= np.percentile(z, marker_percentile)

    z_plane = np.mean(z[plane_mask])
    z_marker = np.mean(z[marker_mask])

    delta_z = z_marker - z_plane

    return z_plane, z_marker, delta_z