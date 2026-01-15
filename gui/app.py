import os
import numpy as np
from PyQt5 import QtWidgets, QtCore
from pyvistaqt import QtInteractor
import pyvista as pv
from dataprocessing.asc_reader import read_asc
from visualization.surface_plot import Z_to_mesh
from algorithms.mark_height_1 import compute_plane_and_marker_height1
# 【修改点1】 引入新的方法2
from algorithms.mark_height_2 import compute_groove_depth_method2
from algorithms.mark_height_3 import comupte_plane_and_marker_height3
from gui.batch_page import BatchPage


class SurfaceApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Surface Height Analysis (Groove & Mark)")
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

        self.stack = QtWidgets.QStackedWidget()
        main_layout.addWidget(self.stack, 1)

        self.page_main = QtWidgets.QWidget()
        self._build_main_page(self.page_main)
        self.stack.addWidget(self.page_main)

        self.page_batch = BatchPage()
        self.stack.addWidget(self.page_batch)

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

        btn_calc = QtWidgets.QPushButton("3. 计算")
        btn_calc.clicked.connect(self.compute_height)
        left.addWidget(btn_calc)

        # 方法选择
        self.rb1 = QtWidgets.QRadioButton("方法1 (旧)")
        self.rb2 = QtWidgets.QRadioButton("方法2 (槽深分析)")  # 【修改点2】 改名
        self.rb3 = QtWidgets.QRadioButton("方法3 (凸起标记)")
        self.rb2.setChecked(True)  # 默认选中槽分析

        left.addWidget(self.rb1)
        left.addWidget(self.rb2)
        left.addWidget(self.rb3)

        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        left.addWidget(self.log_text, 1)

        # ========== 右侧 ==========
        self.right_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        main_layout.addWidget(self.right_splitter, 1)

        self.main_frame = QtWidgets.QFrame()
        self.main_plotter = QtInteractor(self.main_frame)
        l = QtWidgets.QVBoxLayout(self.main_frame)
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(self.main_plotter.interactor)
        self.right_splitter.addWidget(self.main_frame)

        # ---------- 下：参数调整区域 ----------
        self.detail_widget = QtWidgets.QWidget()
        self.detail_layout = QtWidgets.QVBoxLayout(self.detail_widget)
        self.detail_widget.setVisible(False)
        self.right_splitter.addWidget(self.detail_widget)

        # 参数区
        param_layout = QtWidgets.QHBoxLayout()
        self.detail_layout.addLayout(param_layout)

        # 这两个输入框复用：
        # 方法3时代表：Plane分位(如60), Marker分位(如80)
        # 方法2时代表：Plane Top%(如50), Groove Bottom%(如20)
        self.plane_edit = QtWidgets.QSpinBox()
        self.plane_edit.setRange(0, 100)
        self.plane_edit.setValue(50)  # 默认平面取 Top 50%

        self.marker_edit = QtWidgets.QSpinBox()
        self.marker_edit.setRange(0, 100)
        self.marker_edit.setValue(20)  # 默认槽底取 Bottom 20%

        btn_apply = QtWidgets.QPushButton("更新计算")
        btn_apply.clicked.connect(self.re_apply_method)  # 绑定到通用函数

        btn_close = QtWidgets.QPushButton("隐藏")
        btn_close.clicked.connect(lambda: self.detail_widget.setVisible(False))

        self.lbl_p = QtWidgets.QLabel("Param 1")
        self.lbl_m = QtWidgets.QLabel("Param 2")

        param_layout.addWidget(self.lbl_p)
        param_layout.addWidget(self.plane_edit)
        param_layout.addWidget(self.lbl_m)
        param_layout.addWidget(self.marker_edit)
        param_layout.addWidget(btn_apply)
        param_layout.addWidget(btn_close)

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
        self.Z = read_asc(path, header_lines=12)
        self.log(f"已加载 {os.path.basename(path)}")

    def visualize_3d(self):
        if self.Z is None: return
        self.main_plotter.clear()
        self.mesh = Z_to_mesh(self.Z)
        self.main_plotter.add_mesh(self.mesh, scalars="height", cmap="jet")
        self.main_plotter.reset_camera()

    def compute_height(self):
        """点击主按钮时调用"""
        if self.Z is None: return
        self.detail_widget.setVisible(True)  # 默认展开详情以便查看 Mask
        self.re_apply_method()

    def re_apply_method(self):
        """根据当前RadioButton应用对应算法"""
        if self.rb1.isChecked():
            self.lbl_p.setText("Plane %")
            self.lbl_m.setText("Mark %")
            self.apply_method1()

        elif self.rb2.isChecked():
            # 方法2：槽分析
            self.lbl_p.setText("平面(Top%)")
            self.lbl_m.setText("槽底(Bot%)")
            self.apply_method2()

        else:
            # 方法3：凸起分析
            self.lbl_p.setText("Plane < %")
            self.lbl_m.setText("Mark > %")
            self.apply_method3()

    def apply_method1(self):
        # 保持原有逻辑不变...
        pass

    def apply_method2(self):
        """【修改点3】方法2的具体实现：槽深分析"""
        p_pct = self.plane_edit.value()  # 例如 50
        g_pct = self.marker_edit.value()  # 例如 20

        # 调用新算法
        p_h, g_h, depth, p_mask, g_mask = compute_groove_depth_method2(self.Z, p_pct, g_pct)

        self.log(f"--- 方法2 (槽分析) ---")
        self.log(f"参数: 平面取Top {p_pct}%, 槽取Bottom {g_pct}%")
        self.log(f"平面均高: {p_h:.4f}")
        self.log(f"槽底均高: {g_h:.4f}")
        self.log(f"<b>槽平均深度: {depth:.4f}</b>")  # 加粗显示

        # 可视化：左边显示平面(蓝)，右边显示槽(红)
        self._plot_mask(self.plane_plotter, p_mask, "blue")
        self._plot_mask(self.marker_plotter, g_mask, "red")

    def apply_method3(self):
        """方法3：凸起分析 (保持原有逻辑，但更新一下调用)"""
        p_val = self.plane_edit.value()
        m_val = self.marker_edit.value()
        p, m, d, p_mask, m_mask = comupte_plane_and_marker_height3(self.Z, p_val, m_val)
        self.log(f"--- 方法3 (凸起) ---")
        self.log(f"Plane < {p_val}%, Marker > {m_val}%")
        self.log(f"高度差: {d:.4f}")
        self._plot_mask(self.plane_plotter, p_mask, "blue")
        self._plot_mask(self.marker_plotter, m_mask, "red")

    def _plot_mask(self, plotter, mask, color):
        plotter.clear()
        if mask is None: return
        idx = np.column_stack(np.where(mask))
        if idx.size == 0: return
        # 注意：Mask 是 2D，需要索引回 Z 值
        pts = np.c_[idx[:, 1], idx[:, 0], self.Z[mask]]
        cloud = pv.PolyData(pts)
        plotter.add_points(cloud, color=color, point_size=2)
        plotter.reset_camera()