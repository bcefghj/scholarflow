# Attention Is All You Need

**作者**: Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin
**年份**: 2017 | **发表于**: NeurIPS 2017 (NIPS)

## 一句话总结
本文提出了Transformer架构——一种完全基于注意力机制的序列转换模型，彻底摒弃了循环和卷积结构，在机器翻译任务上取得了当时最优结果，并深刻改变了整个深度学习领域的发展方向。

## 核心贡献
1. **提出Transformer架构**: 第一个完全基于自注意力机制的序列到序列模型，不使用任何RNN或CNN
2. **多头注意力机制(Multi-Head Attention)**: 允许模型同时关注不同位置的不同表示子空间
3. **位置编码(Positional Encoding)**: 用正弦/余弦函数注入序列位置信息，替代循环结构的隐式位置建模
4. **大幅提升训练效率**: 高度并行化，训练速度远超RNN，在8个GPU上仅需3.5天即可训练完成
5. **建立了后续所有大语言模型的基础架构**: GPT、BERT、T5等均基于Transformer

## 关键方法/技术
- **Scaled Dot-Product Attention**: $\text{Attention}(Q,K,V) = \text{softmax}(\frac{QK^T}{\sqrt{d_k}})V$
- **Multi-Head Attention**: 将Q、K、V投影到多个子空间，并行计算注意力后拼接
- **Encoder-Decoder架构**: 编码器6层堆叠（自注意力+前馈网络），解码器6层堆叠（自注意力+交叉注意力+前馈网络）
- **残差连接 + Layer Normalization**: 每个子层后应用
- **学习率预热调度**: 先线性增加后按步数逆平方根衰减

## 主要实验结果
- **英德翻译**: 28.4 BLEU（超越所有之前的单模型和集成模型）
- **英法翻译**: 41.0 BLEU（新的SOTA，训练成本仅为之前最优模型的1/4）
- **训练速度**: 在8块P100 GPU上训练3.5天，远低于之前方法数周的训练时间
- **英语句法分析**: 泛化到其他任务也表现出色

## 适合谁读
- 所有深度学习/NLP/AI方向的研究者和学生（必读经典）
- 希望理解GPT、BERT等大模型底层原理的从业者
- 对注意力机制感兴趣的任何人

## 推荐指数：5
## 推荐理由：深度学习领域最重要的论文之一，Transformer已成为现代AI的基石架构，无论做什么方向都值得精读。
