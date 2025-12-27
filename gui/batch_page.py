# batch_page.py
import os
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, QtCore
from algorithms.mark_height_3 import comupte_plane_and_marker_height3
from dataprocessing.read_asc import read_asc

class BatchWorker(QtCore.QRunnable):
    """Worker 用于批量处理单文件"""
    def __init__(self, idx, path, signal):
        super().__init__()
        self.idx = idx
        self.path = path
        self.signal = signal  # pyqtSignal 用于发送结果


    def run(self):
        try:
            # Z, _ = asc_to_csv(self.path, "csv_files", header_lines=12)
            Z = read_asc(self.path, header_lines=12)
            p, m, d, _, _ = comupte_plane_and_marker_height3(Z)
            del Z
            # 发射信号给主线程
            self.signal.emit(self.idx, os.path.basename(self.path), p, m, d)
        except Exception as e:
            print(f"处理 {self.path} 出错: {e}")

class BatchPage(QtWidgets.QWidget):
    result_signal = QtCore.pyqtSignal(int, str, float, float, float)

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

        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["序号", "文件名", "Plane", "Marker", "Δz"]
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

        self.table.setRowCount(len(self.files))
        self.progress.setValue(0)
        self.pool.setMaxThreadCount(self.max_worker.value())

        for i, path in enumerate(self.files):
            worker = BatchWorker(i, path, self.result_signal)
            self.pool.start(worker)

    @QtCore.pyqtSlot(int, str, float, float, float)
    def on_result(self, idx, name, p, m, d):
        self.table.setItem(idx, 0, QtWidgets.QTableWidgetItem(str(idx+1)))
        self.table.setItem(idx, 1, QtWidgets.QTableWidgetItem(name))
        self.table.setItem(idx, 2, QtWidgets.QTableWidgetItem(f"{p:.4f}"))
        self.table.setItem(idx, 3, QtWidgets.QTableWidgetItem(f"{m:.4f}"))
        self.table.setItem(idx, 4, QtWidgets.QTableWidgetItem(f"{d:.4f}"))

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
            columns=["Index", "File", "Plane", "Marker", "Delta"]
        )

        title = self.title_edit.text().strip()
        if title:
            df.attrs["title"] = title

        if path.endswith(".csv"):
            df.to_csv(path, index=False)
        else:
            df.to_excel(path, index=False)
