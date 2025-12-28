import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import os

input_csv = "output_delta_diff_M.csv"
output_dir = "output_by_position_M"
angle_step = 30

os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(input_csv)
df.columns = [c.strip() for c in df.columns]

# 去掉 .asc 后缀，再拆 n-m
df["File_noext"] = df["File"].str.replace(".asc", "", regex=False)
df[["n", "m"]] = df["File_noext"].str.split("-", expand=True).astype(int)

# 按 m 分组
for m_value, group in df.groupby("m"):
    group = group.sort_values("n")
    n_vals = group["n"].values
    delta_vals = group["Delta_diff"].values
    N = len(n_vals)
    angles = (n_vals - 1) * 360.0 / N
    angles_ext = np.append(angles, 360.0)
    delta_ext = np.append(delta_vals, delta_vals[0])
    interp_func = interp1d(angles_ext, delta_ext, kind="linear", fill_value="extrapolate")
    new_angles = np.arange(0, 360 + angle_step, angle_step)
    new_delta = interp_func(new_angles)
    new_index = np.arange(1, len(new_angles) + 1)
    out_df = pd.DataFrame({
        "Index": new_index,
        "Angle_deg": new_angles,
        "File": [f"{i}-{m_value}" for i in new_index],
        "Delta_interp": new_delta
    })
    out_path = os.path.join(output_dir, f"position_{m_value}.csv")
    out_df.to_csv(out_path, index=False)
    print(f"位置 m={m_value} 已生成: {out_path}")


