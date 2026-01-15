import os
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, QtCore
from algorithms.mark_height_3 import comupte_plane_and_marker_height3
from algorithms.mark_height_2 import compute_groove_depth_method2  # 【修改点1】 引入新算法
from algorithms.mark_height_1 import compute_plane_and_marker_height1
from dataprocessing.read_asc import read_asc


class BatchWorker(QtCore.QRunnable):
    def __init__(self, idx, path, method, signal):
        super().__init__()
        self.idx = idx
        self.path = path
        self.method = method
        self.signal = signal

    def run(self):
        try:
            Z = read_asc(self.path, header_lines=12)
            value = 0.0

            if self.method == 1:
                mrr, _, _ = compute_plane_and_marker_height1(Z)
                value = np.mean(mrr)

            elif self.method == 2:
                # 【修改点2】 方法2：槽深分析
                # 这里使用默认参数：平面取 Top 50%，槽取 Bottom 20%
                # 如果你想在UI上设置这些参数，需要在BatchPage传入，这里为了简单直接写死默认值
                _, _, depth, _, _ = compute_groove_depth_method2(Z, plane_top_percent=50, groove_bottom_percent=20)
                value = depth

            else:  # method 3
                _, _, d, _, _ = comupte_plane_and_marker_height3(Z)
                value = d

            del Z
            self.signal.emit(self.idx, os.path.basename(self.path), value)
        except Exception as e:
            print(f"Error {self.path}: {e}")
            self.signal.emit(self.idx, os.path.basename(self.path), -999.0)


class BatchPage(QtWidgets.QWidget):
    result_signal = QtCore.pyqtSignal(int, str, float)

    def __init__(self):
        super().__init__()
        self.files = []
        self.pool = QtCore.QThreadPool.globalInstance()
        self._build_ui()
        self.result_signal.connect(self.on_result)

    def _build_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        left = QtWidgets.QVBoxLayout()
        layout.addLayout(left, 0)

        self.btn_load = QtWidgets.QPushButton("导入 ASC 文件")
        left.addWidget(self.btn_load)

        left.addWidget(QtWidgets.QLabel("选择方法"))
        self.rb1 = QtWidgets.QRadioButton("方法1 (MRR)")
        self.rb2 = QtWidgets.QRadioButton("方法2 (槽深 - Groove)")  # 【修改点3】 改名
        self.rb3 = QtWidgets.QRadioButton("方法3 (凸起 - Mark)")
        self.rb2.setChecked(True)

        left.addWidget(self.rb1)
        left.addWidget(self.rb2)
        left.addWidget(self.rb3)

        # ... (中间代码不变) ...
        left.addWidget(QtWidgets.QLabel("最大同时处理文件数"))
        self.max_worker = QtWidgets.QSpinBox()
        self.max_worker.setRange(1, 8)
        self.max_worker.setValue(3)
        left.addWidget(self.max_worker)

        self.progress = QtWidgets.QProgressBar()
        left.addWidget(self.progress)
        left.addStretch()

        right = QtWidgets.QVBoxLayout()
        layout.addLayout(right, 1)

        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("表名 / Title")
        right.addWidget(self.title_edit)

        # 【修改点4】 表头名称修改，更通用
        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(
            ["序号", "文件名", "深度/变化量"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        right.addWidget(self.table)

        self.btn_save = QtWidgets.QPushButton("保存结果")
        right.addWidget(self.btn_save)

        self.btn_load.clicked.connect(self.load_files)
        self.btn_save.clicked.connect(self.save_table)

    def load_files(self):
        self.files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "选择 ASC 文件", "", "ASC Files (*.asc)"
        )
        if not self.files: return

        if self.rb1.isChecked():
            method = 1
        elif self.rb2.isChecked():
            method = 2
        else:
            method = 3

        self.table.setRowCount(len(self.files))
        self.progress.setValue(0)

        # 批量开始
        for i, path in enumerate(self.files):
            worker = BatchWorker(i, path, method, self.result_signal)
            self.pool.start(worker)

    @QtCore.pyqtSlot(int, str, float)
    def on_result(self, idx, name, value):
        self.table.setItem(idx, 0, QtWidgets.QTableWidgetItem(str(idx + 1)))
        self.table.setItem(idx, 1, QtWidgets.QTableWidgetItem(name))
        self.table.setItem(idx, 2, QtWidgets.QTableWidgetItem(f"{value:.4f}"))

        # 进度条逻辑
        done = sum(self.table.item(i, 2) is not None for i in range(self.table.rowCount()))
        self.progress.setValue(int(done / self.table.rowCount() * 100))

    def save_table(self):
        # 保持原有保存逻辑不变
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "保存", "", "CSV (*.csv);;Excel (*.xlsx)")
        if not path: return
        data = []
        for r in range(self.table.rowCount()):
            row = []
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                row.append(item.text() if item else "")
            data.append(row)
        df = pd.DataFrame(data, columns=["Index", "File", "Value"])
        if path.endswith(".csv"):
            df.to_csv(path, index=False)
        else:
            df.to_excel(path, index=False)