import numpy as np
import os
import pandas as pd

def safe_float(val):
    if val.lower() == 'bad':
        return np.nan
    try:
        return float(val)
    except ValueError:
        return np.nan


def asc_to_csv(asc_path, output_dir, header_lines=13):
    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.basename(asc_path)
    csv_name = filename.replace(".asc", ".csv")
    csv_path = os.path.join(output_dir, csv_name)

    rows = []

    with open(asc_path, "r") as f:
        lines = f.readlines()

    for line in lines[header_lines:-1]:
        line = line.strip()
        if not line:
            continue

        # 🔑 关键：每个 token 都保留
        values = [safe_float(v) for v in line.split()]
        rows.append(values)

    # 这里要求每一行长度一致
    lengths = {len(r) for r in rows}
    if len(lengths) != 1:
        raise ValueError(f"列数不一致，检测到行列长度：{lengths}")

    Z = np.array(rows, dtype=float)

    print("Z shape:", Z.shape)
    print("NaN ratio:", np.isnan(Z).sum() / Z.size)

    pd.DataFrame(Z).to_csv(csv_path, index=False, header=False)
    return Z, csv_path
