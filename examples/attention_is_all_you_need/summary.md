# Attention Is All You Need

**作者**: Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin
**年份**: 2017 | **发表于**: 31st Conference on Neural Information Processing Systems (NIPS 2017)

> ⚠️ **勘误**: 元数据中标注的2024年有误，这是一篇2017年的经典论文，由Google Brain和Google Research团队发表。

## 一句话总结
提出**Transformer**架构，完全基于注意力机制，摒弃了传统的循环和卷积结构，在机器翻译任务上实现了新的最优性能。

## 核心贡献

1. **提出Transformer架构**: 首个完全基于注意力机制的序列转导模型，摒弃RNN和CNN
2. **Multi-Head Attention (多头注意力)**: 通过多个注意力头并行学习不同表示子空间的信息
3. **Scaled Dot-Product Attention**: 改进的缩放点积注意力机制，解决大维度下梯度消失问题
4. **位置编码**: 提出正弦位置编码，使模型能够利用序列位置信息
5. **高度可并行化**: 大幅减少训练时间，8个P100 GPU仅需12小时完成base模型训练

## 关键方法/技术

- **编码器-解码器架构**: 各6层堆叠的编码器和解码器
- **自注意力机制**: Query、Key、Value来自同一序列，计算序列内部的依赖关系
- **残差连接 + Layer Normalization**: 稳定深层网络的训练
- **Adam优化器 + 学习率预热策略**: 自适应学习率调度
- **Label Smoothing + Dropout**: 正则化技术防止过拟合

## 主要实验结果

| 任务 | 模型 | BLEU分数 |
|------|------|----------|
| WMT 2014 英德翻译 | Transformer (big) | **28.4** (超越之前最佳2+ BLEU) |
| WMT 2014 英法翻译 | Transformer (big) | **41.8** (单模型最优) |
| 英成分句法分析 | Transformer (4层) | 91.3 F1 (WSJ only) |
| 英成分句法分析 | Transformer (4层) | 92.7 F1 (半监督) |

- 训练成本仅为竞争对手的**1/4到1/8**

## 适合谁读

- **NLP研究者**: 从事机器翻译、文本生成、序列建模的研究者
- **深度学习工程师**: 理解现代Transformer架构的必读文献
- **AI领域学生**: 作为大语言模型(LLM)、BERT、GPT等模型的基石论文
- **对注意力机制感兴趣的研究者**: 深入理解注意力机制的经典之作

## 推荐指数：5

## 推荐理由：
> 这是深度学习领域最具影响力的论文之一，Transformer架构奠定了现代NLP乃至整个AI领域的基础架构，任何从事AI相关研究的人都应该阅读这篇论文。