# 第 24 课：推理系统优化：KV Cache、量化、投机解码与 vLLM/Triton 内核

## 0. 任务标识

任务名称：推理系统优化：KV Cache、量化、投机解码与 vLLM/Triton 内核

预计学习时长：1.5 到 2 周

前置基础要求：

- 理解 Transformer attention、KV cache、自回归生成。
- 已完成第 18 课，理解吞吐、batch、分布式训练和优化成本。
- 已完成第 21 课，理解长上下文与缓存内存瓶颈。
- 能读懂基础 CUDA/Triton kernel 或至少理解 GPU memory bandwidth 与 compute 的差异。

本课目标：

```text
从“调用模型接口”上升到“理解 LLM serving 的计算图、内存瓶颈、调度策略和 kernel 级优化”。
```

你需要建立以下研究直觉：

- LLM 推理通常不是纯算力瓶颈，decode 阶段常受 KV cache 读写和内存带宽限制。
- Prefill 和 decode 是两种不同 workload，优化策略不同。
- PagedAttention 解决 KV cache 碎片和动态 batch 管理问题。
- 量化不仅包括权重量化，还包括 activation、KV cache 和混合精度 kernel。
- 投机解码用小模型或额外头批量提出 token，再由大模型验证，降低自回归串行开销。

## 1. 本课阅读方式

建议学习顺序：

```text
prefill / decode 分解
  -> KV cache 内存公式
  -> continuous batching
  -> PagedAttention
  -> prefix caching / chunked prefill
  -> weight quantization
  -> KV cache quantization
  -> speculative decoding
  -> Triton kernel 思维
```

【核心】推理优化的目标不是单次 forward 更快，而是在真实请求分布下同时优化吞吐、首 token 延迟、尾延迟、显存占用、成本和输出质量。

## 2. Prefill 与 Decode

### 2.1 Prefill

给定 prompt 长度 $T_p$，prefill 一次性处理 prompt：

$$
K_{1:T_p},V_{1:T_p}
=
f_{\text{KV}}(x_{1:T_p})
$$

公式注释：

- $T_p$ 是输入 prompt token 数。
- prefill 阶段可以并行计算所有 prompt token 的隐藏状态。
- 该阶段类似训练中的 causal forward，但不需要反向传播。
- 输出是后续 decode 需要复用的 KV cache。

理论注释：

Prefill 通常 compute-intensive，长 prompt 会显著增加首 token 延迟。chunked prefill 将长 prompt 切块，避免阻塞其他短请求。

### 2.2 Decode

第 $t$ 步生成：

$$
p(x_t\mid x_{<t})
=
\mathrm{LMHead}(h_t)
$$

并追加：

$$
K_t,V_t
$$

公式注释：

- decode 每步只生成一个或少数 token。
- 当前 query 需要访问历史全部 KV。
- 每步都要读大量 KV cache，但矩阵乘规模相对小。

理论注释：

Decode 阶段常 memory-bandwidth bound。GPU 算力可能没有打满，瓶颈在从 HBM 读取 KV cache 和权重。

## 3. KV Cache 内存模型

### 3.1 KV cache 大小

KV cache 大小近似：

$$
M_{\text{KV}}
=
2 \cdot L \cdot B \cdot T \cdot H \cdot d_h \cdot s
$$

公式注释：

- 2 表示 Key 和 Value 两份缓存。
- $L$ 是层数。
- $B$ 是 batch size 或并发序列数。
- $T$ 是上下文长度。
- $H$ 是 KV heads 数。
- $d_h$ 是每头维度。
- $s$ 是每个元素字节数，例如 FP16 为 2。

理论注释：

KV cache 随 batch 和上下文线性增长。长上下文 serving 中，KV cache 可能超过权重显存，成为并发能力上限。

### 3.2 GQA / MQA

Grouped-query attention 让多个 query head 共享 KV head：

$$
H_{\text{kv}} < H_{\text{q}}
$$

公式注释：

- $H_{\text{q}}$ 是 query head 数。
- $H_{\text{kv}}$ 是 key/value head 数。
- MQA 是 $H_{\text{kv}}=1$ 的极端情况。
- GQA/MQA 可显著降低 KV cache。

理论注释：

GQA 是现代 LLM 推理友好架构的重要设计。它牺牲部分表达能力，换取 KV cache 和 bandwidth 降低。

## 4. Continuous Batching 与 PagedAttention

### 4.1 Continuous batching

传统静态 batch 等所有序列结束；continuous batching 在每个 decode step 动态加入和移除请求：

```text
decode one token
  -> finished requests leave
  -> new requests enter
  -> repack active batch
```

理论注释：

LLM 请求长度高度不均匀。continuous batching 提升 GPU 利用率，是 serving 系统吞吐提升的核心机制。

### 4.2 PagedAttention

PagedAttention 将 KV cache 分为固定大小 block：

$$
\text{logical token position}
\to
\text{physical KV block}
$$

公式注释：

- 每个序列有逻辑连续的 token 位置。
- 物理 KV block 可以非连续存储。
- block table 记录逻辑到物理映射。
- 类似操作系统虚拟内存分页。

理论注释：

PagedAttention 解决传统 KV cache 预分配带来的碎片和浪费。vLLM 通过它支持更高并发、prefix sharing 和动态调度。

## 5. 量化：权重、激活与 KV Cache

### 5.1 对称量化

将浮点数 $x$ 量化为整数：

$$
q
=
\operatorname{round}
\left(
\frac{x}{s}
\right)
$$

反量化：

$$
\hat{x}=s q
$$

公式注释：

- $s$ 是 scale。
- $q$ 是低 bit 整数。
- $\hat{x}$ 是反量化近似值。
- 量化误差为 $x-\hat{x}$。

理论注释：

量化本质是在显存、带宽和精度之间交换。推理中常见权重量化包括 INT8、INT4、GPTQ、AWQ、FP8；KV 量化则更敏感，因为误差会影响每步 attention。

### 5.2 KV cache 量化

KV cache 量化目标：

$$
K,V
\to
Q(K),Q(V)
$$

公式注释：

- $Q(\cdot)$ 是量化算子。
- KV cache 被每个 decode step 反复读取，压缩能显著降低带宽和显存。
- 但 attention score 对 key 误差敏感，value 误差会直接影响上下文聚合。

理论注释：

2025-2026 年 AQUA-KV、KVLinC、KVTC、TurboQuant 等方法说明，KV cache 压缩已成为长上下文推理核心方向。优秀方法通常结合旋转、校正、分组、自适应 bit 或变换编码。

## 6. 投机解码

### 6.1 基本思想

小 draft model 一次生成多个候选 token：

$$
\tilde{y}_{t:t+k}
\sim
q(\cdot\mid x,y_{<t})
$$

大 target model 并行验证：

$$
p(y_i\mid x,y_{<i})
$$

公式注释：

- $q$ 是 draft model，速度快但质量较低。
- $p$ 是 target model，质量高但速度慢。
- 如果候选 token 被接受，大模型一次推进多步。
- 如果拒绝，则回退并采样修正 token。

理论注释：

投机解码不改变目标模型分布，理论上可保持 exact sampling。加速来自把多个串行 decode step 合并为一次 target forward 验证。

### 6.2 接受率

加速效果依赖接受率：

$$
\text{speedup}
\approx
\frac{\text{tokens accepted per target step}}
{\text{extra draft cost}+\text{verification cost}}
$$

公式注释：

- draft 越接近 target，接受率越高。
- draft 太大则自身成本高。
- 最优 draft 是速度和质量的折中。

理论注释：

Medusa、EAGLE、Lookahead 等方法试图减少或改造 draft model。2024-2025 年 speculative decoding 研究核心就是提升接受率、减少额外模型和适配复杂度。

## 7. Triton Kernel 思维

### 7.1 Roofline 直觉

算术强度：

$$
I
=
\frac{\text{FLOPs}}
{\text{Bytes moved}}
$$

公式注释：

- FLOPs 是计算量。
- Bytes moved 是内存读写量。
- $I$ 高表示 compute-bound。
- $I$ 低表示 memory-bound。

理论注释：

LLM decode 中很多操作是 memory-bound。Triton kernel 优化关注减少 HBM 访问、融合算子、复用 SRAM、避免不必要 materialization。

### 7.2 Kernel fusion

常见融合：

```text
dequantize + matmul
attention score + softmax + value aggregation
RMSNorm + residual
sampling logits processing
```

理论注释：

融合的目标不是减少数学操作，而是减少中间张量读写和 kernel launch overhead。

## 8. 前沿研究进展：2024-2026 视角

### 8.1 vLLM 生态成熟

vLLM 已从 PagedAttention 论文系统发展为包含 continuous batching、prefix caching、chunked prefill、speculative decoding、quantization 和 OpenAI-compatible API 的 serving 生态。

### 8.2 KV cache 压缩成为长上下文关键

2025-2026 年 AQUA-KV、KVLinC、KVTC、GPU INT8 KV quantization、TurboQuant 等工作集中压缩 KV cache，目标是在 LongBench、RULER、Needle 等长上下文任务上接近无损。

### 8.3 投机解码方法族扩展

Medusa、EAGLE、Lookahead、Speculative Diffusion Decoding 等方法说明，未来解码加速可能结合多 token heads、feature-level draft、训练无关 lookahead 和并行验证。

## 9. 代码实验一：KV Cache 显存估算器

```python
def kv_cache_gb(layers, batch, tokens, kv_heads, head_dim, dtype_bytes=2):
    bytes_total = 2 * layers * batch * tokens * kv_heads * head_dim * dtype_bytes
    return bytes_total / (1024 ** 3)

print(kv_cache_gb(layers=32, batch=16, tokens=8192, kv_heads=8, head_dim=128))
```

实验要求：

- 比较 MHA、GQA、MQA 的 KV cache。
- 改变上下文长度和并发数，画出显存曲线。

## 10. 代码实验二：投机解码接受率模拟

```python
import torch

def speculative_acceptance(target_probs, draft_tokens):
    # target_probs: [k, vocab]
    # draft_tokens: [k]
    probs = target_probs.gather(1, draft_tokens[:, None]).squeeze(1)
    random = torch.rand_like(probs)
    accepted = random < probs
    return accepted.cumprod(dim=0).sum().item()
```

实验要求：

- 模拟不同 draft 质量下的接受 token 数。
- 分析接受率和加速比关系。

## 11. MCP 调用点设计

### 11.1 MCP 调用点 A：最新推理论文检索

建议 MCP 工具：

```text
arxiv.search
```

建议查询：

```json
{
  "query": "(\"LLM inference\" OR \"KV cache\" OR quantization OR \"speculative decoding\" OR vLLM OR PagedAttention OR Triton)",
  "max_results": 20,
  "sort_by": "submittedDate",
  "date_range": "2024-01-01..2026-12-31"
}
```

预期学习收获：

- 区分方法优化的是 prefill、decode、KV cache、weights、scheduler 还是 kernel。
- 记录吞吐、TTFT、TPOT、显存和质量下降。

### 11.2 MCP 调用点 B：代码库检索

建议 MCP 工具：

```text
github.search_repositories
```

建议查询：

```json
{
  "query": "vLLM speculative decoding KV cache quantization Triton FlashAttention LLM serving",
  "language": "Python",
  "sort": "updated",
  "max_results": 10
}
```

预期学习收获：

- 阅读 vLLM、FlashInfer、TensorRT-LLM、SGLang 的实现。
- 对比 scheduler、block manager、attention kernel。

## 12. 课后研究课题

### 课题 1：KV cache 预算规划

要求：

- 为 7B、14B、32B 模型估算不同上下文和并发下 KV cache。
- 分析 GQA、FP8 KV、INT4 KV 的节省比例。

### 课题 2：vLLM serving 压测

要求：

- 启动 vLLM OpenAI-compatible server。
- 测试 continuous batching、prefix caching、chunked prefill。
- 记录 TTFT、TPOT、throughput。

### 课题 3：投机解码论文复现

要求：

- 阅读 Medusa、EAGLE 或 Lookahead。
- 总结 draft 机制、验证方式和加速来源。
- 实现一个 toy speculative decoding。

## 13. 推荐阅读与动态更新入口

基础阅读：

- vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention.
- FlashAttention: Fast and Memory-Efficient Exact Attention.
- GPTQ, AWQ, SmoothQuant.
- Leviathan et al., Fast Inference from Transformers via Speculative Decoding.

近期阅读：

- vAttention: Dynamic Memory Management for Serving LLMs without PagedAttention, https://www.microsoft.com/en-us/research/publication/vattention-dynamic-memory-management-for-serving-llms-without-pagedattention/
- Cache Me If You Must: Adaptive Key-Value Quantization for Large Language Models, https://arxiv.org/abs/2501.19392
- KV Cache Transform Coding for Compact Storage in LLM Inference, https://arxiv.org/abs/2511.01815
- KVLinC: KV Cache Quantization with Hadamard Rotation and Linear Correction, https://arxiv.org/abs/2510.05373
- GPU-Accelerated INT8 Quantization for KV Cache Compression in Large Language Models, https://arxiv.org/abs/2601.04719
- Unlocking Efficiency in Large Language Model Inference: A Comprehensive Survey of Speculative Decoding, https://aclanthology.org/2024.findings-acl.456/
- vLLM docs: https://docs.vllm.ai

动态阅读入口：

- vLLM: https://github.com/vllm-project/vllm
- FlashInfer: https://github.com/flashinfer-ai/flashinfer
- TensorRT-LLM: https://github.com/NVIDIA/TensorRT-LLM
- Triton: https://triton-lang.org

后续更新本课时，优先通过 MCP 调用点 A 检索 2024-2026 年 LLM inference、KV cache compression、speculative decoding、quantization、PagedAttention 相关论文。
