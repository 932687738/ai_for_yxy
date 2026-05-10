# 项目 01：Python AI 开发环境与房价数据分析

对应课程：第 1 课《Python 与 AI 开发环境》

## 1. 项目目标

本项目用于验证你是否真正具备后续 AI 学习所需的 Python 基础环境和最小数据分析能力。

完成后你应该能够：

1. 创建独立 Python 项目。
2. 使用虚拟环境管理依赖。
3. 使用 NumPy 做基础数值计算。
4. 使用 pandas 读取和分析 CSV。
5. 使用 Matplotlib 绘制图表。
6. 使用 JupyterLab 记录实验过程。

## 2. 推荐目录结构

```text
ai-study-lab/
  |
  +-- .venv/
  +-- requirements.txt
  +-- data/
  |   +-- houses.csv
  |
  +-- src/
  |   +-- hello_ai.py
  |   +-- numpy_demo.py
  |   +-- house_analysis.py
  |
  +-- notebooks/
      +-- 01-python-basics.ipynb
```

## 3. 初始化命令

```powershell
mkdir ai-study-lab
cd ai-study-lab
mkdir src
mkdir data
mkdir notebooks

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install numpy pandas matplotlib jupyterlab scikit-learn
python -m pip freeze > requirements.txt
```

## 4. 示例数据

`data/houses.csv`

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

## 5. 核心脚本

`src/house_analysis.py`

```python
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def load_data() -> pd.DataFrame:
    project_root = Path(__file__).resolve().parents[1]
    data_file = project_root / "data" / "houses.csv"
    return pd.read_csv(data_file)


def print_basic_info(df: pd.DataFrame) -> None:
    print("Data preview:")
    print(df.head())
    print()

    print("Shape:")
    print(df.shape)
    print()

    print("Statistics:")
    print(df.describe())
    print()


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["price_per_area"] = result["price"] / result["area"]
    return result


def plot_area_price(df: pd.DataFrame) -> None:
    project_root = Path(__file__).resolve().parents[1]
    output_file = project_root / "data" / "house_area_price.png"

    plt.scatter(df["area"], df["price"])
    plt.xlabel("Area")
    plt.ylabel("Price")
    plt.title("House Area vs Price")
    plt.grid(True)
    plt.savefig(output_file, dpi=150)
    plt.show()


def main() -> None:
    df = load_data()
    print_basic_info(df)

    enriched_df = add_features(df)
    print("Data with new feature:")
    print(enriched_df)

    plot_area_price(enriched_df)


if __name__ == "__main__":
    main()
```

## 6. 验收标准

项目完成后，你需要确认：

- 能执行 `python --version`。
- 能执行 `python -m pip list` 并看到 numpy、pandas、matplotlib、jupyterlab、scikit-learn。
- 能运行 `python src/house_analysis.py`。
- 能在终端看到数据统计信息。
- 能生成 `data/house_area_price.png`。
- 能启动 `jupyter lab`。
- 能在 Notebook 中复现 pandas 和 Matplotlib 实验。

## 7. 提交物

你最终应该保留：

- `requirements.txt`
- `data/houses.csv`
- `src/hello_ai.py`
- `src/numpy_demo.py`
- `src/house_analysis.py`
- `notebooks/01-python-basics.ipynb`
- `data/house_area_price.png`

