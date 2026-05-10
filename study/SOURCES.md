# 信息源与资料记录

本文件记录课程编写过程中使用过的信息源。后续每生成一课，会继续追加资料来源。

## 已使用信息源

### 第 0 课：AI 全局认知与学习定位

- Google Machine Learning Crash Course：用于校准机器学习基础概念与学习路径。
  - https://developers.google.com/machine-learning/crash-course
- DeepLearning.AI Machine Learning Specialization：用于校准传统机器学习学习顺序。
  - https://www.deeplearning.ai/specializations/machine-learning/
- PyTorch Tutorials：用于校准深度学习与 PyTorch 后续课程安排。
  - https://docs.pytorch.org/tutorials/
- Hugging Face LLM Course：用于校准大模型、Transformer、应用开发学习顺序。
  - https://huggingface.co/learn/llm-course
- OpenAI API Documentation：用于校准大模型 API、文本生成、Embedding、Tool Calling 等应用主题。
  - https://platform.openai.com/docs
- Spring AI Reference Documentation：用于校准 Java/Spring 场景下的 AI 应用开发内容。
  - https://docs.spring.io/spring-ai/reference/
- LangChain4j Documentation：用于校准 Java 大模型应用框架内容。
  - https://docs.langchain4j.dev/
- pgvector GitHub README：用于校准 PostgreSQL 向量检索与向量数据库内容。
  - https://github.com/pgvector/pgvector
- Docker Documentation：用于后续工程化与项目部署章节。
  - https://docs.docker.com/

### 第 1 课：Python 与 AI 开发环境

- Python 官方教程：用于校准 Python 基础语法、数据结构、模块、虚拟环境学习内容。
  - https://docs.python.org/3/tutorial/
- Python venv 官方文档：用于校准虚拟环境创建、激活和依赖隔离说明。
  - https://docs.python.org/3/library/venv.html
- pip 官方文档：用于校准 Python 包安装、依赖管理和常见命令。
  - https://pip.pypa.io/en/stable/
- JupyterLab 官方文档：用于校准 Notebook / JupyterLab 安装与启动方式。
  - https://jupyterlab.readthedocs.io/
- NumPy 官方用户指南：用于校准数组、向量、矩阵和基础数值计算示例。
  - https://numpy.org/doc/stable/user/
- pandas 官方用户指南：用于校准 DataFrame、CSV 读取、数据筛选和基础分析示例。
  - https://pandas.pydata.org/docs/user_guide/
- Matplotlib 官方快速入门：用于校准基础图表绘制示例。
  - https://matplotlib.org/stable/users/explain/quick_start.html
- scikit-learn 官方安装文档：用于校准后续机器学习依赖安装。
  - https://scikit-learn.org/stable/install.html

### 第 2 课：AI 数学基础：向量、矩阵、概率与导数

- MIT OpenCourseWare Linear Algebra：用于校准线性代数核心概念，如向量、矩阵、矩阵乘法、线性变换。
  - https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/
- Khan Academy Linear Algebra：用于校准初学者友好的向量、矩阵、线性代数学习顺序。
  - https://www.khanacademy.org/math/linear-algebra
- Khan Academy Statistics and Probability：用于校准概率、随机变量、均值、方差、分布等基础内容。
  - https://www.khanacademy.org/math/statistics-probability
- Khan Academy Calculus / Derivatives：用于校准导数、斜率、变化率等基础概念。
  - https://www.khanacademy.org/math/calculus-1
- NumPy Linear Algebra 文档：用于校准 NumPy 中向量、矩阵、范数、矩阵运算的代码写法。
  - https://numpy.org/doc/stable/reference/routines.linalg.html
- Google Machine Learning Crash Course：用于校准损失函数、梯度下降和机器学习训练过程中的数学解释。
  - https://developers.google.com/machine-learning/crash-course

### 第 3 课：机器学习完整流程

- scikit-learn User Guide：用于校准机器学习任务类型、估计器接口、模型训练和评估整体流程。
  - https://scikit-learn.org/stable/user_guide.html
- scikit-learn train_test_split 文档：用于校准训练集、测试集拆分代码。
  - https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html
- scikit-learn Model Evaluation 文档：用于校准回归、分类评估指标。
  - https://scikit-learn.org/stable/modules/model_evaluation.html
- scikit-learn Cross-validation 文档：用于校准交叉验证和模型泛化能力评估。
  - https://scikit-learn.org/stable/modules/cross_validation.html
- scikit-learn Pipeline 文档：用于校准数据预处理和模型训练流水线。
  - https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html
- scikit-learn LinearRegression 文档：用于校准线性回归模型接口。
  - https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html
- scikit-learn StandardScaler 文档：用于校准特征标准化处理。
  - https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html
- scikit-learn Glossary：用于补充 estimator、transformer、predictor、fit、transform、score 等专有名词解释。
  - https://scikit-learn.org/stable/glossary.html
- Google Machine Learning Crash Course - Datasets, generalization, and overfitting：用于补充泛化、过拟合和数据集划分相关解释。
  - https://developers.google.com/machine-learning/crash-course/overfitting
- Google Machine Learning Glossary - ML Fundamentals：用于补充机器学习基础术语解释。
  - https://developers.google.com/machine-learning/glossary/fundamentals
- scikit-learn Common pitfalls and recommended practices：用于补充预处理不一致、数据泄漏、Pipeline 推荐实践。
  - https://scikit-learn.org/stable/common_pitfalls.html
- scikit-learn Dummy estimators：用于补充基线模型、DummyRegressor、DummyClassifier。
  - https://scikit-learn.org/stable/modules/model_evaluation.html#dummy-estimators
- scikit-learn GridSearchCV / RandomizedSearchCV：用于补充超参数搜索和模型选择流程。
  - https://scikit-learn.org/stable/modules/grid_search.html
- scikit-learn Validation curves and learning curves：用于补充学习曲线、验证曲线、训练集大小与泛化表现分析。
  - https://scikit-learn.org/stable/modules/learning_curve.html
- scikit-learn metrics API：用于补充混淆矩阵、分类报告、precision、recall、F1 等分类评估指标。
  - https://scikit-learn.org/stable/api/sklearn.metrics.html
- imbalanced-learn Documentation：用于补充分类样本不平衡问题的扩展处理方向。
  - https://imbalanced-learn.org/stable/

### 第 4 课：监督学习：回归与分类

- scikit-learn Supervised Learning User Guide：用于校准监督学习、回归、分类、线性模型、树模型等内容。
  - https://scikit-learn.org/stable/supervised_learning.html
- scikit-learn LinearRegression 文档：用于校准线性回归模型、参数、属性和使用方式。
  - https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html
- scikit-learn LogisticRegression 文档：用于校准逻辑回归分类模型、概率输出和参数说明。
  - https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
- scikit-learn DecisionTreeClassifier 文档：用于校准决策树分类器概念和使用方式。
  - https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html
- scikit-learn DecisionTreeRegressor 文档：用于校准决策树回归器概念和使用方式。
  - https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeRegressor.html
- scikit-learn Classification Metrics 文档：用于校准 Accuracy、Precision、Recall、F1、classification_report、confusion_matrix。
  - https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics
- scikit-learn Regression Metrics 文档：用于校准 MAE、MSE、RMSE、R2 等回归指标。
  - https://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics
- Google Machine Learning Crash Course：用于补充线性回归、逻辑回归、分类阈值、混淆矩阵等基础解释。
  - https://developers.google.com/machine-learning/crash-course

### 第 5 课：无监督学习、特征工程与模型评估

- scikit-learn Clustering User Guide：用于校准聚类、KMeans、层次聚类、DBSCAN 等无监督学习内容。
  - https://scikit-learn.org/stable/modules/clustering.html
- scikit-learn Decomposition User Guide：用于校准 PCA、降维、矩阵分解等内容。
  - https://scikit-learn.org/stable/modules/decomposition.html
- scikit-learn PCA 文档：用于校准 PCA 参数、解释方差、transform 等概念。
  - https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
- scikit-learn Preprocessing User Guide：用于校准标准化、归一化、编码、离散化等预处理内容。
  - https://scikit-learn.org/stable/modules/preprocessing.html
- scikit-learn Feature Extraction User Guide：用于校准文本、图像等非结构化数据转数值特征的概念。
  - https://scikit-learn.org/stable/modules/feature_extraction.html
- scikit-learn Model Selection and Evaluation：用于校准监督学习和无监督学习中的评估框架。
  - https://scikit-learn.org/stable/model_selection.html

### 第 6 课：深度学习与 PyTorch 基础

- PyTorch Beginner Basics：用于校准张量、数据集、自动求导、优化、保存加载模型等入门结构。
  - https://docs.pytorch.org/tutorials/beginner/basics/intro.html
- PyTorch Tensors Tutorial：用于校准 Tensor、shape、dtype、device、张量运算。
  - https://docs.pytorch.org/tutorials/beginner/basics/tensorqs_tutorial.html
- PyTorch Autograd Tutorial：用于校准自动求导、计算图、梯度等概念。
  - https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html
- PyTorch Build Model Tutorial：用于校准 `torch.nn.Module`、层、前向传播等内容。
  - https://docs.pytorch.org/tutorials/beginner/basics/buildmodel_tutorial.html
- PyTorch Optimization Tutorial：用于校准损失函数、优化器、训练循环。
  - https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
- PyTorch Saving and Loading Models：用于校准模型保存、加载和 state_dict。
  - https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html

### 第 7 课：CNN、RNN 与 Transformer 入门

- PyTorch Neural Networks Tutorial：用于校准神经网络层、模型结构、CNN 基础。
  - https://docs.pytorch.org/tutorials/beginner/blitz/neural_networks_tutorial.html
- PyTorch Sequence Models and LSTM Tutorial：用于校准 RNN/LSTM、序列建模基础。
  - https://docs.pytorch.org/tutorials/beginner/nlp/sequence_models_tutorial.html
- PyTorch Transformer 文档：用于校准 Transformer、Encoder、Decoder、Attention 相关 API。
  - https://docs.pytorch.org/docs/stable/generated/torch.nn.Transformer.html
- Hugging Face LLM Course：用于校准 Transformer、大模型、注意力机制、预训练模型学习路径。
  - https://huggingface.co/learn/llm-course
- The Illustrated Transformer：用于辅助解释 Transformer 结构和 Self-Attention 直觉。
  - https://jalammar.github.io/illustrated-transformer/

### 第 8 课：大模型基础、Token 与 Prompt Engineering

- OpenAI Text generation 文档：用于校准大模型文本生成、消息结构、角色指令和输出控制。
  - https://platform.openai.com/docs/guides/text-generation
- OpenAI Prompt engineering 文档：用于校准提示词编写、指令清晰度、上下文提供、分步骤推理等最佳实践。
  - https://platform.openai.com/docs/guides/prompt-engineering
- OpenAI Models 文档：用于校准模型能力、上下文窗口、输入输出等概念。
  - https://platform.openai.com/docs/models
- OpenAI Tokenizer：用于辅助理解 tokenization、token 数量和文本切分。
  - https://platform.openai.com/tokenizer
- Hugging Face LLM Course：用于校准大模型、Tokenization、Transformer、预训练和微调基础。
  - https://huggingface.co/learn/llm-course
- Hugging Face NLP Course - Tokenizers：用于校准 tokenizer、subword tokenization、编码解码等基础概念。
  - https://huggingface.co/learn/nlp-course/chapter6/1

### 第 9 课：Embedding、语义搜索与向量数据库

- OpenAI Embeddings 文档：用于校准 Embedding、向量表示、相似度、语义搜索等概念。
  - https://platform.openai.com/docs/guides/embeddings
- OpenAI Vector stores / Retrieval 相关文档：用于校准向量存储、检索、文件搜索等应用概念。
  - https://platform.openai.com/docs/guides/retrieval
- pgvector GitHub README：用于校准 PostgreSQL 向量类型、距离计算、索引、HNSW、IVFFlat 等内容。
  - https://github.com/pgvector/pgvector
- Pinecone Learning Center：用于辅助解释向量数据库、语义搜索、相似度检索、ANN 等概念。
  - https://www.pinecone.io/learn/
- Qdrant Documentation：用于辅助解释向量数据库、collection、payload、filter、相似度搜索等概念。
  - https://qdrant.tech/documentation/

### 第 10 课：RAG 知识库问答系统

- OpenAI Retrieval / File Search 文档：用于校准检索增强生成、文件搜索、向量存储和问答流程。
  - https://platform.openai.com/docs/guides/retrieval
- OpenAI Embeddings 文档：用于校准 RAG 中查询向量化、文档向量化、相似度检索等内容。
  - https://platform.openai.com/docs/guides/embeddings
- LangChain RAG 官方教程：用于校准 RAG 架构、加载文档、切分、检索、生成等流程。
  - https://python.langchain.com/docs/tutorials/rag/
- Spring AI RAG / ETL Pipeline 文档：用于校准 Java/Spring 场景下的文档读取、切分、向量存储和 RAG 流程。
  - https://docs.spring.io/spring-ai/reference/api/etl-pipeline.html
- Spring AI Vector Databases 文档：用于校准 Java AI 工程中的向量存储集成。
  - https://docs.spring.io/spring-ai/reference/api/vectordbs.html
- LangChain Retrieval Conceptual Guide：用于校准 retriever、document loader、text splitter、retrieval chain 等术语。
  - https://python.langchain.com/docs/concepts/retrieval/

### 第 11 课：Function Calling、Tool Calling 与 Agent

- OpenAI Function Calling 文档：用于校准工具调用流程、函数定义、tool call、tool call output、tool_choice、结构化参数等概念。
  - https://platform.openai.com/docs/guides/function-calling
- OpenAI Tools 文档：用于校准内置工具、自定义函数、远程 MCP、工具使用边界等概念。
  - https://platform.openai.com/docs/guides/tools
- OpenAI Responses API 迁移文档：用于校准 Responses API 中 tool call item、call_id、tool output 等交互模式。
  - https://platform.openai.com/docs/guides/migrate-to-responses
- Spring AI Tool Calling 文档：用于校准 Java/Spring 中 `@Tool`、`ToolCallback`、方法工具、函数工具等概念。
  - https://docs.spring.io/spring-ai/reference/api/tools.html
- LangChain4j Tools 文档：用于校准 Java 中 Function Calling、`@Tool`、AI Services、工具执行等概念。
  - https://docs.langchain4j.dev/tutorials/tools/
- LangChain4j AI Services 文档：用于校准 AI Services、工具、RAG、结构化接口等 Agentic 应用抽象。
  - https://docs.langchain4j.dev/tutorials/ai-services/

### 第 12 课：Spring Boot + Spring AI

- Spring AI Reference Documentation：用于校准 Spring AI 总体架构、模型、ChatClient、Prompt、Advisor、VectorStore 等概念。
  - https://docs.spring.io/spring-ai/reference/
- Spring AI Chat Client API：用于校准 `ChatClient`、系统提示、用户提示、响应处理等内容。
  - https://docs.spring.io/spring-ai/reference/api/chatclient.html
- Spring AI Prompts 文档：用于校准 Prompt、Message、PromptTemplate 等抽象。
  - https://docs.spring.io/spring-ai/reference/api/prompt.html
- Spring AI Tool Calling 文档：用于校准 `@Tool`、`ToolCallback`、工具调用 Java 落地。
  - https://docs.spring.io/spring-ai/reference/api/tools.html
- Spring AI Vector Databases 文档：用于校准 VectorStore、pgvector、检索增强应用。
  - https://docs.spring.io/spring-ai/reference/api/vectordbs.html
- Spring AI ETL Pipeline 文档：用于校准文档读取、转换、切分、向量化入库流程。
  - https://docs.spring.io/spring-ai/reference/api/etl-pipeline.html

### 第 13 课：LangChain4j 应用开发

- LangChain4j Documentation：用于校准 LangChain4j 总体概念、模型、AI Services、RAG、工具、记忆等内容。
  - https://docs.langchain4j.dev/
- LangChain4j AI Services 文档：用于校准接口式 AI 服务、声明式方法、结构化返回等概念。
  - https://docs.langchain4j.dev/tutorials/ai-services/
- LangChain4j Tools 文档：用于校准 `@Tool`、工具调用、函数调用等内容。
  - https://docs.langchain4j.dev/tutorials/tools/
- LangChain4j RAG 文档：用于校准 ContentRetriever、EmbeddingStore、DocumentSplitter、RetrievalAugmentor 等 RAG 组件。
  - https://docs.langchain4j.dev/tutorials/rag/
- LangChain4j Memory 文档：用于校准 ChatMemory、MessageWindowChatMemory、对话记忆等内容。
  - https://docs.langchain4j.dev/tutorials/chat-memory/
- LangChain4j Spring Boot Integration 文档：用于校准 Spring Boot Starter、自动配置、模型 Bean 集成等内容。
  - https://docs.langchain4j.dev/tutorials/spring-boot-integration/

### 第 14 课：Java AI 工程化：流式输出、权限、日志、成本与评估

- OpenAI Production Best Practices：用于校准生产环境安全、限流、成本、流式输出、缓存等最佳实践。
  - https://platform.openai.com/docs/guides/production-best-practices
- OpenAI Rate Limits Guide：用于校准 API 限流、退避重试、容量规划等实践。
  - https://platform.openai.com/docs/guides/rate-limits
- Spring AI Observability 文档：用于校准 ChatModel、Embedding、VectorStore 的观测、指标、追踪和日志。
  - https://docs.spring.io/spring-ai/reference/observability/index.html
- Spring AI Chat Client 文档：用于校准流式调用、ChatClient 调用链和 Advisor。
  - https://docs.spring.io/spring-ai/reference/api/chatclient.html
- LangChain4j Streaming 文档：用于校准 Java 大模型流式响应和 StreamingChatModel。
  - https://docs.langchain4j.dev/tutorials/response-streaming/
- OWASP Top 10 for LLM Applications：用于校准 Prompt Injection、敏感信息泄露、过度代理、供应链等 LLM 安全风险。
  - https://owasp.org/www-project-top-10-for-large-language-model-applications/

### 第 15 课：数值线性代数、随机矩阵理论与深度网络谱分析

- Matrix Computations：用于校准矩阵范数、条件数、SVD、数值稳定性等基础理论。
  - https://www.cs.cornell.edu/cv/GVL4/golubandvanloan.htm
- Random Matrix Theory for Deep Learning: Beyond Eigenvalues of Linear Models：用于补充 2025-2026 年随机矩阵理论与深度学习交叉进展。
  - https://arxiv.org/abs/2506.13139
- Stochastic weight matrix dynamics during learning and Dyson Brownian motion：用于补充权重谱随机动力学进展。
  - https://arxiv.org/abs/2407.16427
- Dyson Brownian motion and random matrix dynamics of weight matrices during learning：用于补充训练过程中权重矩阵谱演化研究。
  - https://arxiv.org/abs/2411.13512
- Zeroth-Order Optimization at the Edge of Stability：用于补充 Hessian 谱与优化稳定性前沿。
  - https://arxiv.org/abs/2604.14669

### 第 16 课：张量分解、低秩结构与大模型参数高效训练

- LoRA: Low-Rank Adaptation of Large Language Models：用于校准 LoRA 低秩适配基本公式和方法。
  - https://arxiv.org/abs/2106.09685
- LoRA+: Efficient Low Rank Adaptation of Large Models：用于补充低秩因子差异化优化进展。
  - https://arxiv.org/abs/2402.12354
- DoRA: Weight-Decomposed Low-Rank Adaptation：用于补充权重方向和幅值解耦适配。
  - https://arxiv.org/abs/2402.09353
- GaLore: Memory-Efficient LLM Training by Gradient Low-Rank Projection：用于补充低秩梯度投影训练。
  - https://arxiv.org/abs/2403.03507
- PiSSA: Principal Singular Values and Singular Vectors Adaptation of Large Language Models：用于补充基于主奇异方向的低秩初始化。
  - https://arxiv.org/abs/2404.02948
- LoRTA: Low Rank Tensor Adaptation of Large Language Models：用于补充张量化低秩适配。
  - https://arxiv.org/abs/2402.11417

### 第 17 课：变分推断、归一化流与贝叶斯深度学习

- Pattern Recognition and Machine Learning：用于校准贝叶斯推断、变分推断、KL 散度和概率图模型基础。
  - https://www.microsoft.com/en-us/research/people/cmbishop/prml-book/
- Weight Uncertainty in Neural Networks：用于校准 Bayes by Backprop 和贝叶斯神经网络权重不确定性。
  - https://arxiv.org/abs/1505.05424
- Auto-Encoding Variational Bayes：用于校准重参数化 trick 和 ELBO 推导。
  - https://arxiv.org/abs/1312.6114
- Variational Inference with Normalizing Flows：用于校准归一化流增强变分后验。
  - https://arxiv.org/abs/1505.05770
- Normalizing Flows for Probabilistic Modeling and Inference：用于校准归一化流综述、变量变换公式和 flow 类型。
  - https://arxiv.org/abs/1912.02762

### 第 18 课：大规模优化：AdamW、自然梯度、SAM 与分布式优化动力学

- Adam: A Method for Stochastic Optimization：用于校准 Adam 一阶矩、二阶矩、偏差修正和更新公式。
  - https://arxiv.org/abs/1412.6980
- Decoupled Weight Decay Regularization：用于校准 AdamW 解耦权重衰减。
  - https://arxiv.org/abs/1711.05101
- Natural Gradient Works Efficiently in Learning：用于校准自然梯度和 Fisher 信息矩阵。
  - https://ieeexplore.ieee.org/document/6790500
- Sharpness-Aware Minimization for Efficiently Improving Generalization：用于校准 SAM 目标函数和 sharpness 解释。
  - https://arxiv.org/abs/2010.01412
- Sophia: A Scalable Stochastic Second-order Optimizer for Language Model Pre-training：用于补充轻量二阶 LLM 优化器。
  - https://arxiv.org/abs/2305.14342
- Muon is Scalable for LLM Training：用于补充 2025 年矩阵正交化优化器进展。
  - https://arxiv.org/abs/2502.16982
- Sharpness-Aware Minimization Efficiently Selects Flatter Minima Late in Training：用于补充 2024 年 SAM 训练阶段分析。
  - https://arxiv.org/abs/2410.10373
- Asynchronous Sharpness-Aware Minimization For Fast and Accurate Deep Learning：用于补充分布式/异步 SAM 进展。
  - https://arxiv.org/abs/2503.11147

### 第 19 课：Transformer 深层机理：注意力信息瓶颈、缩放定律与电路理论

- Attention Is All You Need：用于校准 Transformer、Self-Attention 和多头注意力基础公式。
  - https://arxiv.org/abs/1706.03762
- Scaling Laws for Neural Language Models：用于校准语言模型缩放定律基础。
  - https://arxiv.org/abs/2001.08361
- Training Compute-Optimal Large Language Models：用于校准 Chinchilla compute-optimal 训练观点。
  - https://arxiv.org/abs/2203.15556
- A Mathematical Framework for Transformer Circuits：用于校准 QK/OV 电路、残差流和注意力头机制分析。
  - https://transformer-circuits.pub/2021/framework/index.html
- In-context Learning and Induction Heads：用于校准归纳头与上下文学习机制。
  - https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html
- Mechanistically Interpreting a Transformer-based 2-SAT Solver: An Axiomatic Approach：用于补充 2024 年 Transformer 机制解释案例。
  - https://arxiv.org/abs/2407.13594
- Towards Global-level Mechanistic Interpretability：用于补充 2025 年模块化电路视角。
  - https://proceedings.mlr.press/v267/he25x.html

### 第 20 课：稀疏专家模型 MoE：路由、负载均衡、容量因子与系统实现

- Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer：用于校准稀疏门控 MoE 基础。
  - https://arxiv.org/abs/1701.06538
- Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity：用于校准 top-1 routing 和 capacity factor。
  - https://arxiv.org/abs/2101.03961
- GShard: Scaling Giant Models with Conditional Computation and Automatic Sharding：用于校准 MoE 分布式训练。
  - https://arxiv.org/abs/2006.16668
- DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models：用于补充细粒度专家与共享专家。
  - https://arxiv.org/abs/2401.06066
- DeepSeek-V3 Technical Report：用于补充 auxiliary-loss-free 负载均衡和大规模 MoE 工程实践。
  - https://arxiv.org/abs/2412.19437
- LocMoE: A Low-Overhead MoE for Large Language Model Training：用于补充 MoE 通信局部性优化。
  - https://arxiv.org/abs/2401.13920
- Mixture of Experts in Large Language Models：用于补充 2025 年 MoE 综述。
  - https://arxiv.org/abs/2507.11181

### 第 21 课：状态空间模型、RWKV 与长上下文建模

- Efficiently Modeling Long Sequences with Structured State Spaces：用于校准 S4 和结构化状态空间模型基础。
  - https://arxiv.org/abs/2111.00396
- Mamba: Linear-Time Sequence Modeling with Selective State Spaces：用于校准 selective SSM 和 selective scan。
  - https://arxiv.org/abs/2312.00752
- Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality：用于补充 Mamba-2 和 State Space Duality。
  - https://arxiv.org/abs/2405.21060
- RWKV: Reinventing RNNs for the Transformer Era：用于校准 RWKV 的时间混合和 RNN 式推理。
  - https://arxiv.org/abs/2305.13048
- Retentive Network: A Successor to Transformer for Large Language Models：用于补充 RetNet 和 retention 机制。
  - https://arxiv.org/abs/2307.08621
- Stuffed Mamba: State Collapse and State Capacity of RNN-Based Long-Context Modeling：用于补充状态容量和长上下文边界。
  - https://openreview.net/forum?id=cu2CT2VAvs
- Enhancing RWKV-based Language Models for Long-Sequence Text Generation：用于补充 RWKV 长序列生成研究。
  - https://arxiv.org/abs/2502.15485

### 第 22 课：扩散模型、Score-based SDE 与 Flow Matching

- Denoising Diffusion Probabilistic Models：用于校准 DDPM 前向加噪、反向去噪和噪声预测目标。
  - https://arxiv.org/abs/2006.11239
- Score-Based Generative Modeling through Stochastic Differential Equations：用于校准 score-based SDE 和 probability flow ODE。
  - https://arxiv.org/abs/2011.13456
- Flow Matching for Generative Modeling：用于校准 Flow Matching 速度场学习。
  - https://arxiv.org/abs/2210.02747
- Flow Straight and Fast: Learning to Generate and Transfer Data with Rectified Flow：用于校准 Rectified Flow。
  - https://arxiv.org/abs/2209.03003
- An Introduction to Flow Matching and Diffusion Models：用于补充 2025 年统一教程视角。
  - https://arxiv.org/abs/2506.02070
- Consistency Flow Matching：用于补充少步生成和一致性速度场。
  - https://arxiv.org/abs/2407.02398
- Transition Matching：用于补充 2025 年统一转移生成框架。
  - https://openreview.net/forum?id=An0ePypuOJ

### 第 23 课：大模型对齐：RLHF、DPO、RLAIF 与偏好优化理论

- Training language models to follow instructions with human feedback：用于校准 RLHF、奖励模型和 PPO 对齐流程。
  - https://arxiv.org/abs/2203.02155
- Direct Preference Optimization：用于校准 DPO 推导和直接偏好优化目标。
  - https://arxiv.org/abs/2305.18290
- Constitutional AI：用于校准 RLAIF 和原则驱动 AI 反馈。
  - https://arxiv.org/abs/2212.08073
- Proximal Policy Optimization Algorithms：用于校准 PPO clipped objective。
  - https://arxiv.org/abs/1707.06347
- A Survey of Direct Preference Optimization：用于补充 2025 年 DPO 方法族综述。
  - https://arxiv.org/abs/2503.11701
- DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning：用于补充 GRPO/RLVR 推理模型训练趋势。
  - https://arxiv.org/abs/2501.12948
- URPO: A Unified Reward & Policy Optimization Framework for Large Language Models：用于补充 2025 年统一奖励和策略优化。
  - https://arxiv.org/abs/2507.17515

### 第 24 课：推理系统优化：KV Cache、量化、投机解码与 vLLM/Triton 内核

- vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention：用于校准 PagedAttention、KV cache block 管理和 continuous batching。
  - https://arxiv.org/abs/2309.06180
- FlashAttention: Fast and Memory-Efficient Exact Attention：用于校准 attention IO-aware 优化。
  - https://arxiv.org/abs/2205.14135
- Fast Inference from Transformers via Speculative Decoding：用于校准投机解码理论。
  - https://arxiv.org/abs/2211.17192
- Cache Me If You Must：用于补充 2025 年自适应 KV cache 量化。
  - https://arxiv.org/abs/2501.19392
- KVLinC: KV Cache Quantization with Hadamard Rotation and Linear Correction：用于补充 KV cache 量化校正。
  - https://arxiv.org/abs/2510.05373
- Unlocking Efficiency in Large Language Model Inference: A Comprehensive Survey of Speculative Decoding：用于补充投机解码综述。
  - https://aclanthology.org/2024.findings-acl.456/
- vLLM Documentation：用于校准服务端配置、prefix caching、chunked prefill、量化和 speculative decoding。
  - https://docs.vllm.ai

### 第 25 课：表示学习与自监督：对比学习、掩码建模、蒸馏与几何结构

- SimCLR：用于校准 InfoNCE 和对比学习基本框架。
  - https://arxiv.org/abs/2002.05709
- Understanding Contrastive Representation Learning through Alignment and Uniformity：用于校准 alignment/uniformity 表示几何。
  - https://arxiv.org/abs/2005.10242
- BYOL：用于校准无负样本自蒸馏和 stop-gradient 机制。
  - https://arxiv.org/abs/2006.07733
- DINO：用于校准 self-distillation vision transformer。
  - https://arxiv.org/abs/2104.14294
- Masked Autoencoders Are Scalable Vision Learners：用于校准 MAE 掩码重构。
  - https://arxiv.org/abs/2111.06377
- DINOv2：用于补充大规模无监督视觉表示。
  - https://arxiv.org/abs/2304.07193
- KDC-MAE：用于补充 2024 年对比、掩码和蒸馏混合目标。
  - https://arxiv.org/abs/2411.12270

### 第 26 课：可解释性与模型行为分析：归因、探针、因果干预与神经科学连接

- Axiomatic Attribution for Deep Networks：用于校准 Integrated Gradients。
  - https://arxiv.org/abs/1703.01365
- Locating and Editing Factual Associations in GPT：用于校准 causal tracing 和模型编辑。
  - https://arxiv.org/abs/2202.05262
- A Mathematical Framework for Transformer Circuits：用于校准机制可解释性和残差流分析。
  - https://transformer-circuits.pub/2021/framework/index.html
- Towards Monosemanticity：用于校准稀疏自编码器和 monosemantic feature。
  - https://transformer-circuits.pub/2023/monosemantic-features/index.html
- Representation Engineering: A Top-Down Approach to AI Transparency：用于校准 activation steering 和表示工程。
  - https://arxiv.org/abs/2310.01405
- AtP*: An efficient and scalable method for localizing LLM behaviour to components：用于补充 attribution patching。
  - https://arxiv.org/abs/2403.00745
- Scaling and evaluating sparse autoencoders：用于补充 2024 年 SAE 扩展与评估。
  - https://arxiv.org/abs/2406.04093
- Decoding the brain: From neural representations to mechanistic models：用于补充神经科学连接。
  - https://doi.org/10.1016/j.cell.2024.08.051
