import numpy as np
from PyQt5 import QtWidgets, QtCore
import pyvista as pv

def Z_to_mesh(Z, size_um=437):
    Nx, Ny = Z.shape
    x = np.linspace(0, size_um, Nx)
    y = np.linspace(0, size_um, Ny)
    X, Y = np.meshgrid(x, y)
    Z = np.nan_to_num(Z, nan=np.nanmin(Z))
    grid = pv.StructuredGrid(X, Y, Z)
    grid["height"] = Z.ravel(order="F")
    return grid

def visualize_3d(self):
    if self.Z is None:
        QtWidgets.QMessageBox.warning(self, "提示", "请先加载数据")
        return

    self.plotter.clear()
    mesh = Z_to_mesh(self.Z)
    self.plotter.add_mesh(mesh, scalars="height", cmap="jet")
    self.plotter.enable_eye_dome_lighting()
    self.plotter.reset_camera()
    self.plotter.render()


