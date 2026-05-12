"""第 2 课实践任务 3：房价统计与直方图（matplotlib 可选）。"""
from pathlib import Path

import pandas as pd
# import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


def main():
    csv_path = Path(__file__).resolve().parent.parent / "data" / "houses.csv"
    df = pd.read_csv(csv_path)
    prices = df["price"]
    print("mean(price) =", prices.mean())
    print("var(price) =", prices.var())
    print("std(price) =", prices.std())
    idx_max = int(prices.idxmax())
    idx_min = int(prices.idxmin())
    print("max price row:", df.loc[idx_max].to_dict())
    print("min price row:", df.loc[idx_min].to_dict())

    if plt is None:
        print(
            "skip histogram: matplotlib not installed. "
            "Run: pip install matplotlib"
        )
        return

    plt.figure(figsize=(6, 4))
    plt.hist(prices, bins=5, edgecolor="black")
    plt.xlabel("Price")
    plt.ylabel("Count")
    plt.title("Price Distribution")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
