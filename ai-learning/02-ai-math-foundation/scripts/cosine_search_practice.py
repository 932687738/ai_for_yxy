"""第 2 课实践任务 2 / 编程题：余弦相似度与排序。"""
import numpy as np


def cosine_similarity(u: np.ndarray, v: np.ndarray) -> float:
    nu = np.linalg.norm(u)
    nv = np.linalg.norm(v)
    if nu == 0.0 or nv == 0.0:
        return 0.0
    return float(np.dot(u, v) / (nu * nv))


def main():
    products = {
        "办公电脑": np.array([0.9, 0.8, 0.2], dtype=float),
        "游戏显卡": np.array([0.7, 0.9, 0.4], dtype=float),
        "厨房锅具": np.array([0.1, 0.2, 0.95], dtype=float),
        "机械键盘": np.array([0.85, 0.7, 0.15], dtype=float),
        "显示器": np.array([0.88, 0.75, 0.22], dtype=float),
    }
    query = np.array([0.85, 0.75, 0.25], dtype=float)

    scores = []
    for name, vec in products.items():
        scores.append((name, cosine_similarity(query, vec)))

    scores.sort(key=lambda x: x[1], reverse=True)
    print("query =", query)
    print("ranked by cosine similarity (high -> low):")
    for name, s in scores:
        print(f"  {name}: {s:.6f}")


if __name__ == "__main__":
    main()
