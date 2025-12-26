import numpy as np
import open3d as o3d


def Z_to_point_cloud(Z, size_um=437):
    """
    Z: 2D 高度矩阵
    size_um: 实际物理尺寸，映射 X/Y
    """
    Nx, Ny = Z.shape
    x = np.linspace(0, size_um, Nx)
    y = np.linspace(0, size_um, Ny)
    X, Y = np.meshgrid(x, y)

    # 平面展开为 Nx*Ny 个点
    points = np.vstack((X.ravel(), Y.ravel(), Z.ravel())).T
    # 去掉 NaN
    points = points[~np.isnan(points).any(axis=1)]

    # 创建 Open3D 点云对象
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    return pcd


def visualize_3d(Z, size_um=437, window_name="Surface 3D"):
    pcd = Z_to_point_cloud(Z, size_um=size_um)

    # Open3D 可交互窗口
    o3d.visualization.draw_geometries([pcd], window_name=window_name)

def Z_to_mesh(Z, size_um=437):
    Nx, Ny = Z.shape
    x = np.linspace(0, size_um, Nx)
    y = np.linspace(0, size_um, Ny)
    X, Y = np.meshgrid(x, y)
    Z = np.nan_to_num(Z, nan=np.nanmin(Z))
    grid = pv.StructuredGrid(X, Y, Z)
    grid["height"] = Z.ravel(order="F")
    return grid
