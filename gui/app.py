import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
from algorithms import *
from dataprocessing import *
from visualization import *

class SurfaceApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Surface Height Analysis")

        self.Z = None
        self.current_file = None

        self.build_ui()

    def build_ui(self):
        # 左侧按钮区
        left = tk.Frame(self.root)
        left.pack(side="left", fill="y", padx=5, pady=5)

        tk.Button(left, text="1. 导入 ASC", command=self.load_file).pack(fill="x")
        tk.Button(left, text="3. 3D 可视化", command=self.visualize_3d).pack(fill="x")

        # 右侧绘图区 ⭐
        self.plot_frame = tk.Frame(self.root, bg="white")
        self.plot_frame.pack(side="right", fill="both", expand=True)

        # ===== 方法选择 =====
        self.method = tk.StringVar(value="method3")
        ttk.Radiobutton(left, text="方法1", variable=self.method, value="method1").pack(anchor="w")
        ttk.Radiobutton(left, text="方法2", variable=self.method, value="method2").pack(anchor="w")
        ttk.Radiobutton(left, text="方法3", variable=self.method, value="method3").pack(anchor="w")

        # ===== 输出区 =====
        self.output = tk.Text(self.root, height=10)
        self.output.pack(fill="both", expand=True)

    def log(self, msg):
        self.output.insert("end", msg + "\n")
        self.output.see("end")

    def load_file(self):
        paths = filedialog.askopenfilenames(
            title="选择 ASC 文件",
            filetypes=[("ASC files", "*.asc")]
        )
        if not paths:
            return

        self.current_file = paths[0]  # 先做单文件
        self.Z, _ = asc_to_csv(self.current_file, "csv_files", header_lines=12)

        self.log(f"已加载文件：{os.path.basename(self.current_file)}")
        self.log(f"数据尺寸：{self.Z.shape}")

    def visualize_3d(self):
        if self.Z is None:
            messagebox.showwarning("提示", "请先导入数据")
            return

        visualize_3d(self.Z, size_um=437)

    def compute_height(self):
        if self.Z is None:
            messagebox.showwarning("提示", "请先导入数据")
            return

        m = self.method.get()

        if m == "method1":
            dz, plane, mark = plane_and_marker_height1(self.Z)

        elif m == "method2":
            plane, mark, dz = compute_plane_and_mark_height2(self.Z)

        elif m == "method3":
            plane, mark, dz, _ = plane_and_marker_height3(self.Z)

        self.log(f"[{m}] 平面高度: {plane:.4f}")
        self.log(f"[{m}] 标记高度: {mark:.4f}")
        self.log(f"[{m}] 高度差: {dz:.4f}")
