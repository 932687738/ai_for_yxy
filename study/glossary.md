# AI 与机器学习术语表

本文件用于集中记录课程中出现的重要专有名词。后续章节会持续补充。

## 第 1 课相关术语

### Python

AI 学习中最常用的实验和数据处理语言。Java 开发者不一定要转 Python 后端，但需要能阅读和修改 Python AI 示例代码。

### Interpreter

解释器。执行 Python 代码的程序。环境问题经常来自解释器选择错误。

### Script

脚本。可执行的 `.py` 文件，适合沉淀正式逻辑。

### REPL

交互式命令环境，适合快速验证简单表达式。

### Jupyter Notebook

交互式实验文档，适合代码、结果、图表和说明放在一起。

### JupyterLab

Jupyter 的完整工作界面，适合管理 Notebook、文件和实验。

### Kernel

Notebook 背后执行代码的运行环境。Notebook 导包是否成功取决于 Kernel 对应环境是否安装依赖。

### Virtual Environment / venv

虚拟环境。为单个 Python 项目隔离依赖，避免不同项目包版本冲突。

### pip

Python 包管理工具，用于安装、查看和导出依赖。

### requirements.txt

Python 项目依赖清单，用于记录和恢复项目依赖。

### Package

包。由一个或多个模块组成的可导入代码集合。

### Module

模块。通常是一个 `.py` 文件。

### NumPy

Python 数值计算基础库，AI 中常用于理解向量、矩阵、张量和批量计算。

### pandas

Python 表格数据分析库，常用于读取 CSV、清洗数据、构造特征。

### DataFrame

pandas 中的二维表格结构，可类比数据库查询结果或 Excel 表。

### Series

pandas 中的一维数据结构，通常表示 DataFrame 的一列。

### Matplotlib

Python 基础绘图库，用于观察数据分布、趋势和训练结果。

### Working Directory

工作目录。程序运行时的当前目录，很多文件路径错误都与它有关。

### pathlib

Python 标准库中的路径处理工具，比手写字符串路径更稳。

## 第 2 课相关术语

### Scalar

标量。一个单独的数，例如学习率、损失值、概率。

### Vector

向量。一组有顺序的数，常用于表示一个样本、一个用户、一段文本的 Embedding。

### Dimension

维度。向量中数字的个数。

### Matrix

矩阵。二维数字表格，机器学习中常表示一批样本的特征。

### Tensor

张量。多维数组，深度学习框架中用于表示数据、参数和中间结果。

### shape

数组或张量的形状。AI 代码调试中最重要的信息之一。

### Dot Product

点积。两个向量对应元素相乘后求和，常用于线性模型、相似度和神经网络计算。

### Weight

权重。模型中表示特征影响强度的参数。

### Bias

偏置。模型中的常数项，可理解为预测公式的基础偏移。

### Norm

范数。向量长度，常用于距离、归一化和相似度计算。

### Euclidean Distance

欧氏距离。衡量两个向量在空间中的直线距离。

### Cosine Similarity

余弦相似度。衡量两个向量方向是否接近，是语义搜索和 RAG 的基础之一。

### Embedding

嵌入向量。把文本、图片、商品、用户等对象转换成可计算的向量表示。

### Probability

概率。描述不确定性的数值。

### Conditional Probability

条件概率。在某个条件成立时，另一个事件发生的概率。

### Random Variable

随机变量。结果不确定、需要用概率描述的变量。

### Mean

均值。描述数据平均水平。

### Variance

方差。描述数据波动程度。

### Standard Deviation

标准差。方差的平方根，用于描述数据离均值的典型距离。

### Distribution

分布。描述数据整体出现形态。

### Derivative

导数。描述变化率，在模型训练中用于判断参数变化对损失的影响。

### Gradient

梯度。多个参数导数组成的向量，指示参数更新方向。

### Loss Function

损失函数。衡量模型预测错误程度的函数。

### MSE

均方误差。回归任务常用损失函数，对大错误更敏感。

### Learning Rate

学习率。控制每次参数更新步长的超参数。

### Gradient Descent

梯度下降。沿着降低损失的方向迭代更新参数的优化方法。

## 第 14 课相关术语

### AI Engineering

AI 工程化。把模型能力稳定、可控、可观测地接入真实业务系统的工程实践。

### Streaming

流式输出。模型边生成边返回内容的响应方式。

### Authorization

权限控制。限制用户能访问的数据、工具、功能和日志。

### Audit Log

审计日志。记录 AI 调用、检索、工具调用、成本和错误的日志。

### Cost Control

成本控制。通过限流、缓存、模型分级、token 限制等方式控制 AI 调用费用。

### Rate Limit

限流。限制请求频率、并发或 token 使用量。

### Retry and Backoff

重试与退避。失败后按策略延迟重试，避免请求风暴。

### Observability

可观测性。通过日志、指标和 Trace 监控 AI 系统运行状态。

### Guardrails

护栏。输入过滤、输出校验、权限、人工确认等安全保护机制。

## 第 13 课相关术语

### LangChain4j

面向 Java 的大模型应用开发框架，提供模型、AI Services、工具、记忆、RAG、Embedding 等抽象。

### StreamingChatModel

支持流式输出的聊天模型抽象。

### AI Services

LangChain4j 的高级抽象，用 Java 接口定义 AI 服务并由框架生成实现。

### SystemMessage

定义助手角色、规则和行为边界的系统消息。

### UserMessage

表示用户输入的消息。

### ChatMemory

对话记忆，用于保存多轮对话上下文。

### MessageWindowChatMemory

按消息数量保留最近对话的记忆实现。

### EmbeddingStore

LangChain4j 中保存向量、文本和 metadata 的向量存储抽象。

### ContentRetriever

根据用户问题检索相关内容的组件，是 RAG 的关键部分。

### RetrievalAugmentor

把检索结果增强到模型输入中的组件。

### DocumentSplitter

文档切分器，把长文档拆成适合检索的片段。

## 第 12 课相关术语

### Spring AI

Spring 生态中的 AI 应用框架，用于连接模型、Prompt、Embedding、VectorStore、工具调用和 RAG。

### Chat Model

聊天模型抽象，代表可接收对话消息并返回响应的模型。

### ChatClient

Spring AI 中用于构造和执行聊天模型调用的高级客户端。

### PromptTemplate

提示词模板，用于把变量填入稳定的 Prompt 结构。

### Advisor

Spring AI 中增强 ChatClient 调用过程的组件，可用于 RAG、记忆、日志等。

### EmbeddingModel

Spring AI 中用于生成文本向量的模型抽象。

### VectorStore

Spring AI 中的向量存储抽象，用于写入和检索向量化文档。

### Document

Spring AI 中表示文本内容和 metadata 的对象。

### ETL Pipeline

文档入库流程：Extract 读取、Transform 转换切分、Load 写入向量库。

### ToolCallback

Spring AI 中工具回调抽象，用于把外部函数或方法暴露给模型调用。

## 第 11 课相关术语

### Function Calling

函数调用。让模型按照函数 schema 生成结构化调用请求的机制。

### Tool Calling

工具调用。模型提出调用外部工具的意图，应用执行工具并把结果返回模型。

### Tool

工具。提供给模型可选择的外部能力，例如 Java 方法、HTTP API、数据库查询。

### Tool Schema

工具参数结构定义，是模型和业务系统之间的参数契约。

### Tool Call

模型生成的工具调用请求，通常包含工具名、参数和调用 ID。

### Tool Call Output

应用执行工具后返回给模型的结果。

### tool_choice

控制模型是否调用工具或调用哪个工具的策略。

### Strict Mode

严格模式。要求模型严格遵守工具参数 schema。

### Agent

由模型、工具、状态和控制循环组成的系统，可多步完成任务。

### Agent Loop

Agent 的执行循环：观察、决策、调用工具、获取结果、继续或停止。

### Planning

规划。模型把复杂任务拆解为多个步骤。

### Memory

记忆。保存对话历史、任务状态、用户偏好或工具执行记录的机制。

### Observation

观察。工具执行后的结果或环境反馈。

### Guardrails

保护机制，包括权限、参数校验、调用次数限制、人工确认和审计。

### Human-in-the-loop

人在回路。关键操作前需要人工确认。

### MCP

Model Context Protocol，用于以统一协议暴露外部工具和上下文。

## 第 10 课相关术语

### RAG

检索增强生成。先检索外部知识，再让大模型基于检索结果生成回答。

### Knowledge Base

知识库。RAG 系统中可检索的数据集合，例如制度、手册、FAQ、项目文档。

### Document Loader

文档加载器。从文件、网页、数据库等来源读取原始内容的组件。

### Text Splitter

文本切分器。把长文档切成适合检索和上下文拼装的 chunk。

### Retriever

检索器。根据用户问题返回相关文档片段的组件。

### Context

上下文。送给大模型参考的检索资料、用户问题、回答规则等内容。

### Grounded Answer

基于资料的回答。回答内容必须能从提供资料中找到依据。

### Citation

引用来源。回答中标注依据文档、章节、页码或 chunk 来源。

### Query Rewrite

查询改写。把用户原始问题改写成更适合检索的问题。

### Multi-query Retrieval

多查询检索。把一个问题扩展为多个查询，从多个角度召回资料。

### Refusal / No Answer

拒答或无答案。当资料不足时明确说明无法确认，而不是猜测。

### Permission Filtering

权限过滤。根据用户权限限制可检索文档范围。

### Freshness

知识新鲜度。知识库内容更新后，RAG 系统能否使用最新资料。

### RAG Evaluation

RAG 评估。分别评估检索是否命中正确资料，以及生成回答是否正确基于资料。

## 第 9 课相关术语

### Embedding Model

嵌入模型。把文本、图片等输入转换成向量表示的模型。

### Semantic Search

语义搜索。根据语义相似度检索内容，而不是只匹配关键词。

### Keyword Search

关键词搜索。根据词项匹配查找内容。

### Similarity

相似度。衡量两个向量或对象接近程度的指标。

### Vector Database

向量数据库。用于存储向量并执行相似度检索的数据库。

### Collection

向量数据库中组织向量数据的集合，可类比关系数据库中的表。

### Metadata / Payload

元数据。和向量一起存储的业务信息，用于过滤、权限、展示和溯源。

### Chunk

文档切分后的片段，是 RAG 检索和入库的基本单位。

### Chunking Strategy

切分策略。决定如何把文档拆成适合检索的片段。

### Overlap

重叠。相邻 chunk 之间保留的重复内容，用于防止上下文断裂。

### Top-k

返回相似度最高的前 k 条结果。

### ANN

近似最近邻搜索，用于在大量向量中高效查找相似向量。

### HNSW

常见 ANN 索引算法，通过图结构加速向量检索。

### IVFFlat

常见向量索引方式，通过聚类分区减少搜索范围。

### pgvector

PostgreSQL 向量扩展，使 PostgreSQL 支持向量存储和相似度检索。

### Hybrid Search

混合检索。结合关键词搜索和向量搜索的检索方式。

### Rerank

重排序。对初步召回结果再次排序，提高最终上下文质量。

### Recall@k

检索评估指标，衡量正确结果是否出现在前 k 个结果中。

## 第 8 课相关术语

### LLM

大语言模型。基于大规模文本和深度学习训练，能够根据上下文理解和生成文本的模型。

### Foundation Model

基础模型。具备通用能力，可通过 Prompt、RAG、微调、工具调用适配不同任务的大模型。

### Generative AI

生成式 AI。能够生成文本、图片、音频、视频、代码等内容的 AI。

### Tokenization

分词或切词。把原始文本转换成 token 序列的过程。

### Token ID

Token 在模型词表中的数字编号。

### Context Window

上下文窗口。模型一次请求中能处理的 token 总量上限。

### Prompt

提示词。提供给模型的任务指令、上下文、约束和输出要求。

### Prompt Engineering

提示词工程。设计、优化和评估 Prompt，使模型稳定完成任务的方法。

### System Message

系统消息。用于设置模型全局行为、角色和边界的高优先级指令。

### Developer Message

开发者消息。用于表达应用开发者对任务流程、输出格式、工具使用等稳定规则的指令。

### User Message

用户消息。用户当前输入的请求或问题。

### Few-shot Prompting

少样本提示。在 Prompt 中提供若干输入输出示例，帮助模型理解任务和格式。

### Zero-shot Prompting

零样本提示。不提供示例，直接要求模型完成任务。

### Structured Output

结构化输出。让模型按 JSON、表格、固定字段等格式输出，便于系统解析。

### Hallucination

幻觉。模型生成看似合理但不真实或无法由上下文支持的内容。

### Grounding

让模型基于指定资料、数据或工具结果回答，以降低幻觉。

### Prompt Injection

提示词注入。用户输入中包含恶意或冲突指令，试图覆盖系统规则。

### Temperature

控制模型输出随机性的参数，值越高通常输出越发散。

### Top-p

采样控制参数，限制模型从累计概率前 p 的候选 token 中采样。

### Max Output Tokens

最大输出 token 数，限制模型回答长度。

## 第 7 课相关术语

### CNN

卷积神经网络，擅长处理图像等局部空间结构数据。

### Convolution

卷积。使用卷积核在输入上滑动以提取局部特征。

### Kernel / Filter

卷积核。CNN 中可学习的局部特征检测器。

### Feature Map

特征图。卷积层输出的局部特征响应。

### Pooling

池化。压缩特征图大小并保留重要信息的操作。

### RNN

循环神经网络，擅长处理序列数据。

### Hidden State

隐藏状态。RNN 中用于传递历史信息的向量。

### LSTM

长短期记忆网络，使用门控机制缓解普通 RNN 长距离依赖问题。

### GRU

门控循环单元，RNN 的一种门控改进结构。

### Transformer

基于 Attention 的序列建模结构，是现代大模型的核心架构。

### Attention

注意力机制。让模型在处理当前位置时动态关注其他位置。

### Self-Attention

自注意力。序列内部 token 之间互相关注的机制。

### Token

模型处理文本的基本单位，可能是词、子词、字符片段或标点。

### Positional Encoding

位置编码。向 Transformer 提供 token 顺序信息的机制。

### Encoder

编码器。用于理解输入并生成表示的结构。

### Decoder

解码器。用于根据已有上下文生成输出的结构。

## 第 6 课相关术语

### Deep Learning

深度学习。使用多层神经网络从数据中学习复杂表示和规律。

### Neural Network

神经网络。由多层参数化变换组成的模型。

### Tensor

张量。PyTorch 中的核心数据结构，可表示标量、向量、矩阵和高维数组。

### Batch

批次。一次送入模型训练或推理的一组样本。

### Forward Pass

前向传播。输入经过模型得到预测结果的过程。

### Backward Pass

反向传播。根据损失计算模型参数梯度的过程。

### Autograd

PyTorch 自动求导机制，根据计算图自动计算梯度。

### Computational Graph

计算图。记录张量运算依赖关系的数据结构，用于自动求导。

### Optimizer

优化器。根据梯度更新模型参数的组件，例如 SGD、Adam。

### nn.Module

PyTorch 中定义神经网络模型的基础类。

### Activation Function

激活函数。为神经网络引入非线性的函数，例如 ReLU、Sigmoid。

### Epoch

训练轮次。完整遍历训练集一次称为一个 epoch。

### state_dict

PyTorch 中保存模型参数的字典结构。

## 第 5 课相关术语

### Unsupervised Learning

无监督学习。训练数据没有标签，模型根据特征发现数据结构。

### Clustering

聚类。把相似样本自动分到同一组。

### KMeans

常见聚类算法，需要预先指定簇数量 K，通过迭代更新簇中心完成聚类。

### DBSCAN

基于密度的聚类算法，可以发现不规则形状的簇和噪声点。

### Dimensionality Reduction

降维。把高维数据压缩到低维表示。

### PCA

主成分分析。常见线性降维方法，通过主成分保留数据主要变化方向。

### Principal Component

主成分。PCA 生成的新特征方向，不等同于原始字段。

### Explained Variance Ratio

解释方差比例。PCA 中每个主成分解释原始数据变化的比例。

### Feature Engineering

特征工程。把原始数据转换成更适合模型学习的特征。

### Feature Selection

特征选择。从已有特征中挑选一部分特征。

### Feature Extraction

特征提取。从原始数据中生成新的特征表示。

### Preprocessing

预处理。建模前对数据做清洗、编码、缩放等转换。

### Standardization

标准化。把特征转换为均值约为 0、标准差约为 1。

### Normalization

归一化。把数据缩放到固定范围，常见如 0 到 1。

### One-Hot Encoding

独热编码。把无序类别转换成多个 0/1 特征。

### Silhouette Score

轮廓系数。用于评估聚类紧凑度和分离度的指标。

## 第 4 课相关术语

### Supervised Learning

监督学习。使用带标签的数据训练模型，让模型学习输入特征到正确答案之间的映射关系。

### Regression

回归。预测连续数值的监督学习任务，例如房价、销量、配送时长。

### Classification

分类。预测离散类别的监督学习任务，例如是否流失、工单类别、风险等级。

### Binary Classification

二分类。只有两个类别的分类任务，例如流失/未流失、欺诈/正常。

### Multiclass Classification

多分类。多个类别中选择一个类别的分类任务，例如工单类型分类。

### Multilabel Classification

多标签分类。一个样本可以同时属于多个标签，例如一篇文章同时属于 Java、AI、后端。

### Linear Regression

线性回归。通过特征加权求和预测连续数值的回归模型。

### Logistic Regression

逻辑回归。常用于分类的线性模型，通常输出正例概率。

### Sigmoid

Sigmoid 函数。把任意实数压缩到 0 到 1 之间，常用于逻辑回归中将线性分数转换为概率。

### Decision Tree

决策树。通过一系列条件判断进行预测的模型，可用于回归和分类。

### DecisionTreeClassifier

scikit-learn 中的决策树分类器，用于分类任务。

### DecisionTreeRegressor

scikit-learn 中的决策树回归器，用于回归任务。

### Accuracy

准确率。预测正确的样本数占总样本数的比例。类别不平衡时可能误导。

### ROC-AUC

衡量分类模型区分正负样本能力的指标，不依赖单一固定阈值。

### Probability Calibration

概率校准。检查模型输出概率是否和真实发生频率一致。

### Threshold

分类阈值。把预测概率转换成类别或业务动作的分界线。

## 第 3 课相关术语

### Machine Learning

机器学习。让程序从数据中学习规律，而不是完全由程序员手写规则。

### Sample / Instance

样本。一条训练数据。例如房价预测中的一套房子，用户流失预测中的一个用户。

### Feature

特征。描述样本的输入变量。例如面积、房间数、房龄、距离地铁距离。

### Label / Target

标签或目标值。监督学习中希望模型学习和预测的答案。例如房价、是否流失。

### Dataset

数据集。样本集合。通常包含特征和标签。

### Training Set

训练集。用于让模型学习规律的数据。

### Validation Set

验证集。用于调参、选择模型、比较方案的数据。它不应该用于最终报告模型效果。

### Test Set

测试集。用于最终评估模型泛化能力的数据。原则上应尽量少碰，不能反复用它调参。

### Generalization

泛化能力。模型在没见过的新数据上表现良好的能力。

### Overfitting

过拟合。模型对训练数据表现很好，但对新数据表现差，说明它可能记住了训练数据中的细节和噪声。

### Underfitting

欠拟合。模型过于简单，连训练数据中的基本规律都没有学好。

### Regression

回归。预测连续数值的任务。例如预测房价、销量、温度。

### Classification

分类。预测离散类别的任务。例如是否流失、是否垃圾邮件、图片类别。

### Binary Classification

二分类。只有两个类别的分类任务。例如是/否、流失/未流失、垃圾邮件/正常邮件。

### Multiclass Classification

多分类。多个类别中选一个。例如工单分类为物流、支付、售后、账号等。

### Model

模型。机器学习算法从数据中学习到的规则或函数。

### Algorithm

算法。用于训练模型的方法。例如线性回归、逻辑回归、决策树、随机森林。

### Parameter

参数。模型从训练数据中学习得到的值。例如线性回归中的权重和截距。

### Hyperparameter

超参数。训练前由人设置的配置，不是模型自己从数据中学出来的。例如决策树最大深度、学习率、KNN 的 K。

### Estimator

scikit-learn 中的估计器。通常指实现了 `fit` 方法的对象，例如 `LinearRegression()`。

### Transformer

scikit-learn 中的转换器。通常实现 `fit` 和 `transform`，用于数据预处理，例如 `StandardScaler()`。

### Predictor

预测器。通常实现 `predict`，可以对新数据输出预测结果。

### fit

训练或拟合。让模型或预处理器从数据中学习必要信息。

### transform

转换。使用已经学到的规则处理数据。例如使用训练集均值和标准差标准化测试集。

### fit_transform

先 `fit` 再 `transform` 的组合，常用于训练集预处理。

### predict

预测。使用训练好的模型对新样本输出结果。

### score

评分。使用某种默认指标评价模型效果。

### Pipeline

流水线。把预处理步骤和模型串起来，形成一个整体训练和预测流程。

### Cross-validation

交叉验证。把数据分成多个折，多次训练和评估，用于更稳定地估计模型效果。

### Data Leakage

数据泄漏。训练时使用了真实预测场景中不应该知道的信息，导致离线评估虚高，上线表现变差。

### Metric

评估指标。用于量化模型效果的数值，例如 MAE、RMSE、Accuracy、Precision、Recall。

### MAE

平均绝对误差。回归指标，表示预测值与真实值绝对误差的平均值。

### MSE

均方误差。回归指标，先对误差平方再求平均，对大误差更敏感。

### RMSE

均方根误差。MSE 开平方，单位和目标值一致。

### R2

决定系数。衡量模型解释目标变量波动的能力，通常越接近 1 越好。

### Bias

偏差。模型假设过于简单导致的系统性错误。高偏差常对应欠拟合。

### Variance

方差。模型对训练数据变化过于敏感。高方差常对应过拟合。

### Feature Engineering

特征工程。根据业务和数据构造、选择、转换特征，提高模型效果。

### Baseline

基线模型。第一个简单可比较的模型，用来判断后续复杂模型是否真的带来提升。

### Inference

推理。使用训练好的模型对新数据进行预测。

### Model Serving

模型服务化。把模型封装成可被业务系统调用的服务。

### Dummy Model

哑模型或基线模型。不真正学习复杂规律，只用简单策略预测，例如回归中永远预测平均值，分类中永远预测最多类别。用于判断真正模型是否比简单规则更好。

### Grid Search

网格搜索。给定一组超参数候选值，穷举所有组合并通过交叉验证选择较好的组合。

### Random Search

随机搜索。从给定超参数空间中随机采样若干组合，通常比网格搜索更节省计算资源。

### Learning Curve

学习曲线。观察训练样本数量变化时，训练分数和验证分数如何变化，用于判断模型是否需要更多数据或更复杂模型。

### Validation Curve

验证曲线。观察某个超参数变化时，训练分数和验证分数如何变化，用于分析欠拟合或过拟合。

### Confusion Matrix

混淆矩阵。分类任务中统计真实类别和预测类别对应关系的表格，用于分析模型把哪些类别预测错了。

### Precision

精确率。模型预测为正例的样本中，有多少确实是正例。

### Recall

召回率。真实正例中，有多少被模型找出来。

### F1 Score

F1 分数。Precision 和 Recall 的调和平均，用于综合衡量二者。

### Class Imbalance

类别不平衡。分类任务中某些类别样本远多于其他类别，例如欺诈检测中正常订单远多于欺诈订单。

### Threshold

阈值。把概率转换成类别的分界线。例如流失概率大于 0.7 才判定为高风险。

### Data Drift

数据漂移。线上输入数据分布和训练数据分布发生变化。

### Concept Drift

概念漂移。输入和目标之间的关系发生变化，例如用户行为规则改变导致旧模型失效。
