import numpy as np

def safe_float(val):
    if val.lower() == 'bad':
        return np.nan
    try:
        return float(val)
    except ValueError:
        return np.nan

def read_asc(asc_path, header_lines=13, scale=0.6328):
    rows = []

    with open(asc_path, "r") as f:
        lines = f.readlines()

    for line in lines[header_lines:-1]:
        line = line.strip()
        if not line:
            continue

        values = [safe_float(v) for v in line.split()]
        rows.append(values)

    lengths = {len(r) for r in rows}
    if len(lengths) != 1:
        raise ValueError(f"列数不一致，检测到行列长度：{lengths}")

    Z0 = np.array(rows, dtype=float)
    Z = Z0 * scale

    return Z