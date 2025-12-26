from pyvistaqt import QtInteractor
from dataprocessing import *
from visualization import *
from algorithms import *

class SurfaceApp(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Surface Height Analysis")
        self.resize(1000, 700)

        self.Z = None
        self.current_file = None

        self._build_ui()

    def _build_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        layout = QtWidgets.QHBoxLayout(central_widget)

        # 左侧按钮和日志
        left = QtWidgets.QVBoxLayout()
        layout.addLayout(left, 0)

        self.load_btn = QtWidgets.QPushButton("1. 导入 ASC")
        self.load_btn.clicked.connect(self.load_file)
        left.addWidget(self.load_btn)

        self.visual_btn = QtWidgets.QPushButton("2. 3D 可视化")
        self.visual_btn.clicked.connect(self.visualize_3d)
        left.addWidget(self.visual_btn)

        self.height_btn = QtWidgets.QPushButton("3. 高度计算")
        self.height_btn.clicked.connect(self.compute_height)
        left.addWidget(self.height_btn)

        # 方法选择
        self.method_group = QtWidgets.QButtonGroup()
        self.method1_radio = QtWidgets.QRadioButton("方法1")
        self.method2_radio = QtWidgets.QRadioButton("方法2")
        self.method3_radio = QtWidgets.QRadioButton("方法3")
        self.method3_radio.setChecked(True)
        self.method_group.addButton(self.method1_radio)
        self.method_group.addButton(self.method2_radio)
        self.method_group.addButton(self.method3_radio)
        left.addWidget(self.method1_radio)
        left.addWidget(self.method2_radio)
        left.addWidget(self.method3_radio)

        # 日志输出
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        left.addWidget(self.log_text, 1)

        # 右侧 PyVista 3D 绘图
        self.plotter_frame = QtWidgets.QFrame()
        layout.addWidget(self.plotter_frame, 1)

        self.plotter = QtInteractor(self.plotter_frame)
        pv.set_plot_theme("document")
        self.plotter_frame_layout = QtWidgets.QVBoxLayout(self.plotter_frame)
        self.plotter_frame_layout.addWidget(self.plotter.interactor)

    def log(self, msg):
        self.log_text.append(msg)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    # -------------------
    # 按钮回调
    # -------------------
    def load_file(self):
        paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "选择 ASC 文件", "", "ASC Files (*.asc)")
        if not paths:
            return
        try:
            self.Z, csv_path = asc_to_csv(paths[0], output_dir="csv_files", header_lines=12)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", str(e))
            return
        self.current_file = paths[0]
        self.log(f"已加载: {os.path.basename(paths[0])}, CSV: {csv_path}, 数据形状: {self.Z.shape}")

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

    def compute_height(self):
        if self.Z is None:
            QtWidgets.QMessageBox.warning(self, "提示", "请先加载数据")
            return

        if self.method1_radio.isChecked():
            plane, mark, delta = comupte_plane_and_marker_height1(self.Z)
            method = "方法1"
        elif self.method2_radio.isChecked():
            plane, mark, delta =compute_plane_and_mark_height2(self.Z)
            method = "方法2"
        else:
            plane, mark, delta = comupte_plane_and_marker_height3(self.Z)
            method = "方法3"

        self.log(f"[{method}] 平面高度: {plane:.4f}")
        self.log(f"[{method}] 标记高度: {mark:.4f}")
        self.log(f"[{method}] 高度差: {delta:.4f}")