# 项目 04：监督学习概念验收：回归与分类

对应课程：第 4 课《监督学习：回归与分类》

## 1. 项目目标

本项目不是为了写复杂代码，而是验证你是否真正理解监督学习、回归、分类和评估指标。

完成后你应该能够：

1. 判断业务问题属于回归还是分类。
2. 解释回归标签和分类标签的区别。
3. 理解线性回归、逻辑回归、决策树的基本作用。
4. 根据业务错误成本选择评估指标。
5. 解释 Precision、Recall、F1、Accuracy 的适用场景。
6. 说明阈值如何影响业务动作。

## 2. 项目结构

建议目录：

```text
ai-study-lab/
  |
  +-- data/
  |   +-- houses_ml.csv
  |   +-- churn_demo.csv
  |
  +-- reports/
  |   +-- supervised_learning_concepts.md
  |   +-- metric_selection_report.md
  |
  +-- src/
      +-- regression_demo.py
      +-- classification_demo.py
      +-- threshold_analysis.py
```

## 3. 任务一：术语理解报告

创建：

```text
reports/supervised_learning_concepts.md
```

请用自己的话解释以下术语，每个术语至少包含：

1. 一句话定义。
2. 一个业务例子。
3. 一个常见误区。

术语清单：

- 监督学习
- 样本
- 特征
- 标签
- 回归
- 分类
- 二分类
- 多分类
- 多标签分类
- 线性回归
- 逻辑回归
- 决策树
- Accuracy
- Precision
- Recall
- F1
- 混淆矩阵
- 阈值
- 类别不平衡

验收标准：

- 不是照抄教材定义。
- 能结合业务解释。
- 能说出至少 5 个易错点。

## 4. 任务二：业务问题归类

在报告中完成下面表格：

| 业务问题 | 回归/分类 | 理由 | 标签是什么 | 主要指标 |
|---|---|---|---|---|
| 预测房屋成交价 |  |  |  |  |
| 预测用户是否流失 |  |  |  |  |
| 预测订单是否欺诈 |  |  |  |  |
| 预测明天商品销量 |  |  |  |  |
| 预测工单类型 |  |  |  |  |
| 预测客户风险等级 |  |  |  |  |
| 预测设备剩余寿命 |  |  |  |  |

要求：

- 如果是连续数值，通常是回归。
- 如果是类别，通常是分类。
- 指标选择要结合业务错误成本。

## 5. 任务三：回归最小验证

数据：

```text
data/houses_ml.csv
```

字段：

```text
area, rooms, age, distance_to_subway, price
```

概念要求：

- `X` 是什么？
- `y` 是什么？
- 为什么这是回归？
- MAE 如何解释？
- RMSE 和 MAE 有什么区别？
- R2 高是否一定可以上线？

代码只作为辅助：

```python
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    df = pd.read_csv(project_root / "data" / "houses_ml.csv")

    X = df[["area", "rooms", "age", "distance_to_subway"]]
    y = df["price"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = mse ** 0.5
    r2 = r2_score(y_test, y_pred)

    print(f"MAE: {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R2: {r2:.4f}")


if __name__ == "__main__":
    main()
```

报告中必须写：

```text
这是回归任务，因为标签 price 是连续数值。
MAE 表示模型平均预测误差。
RMSE 更关注大误差。
R2 表示整体解释能力，但不能单独决定模型是否可上线。
```

## 6. 任务四：分类最小验证

数据：

```text
data/churn_demo.csv
```

示例：

```csv
login_days,last_order_days,order_count,total_amount,complaint_count,is_churn
25,2,12,3000,0,0
20,5,9,2200,0,0
3,45,1,120,2,1
5,30,2,300,1,1
28,1,15,5000,0,0
10,18,4,800,1,0
2,60,0,0,3,1
8,25,3,500,1,1
30,1,20,8000,0,0
15,10,6,1500,0,0
```

概念要求：

- `X` 是什么？
- `y` 是什么？
- 为什么这是二分类？
- 正例是什么？
- FP 和 FN 分别代表什么业务含义？
- Precision 和 Recall 应该更关注哪个？

代码只作为辅助：

```python
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    df = pd.read_csv(project_root / "data" / "churn_demo.csv")

    X = df[["login_days", "last_order_days", "order_count", "total_amount", "complaint_count"]]
    y = df["is_churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression()),
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    print(confusion_matrix(y_test, y_pred))
    print(classification_report(y_test, y_pred))


if __name__ == "__main__":
    main()
```

## 7. 任务五：阈值分析

请解释下面三个阈值策略：

```text
threshold = 0.3
threshold = 0.5
threshold = 0.8
```

需要回答：

1. 阈值越高，模型判为正例会更谨慎还是更宽松？
2. 阈值提高后，Precision 通常怎么变化？
3. 阈值提高后，Recall 通常怎么变化？
4. 如果运营资源有限，应该使用较高阈值还是较低阈值？
5. 如果不想漏掉高风险用户，应该使用较高阈值还是较低阈值？

参考代码：

```python
y_proba = pipeline.predict_proba(X_test)[:, 1]

threshold = 0.7
y_pred_custom = (y_proba >= threshold).astype(int)
```

【重点】阈值调整不是为了让指标好看，而是为了匹配业务成本。

## 8. 任务六：指标选择报告

创建：

```text
reports/metric_selection_report.md
```

完成下面表格：

| 场景 | 误报成本 | 漏报成本 | 更关注指标 | 原因 |
|---|---|---|---|---|
| 欺诈检测 |  |  |  |  |
| 用户流失挽留 |  |  |  |  |
| 外呼营销名单 |  |  |  |  |
| 垃圾邮件识别 |  |  |  |  |
| 设备故障预警 |  |  |  |  |
| 工单自动分类 |  |  |  |  |

验收标准：

- 能解释 FP 和 FN 的业务含义。
- 能说明为什么选择 Precision / Recall / F1 / Accuracy。
- 能说明阈值是否需要调整。

## 9. 项目验收清单

- [ ] 能解释监督学习。
- [ ] 能区分回归和分类。
- [ ] 能判断业务问题的建模类型。
- [ ] 能解释线性回归。
- [ ] 能解释逻辑回归。
- [ ] 能解释决策树。
- [ ] 能解释 Accuracy、Precision、Recall、F1。
- [ ] 能解释混淆矩阵。
- [ ] 能解释类别不平衡。
- [ ] 能解释阈值对业务动作的影响。
- [ ] 能完成术语理解报告。
- [ ] 能完成指标选择报告。
- [ ] 能运行回归和分类最小代码。

