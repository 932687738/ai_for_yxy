# 项目 03：机器学习完整流程：房价预测

对应课程：第 3 课《机器学习完整流程》

## 1. 项目目标

本项目用于完成第一个真正的机器学习闭环。你需要从 CSV 数据出发，完成数据读取、特征构造、训练测试拆分、模型训练、模型评估、误差分析、Pipeline 重构和模型保存。

完成后你应该能够：

1. 把业务问题转换成监督学习回归问题。
2. 使用 pandas 构造特征 `X` 和标签 `y`。
3. 使用 scikit-learn 拆分训练集和测试集。
4. 使用线性回归训练模型。
5. 使用 MAE、MSE、RMSE、R2 评估模型。
6. 使用 Pipeline 组织预处理和模型。
7. 使用交叉验证评估模型稳定性。
8. 使用 joblib 保存和加载模型。

## 2. 推荐目录结构

```text
ai-study-lab/
  |
  +-- data/
  |   +-- houses_ml.csv
  |
  +-- models/
  |   +-- house_price_pipeline.joblib
  |
  +-- src/
      +-- house_price_linear_regression.py
      +-- house_price_pipeline.py
      +-- house_price_cross_validation.py
      +-- house_price_save_load.py
```

## 3. 数据文件

`data/houses_ml.csv`

```csv
area,rooms,age,distance_to_subway,price
60,1,18,3.5,88
70,2,15,3.0,105
80,2,12,2.8,122
90,2,10,2.5,138
100,3,8,2.0,158
110,3,7,1.8,172
120,3,6,1.5,190
130,3,5,1.3,205
140,4,4,1.0,225
150,4,3,0.8,245
160,4,2,0.6,265
170,5,2,0.5,285
75,2,16,3.2,112
85,2,11,2.7,128
95,3,9,2.3,150
105,3,8,2.1,162
115,3,6,1.7,180
125,3,5,1.4,198
135,4,4,1.2,218
145,4,3,0.9,238
```

## 4. 任务一：最小训练闭环

文件：

```text
src/house_price_linear_regression.py
```

要求：

1. 读取 `houses_ml.csv`。
2. 使用 `area`、`rooms`、`age`、`distance_to_subway` 作为特征。
3. 使用 `price` 作为标签。
4. 使用 `train_test_split` 拆分数据。
5. 使用 `LinearRegression` 训练。
6. 输出模型系数和截距。
7. 输出 MAE、MSE、RMSE、R2。
8. 输出每个测试样本的真实值、预测值和误差。

验收标准：

- 代码能正常运行。
- 能解释 `fit` 和 `predict`。
- 能解释每个评估指标的业务含义。

## 5. 任务二：Pipeline 重构

文件：

```text
src/house_price_pipeline.py
```

要求：

1. 使用 `StandardScaler` 进行标准化。
2. 使用 `LinearRegression` 作为模型。
3. 用 `Pipeline` 组合预处理和模型。
4. 训练并评估 Pipeline。
5. 构造一个新房屋样本并预测价格。

新样本示例：

```python
new_house = pd.DataFrame([
    {
        "area": 118,
        "rooms": 3,
        "age": 6,
        "distance_to_subway": 1.6,
    }
])
```

验收标准：

- 能说明为什么 Pipeline 能降低预处理错误风险。
- 能说明为什么标准化应该只在训练集上 fit。

## 6. 任务三：交叉验证

文件：

```text
src/house_price_cross_validation.py
```

参考代码：

```python
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    df = pd.read_csv(project_root / "data" / "houses_ml.csv")

    X = df[["area", "rooms", "age", "distance_to_subway"]]
    y = df["price"]

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", LinearRegression()),
    ])

    scores = cross_val_score(
        pipeline,
        X,
        y,
        cv=5,
        scoring="neg_mean_absolute_error",
    )

    mae_scores = -scores

    print("MAE for each fold:")
    print(mae_scores)
    print(f"Average MAE: {mae_scores.mean():.4f}")


if __name__ == "__main__":
    main()
```

验收标准：

- 能解释为什么 scikit-learn 返回的是负数分数。
- 能解释交叉验证比单次拆分更稳定的原因。

## 7. 任务四：保存和加载模型

文件：

```text
src/house_price_save_load.py
```

参考代码：

```python
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    data_file = project_root / "data" / "houses_ml.csv"
    model_file = project_root / "models" / "house_price_pipeline.joblib"
    model_file.parent.mkdir(exist_ok=True)

    df = pd.read_csv(data_file)

    X = df[["area", "rooms", "age", "distance_to_subway"]]
    y = df["price"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", LinearRegression()),
    ])

    pipeline.fit(X_train, y_train)
    joblib.dump(pipeline, model_file)

    loaded_pipeline = joblib.load(model_file)

    new_house = pd.DataFrame([
        {
            "area": 118,
            "rooms": 3,
            "age": 6,
            "distance_to_subway": 1.6,
        }
    ])

    prediction = loaded_pipeline.predict(new_house)
    print(f"Predicted price: {prediction[0]:.2f}")


if __name__ == "__main__":
    main()
```

运行前安装：

```powershell
python -m pip install joblib
```

验收标准：

- 能生成 `models/house_price_pipeline.joblib`。
- 能加载模型并完成预测。
- 能说明为什么要保存 Pipeline，而不是只保存模型。

## 8. 误差分析报告

请单独写一段分析，回答：

1. 测试集中误差最大的样本是哪一个？
2. 模型是高估还是低估？
3. 你认为可能缺少哪些特征？
4. 当前数据集太小会带来什么风险？
5. 如果要接入真实 Java 系统，需要提供什么 API？

建议新增特征：

- 小区位置
- 楼层
- 朝向
- 装修情况
- 学区
- 商圈
- 地铁线路
- 建筑类型
- 成交时间

## 9. 项目验收清单

- [ ] 完成 `houses_ml.csv`
- [ ] 完成 `house_price_linear_regression.py`
- [ ] 完成 `house_price_pipeline.py`
- [ ] 完成 `house_price_cross_validation.py`
- [ ] 完成 `house_price_save_load.py`
- [ ] 能解释 `X` 和 `y`
- [ ] 能解释训练集和测试集
- [ ] 能解释 MAE、MSE、RMSE、R2
- [ ] 能解释过拟合、欠拟合、数据泄漏
- [ ] 能完成误差分析报告
- [ ] 能保存和加载模型

## 10. 术语理解任务

请在项目报告中补充下面术语解释。要求不要照抄定义，要结合房价预测项目说明。

| 术语 | 你需要解释的问题 |
|---|---|
| 样本 | 在房价预测中，一条样本是什么？ |
| 特征 | 哪些字段是特征？为什么？ |
| 标签 | 哪个字段是标签？为什么？ |
| 训练集 | 它用来做什么？ |
| 测试集 | 它为什么不能参与训练？ |
| 泛化能力 | 如何判断模型是否能预测新房子？ |
| 过拟合 | 如果训练集很好但测试集很差，说明什么？ |
| 数据泄漏 | 哪些房屋字段可能造成泄漏？ |
| Pipeline | 它如何避免预处理和预测不一致？ |

## 11. 业务建模报告模板

请用下面模板写一份简短报告：

```text
项目名称：
  房价预测模型

业务目标：
  用模型辅助估算房屋价格。

预测对象：
  一套房子。

样本粒度：
  每一行 CSV 代表一套房子。

输入特征：
  area、rooms、age、distance_to_subway。

预测目标：
  price。

任务类型：
  监督学习 - 回归。

训练方式：
  使用训练集拟合模型参数。

评估方式：
  使用测试集计算 MAE、RMSE、R2。

主要风险：
  数据量太小，缺少地段、楼层、装修、学区等关键特征。

可能的数据泄漏：
  不能把成交后才知道的税费、佣金、贷款金额等字段作为特征。

上线建议：
  仅作为学习示例。真实上线需要更多数据、更多特征、更严格验证和人工审核。
```

## 12. Java 接入思考题

假设你要让 Spring Boot 系统调用这个房价预测模型，请回答：

1. Java 接口路径设计成什么？
2. 请求 JSON 包含哪些字段？
3. 响应 JSON 包含哪些字段？
4. 如果 Python 模型服务超时，Java 如何兜底？
5. 是否需要记录模型版本？
6. 是否需要保存每次预测请求和结果？

参考接口：

```text
POST /api/house-price/predict
```

参考请求：

```json
{
  "area": 118,
  "rooms": 3,
  "age": 6,
  "distanceToSubway": 1.6
}
```

参考响应：

```json
{
  "predictedPrice": 185.32,
  "modelVersion": "house-price-v1",
  "unit": "万元"
}
```

## 13. 扩展任务：Baseline 对比

请新增文件：

```text
src/house_price_baseline.py
```

要求：

1. 使用 `DummyRegressor(strategy="mean")` 建立基线模型。
2. 使用 `LinearRegression` 建立真实模型。
3. 分别输出两个模型的 MAE、RMSE、R2。
4. 判断线性回归是否明显优于 baseline。

参考结论格式：

```text
Baseline MAE: 18.50
LinearRegression MAE: 6.20

结论：
  线性回归明显优于简单预测均值，说明当前特征对房价有预测价值。
```

## 14. 扩展任务：数据质量检查报告

请新增文件：

```text
reports/house_price_data_quality.md
```

报告至少包含：

1. 数据行数和列数。
2. 每个字段的含义。
3. 每个字段的数据类型。
4. 缺失值统计。
5. 重复样本数量。
6. 目标值 `price` 的分布。
7. 是否存在明显异常值。
8. 哪些字段可能造成数据泄漏。

建议代码：

```python
print(df.shape)
print(df.info())
print(df.describe())
print(df.isna().sum())
print(df.duplicated().sum())
```

## 15. 扩展任务：分类任务迷你实验

为了理解分类评估，请创建一个用户流失预测小实验。

数据文件：

```text
data/churn_demo.csv
```

内容：

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

任务：

1. 使用 `LogisticRegression` 训练二分类模型。
2. 使用 `stratify=y` 拆分训练集和测试集。
3. 输出 `confusion_matrix`。
4. 输出 `classification_report`。
5. 解释 Precision、Recall、F1。

说明：

这个数据很小，只用于理解分类流程和指标，不代表真实模型效果。

## 16. 扩展任务：阈值分析

在用户流失预测中，模型通常输出流失概率。

请尝试：

```python
y_proba = model.predict_proba(X_test)[:, 1]
```

然后分别使用不同阈值：

```text
0.3
0.5
0.7
```

观察 Precision 和 Recall 如何变化。

你需要回答：

1. 阈值升高后，Precision 通常怎么变？
2. 阈值升高后，Recall 通常怎么变？
3. 如果运营资源有限，应该提高还是降低阈值？
4. 如果不想漏掉高风险用户，应该提高还是降低阈值？

## 17. 扩展任务：模型上线前检查

请针对房价预测项目填写下面清单：

- [ ] 业务目标是否明确？
- [ ] 标签 `price` 定义是否明确？
- [ ] 所有特征是否在预测时可获得？
- [ ] 是否检查过数据泄漏？
- [ ] 是否和 baseline 对比？
- [ ] 是否做过训练集/测试集拆分？
- [ ] 是否做过误差分析？
- [ ] 是否保存 Pipeline？
- [ ] 是否记录模型版本？
- [ ] Java 调用失败时是否有兜底方案？
- [ ] 是否需要人工审核预测结果？

## 18. 扩展任务：第 3 课复述

请用自己的话写一篇 800 字以内的小结，必须包含：

1. 机器学习完整流程。
2. 训练集、验证集、测试集。
3. 特征和标签。
4. baseline。
5. 评估指标。
6. 过拟合和欠拟合。
7. 数据泄漏。
8. Pipeline。
9. Java 系统如何调用模型。

这个复述任务很重要。能复述出来，说明你不是只跑通了代码，而是真的理解了流程。
