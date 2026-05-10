# 第 1 课：Python 与 AI 开发环境

## 0. 本课阅读方式

本课的重点不是背 Python 语法，也不是机械安装一堆工具，而是理解 AI 学习中为什么需要 Python，以及每个开发环境组件到底解决什么问题。

建议学习顺序：

```text
先理解术语和工具分工
  -> 再搭建 Windows 本地环境
  -> 再运行最小代码
  -> 最后完成数据分析小练习
```

本课你真正需要掌握的是：

```text
Python 在 AI 学习中承担什么角色？
解释器、虚拟环境、pip、requirements.txt 分别是什么？
Jupyter 为什么适合 AI 实验？
NumPy、pandas、Matplotlib 分别解决什么问题？
为什么 Java 开发者仍然需要具备 Python 阅读和实验能力？
```

【核心】本课代码只是帮助你验证环境是否可用。真正重要的是理解 AI 开发环境中每个工具的定位。

## 0.1 概念讲义：Python AI 开发环境术语与核心知识详解

### 0.1.1 第 1 课到底在学什么

第 1 课不是把你培养成 Python 后端工程师，而是让你具备后续 AI 学习的最小 Python 工具能力。

你有 Java 基础，所以本课要解决的不是“编程从零开始”，而是：

```text
如何从 Java 工程思维切换到 Python 实验思维？
如何理解 Python 生态里的解释器、虚拟环境、包管理？
如何使用 AI 学习中最常见的数据工具？
如何把 Notebook 实验和正式脚本区分开？
```

【重点】Java 是你做 AI 应用工程化的主力语言，Python 是你理解 AI 训练、数据处理和算法实验的必要工具。

### 0.1.2 Python

Python 是一种解释型、动态类型、语法简洁的编程语言。

在 AI 领域，Python 重要不是因为语法高级，而是因为生态成熟：

| 场景 | 常用 Python 工具 |
|---|---|
| 数值计算 | NumPy |
| 表格数据分析 | pandas |
| 数据可视化 | Matplotlib |
| 传统机器学习 | scikit-learn |
| 深度学习 | PyTorch |
| 大模型生态 | Transformers、datasets |
| 实验记录 | Jupyter Notebook / JupyterLab |

【核心】学习 AI 时，Python 是算法、数据和实验的通用工作台。

【类比】如果 Java + Spring Boot 是生产系统的后端框架，那么 Python + Jupyter + NumPy/pandas 就是 AI 学习阶段的实验室。

### 0.1.3 Python 解释器 Interpreter

解释器是执行 Python 代码的程序。

当你运行：

```powershell
python src/hello_ai.py
```

真正执行代码的是 Python 解释器。

你可以把解释器理解为：

```text
读取 .py 文件
理解 Python 语法
执行代码
输出结果
```

【重点】电脑里可能有多个 Python 解释器。后续很多环境问题，本质上都是“你以为用的是 A 解释器，实际用的是 B 解释器”。

常见检查命令：

```powershell
python --version
where python
```

### 0.1.4 脚本 Script

脚本就是一个可执行的 `.py` 文件。

例如：

```text
src/hello_ai.py
```

脚本适合：

- 固定流程的数据处理。
- 可以重复执行的训练任务。
- 项目中的正式代码。
- 被其他模块导入复用的函数。

Notebook 适合探索，脚本适合沉淀。

【重点】AI 学习中常见流程是：先用 Notebook 探索，再整理成 `.py` 脚本。

### 0.1.5 REPL

REPL 是 Read-Eval-Print Loop，交互式命令环境。

你在命令行输入：

```powershell
python
```

进入的交互环境就是 REPL。

它适合快速验证：

```python
1 + 2
```

但不适合写复杂项目。

### 0.1.6 Jupyter Notebook / JupyterLab

Jupyter 是交互式实验环境。

Notebook 的特点是：

```text
一段代码
  -> 立即运行
  -> 立即看到结果
  -> 旁边还能写解释文字和图表
```

它非常适合 AI 学习，因为 AI 学习经常需要：

- 观察数据。
- 尝试不同参数。
- 查看图表。
- 记录实验结论。
- 分步骤理解模型训练。

JupyterLab 是 Jupyter 的更完整工作界面。

【易错】Notebook 不是正式项目结构。它适合实验，不适合长期堆积业务代码。

推荐流程：

```text
Notebook 里探索数据和思路
  -> 把稳定逻辑整理到 src/*.py
  -> 项目化管理依赖和数据
```

### 0.1.7 Kernel

Kernel 是 Notebook 背后真正执行代码的 Python 运行环境。

你在 Notebook 单元格里写：

```python
import pandas as pd
```

这行代码是在 Kernel 中执行的。

【重点】Notebook 能否导入某个包，取决于当前 Kernel 对应的 Python 环境里是否安装了这个包。

常见问题：

```text
命令行里 pip install pandas 成功
但 Notebook 里 import pandas 失败
```

常见原因：

```text
命令行和 Notebook 使用的不是同一个 Python 环境。
```

### 0.1.8 虚拟环境 venv

虚拟环境是给每个 Python 项目单独准备的一套依赖环境。

它解决的问题是：

```text
不同项目需要不同版本的依赖，不能全部混在系统 Python 里。
```

类比 Java：

```text
Java 项目：
  pom.xml / build.gradle 管理依赖

Python 项目：
  .venv + requirements.txt 管理依赖
```

【核心】每个 AI 学习项目都应该有自己的虚拟环境。

【易错】不要把所有 Python 包都安装到系统全局环境里。这样很容易造成版本冲突。

### 0.1.9 pip

pip 是 Python 包管理工具。

它的作用类似：

```text
下载依赖
安装依赖
查看已安装依赖
根据 requirements.txt 恢复依赖
```

常见命令：

```powershell
python -m pip install pandas
python -m pip list
python -m pip freeze > requirements.txt
python -m pip install -r requirements.txt
```

【重点】推荐使用 `python -m pip`，因为它能明确使用当前 Python 解释器对应的 pip。

### 0.1.10 requirements.txt

`requirements.txt` 是 Python 项目的依赖清单。

它记录项目需要哪些包。

例如：

```text
numpy
pandas
matplotlib
jupyterlab
scikit-learn
```

它解决的是“换一台机器如何恢复环境”的问题。

【工程经验】项目能不能复现，依赖清单非常重要。

### 0.1.11 包 Package 和模块 Module

模块通常是一个 `.py` 文件。

包通常是一个包含多个模块的目录。

例如：

```python
import numpy as np
import pandas as pd
```

这里的 NumPy 和 pandas 是第三方包。

【重点】`import` 不是下载安装，它只是把已经安装好的模块或包加载到当前代码中。

如果包没有安装，会出现：

```text
ModuleNotFoundError
```

### 0.1.12 NumPy

NumPy 是 Python 数值计算基础库。

它最重要的对象是数组 `ndarray`。

在 AI 中，NumPy 用于理解：

- 向量。
- 矩阵。
- 张量。
- 点积。
- 矩阵乘法。
- 批量计算。

【核心】AI 中大量数据最终都会变成数字数组。NumPy 是理解这些数字数组的第一站。

### 0.1.13 pandas

pandas 是表格数据分析工具。

它最重要的对象是：

- `DataFrame`
- `Series`

DataFrame 可以理解为内存中的表。

```text
行：样本
列：字段或特征
```

【核心】传统机器学习的大量数据处理工作都发生在 pandas DataFrame 中。

### 0.1.14 DataFrame

DataFrame 是二维表格数据结构。

例如：

```text
area  rooms  age  price
80    2      10   120
100   3      8    150
```

你可以把它类比为：

```text
数据库查询结果
Excel 表格
CSV 文件读入内存后的表
```

【重点】机器学习中经常从 DataFrame 中拆出 `X` 和 `y`。

### 0.1.15 Series

Series 是 pandas 中的一维数据结构，可以理解为 DataFrame 的一列。

例如：

```python
df["price"]
```

返回的就是一个 Series。

【重点】特征矩阵通常是 DataFrame，标签列通常是 Series。

### 0.1.16 Matplotlib

Matplotlib 是基础绘图库。

AI 学习中，它主要用于：

- 观察数据分布。
- 画散点图。
- 画训练曲线。
- 画模型误差。

【重点】图表不是为了好看，而是为了发现数据规律和异常。

### 0.1.17 工作目录 Working Directory

工作目录是程序运行时的当前目录。

很多路径错误都来自不理解工作目录。

例如：

```python
pd.read_csv("data/houses.csv")
```

这行代码会从当前工作目录下找 `data/houses.csv`，不是一定从脚本所在目录找。

【易错】脚本所在目录和当前工作目录不一定相同。

推荐使用 `pathlib` 基于 `__file__` 构造稳定路径。

### 0.1.18 pathlib

`pathlib` 是 Python 标准库中的路径处理工具。

它比手写字符串路径更稳。

```python
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
data_file = project_root / "data" / "houses.csv"
```

【重点】Windows 路径中反斜杠容易引发转义问题，`pathlib` 可以减少路径错误。

### 0.1.19 第 1 课重点标注汇总

【核心】Python 是 AI 学习中用于数据、算法和实验的通用工作台。

【核心】虚拟环境用于隔离项目依赖，每个项目都应该有独立 `.venv`。

【核心】pip 负责安装依赖，`requirements.txt` 负责记录依赖。

【核心】Jupyter 适合探索实验，`.py` 脚本适合沉淀正式逻辑。

【核心】NumPy 负责数值数组，pandas 负责表格数据，Matplotlib 负责可视化。

【重点】Notebook 的 Kernel 必须和你安装依赖的 Python 环境一致。

【重点】AI 初学阶段学习 Python 的目标是“能读、能改、能实验”，不是转成 Python 后端。

【易错】不要把所有包安装到系统全局 Python。

【易错】不要把 Notebook 当成正式项目无限堆代码。

【易错】路径错误通常来自工作目录理解不清。

### 0.1.20 自我检查问题

请先不用代码回答下面问题：

1. 为什么 Java 开发者学习 AI 仍然需要 Python？
2. Python 解释器是什么？
3. 虚拟环境解决什么问题？
4. pip 和 requirements.txt 分别解决什么问题？
5. Jupyter Notebook 适合做什么，不适合做什么？
6. Kernel 是什么？
7. NumPy、pandas、Matplotlib 分别负责什么？
8. DataFrame 和 Series 有什么区别？
9. 为什么路径问题在 Python 项目中很常见？
10. 为什么 AI 学习中要先用 Notebook 探索，再整理成脚本？

## 1. 本课目标

你有 Java 开发基础，所以本课不会把 Python 当作第一门编程语言来讲，而是从 Java 开发者的视角，快速建立 AI 学习必须具备的 Python 能力。

学完本课后，你应该能够：

1. 理解为什么学习 AI 不能只依赖 Java。
2. 在 Windows 上安装 Python、创建虚拟环境、安装 AI 常用依赖。
3. 使用 VS Code 或 PyCharm 编写 Python 脚本。
4. 使用 Jupyter Notebook / JupyterLab 做交互式实验。
5. 掌握 Python 中最常见的数据结构、函数、模块、包管理方式。
6. 使用 NumPy 完成向量和矩阵计算。
7. 使用 pandas 读取和分析 CSV 数据。
8. 使用 Matplotlib 绘制简单图表。
9. 建立一个后续课程可复用的 AI 学习项目目录。

## 2. 为什么 Java 开发者也要学 Python

Java 很适合做企业级系统：

- Spring Boot 后端服务
- 权限系统
- 工作流
- 事务处理
- 数据库操作
- 消息队列
- 微服务
- 生产环境部署

但 AI 训练、数据处理、实验分析的主流生态在 Python：

- NumPy：数值计算
- pandas：数据分析
- scikit-learn：传统机器学习
- PyTorch：深度学习
- Transformers：大模型和 Transformer 生态
- Jupyter Notebook：实验记录与交互式分析

这并不意味着你要放弃 Java。更合理的分工是：

```text
Python
  |
  +-- 数据分析
  +-- 模型实验
  +-- 训练代码阅读
  +-- 算法原型验证

Java
  |
  +-- 业务系统
  +-- API 服务
  +-- 权限与日志
  +-- RAG 工程化
  +-- 大模型应用上线
```

本课程对 Python 的要求是“够用、能读、能改、能实验”，不是要求你马上成为 Python 后端专家。

## 3. 本课最终产出

完成本课后，你将在本地拥有一个目录：

```text
ai-study-lab/
  |
  +-- .venv/
  +-- requirements.txt
  +-- notebooks/
  |   +-- 01-python-basics.ipynb
  |
  +-- data/
  |   +-- houses.csv
  |
  +-- src/
      +-- hello_ai.py
      +-- numpy_demo.py
      +-- pandas_demo.py
      +-- plot_demo.py
```

这个目录会作为后续机器学习、深度学习、大模型实验的基础工作区。

## 4. Windows 环境准备

### 4.1 检查系统中是否已有 Python

打开 PowerShell，执行：

```powershell
python --version
```

如果输出类似：

```text
Python 3.12.6
```

说明系统已经能找到 Python。

如果提示找不到命令，再执行：

```powershell
py --version
```

Windows 上有时会安装 Python Launcher，此时 `py` 命令可用。

建议使用 Python 3.10 及以上版本。后续课程中，很多 AI 库对 Python 版本有要求，过老版本会带来安装问题。

### 4.2 安装 Python

推荐从 Python 官方网站下载安装：

```text
https://www.python.org/downloads/
```

安装时注意勾选：

```text
Add python.exe to PATH
```

如果你忘记勾选，PowerShell 里可能无法直接执行 `python`。

### 4.3 验证 pip

pip 是 Python 的包管理工具，类似 Java 生态里的 Maven / Gradle 依赖下载能力。

执行：

```powershell
python -m pip --version
```

如果输出 pip 版本，说明可用。

升级 pip：

```powershell
python -m pip install --upgrade pip
```

如果下载慢，可以后续配置国内镜像。但初学阶段建议先理解标准命令。

## 5. 创建 AI 学习工作区

下面以 `C:\Users\你的用户名\IdeaProjects\ai-study-lab` 为例。你也可以放在任意目录。

```powershell
cd C:\Users\你的用户名\IdeaProjects
mkdir ai-study-lab
cd ai-study-lab
mkdir src
mkdir data
mkdir notebooks
```

如果你想放在当前课程目录旁边，也可以使用：

```powershell
cd C:\Users\BG518089\IdeaProjects\test\study
mkdir ai-study-lab
cd ai-study-lab
mkdir src
mkdir data
mkdir notebooks
```

## 6. 虚拟环境 venv

### 6.1 为什么需要虚拟环境

Java 项目一般通过 Maven / Gradle 管理依赖，每个项目的依赖版本写在 `pom.xml` 或 `build.gradle` 中。

Python 项目如果不隔离环境，容易出现：

- A 项目需要 numpy 1.x
- B 项目需要 numpy 2.x
- 全局安装后版本冲突
- 代码在自己电脑能跑，换台机器不能跑

虚拟环境就是给每个项目单独创建一套 Python 依赖目录。

类比 Java：

```text
Java 项目
  pom.xml / build.gradle
  Maven 本地仓库

Python 项目
  requirements.txt / pyproject.toml
  .venv 虚拟环境
```

### 6.2 创建虚拟环境

在项目根目录执行：

```powershell
python -m venv .venv
```

创建后会出现：

```text
.venv/
  |
  +-- Scripts/
  +-- Lib/
  +-- pyvenv.cfg
```

### 6.3 激活虚拟环境

PowerShell 中执行：

```powershell
.\.venv\Scripts\Activate.ps1
```

激活成功后，命令行前面通常会出现：

```text
(.venv) PS C:\...\ai-study-lab>
```

如果提示 PowerShell 执行策略限制，可以执行：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

然后重新激活虚拟环境。

### 6.4 退出虚拟环境

```powershell
deactivate
```

### 6.5 确认当前 Python 来自虚拟环境

```powershell
where python
```

理想情况下，第一行应该指向当前项目的 `.venv`：

```text
C:\...\ai-study-lab\.venv\Scripts\python.exe
```

## 7. 安装 AI 常用依赖

激活虚拟环境后，安装本阶段常用包：

```powershell
python -m pip install numpy pandas matplotlib jupyterlab scikit-learn
```

这些包的用途：

| 包 | 用途 | 后续课程作用 |
|---|---|---|
| numpy | 数值计算、向量、矩阵 | 数学基础、机器学习、深度学习 |
| pandas | 表格数据处理 | 数据清洗、特征工程 |
| matplotlib | 绘图 | 数据可视化、训练曲线 |
| jupyterlab | 交互式 Notebook | 实验记录、代码演示 |
| scikit-learn | 传统机器学习 | 回归、分类、聚类、评估 |

生成依赖清单：

```powershell
python -m pip freeze > requirements.txt
```

以后换一台机器，可以用：

```powershell
python -m pip install -r requirements.txt
```

恢复依赖。

## 8. 第一个 Python 程序

创建文件：

```text
src/hello_ai.py
```

写入：

```python
name = "Java Developer"
topic = "AI"

print(f"Hello, {name}. Welcome to {topic}.")
```

运行：

```powershell
python src/hello_ai.py
```

输出：

```text
Hello, Java Developer. Welcome to AI.
```

### 8.1 和 Java 的直观对比

Java：

```java
public class HelloAi {
    public static void main(String[] args) {
        String name = "Java Developer";
        String topic = "AI";
        System.out.println("Hello, " + name + ". Welcome to " + topic + ".");
    }
}
```

Python：

```python
name = "Java Developer"
topic = "AI"
print(f"Hello, {name}. Welcome to {topic}.")
```

Python 更适合快速实验，因为：

- 不需要定义类才能运行简单脚本。
- 不需要显式声明变量类型。
- 代码更短，适合数据探索和模型实验。

## 9. Python 基础语法速通

### 9.1 变量与类型

```python
age = 30
price = 19.99
name = "Alice"
is_active = True
```

查看类型：

```python
print(type(age))
print(type(price))
print(type(name))
print(type(is_active))
```

输出：

```text
<class 'int'>
<class 'float'>
<class 'str'>
<class 'bool'>
```

和 Java 不同，Python 变量本身不声明类型：

```java
int age = 30;
String name = "Alice";
```

Python 是动态类型语言，但对象仍然有类型。

### 9.2 字符串

```python
name = "Alice"
score = 95

message = f"{name}'s score is {score}"
print(message)
```

`f"..."` 是格式化字符串，AI 示例代码中非常常见。

常用字符串操作：

```python
text = "  Machine Learning  "

print(text.strip())        # 去掉首尾空白
print(text.lower())        # 转小写
print(text.upper())        # 转大写
print(text.replace("Machine", "Deep"))
print("Learning" in text)  # 判断是否包含
```

### 9.3 列表 list

Python 的 list 类似 Java 中的 `ArrayList`。

```python
scores = [88, 92, 79, 95]

print(scores[0])
print(scores[-1])
print(len(scores))

scores.append(100)
print(scores)
```

遍历：

```python
for score in scores:
    print(score)
```

带下标遍历：

```python
for index, score in enumerate(scores):
    print(index, score)
```

列表推导式：

```python
scores = [88, 92, 79, 95]
passed = [score for score in scores if score >= 80]
print(passed)
```

等价于：

```python
passed = []
for score in scores:
    if score >= 80:
        passed.append(score)
```

AI 数据处理中经常看到列表推导式。

### 9.4 字典 dict

Python 的 dict 类似 Java 中的 `HashMap`。

```python
user = {
    "id": 1001,
    "name": "Alice",
    "role": "admin"
}

print(user["name"])
print(user.get("email", "unknown"))
```

遍历键值：

```python
for key, value in user.items():
    print(key, value)
```

常见用途：

- 表示一条 JSON 数据
- 表示模型配置
- 表示 API 请求参数
- 表示训练超参数

例如：

```python
config = {
    "learning_rate": 0.01,
    "batch_size": 32,
    "epochs": 10
}
```

### 9.5 元组 tuple

tuple 是不可变序列。

```python
point = (10, 20)
x, y = point
print(x, y)
```

常用于函数返回多个值：

```python
def split_dataset():
    train_size = 800
    test_size = 200
    return train_size, test_size

train, test = split_dataset()
print(train, test)
```

### 9.6 条件语句

```python
score = 85

if score >= 90:
    print("A")
elif score >= 80:
    print("B")
else:
    print("C")
```

注意 Python 使用缩进表示代码块，而不是 `{}`。

这是 Java 开发者最容易踩坑的地方之一。

### 9.7 函数

```python
def add(a, b):
    return a + b

result = add(3, 5)
print(result)
```

带默认参数：

```python
def greet(name, prefix="Hello"):
    return f"{prefix}, {name}"

print(greet("Alice"))
print(greet("Bob", prefix="Hi"))
```

AI 代码中的函数通常用于：

- 加载数据
- 清洗数据
- 构建模型
- 训练模型
- 评估模型

### 9.8 模块导入

```python
import math

print(math.sqrt(16))
```

给模块起别名：

```python
import numpy as np
import pandas as pd
```

这是 AI 代码中的标准写法：

- `np` 通常代表 NumPy
- `pd` 通常代表 pandas

从模块导入指定对象：

```python
from pathlib import Path

path = Path("data/houses.csv")
print(path.exists())
```

## 10. 文件路径与 pathlib

AI 项目经常要读取数据文件。建议使用 `pathlib`，比手写字符串路径更稳。

```python
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
data_file = project_root / "data" / "houses.csv"

print(data_file)
print(data_file.exists())
```

解释：

- `__file__`：当前 Python 文件路径。
- `resolve()`：转成绝对路径。
- `parents[1]`：向上找一级目录。
- `/`：pathlib 重载的路径拼接写法。

Windows 路径里有反斜杠，初学者容易写错：

```python
path = "C:\new\data.csv"
```

这里 `\n` 会被解释为换行。更稳的写法：

```python
path = r"C:\new\data.csv"
```

或使用 pathlib：

```python
from pathlib import Path
path = Path("C:/new/data.csv")
```

## 11. NumPy：AI 里的数组和矩阵

NumPy 是 AI 学习中最重要的基础库之一。机器学习和深度学习底层大量使用向量、矩阵、张量。

### 11.1 创建数组

创建文件：

```text
src/numpy_demo.py
```

写入：

```python
import numpy as np

a = np.array([1, 2, 3])
b = np.array([10, 20, 30])

print(a)
print(b)
print(a + b)
print(a * b)
```

运行：

```powershell
python src/numpy_demo.py
```

输出：

```text
[1 2 3]
[10 20 30]
[11 22 33]
[10 40 90]
```

注意：`a * b` 是逐元素相乘，不是矩阵乘法。

### 11.2 向量点积

```python
import numpy as np

a = np.array([1, 2, 3])
b = np.array([10, 20, 30])

dot = np.dot(a, b)
print(dot)
```

计算过程：

```text
1*10 + 2*20 + 3*30 = 140
```

点积在 AI 里的典型用途：

- 计算两个向量的相似度
- 神经网络一层中的加权求和
- Embedding 检索中的相关性计算

### 11.3 矩阵

```python
import numpy as np

matrix = np.array([
    [1, 2, 3],
    [4, 5, 6]
])

print(matrix)
print(matrix.shape)
```

输出：

```text
[[1 2 3]
 [4 5 6]]
(2, 3)
```

`shape` 表示维度。这里是 2 行 3 列。

### 11.4 矩阵乘法

```python
import numpy as np

x = np.array([
    [1, 2],
    [3, 4]
])

w = np.array([
    [10],
    [20]
])

y = x @ w
print(y)
```

输出：

```text
[[ 50]
 [110]]
```

计算过程：

```text
第一行：1*10 + 2*20 = 50
第二行：3*10 + 4*20 = 110
```

在神经网络中，很多计算可以抽象为：

```text
输入矩阵 X @ 权重矩阵 W + 偏置 b = 输出
```

### 11.5 常用 NumPy 函数

```python
import numpy as np

data = np.array([1, 2, 3, 4, 5])

print(np.mean(data))    # 平均值
print(np.max(data))     # 最大值
print(np.min(data))     # 最小值
print(np.std(data))     # 标准差
print(np.sum(data))     # 求和
```

### 11.6 随机数

```python
import numpy as np

np.random.seed(42)

values = np.random.rand(5)
print(values)
```

`seed` 用于固定随机结果，便于实验复现。

机器学习中常见随机场景：

- 初始化模型参数
- 切分训练集和测试集
- 随机打乱数据
- Dropout 等训练策略

## 12. pandas：表格数据分析

机器学习项目的输入数据大量来自表格：

- CSV
- Excel
- 数据库查询结果
- 日志导出
- 用户行为数据

pandas 的核心对象是 `DataFrame`，可以理解为内存中的表。

### 12.1 创建示例 CSV

在 `data/houses.csv` 中写入：

```csv
area,rooms,age,price
80,2,10,120
100,3,8,150
120,3,5,180
150,4,3,230
60,1,15,90
```

字段含义：

| 字段 | 含义 |
|---|---|
| area | 房屋面积 |
| rooms | 房间数 |
| age | 房龄 |
| price | 房价，单位可假设为万元 |

### 12.2 读取 CSV

创建文件：

```text
src/pandas_demo.py
```

写入：

```python
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parents[1]
data_file = project_root / "data" / "houses.csv"

df = pd.read_csv(data_file)

print(df)
```

运行：

```powershell
python src/pandas_demo.py
```

### 12.3 查看数据基本信息

```python
print(df.head())
print(df.info())
print(df.describe())
```

常用方法：

| 方法 | 用途 |
|---|---|
| `head()` | 查看前几行 |
| `tail()` | 查看后几行 |
| `info()` | 查看字段、类型、空值 |
| `describe()` | 查看数值列统计信息 |
| `shape` | 查看行数和列数 |
| `columns` | 查看列名 |

### 12.4 选择列

选择单列：

```python
prices = df["price"]
print(prices)
```

选择多列：

```python
features = df[["area", "rooms", "age"]]
print(features)
```

在机器学习里，一般把输入特征记作 `X`，目标值记作 `y`：

```python
X = df[["area", "rooms", "age"]]
y = df["price"]
```

这是一种非常常见的写法。

### 12.5 筛选数据

筛选面积大于 100 的房子：

```python
large_houses = df[df["area"] > 100]
print(large_houses)
```

筛选面积大于 100 且房间数不少于 3 的房子：

```python
result = df[(df["area"] > 100) & (df["rooms"] >= 3)]
print(result)
```

注意 pandas 里多个条件要用 `&`，并且每个条件要加括号。

### 12.6 新增列

```python
df["price_per_area"] = df["price"] / df["area"]
print(df)
```

这就是简单的特征构造。后续机器学习中，特征工程会大量使用类似操作。

### 12.7 缺失值处理

真实数据经常有空值。示例：

```python
import pandas as pd

df = pd.DataFrame({
    "area": [80, 100, None, 150],
    "price": [120, 150, 180, None]
})

print(df.isna())
print(df.isna().sum())
```

删除缺失行：

```python
clean_df = df.dropna()
```

用平均值填充：

```python
df["area"] = df["area"].fillna(df["area"].mean())
```

在真实机器学习项目中，缺失值处理不是机械选择删除或填充，而要结合业务含义。

## 13. Matplotlib：基础可视化

数据可视化的目标不是画漂亮图，而是帮助你理解数据分布、趋势和异常。

创建文件：

```text
src/plot_demo.py
```

写入：

```python
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

project_root = Path(__file__).resolve().parents[1]
data_file = project_root / "data" / "houses.csv"

df = pd.read_csv(data_file)

plt.scatter(df["area"], df["price"])
plt.xlabel("Area")
plt.ylabel("Price")
plt.title("House Area vs Price")
plt.grid(True)
plt.show()
```

运行：

```powershell
python src/plot_demo.py
```

你会看到一个散点图。横轴是面积，纵轴是价格。

如果面积越大，价格通常越高，那么散点会呈现向右上方上升的趋势。这就是机器学习中“特征和目标之间存在关系”的直观表现。

### 13.1 保存图片

```python
output_file = project_root / "data" / "house_area_price.png"
plt.savefig(output_file, dpi=150)
```

完整示例：

```python
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

project_root = Path(__file__).resolve().parents[1]
data_file = project_root / "data" / "houses.csv"
output_file = project_root / "data" / "house_area_price.png"

df = pd.read_csv(data_file)

plt.scatter(df["area"], df["price"])
plt.xlabel("Area")
plt.ylabel("Price")
plt.title("House Area vs Price")
plt.grid(True)
plt.savefig(output_file, dpi=150)
plt.show()
```

## 14. JupyterLab

### 14.1 JupyterLab 是什么

JupyterLab 是一种交互式编程环境，特别适合 AI 学习。

你可以在一个 Notebook 中同时保存：

- 代码
- 运行结果
- 图表
- 文本说明
- 实验记录

它非常适合做：

- 数据探索
- 模型训练实验
- 参数对比
- 学习笔记

### 14.2 启动 JupyterLab

在激活虚拟环境后执行：

```powershell
jupyter lab
```

浏览器会打开一个页面，通常地址类似：

```text
http://localhost:8888/lab
```

如果没有自动打开，可以复制终端输出的链接到浏览器。

### 14.3 创建 Notebook

在 `notebooks` 目录下创建：

```text
01-python-basics.ipynb
```

建议在 Notebook 中按下面结构记录：

```text
# Python 基础实验

## 1. 变量与数据结构
代码单元

## 2. NumPy 数组
代码单元

## 3. pandas 读取 CSV
代码单元

## 4. Matplotlib 绘图
代码单元
```

### 14.4 Notebook 使用建议

Notebook 很方便，但也容易写乱。建议：

1. 每个 Notebook 只服务一个主题。
2. 重要代码最终整理到 `src/` 里的 `.py` 文件。
3. 不要只依赖单元格执行顺序，必要时重启内核从头运行。
4. 数据文件统一放在 `data/`。
5. 图表输出和实验结果要保留说明。

## 15. 构建本课完整练习项目

现在把前面的内容组织成一个小项目。

### 15.1 requirements.txt

项目根目录创建：

```text
requirements.txt
```

内容可以是：

```text
numpy
pandas
matplotlib
jupyterlab
scikit-learn
```

初学阶段可以不固定版本。后续进入项目实战时，再根据需要锁定版本。

### 15.2 data/houses.csv

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

### 15.3 src/house_analysis.py

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

运行：

```powershell
python src/house_analysis.py
```

这个小项目虽然简单，但已经包含了 AI 项目最常见的几个动作：

1. 读取数据。
2. 查看数据结构。
3. 计算统计信息。
4. 构造新特征。
5. 绘制图表。

后续机器学习课程会在这个基础上加入：

1. 切分训练集和测试集。
2. 训练线性回归模型。
3. 预测房价。
4. 评估误差。

## 16. Java 开发者常见误区

### 16.1 误区一：用 Java 思维写 Python

初学者容易把 Python 写得像 Java：

```python
class User:
    def __init__(self):
        self.name = None

user = User()
user.name = "Alice"
```

这不是错，但数据分析场景下，经常直接使用 dict、list、DataFrame 更高效：

```python
user = {"name": "Alice"}
```

### 16.2 误区二：不使用虚拟环境

全局安装一堆包，早晚会遇到版本冲突。每个 AI 项目都应该有自己的 `.venv`。

### 16.3 误区三：只看代码，不看数据

AI 项目里，数据比代码更重要。拿到数据后，第一步不是训练模型，而是：

```python
df.head()
df.info()
df.describe()
df.isna().sum()
```

### 16.4 误区四：认为 Notebook 就是正式项目

Notebook 适合实验，但正式项目代码应该整理成 `.py` 文件或服务代码。

合理流程：

```text
Notebook 探索
  -> Python 脚本整理
  -> 模块化封装
  -> API 服务化
  -> Java 系统集成
```

## 17. 常见问题与排错

### 17.1 python 不是内部或外部命令

原因：

- 未安装 Python。
- 安装时没有加入 PATH。
- 终端没有重启。

处理：

1. 重新安装 Python，勾选 Add python.exe to PATH。
2. 或使用 `py --version` 检查 Python Launcher。
3. 重启 PowerShell。

### 17.2 pip install 很慢

可能是网络问题。可以临时使用镜像：

```powershell
python -m pip install numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

但生产环境或团队项目中，建议统一依赖源策略。

### 17.3 无法激活虚拟环境

错误可能类似：

```text
running scripts is disabled on this system
```

处理：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

然后重新执行：

```powershell
.\.venv\Scripts\Activate.ps1
```

### 17.4 ModuleNotFoundError

错误：

```text
ModuleNotFoundError: No module named 'pandas'
```

常见原因：

- 没有安装 pandas。
- 安装到了全局 Python，不在当前虚拟环境。
- IDE 选择了错误解释器。

处理：

```powershell
where python
python -m pip install pandas
```

并检查 VS Code / PyCharm 使用的解释器是否指向 `.venv`。

### 17.5 读取 CSV 路径错误

错误：

```text
FileNotFoundError
```

处理：

1. 打印当前工作目录：

   ```python
   from pathlib import Path
   print(Path.cwd())
   ```

2. 使用基于 `__file__` 的绝对路径定位项目文件。

## 18. 本课实践任务

### 任务 1：完成环境搭建

要求：

1. 安装 Python。
2. 创建 `ai-study-lab` 项目目录。
3. 创建并激活 `.venv`。
4. 安装 `numpy pandas matplotlib jupyterlab scikit-learn`。
5. 生成 `requirements.txt`。

验收命令：

```powershell
python --version
python -m pip --version
python -m pip list
```

### 任务 2：完成 Python 基础脚本

创建：

```text
src/hello_ai.py
```

要求：

1. 定义你的姓名、学习目标、当前阶段。
2. 使用 f-string 输出一句学习声明。
3. 至少使用一次 list。
4. 至少使用一次 dict。
5. 至少定义一个函数。

### 任务 3：完成房价数据分析

创建：

```text
data/houses.csv
src/house_analysis.py
```

要求：

1. 读取 CSV。
2. 输出前 5 行。
3. 输出统计信息。
4. 新增 `price_per_area` 字段。
5. 绘制面积和价格的散点图。
6. 保存图片到 `data/house_area_price.png`。

### 任务 4：完成 Notebook 实验

创建：

```text
notebooks/01-python-basics.ipynb
```

要求：

1. 记录 Python 基础语法。
2. 记录 NumPy 数组实验。
3. 记录 pandas 读取 CSV 实验。
4. 记录 Matplotlib 绘图实验。

## 19. 自测题

### 19.1 选择题

1. Python 虚拟环境的主要作用是什么？

   A. 提高 CPU 性能  
   B. 隔离不同项目的依赖  
   C. 自动训练模型  
   D. 替代 Git

2. pandas 中常用于表示二维表格数据的对象是：

   A. ArrayList  
   B. HashMap  
   C. DataFrame  
   D. Thread

3. NumPy 中查看数组维度通常使用：

   A. `array.length()`  
   B. `array.shape`  
   C. `array.size()`  
   D. `array.dimension()`

4. Python 中导入 NumPy 的常见写法是：

   A. `import numpy as np`  
   B. `import numpy as pd`  
   C. `from numpy import pandas`  
   D. `include numpy`

5. 在机器学习中，通常用 `X` 表示：

   A. 输入特征  
   B. 目标标签  
   C. 错误日志  
   D. 数据库连接

答案：

1. B
2. C
3. B
4. A
5. A

### 19.2 简答题

1. 为什么 AI 学习中推荐使用 Python，而 Java 更适合做工程化落地？
2. `.venv`、`requirements.txt`、`pip` 分别解决什么问题？
3. NumPy 的数组和 Python 原生 list 有什么不同？
4. pandas 的 `head()`、`info()`、`describe()` 分别适合什么时候使用？
5. 为什么数据分析时要先看数据分布，再考虑训练模型？

### 19.3 编程题

给定学生成绩数据：

```csv
name,math,english,programming
Alice,90,85,95
Bob,70,80,75
Cindy,88,92,90
David,60,65,70
```

请完成：

1. 使用 pandas 读取数据。
2. 新增 `average_score` 字段。
3. 筛选平均分大于 85 的学生。
4. 绘制每个学生的平均分柱状图。

参考思路：

```python
df["average_score"] = df[["math", "english", "programming"]].mean(axis=1)
top_students = df[df["average_score"] > 85]
```

## 20. 阶段验收标准

完成本课后，你应该能做到：

1. 能独立创建 Python 虚拟环境。
2. 能安装和导出 Python 项目依赖。
3. 能读懂基础 Python 脚本。
4. 能写出函数、列表、字典、循环、条件语句。
5. 能使用 NumPy 完成向量和矩阵基础计算。
6. 能使用 pandas 读取 CSV、查看数据、筛选数据、新增字段。
7. 能使用 Matplotlib 绘制简单图表。
8. 能用 JupyterLab 做交互式实验。
9. 能完成一个小型数据分析脚本。

## 21. 本课使用的信息源

- Python 官方教程：Python 语法、数据结构、模块基础。
- Python venv 官方文档：虚拟环境创建与激活方式。
- pip 官方文档：包安装与依赖管理。
- JupyterLab 官方文档：Notebook / Lab 安装与启动方式。
- NumPy 官方用户指南：数组、向量、矩阵和数值计算。
- pandas 官方用户指南：DataFrame、CSV 读取、数据选择和分析。
- Matplotlib 官方快速入门：基础绘图流程。
- scikit-learn 官方安装文档：后续机器学习环境依赖准备。
