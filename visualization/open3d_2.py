import numpy as np
import pyvista as pv
from pyvista import examples


def Z_to_mesh(Z, size_um=437):
    """
    Z: 2D 高度矩阵
    size_um: 实际物理尺寸
    返回 PyVista 网格对象
    """
    Nx, Ny = Z.shape
    x = np.linspace(0, size_um, Nx)
    y = np.linspace(0, size_um, Ny)
    X, Y = np.meshgrid(x, y)

    # PyVista 支持网格直接生成
    # 注意 PyVista 的 grid 要求 shape (Ny, Nx)
    Z = np.nan_to_num(Z, nan=np.nanmin(Z))  # NaN 替换为最小值
    grid = pv.StructuredGrid(X, Y, Z)

    # 可选：高度映射颜色
    grid["height"] = Z.ravel(order="F")  # order="F" 按列展开，匹配网格
    return grid
