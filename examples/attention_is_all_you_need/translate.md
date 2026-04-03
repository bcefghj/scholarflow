# Bilingual Summary / 双语摘要

## Attention Is All You Need

### English Summary

**What**: The paper introduces the Transformer, a novel neural network architecture based entirely on attention mechanisms that replaces recurrent and convolutional layers commonly used in sequence transduction models.

**Why**: This work addresses the fundamental sequential computation bottleneck of recurrent neural networks (RNNs), which prevents parallelization during training and limits the ability to learn long-range dependencies. It is important because it enables dramatically more parallel computation and achieves superior performance with significantly less training time.

**How**: The Transformer uses stacked self-attention and point-wise fully connected layers for both encoder and decoder. Key components include: multi-head attention (h=8 parallel attention heads), scaled dot-product attention (dividing dot products by √dk), residual connections around sub-layers with layer normalization, sinusoidal positional encodings to incorporate position information without recurrence, and position-wise feed-forward networks with ReLU activation (dmodel=512, dff=2048).

**Results**: On WMT 2014 English-to-German translation, the big Transformer achieves 28.4 BLEU, improving over the previous best results (including ensembles) by over 2 BLEU. On WMT 2014 English-to-French translation, it achieves 41.8 BLEU, establishing a new single-model state-of-the-art after training for only 3.5 days on eight GPUs—a fraction of the training cost of competing models. The model also generalizes well to English constituency parsing, achieving 91.3 F1 with WSJ only training data.

**Impact**: This paper fundamentally transformed deep learning and natural language processing, becoming the foundation for modern large language models (including GPT, BERT, and their variants). The attention-based approach has since been applied across nearly all domains of AI, establishing attention mechanisms as the dominant paradigm for sequence modeling and beyond.

---

### 中文摘要

**做了什么**: 本论文提出了Transformer，这是一种完全基于注意力机制的新型神经网络架构，用多头自注意力机制取代了序列转导模型中常用的循环和卷积层。

**为什么重要**: 这项工作解决了循环神经网络（RNNs）固有的顺序计算瓶颈问题——该瓶颈阻碍了训练期间的并行化，并限制了模型学习长距离依赖的能力。重要的是，它实现了显著的并行计算提升，同时以更少的训练时间获得更优的性能。

**怎么做的**: Transformer在编码器和解码器中均使用堆叠的自注意力层和逐位置全连接层。主要组件包括：多头注意力（h=8个并行注意力头）、缩放点积注意力（将点积除以√dk）、围绕子层的残差连接配合层归一化、正弦位置编码（无需循环即可融入位置信息），以及带有ReLU激活的逐位置前馈网络（dmodel=512, dff=2048）。

**主要结果**: 在WMT 2014英德翻译任务中，大型Transformer模型达到28.4 BLEU分数，比之前的最佳结果（包括集成模型）提升了超过2个BLEU。在WMT 2014英法翻译任务中，模型达到41.8 BLEU，仅在8块GPU上训练3.5天便创下单一模型最高分数——远低于竞争模型的训练成本。该模型还展现出良好的泛化能力，在仅使用WSJ数据训练的情况下达到91.3 F1的英语成分句法分析成绩。

**影响力**: 本论文从根本上改变了深度学习和自然语言处理领域，成为现代大型语言模型（包括GPT、BERT及其变体）的基础。该注意力方法此后被应用于几乎所有人工智能领域确立了注意力机制作为序列建模及其他领域的主导范式地位。

---

### Key Terms / 关键术语对照

| English | 中文 |
|---------|------|
| Transformer | Transformer模型 |
| Attention Mechanism | 注意力机制 |
| Self-Attention | 自注意力 |
| Multi-Head Attention | 多头注意力 |
| Scaled Dot-Product Attention | 缩放点积注意力 |
| Encoder-Decoder | 编码器-解码器 |
| Positional Encoding | 位置编码 |
| BLEU Score | BLEU分数 |
| Sequence Transduction | 序列转导 |
| Residual Connection | 残差连接 |
| Layer Normalization | 层归一化 |
| Feed-Forward Network | 前馈神经网络 |
| Machine Translation | 机器翻译 |
| Constituency Parsing | 成分句法分析 |
| Neural Network | 神经网络 |
| Parallelization | 并行化 |