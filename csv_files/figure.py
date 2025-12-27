import pandas as pd
import matplotlib.pyplot as plt
import os

# ================= 参数 =================
input_dir = "output_by_position"  # CSV 文件夹
positions = [1, 2, 3]  # 位置编号
colors = ['r', 'g', 'b']  # 每条曲线颜色
avg_color = 'k'  # 平均曲线颜色（黑色）

# ================= 读取平均文件 =================
avg_path = os.path.join(input_dir, "average.csv")
if not os.path.exists(avg_path):
    raise FileNotFoundError(f"{avg_path} 不存在，请先生成平均文件")
df_avg = pd.read_csv(avg_path)

# ================= 分别画每个文件 + 平均 =================
for i, pos in enumerate(positions):
    file_path = os.path.join(input_dir, f"position_{pos}.csv")
    df = pd.read_csv(file_path)

    plt.figure()
    # 单个位置曲线
    plt.plot(df["Angle_deg"], df["Delta_interp"], label=f"Position {pos}", color=colors[i])
    # 平均曲线
    plt.plot(df_avg["Angle_deg"], df_avg["Delta_avg"], label="Average", color=avg_color, linestyle='--')

    plt.xlabel("Angle (deg)")
    plt.ylabel("Delta_interp")
    plt.title(f"Position {pos} with Average")
    plt.grid(True)
    plt.legend()
    plt.show()

# ================= 全部位置 + 平均 =================
plt.figure()
for i, pos in enumerate(positions):
    file_path = os.path.join(input_dir, f"position_{pos}.csv")
    df = pd.read_csv(file_path)
    plt.plot(df["Angle_deg"], df["Delta_interp"], label=f"Position {pos}", color=colors[i])

# 平均曲线
plt.plot(df_avg["Angle_deg"], df_avg["Delta_avg"], label="Average", color=avg_color, linestyle='--')

plt.xlabel("Angle (deg)")
plt.ylabel("Delta_interp")
plt.title("All Positions Comparison with Average")
plt.grid(True)
plt.legend()
plt.show()
