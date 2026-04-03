# Bilingual Summary / 双语摘要

## Attention Is All You Need

### English Summary

**What**: This paper introduces the Transformer, a novel neural network architecture based entirely on self-attention mechanisms that replaces recurrent and convolutional layers in sequence transduction models.

**Why**: Traditional sequence transduction models relied on recurrent neural networks (RNNs/LSTMs), which have inherent sequential computation limitations that prevent parallelization and struggle with long-range dependencies. This paper fundamentally reimagines sequence modeling.

**How**: The Transformer uses multi-head self-attention to compute representations by relating different positions within sequences. It employs scaled dot-product attention, positional encodings using sine/cosine functions, and stacks six identical layers for both encoder and decoder with residual connections and layer normalization. The architecture allows parallel computation across all positions in a sequence.

**Results**: On WMT 2014 English-to-German translation, the Transformer achieved 28.4 BLEU, surpassing all previous models including ensembles by over 2 BLEU. On English-to-French translation, it established a new single-model state-of-the-art of 41.8 BLEU while training for only 3.5 days on eight P100 GPUs—a fraction of the computational cost of competing models.

**Impact**: This work laid the foundation for modern large language models (BERT, GPT, and their descendants) and revolutionized natural language processing by demonstrating that attention alone can outperform traditional recurrent architectures while being more efficient and parallelizable.

---

### 中文摘要

**做了什么**：本文提出了Transformer，一种完全基于自注意力机制的全新神经网络架构，用于替代序列转导模型中的循环和卷积层。

**为什么重要**：传统的序列转导模型依赖于循环神经网络（RNN/LSTM），这些模型存在固有的顺序计算限制，阻碍了并行化，且难以处理长距离依赖关系。本文从根本上重新设计了序列建模方法。

**怎么做的**：Transformer使用多头自注意力来计算表示，通过关联序列中不同位置之间的关系。它采用缩放点积注意力、使用正弦/余弦函数的 positional encoding，并在编码器和解码器各堆叠六层相同的结构，辅以残差连接和层归一化。该架构允许在序列的所有位置上进行并行计算。

**主要结果**：在WMT 2014英德翻译任务中，Transformer达到28.4 BLEU分数，超过所有先前模型（包括集成模型）2个BLEU以上。在英法翻译任务中，它创下新的单模型最高分41.8 BLEU，而在八块P100 GPU上仅需训练3.5天——这仅仅是竞争模型计算成本的一小部分。

**影响力**：这项工作为现代大型语言模型（BERT、GPT及其后继者）奠定了基础，通过证明仅凭注意力机制就能超越传统循环架构的卓越性能，彻底改变了自然语言处理领域。

---

### Key Terms / 关键术语对照

| English | 中文 |
|---------|------|
| Transformer | Transformer模型 |
| Self-Attention | 自注意力机制 |
| Encoder-Decoder | 编码器-解码器 |
| Multi-Head Attention | 多头注意力 |
| Scaled Dot-Product Attention | 缩放点积注意力 |
| Positional Encoding | 位置编码 |
| BLEU Score | BLEU分数 |
| Sequence Transduction | 序列转导 |
| Parallelization | 并行化 |
| Residual Connection | 残差连接 |
| Layer Normalization | 层归一化 |
| Feed-Forward Network | 前馈神经网络 |
| Machine Translation | 机器翻译 |
| Constituency Parsing | 成分句法分析 |