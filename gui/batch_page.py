# batch_page.py
import os
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, QtCore
from dataprocessing import asc_to_csv
from algorithms.mark_height_3 import comupte_plane_and_marker_height3

class BatchWorker(QtCore.QRunnable):
    """Worker 用于批量处理单文件"""
    def __init__(self, idx, path, callback):
        super().__init__()
        self.idx = idx
        self.path = path
        self.callback = callback

    def run(self):
        Z, _ = asc_to_csv(self.path, "csv_files", header_lines=12)
        p, m, d, _, _ = comupte_plane_and_marker_height3(Z)
        del Z  # 释放内存
        # 回调主线程更新UI
        QtCore.QMetaObject.invokeMethod(
            self.callback,
            QtCore.Qt.QueuedConnection,
            QtCore.Q_ARG(int, self.idx),
            QtCore.Q_ARG(str, os.path.basename(self.path)),
            QtCore.Q_ARG(float, p),
            QtCore.Q_ARG(float, m),
            QtCore.Q_ARG(float, d)
        )

class BatchPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.files = []
        self._build_ui()
        self.pool = QtCore.QThreadPool.globalInstance()

    def _build_ui(self):
        layout = QtWidgets.QHBoxLayout(self)

        # 左侧控制区
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
            worker = BatchWorker(i, path, self.on_result)
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
