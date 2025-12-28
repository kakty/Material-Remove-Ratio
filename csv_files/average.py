import pandas as pd
import os

# ================= 参数 =================
input_dir = "output_by_position_M"   # 原 CSV 文件夹
output_csv = os.path.join(input_dir, "average.csv")

# ================= 找到所有 position_X.csv 文件 =================
files = [f for f in os.listdir(input_dir) if f.startswith("position_") and f.endswith(".csv")]

if not files:
    raise FileNotFoundError(f"{input_dir} 中没有 position_X.csv 文件")

# ================= 读取并合并 =================
dfs = []
for f in files:
    df = pd.read_csv(os.path.join(input_dir, f))
    dfs.append(df)

# 假设每个 CSV 的角度点完全相同
# 使用 Angle_deg 对齐，然后求 Delta_interp 平均
merged_df = dfs[0][["Angle_deg"]].copy()
delta_arrays = [df["Delta_interp"].values for df in dfs]

import numpy as np
delta_mean = np.mean(delta_arrays, axis=0)

merged_df["Delta_avg"] = delta_mean

# ================= 保存 =================
merged_df.to_csv(output_csv, index=False)
print(f"平均结果已保存到: {output_csv}")
