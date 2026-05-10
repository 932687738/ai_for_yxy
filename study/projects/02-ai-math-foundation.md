# 项目 02：AI 数学基础实验室

对应课程：第 2 课《AI 数学基础：向量、矩阵、概率与导数》

## 1. 项目目标

本项目用于把向量、矩阵、概率、统计、损失函数、梯度下降这些概念落到 Python 代码中。

完成后你应该能够：

1. 使用 NumPy 表示向量和矩阵。
2. 计算点积、范数、欧氏距离、余弦相似度。
3. 使用 pandas 和 Matplotlib 分析数据分布。
4. 手写均方误差 MSE。
5. 手写梯度下降训练一个极简线性回归模型。
6. 理解后续机器学习训练代码的基本结构。

## 2. 推荐目录结构

```text
ai-study-lab/
  |
  +-- data/
  |   +-- houses.csv
  |
  +-- src/
      +-- vector_matrix_practice.py
      +-- cosine_search_practice.py
      +-- statistics_practice.py
      +-- linear_regression_from_scratch.py
```

## 3. 实验一：向量与矩阵计算

文件：

```text
src/vector_matrix_practice.py
```

参考代码：

```python
import numpy as np


def main() -> None:
    a = np.array([1, 2, 3])
    b = np.array([10, 20, 30])

    print("a:", a)
    print("b:", b)
    print("a shape:", a.shape)
    print("b shape:", b.shape)

    print("a + b:", a + b)
    print("2 * a:", 2 * a)
    print("dot:", np.dot(a, b))
    print("norm a:", np.linalg.norm(a))
    print("distance:", np.linalg.norm(a - b))

    matrix_a = np.array([
        [1, 2],
        [3, 4],
        [5, 6],
    ])

    matrix_b = np.array([
        [10],
        [20],
    ])

    result = matrix_a @ matrix_b

    print("matrix_a shape:", matrix_a.shape)
    print("matrix_b shape:", matrix_b.shape)
    print("result shape:", result.shape)
    print(result)


if __name__ == "__main__":
    main()
```

验收标准：

- 能解释每个输出的含义。
- 能说明 `a * b` 和 `a @ b` 的区别。
- 能根据 shape 判断矩阵乘法是否合法。

## 4. 实验二：余弦相似度排序

文件：

```text
src/cosine_search_practice.py
```

参考代码：

```python
import numpy as np


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def main() -> None:
    query = np.array([0.85, 0.75, 0.25])

    documents = {
        "Java Spring Boot 实战": np.array([0.90, 0.80, 0.20]),
        "AI 机器学习入门": np.array([0.75, 0.70, 0.35]),
        "数据库索引优化": np.array([0.60, 0.65, 0.30]),
        "旅游攻略": np.array([0.10, 0.20, 0.90]),
        "烹饪教程": np.array([0.20, 0.10, 0.85]),
    }

    scores = []
    for title, vector in documents.items():
        score = cosine_similarity(query, vector)
        scores.append((title, score))

    scores.sort(key=lambda item: item[1], reverse=True)

    for title, score in scores:
        print(f"{title}: {score:.4f}")


if __name__ == "__main__":
    main()
```

验收标准：

- 能说明为什么相似文档排在前面。
- 能解释这个实验和 RAG 检索的关系。
- 能新增一个文档向量并观察排序变化。

## 5. 实验三：统计分析与分布观察

文件：

```text
src/statistics_practice.py
```

示例数据：

```csv
area,rooms,age,price
80,2,10,120
100,3,8,150
120,3,5,180
150,4,3,230
60,1,15,90
90,2,12,130
110,3,7,165
130,3,6,195
160,4,2,250
70,2,20,100
```

参考代码：

```python
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    data_file = project_root / "data" / "houses.csv"

    df = pd.read_csv(data_file)

    print("price mean:", df["price"].mean())
    print("price variance:", df["price"].var())
    print("price std:", df["price"].std())

    print("max price row:")
    print(df.loc[df["price"].idxmax()])

    print("min price row:")
    print(df.loc[df["price"].idxmin()])

    plt.hist(df["price"], bins=5)
    plt.xlabel("Price")
    plt.ylabel("Count")
    plt.title("Price Distribution")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()
```

验收标准：

- 能解释均值、方差、标准差分别代表什么。
- 能看懂直方图反映的数据分布。
- 能说明为什么训练模型前要先观察数据。

## 6. 实验四：从零实现线性回归

文件：

```text
src/linear_regression_from_scratch.py
```

参考代码：

```python
import numpy as np


def main() -> None:
    X = np.array([1, 2, 3, 4, 5], dtype=float)
    y = np.array([3, 5, 7, 9, 11], dtype=float)

    w = 0.0
    b = 0.0

    learning_rate = 0.01
    epochs = 1000
    n = len(X)

    for epoch in range(epochs):
        y_pred = w * X + b
        loss = np.mean((y_pred - y) ** 2)

        dw = (2 / n) * np.sum((y_pred - y) * X)
        db = (2 / n) * np.sum(y_pred - y)

        w -= learning_rate * dw
        b -= learning_rate * db

        if epoch % 100 == 0:
            print(f"epoch={epoch}, loss={loss:.6f}, w={w:.4f}, b={b:.4f}")

    print(f"final: y = {w:.4f} * x + {b:.4f}")


if __name__ == "__main__":
    main()
```

验收标准：

- loss 应该整体下降。
- `w` 应该逐渐接近 2。
- `b` 应该逐渐接近 1。
- 能解释训练循环中的预测、损失、梯度、参数更新四步。

## 7. 拓展任务

完成基础实验后，继续尝试：

1. 把学习率改成 `0.001`，观察训练速度。
2. 把学习率改成 `0.1`，观察是否震荡。
3. 把训练轮数改成 `100`、`500`、`2000`，观察最终参数。
4. 给训练数据加入噪声，例如 `y = 2x + 1 + noise`。
5. 把线性回归改成房价预测：`price = w1*area + w2*rooms + w3*age + b`。

## 8. 项目验收清单

- [ ] 完成 `vector_matrix_practice.py`
- [ ] 完成 `cosine_search_practice.py`
- [ ] 完成 `statistics_practice.py`
- [ ] 完成 `linear_regression_from_scratch.py`
- [ ] 能解释向量、矩阵、shape 的含义
- [ ] 能解释余弦相似度和 RAG 的关系
- [ ] 能解释均值、方差、标准差
- [ ] 能解释损失函数和梯度下降
- [ ] 能独立运行所有脚本

