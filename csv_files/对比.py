import pandas as pd

# ===== 参数 =====
input_csv = "0min.csv"
output_csv = "output_delta_diff.csv"

# ===== 读取 CSV =====
df = pd.read_csv(input_csv)

# 统一列名（防止大小写/空格问题）
df.columns = [c.strip() for c in df.columns]

# 检查必要列
required_cols = {"Index", "File", "Delta"}
missing = required_cols - set(df.columns)
if missing:
    raise ValueError(f"缺少必要列: {missing}")

results = []

# ===== 按 File 分组 =====
for file_name, group in df.groupby("File", sort=False):
    group = group.reset_index(drop=True)

    if len(group) < 2:
        continue  # 不成对的直接跳过

    # 两两做差：前 - 后
    for i in range(0, len(group) - 1, 2):
        delta_diff = group.loc[i, "Delta"] - group.loc[i + 1, "Delta"]

        results.append({
            "Index": group.loc[i, "Index"],
            "File": file_name,
            "Delta_diff": delta_diff
        })

# ===== 输出 =====
out_df = pd.DataFrame(results)
out_df.to_csv(output_csv, index=False)

print(f"处理完成，结果已保存到: {output_csv}")
