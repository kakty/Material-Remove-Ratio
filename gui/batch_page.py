# batch_page.py
import os
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, QtCore
from algorithms.mark_height_3 import comupte_plane_and_marker_height3
from algorithms.mark_height_2 import compute_plane_and_mark_height2
from algorithms.mark_height_1 import compute_plane_and_marker_height1
from dataprocessing.read_asc import read_asc

class BatchWorker(QtCore.QRunnable):
    """Worker 用于批量处理单文件"""
    def __init__(self, idx, path, method, signal):
        super().__init__()
        self.idx = idx
        self.path = path
        self.method = method
        self.signal = signal  # pyqtSignal 用于发送结果


    def run(self):
        try:
            Z = read_asc(self.path, header_lines=12)
            if self.method == 1:
                mrr, _, _ = compute_plane_and_marker_height1(Z)
                value = np.mean(mrr)  # 平均 MRR
            elif self.method == 2:
                _, _, d = compute_plane_and_mark_height2(Z)
                value = d
            else:  # method 3
                _, _, d, _, _ = comupte_plane_and_marker_height3(Z)
                value = d
            del Z
            # 发射信号给主线程
            self.signal.emit(self.idx, os.path.basename(self.path), value)
        except Exception as e:
            print(f"处理 {self.path} 出错: {e}")

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
        # 左侧
        left = QtWidgets.QVBoxLayout()
        layout.addLayout(left, 0)

        self.btn_load = QtWidgets.QPushButton("导入 ASC 文件")
        left.addWidget(self.btn_load)

        # 方法选择
        left.addWidget(QtWidgets.QLabel("选择方法"))
        self.rb1 = QtWidgets.QRadioButton("方法1 (MRR)")
        self.rb2 = QtWidgets.QRadioButton("方法2")
        self.rb3 = QtWidgets.QRadioButton("方法3（百分位）")
        self.rb3.setChecked(True)
        left.addWidget(self.rb1)
        left.addWidget(self.rb2)
        left.addWidget(self.rb3)

        left.addWidget(QtWidgets.QLabel("最大同时处理文件数"))
        self.max_worker = QtWidgets.QSpinBox()
        self.max_worker.setRange(1, 8)
        self.max_worker.setValue(3)
        left.addWidget(self.max_worker)

        self.progress = QtWidgets.QProgressBar()
        left.addWidget(self.progress)
        left.addStretch()

        # 右侧表格
        right = QtWidgets.QVBoxLayout()
        layout.addLayout(right, 1)

        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setPlaceholderText("表名 / Title")
        right.addWidget(self.title_edit)

        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(
            ["序号", "文件名", "值"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        right.addWidget(self.table)

        self.btn_save = QtWidgets.QPushButton("保存结果")
        right.addWidget(self.btn_save)

        # signals
        self.btn_load.clicked.connect(self.load_files)
        self.btn_save.clicked.connect(self.save_table)

    def load_files(self):
        self.files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "选择 ASC 文件", "", "ASC Files (*.asc)"
        )
        if not self.files:
            return

        # 获取当前方法
        if self.rb1.isChecked():
            method = 1
        elif self.rb2.isChecked():
            method = 2
        else:
            method = 3

        self.table.setRowCount(len(self.files))
        self.progress.setValue(0)
        self.pool.setMaxThreadCount(self.max_worker.value())

        for i, path in enumerate(self.files):
            worker = BatchWorker(i, path, method, self.result_signal)
            self.pool.start(worker)

    @QtCore.pyqtSlot(int, str, float)
    def on_result(self, idx, name, value):
        self.table.setItem(idx, 0, QtWidgets.QTableWidgetItem(str(idx+1)))
        self.table.setItem(idx, 1, QtWidgets.QTableWidgetItem(name))
        self.table.setItem(idx, 2, QtWidgets.QTableWidgetItem(f"{value:.4f}"))

        done = sum(
            self.table.item(i, 2) is not None
            for i in range(self.table.rowCount())
        )
        self.progress.setValue(int(done / self.table.rowCount() * 100))

    def save_table(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "保存", "", "CSV (*.csv);;Excel (*.xlsx)"
        )
        if not path:
            return

        data = []
        for r in range(self.table.rowCount()):
            row = []
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                row.append(item.text() if item else "")
            data.append(row)

        df = pd.DataFrame(
            data,
            columns=["Index", "File", "Value"]
        )

        title = self.title_edit.text().strip()
        if title:
            df.attrs["title"] = title

        if path.endswith(".csv"):
            df.to_csv(path, index=False)
        else:
            df.to_excel(path, index=False)
