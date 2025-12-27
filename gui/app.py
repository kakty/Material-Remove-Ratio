import os
import numpy as np
from PyQt5 import QtWidgets, QtCore
from pyvistaqt import QtInteractor
import pyvista as pv
from dataprocessing.asc_reader import asc_to_csv
from visualization.surface_plot import Z_to_mesh
from algorithms.mark_height_1 import comupte_plane_and_marker_height1
from algorithms.mark_height_2 import compute_plane_and_mark_height2
from algorithms.mark_height_3 import comupte_plane_and_marker_height3
from gui.batch_page import BatchPage
from dataprocessing import *

class SurfaceApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Surface Height Analysis")
        self.resize(1300, 800)

        self.Z = None
        self.mesh = None

        self._build_ui()

    # ---------------- UI ----------------
    def _build_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)

        # Top bar: 切换页面
        top_bar = QtWidgets.QHBoxLayout()
        main_layout.addLayout(top_bar)
        btn_main = QtWidgets.QPushButton("主界面")
        btn_batch = QtWidgets.QPushButton("批量处理")
        top_bar.addWidget(btn_main)
        top_bar.addWidget(btn_batch)
        top_bar.addStretch()

        # 堆叠页面
        self.stack = QtWidgets.QStackedWidget()
        main_layout.addWidget(self.stack, 1)

        # 主界面
        self.page_main = QtWidgets.QWidget()
        self._build_main_page(self.page_main)
        self.stack.addWidget(self.page_main)

        # 批处理页面
        self.page_batch = BatchPage()
        self.stack.addWidget(self.page_batch)

        # 切换按钮
        btn_main.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        btn_batch.clicked.connect(lambda: self.stack.setCurrentIndex(1))

    def _build_main_page(self, widget):
        main_layout = QtWidgets.QHBoxLayout(widget)

        # ========== 左侧 ==========
        left = QtWidgets.QVBoxLayout()
        main_layout.addLayout(left, 0)

        btn_load = QtWidgets.QPushButton("1. 导入 ASC")
        btn_load.clicked.connect(self.load_file)
        left.addWidget(btn_load)

        btn_vis = QtWidgets.QPushButton("2. 3D 可视化")
        btn_vis.clicked.connect(self.visualize_3d)
        left.addWidget(btn_vis)

        btn_calc = QtWidgets.QPushButton("3. 高度计算")
        btn_calc.clicked.connect(self.compute_height)
        left.addWidget(btn_calc)

        # 方法选择
        self.rb1 = QtWidgets.QRadioButton("方法1")
        self.rb2 = QtWidgets.QRadioButton("方法2")
        self.rb3 = QtWidgets.QRadioButton("方法3（百分位）")
        self.rb3.setChecked(True)

        left.addWidget(self.rb1)
        left.addWidget(self.rb2)
        left.addWidget(self.rb3)

        # log
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        left.addWidget(self.log_text, 1)

        # ========== 右侧 ==========
        self.right_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        main_layout.addWidget(self.right_splitter, 1)

        # ---------- 上：主 3D ----------
        self.main_frame = QtWidgets.QFrame()
        self.main_plotter = QtInteractor(self.main_frame)
        l = QtWidgets.QVBoxLayout(self.main_frame)
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(self.main_plotter.interactor)
        self.right_splitter.addWidget(self.main_frame)

        # ---------- 下：方法3 ----------
        self.detail_widget = QtWidgets.QWidget()
        self.detail_layout = QtWidgets.QVBoxLayout(self.detail_widget)
        self.detail_widget.setVisible(False)
        self.right_splitter.addWidget(self.detail_widget)

        # 参数区
        param_layout = QtWidgets.QHBoxLayout()
        self.detail_layout.addLayout(param_layout)

        self.plane_edit = QtWidgets.QSpinBox()
        self.plane_edit.setRange(0, 100)
        self.plane_edit.setValue(60)

        self.marker_edit = QtWidgets.QSpinBox()
        self.marker_edit.setRange(0, 100)
        self.marker_edit.setValue(80)

        btn_apply = QtWidgets.QPushButton("确定")
        btn_apply.clicked.connect(self.apply_method3)

        btn_close = QtWidgets.QPushButton("关闭")
        btn_close.clicked.connect(lambda: self.detail_widget.setVisible(False))

        param_layout.addWidget(QtWidgets.QLabel("Plane %"))
        param_layout.addWidget(self.plane_edit)
        param_layout.addWidget(QtWidgets.QLabel("Marker %"))
        param_layout.addWidget(self.marker_edit)
        param_layout.addWidget(btn_apply)
        param_layout.addWidget(btn_close)

        # mask 视图
        mask_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.detail_layout.addWidget(mask_splitter, 1)

        self.plane_plotter = QtInteractor()
        self.marker_plotter = QtInteractor()
        mask_splitter.addWidget(self.plane_plotter.interactor)
        mask_splitter.addWidget(self.marker_plotter.interactor)

    # ---------------- 功能 ----------------
    def log(self, msg):
        self.log_text.append(msg)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def load_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "选择 ASC 文件", "", "ASC Files (*.asc)"
        )
        if not path:
            return

        #self.Z, csv_path = asc_to_csv(path, "csv_files", header_lines=12)
        self.Z = read_asc(path, header_lines=12)
        self.log(f"已加载 {os.path.basename(path)}  Z shape={self.Z.shape}")

    def visualize_3d(self):
        if self.Z is None:
            return

        self.main_plotter.clear()
        self.mesh = Z_to_mesh(self.Z)
        self.main_plotter.add_mesh(self.mesh, scalars="height", cmap="jet")
        self.main_plotter.reset_camera()

    def compute_height(self):
        if self.Z is None:
            return

        self.detail_widget.setVisible(False)

        if self.rb1.isChecked():
            p, m, d = comupte_plane_and_marker_height1(self.Z)
            self.log(f"[方法1] plane={p:.4f}, marker={m:.4f}, Δz={d:.4f}")

        elif self.rb2.isChecked():
            p, m, d = compute_plane_and_mark_height2(self.Z)
            self.log(f"[方法2] plane={p:.4f}, marker={m:.4f}, Δz={d:.4f}")

        else:
            self.detail_widget.setVisible(True)
            self.apply_method3()

    def apply_method3(self):
        plane_p = self.plane_edit.value()
        marker_p = self.marker_edit.value()

        p, m, d, plane_mask, marker_mask = \
            comupte_plane_and_marker_height3(
                self.Z, plane_p, marker_p
            )

        self.log(
            f"[方法3] plane%={plane_p}, marker%={marker_p} "
            f"| plane={p:.4f}, marker={m:.4f}, Δz={d:.4f}"
        )

        self._plot_mask(self.plane_plotter, plane_mask, "blue")
        self._plot_mask(self.marker_plotter, marker_mask, "red")

    def _plot_mask(self, plotter, mask, color):
        plotter.clear()
        idx = np.column_stack(np.where(mask))
        if idx.size == 0:
            return

        pts = np.c_[idx[:, 1], idx[:, 0], self.Z[mask]]
        cloud = pv.PolyData(pts)
        plotter.add_points(cloud, color=color, point_size=3)
        plotter.reset_camera()
