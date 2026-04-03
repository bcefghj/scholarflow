# ScholarFlow 📚

**全网最强的学术论文处理工具** — 一个工具，搞定所有论文处理需求。

输入一篇论文（PDF / 标题 / DOI / arXiv链接），自动生成 **简要介绍 + 汇报PPT + Beamer幻灯片 + PPT讲解稿 + 学习笔记 + 思维导图 + 学术海报 + 双语翻译** 全套材料。

---

[English](#english) | [中文](#中文)

---

<a id="中文"></a>

## 为什么需要 ScholarFlow？

> 看到一篇新论文，不知道值不值得读？
> 组会要汇报，需要做PPT和讲稿？
> 想深入学习，需要整理笔记？
>
> **以前**: 用ChatPaper看摘要 → 用Paper2Slides做PPT → 用Auto-Slides生成讲稿 → 自己手写笔记
>
> **现在**: `sf full paper.pdf` — **一个命令，全部搞定。**

---

## 核心功能

| 输出 | 格式 | 说明 |
|------|------|------|
| 📋 简要介绍 | Markdown | 200-500字摘要 + 推荐阅读指数(1-5星)，快速判断值不值得读 |
| 📊 汇报PPT | .pptx | 10-15页，3套主题，可在PowerPoint/WPS直接编辑 |
| 🎭 Beamer幻灯片 | .pdf (LaTeX) | 学术风格，支持Madrid/Berlin等多种主题 |
| 🎤 PPT讲解稿 | .pdf (LaTeX) | 每页PPT对应讲解文字，拿着就能讲 |
| 📝 学习笔记 | .pdf (LaTeX) | 三种模式: 深度学习 / 考试复习 / 快速笔记 |
| 🧠 思维导图 | .html | 交互式Markmap可视化 |
| 🖼️ 学术海报 | .html | A0横版学术海报 |
| 🌐 双语翻译 | Markdown | 中英双语摘要 + 关键术语对照 |

---

## 示例: Attention Is All You Need (Transformer 经典论文)

以下所有内容均由 ScholarFlow 使用 MiniMax M2.7 模型自动生成，**非人工编写**。

```bash
sf full --arxiv 1706.03762 --lang zh --model minimax/MiniMax-M2.7
```

---

### 📋 1. 简要介绍 ([完整文件](examples/attention_is_all_you_need/summary.md))

> **一句话总结**: 提出Transformer架构，完全基于注意力机制，摒弃了传统的循环和卷积结构，在机器翻译任务上实现了新的最优性能。
>
> **核心贡献**:
> 1. **提出Transformer架构**: 首个完全基于注意力机制的序列转导模型，摒弃RNN和CNN
> 2. **Multi-Head Attention (多头注意力)**: 通过多个注意力头并行学习不同表示子空间的信息
> 3. **Scaled Dot-Product Attention**: 改进的缩放点积注意力机制，解决大维度下梯度消失问题
> 4. **位置编码**: 提出正弦位置编码，使模型能够利用序列位置信息
> 5. **高度可并行化**: 大幅减少训练时间，8个P100 GPU仅需12小时完成base模型训练
>
> | 任务 | BLEU分数 |
> |------|----------|
> | WMT 2014 英德翻译 | **28.4** (超越之前最佳2+ BLEU) |
> | WMT 2014 英法翻译 | **41.8** (单模型最优) |
>
> **推荐指数: ⭐⭐⭐⭐⭐** (5/5)
>
> **推荐理由**: 这是深度学习领域最具影响力的论文之一，Transformer架构奠定了现代NLP乃至整个AI领域的基础架构。

---

### 📊 2. 汇报PPT ([下载 .pptx](examples/attention_is_all_you_need/slides.pptx))

自动生成13页PPT，包含封面、背景动机、方法详解、实验结果、消融分析、总结展望等完整结构。

**PPT结构:**
| 页码 | 标题 |
|------|------|
| 1 | Attention Is All You Need (封面) |
| 2 | 研究背景与动机 |
| 3 | 相关工作 |
| 4 | 模型架构概述 |
| 5 | 注意力机制：缩放点积注意力 |
| 6 | 多头注意力机制 |
| 7 | 位置编码与前馈网络 |
| 8 | 自注意力的优势分析 |
| 9 | 机器翻译实验结果 |
| 10 | 模型变体消融分析 |
| 11 | 泛化能力：句法分析 |
| 12 | 总结与展望 |
| 13 | 关键参考文献 |

3套内置主题: `academic_blue`(学术蓝) / `minimal_white`(简约白) / `dark_modern`(深色)

---

### 🎭 3. Beamer幻灯片 ([查看 PDF](examples/attention_is_all_you_need/beamer.pdf))

LaTeX Beamer格式的学术幻灯片，支持 Madrid / Berlin / Singapore / CambridgeUS 等多种经典 Beamer 主题。适合学术会议风格的正式演示。

---

### 🎤 4. PPT讲解稿 ([查看 PDF](examples/attention_is_all_you_need/script.pdf))

每一页PPT都有对应的300-500字讲解文字，包含：
- 这页要讲什么
- 技术细节的通俗解释
- 与前后页的过渡语
- 可能被问到的问题提示

拿着讲稿就能流畅地做学术汇报。

---

### 📝 5. 学习笔记 ([查看 PDF](examples/attention_is_all_you_need/notes_deep.pdf))

深度学习笔记包含：
- 研究背景与问题定义
- 相关工作梳理
- 核心方法详解（含数学公式推导）
- 实验设计与结果分析
- 优缺点评价
- 个人思考与启发
- 关键词与核心概念

**三种笔记模式:**
```bash
sf notes paper.pdf --mode deep    # 深度学习笔记 (全面深入)
sf notes paper.pdf --mode exam    # 考试复习笔记 (公式+自测题)
sf notes paper.pdf --mode quick   # 快速笔记 (1-2页精炼)
```

---

### 🧠 6. 思维导图 ([查看 HTML](examples/attention_is_all_you_need/mindmap.html))

交互式思维导图，使用 Markmap 可视化，可以展开/折叠各个分支，覆盖论文的所有关键内容。

浏览器中打开 `mindmap.html` 即可查看交互式思维导图。

---

### 🖼️ 7. 学术海报 ([查看 HTML](examples/attention_is_all_you_need/poster.html))

A0横版学术海报，包含 Introduction、Method、Results、Conclusion、References 等完整模块，精美的蓝色渐变设计。

浏览器中打开 `poster.html` 即可查看。

---

### 🌐 8. 双语翻译 ([完整文件](examples/attention_is_all_you_need/translate.md))

> **English Summary**
>
> **What**: This paper introduces the Transformer, a novel neural network architecture based entirely on self-attention mechanisms that replaces recurrent and convolutional layers in sequence transduction models.
>
> **Results**: On WMT 2014 English-to-German translation, the Transformer achieved 28.4 BLEU, surpassing all previous models including ensembles by over 2 BLEU.
>
> ---
>
> **中文摘要**
>
> **做了什么**：本文提出了Transformer，一种完全基于自注意力机制的全新神经网络架构。
>
> **主要结果**：在WMT 2014英德翻译任务中，达到28.4 BLEU分数，超过所有先前模型2个BLEU以上。
>
> ---
>
> | English | 中文 |
> |---------|------|
> | Self-Attention | 自注意力机制 |
> | Multi-Head Attention | 多头注意力 |
> | Positional Encoding | 位置编码 |
> | Scaled Dot-Product Attention | 缩放点积注意力 |
> | Layer Normalization | 层归一化 |

---

## 4种输入方式

```bash
sf full paper.pdf                           # PDF文件
sf full --title "Attention Is All You Need" # 论文标题 (自动搜索下载)
sf full --arxiv 1706.03762                  # arXiv ID
sf full --doi 10.48550/arXiv.1706.03762     # DOI
```

## 5种使用方式

- **CLI命令行**: `pip install scholarflow` → `sf full paper.pdf`
- **Web应用**: 拖拽上传PDF，勾选输出，一键下载
- **桌面应用**: Win/Mac安装包，拖入PDF即用
- **MCP Server**: Cursor/Claude Desktop直接调用
- **OpenClaw技能**: `clawhub install scholarflow`

## 支持的LLM

OpenAI GPT-4o | Claude | Gemini | DeepSeek | **MiniMax M2.7** | Ollama本地模型 | 任何litellm支持的模型

---

## 快速开始

### 安装

```bash
pip install scholarflow
```

### 配置API Key

```bash
# 方式1: 环境变量
export OPENAI_API_KEY=sk-xxx
# 或 MiniMax
export MINIMAX_API_KEY=sk-xxx

# 方式2: sf命令
sf config set api-key sk-xxx

# 方式3: .env文件
cp .env.example .env  # 编辑填入API Key
```

### 使用

```bash
# 快速筛选 - 这篇论文值不值得读？(最快，几秒)
sf scan --arxiv 1706.03762

# 生成全套材料 (8种输出)
sf full --arxiv 1706.03762 --lang zh

# 单独生成
sf slides paper.pdf                    # PPT
sf slides paper.pdf --beamer           # Beamer PDF
sf script paper.pdf                    # 讲解稿
sf notes paper.pdf --mode deep         # 深度笔记
sf notes paper.pdf --mode exam         # 考试复习笔记
sf mindmap paper.pdf                   # 思维导图
sf poster paper.pdf                    # 学术海报
sf translate paper.pdf                 # 双语翻译

# 批量处理
sf batch ./papers/

# 指定模型
sf full paper.pdf --model minimax/MiniMax-M2.7
sf full paper.pdf --model deepseek/deepseek-chat
```

---

## 命令参考

```bash
sf full [PDF] [OPTIONS]      # 生成全部8种输出
sf scan [PDF] [OPTIONS]      # 快速筛选
sf slides [PDF] [OPTIONS]    # 生成PPT (--beamer 生成Beamer)
sf script [PDF] [OPTIONS]    # 生成讲解稿
sf notes [PDF] [OPTIONS]     # 生成笔记 (--mode deep/exam/quick)
sf mindmap [PDF] [OPTIONS]   # 生成思维导图
sf poster [PDF] [OPTIONS]    # 生成海报
sf translate [PDF] [OPTIONS] # 生成双语摘要
sf batch DIR [OPTIONS]       # 批量处理
sf config show/set           # 配置管理
```

**通用选项:**
| 选项 | 说明 |
|------|------|
| `--title, -t` | 论文标题 (自动搜索下载) |
| `--arxiv, -a` | arXiv ID 或链接 |
| `--doi, -d` | DOI号 |
| `--model, -m` | LLM模型 |
| `--lang, -l` | 输出语言 (`zh` / `en`) |
| `--verbosity, -v` | 详细度 (`concise` / `normal` / `detailed`) |
| `--output, -o` | 输出目录 |
| `--theme` | PPT主题 |
| `--beamer-theme` | Beamer主题 |
| `--notes-mode, -n` | 笔记模式 (`deep` / `exam` / `quick`) |

---

## 部署方式

### 方式1: pip安装 (最简单)
```bash
pip install scholarflow
sf full paper.pdf
```

### 方式2: Docker一键部署
```bash
git clone https://github.com/bcefghj/scholarflow
cd scholarflow
cp .env.example .env  # 填入API Key
docker compose -f docker/docker-compose.yml up -d
# 访问 http://localhost:8080
```

### 方式3: OpenClaw 小龙虾
```bash
clawhub install scholarflow
# 然后告诉小龙虾: "帮我分析论文 Attention Is All You Need"
```

### 方式4: MCP Server (Cursor / Claude Desktop)

在 MCP 配置中添加:
```json
{
  "mcpServers": {
    "scholarflow": {
      "command": "python",
      "args": ["-m", "mcp.server"]
    }
  }
}
```

---

## 与竞品对比

| 功能 | ScholarFlow | Paper2Slides | Auto-Slides | ChatPaper | SlidesAI |
|------|:-----------:|:------------:|:-----------:|:---------:|:--------:|
| 论文标题/DOI/arXiv输入 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 简要介绍+推荐指数 | ✅ | ❌ | ❌ | 部分 | ❌ |
| 汇报PPT (.pptx) | ✅ | ✅ | ❌ | ❌ | ✅ |
| Beamer幻灯片 | ✅ | ❌ | ✅ | ❌ | ❌ |
| PPT讲解稿 | ✅ | ❌ | ✅ | ❌ | ❌ |
| 学习笔记 (3种模式) | ✅ | ❌ | ❌ | ❌ | ❌ |
| 思维导图 | ✅ | ❌ | ❌ | ✅ | ❌ |
| 学术海报 | ✅ | ✅ | ❌ | ❌ | ✅ |
| 双语翻译 | ✅ | ❌ | ❌ | ✅ | ❌ |
| 一键全部生成 | ✅ | ❌ | ❌ | ❌ | ❌ |
| MCP Server | ✅ | ❌ | ❌ | ❌ | ❌ |
| OpenClaw技能 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 批量处理 | ✅ | ✅ | ❌ | ❌ | ❌ |
| MiniMax M2.7 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 保姆级教程 | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 项目结构

```
scholarflow/
├── scholarflow/          # 核心Python包
│   ├── fetcher/          # 论文获取 (arXiv/Semantic Scholar/DOI)
│   ├── parser/           # PDF解析 (PyMuPDF)
│   ├── analyzer/         # LLM分析 (litellm, 支持MiniMax)
│   ├── generator/        # 8种输出生成器
│   ├── prompts/          # Jinja2 Prompt模板
│   ├── templates/        # LaTeX/HTML输出模板
│   └── pipeline.py       # 主流水线
├── cli/                  # CLI工具 (sf命令)
├── web/                  # Web应用 (FastAPI)
├── mcp/                  # MCP Server
├── skill/                # OpenClaw Skill
├── docker/               # Docker部署
├── examples/             # 示例输出 (Attention Is All You Need)
└── docs/                 # 保姆级教程 (5篇)
```

---

## 保姆级教程 (小白友好)

1. [环境准备](docs/beginner-guide/01-环境准备.md) — Python安装、API Key获取
2. [本地安装使用](docs/beginner-guide/02-本地安装使用.md) — pip安装、基础命令
3. [服务器部署](docs/beginner-guide/03-服务器部署.md) — 云服务器、Docker、域名、HTTPS
4. [OpenClaw安装](docs/beginner-guide/04-OpenClaw安装.md) — 小龙虾技能安装使用
5. [桌面应用使用](docs/beginner-guide/05-桌面应用使用.md) — Win/Mac安装包

---

## Contributing

欢迎贡献! 请提交 Issue 或 Pull Request。

## License

MIT License

---

<a id="english"></a>

## English

### What is ScholarFlow?

ScholarFlow is the ultimate all-in-one academic paper processing tool. Give it a paper (PDF, title, DOI, or arXiv link), and it automatically generates **8 types of output**:

| Output | Format | Description |
|--------|--------|-------------|
| Brief Summary | .md | 200-500 word summary + reading recommendation score (1-5 stars) |
| Presentation PPT | .pptx | 10-15 slides, 3 themes, editable in PowerPoint/WPS |
| Beamer Slides | .pdf | Academic LaTeX Beamer with multiple themes |
| Speech Script | .pdf | Per-slide presentation notes (LaTeX) |
| Study Notes | .pdf | 3 modes: deep / exam / quick (LaTeX) |
| Mind Map | .html | Interactive Markmap visualization |
| Academic Poster | .html | A0 landscape poster |
| Bilingual Translation | .md | Chinese + English summary with key terms |

### Quick Start

```bash
pip install scholarflow
export OPENAI_API_KEY=sk-xxx  # or MINIMAX_API_KEY

# Quick scan - is this paper worth reading?
sf scan --arxiv 1706.03762

# Generate everything
sf full --arxiv 1706.03762 --lang en

# Individual outputs
sf slides paper.pdf
sf notes paper.pdf --mode exam
sf batch ./papers/
```

### Demo: Attention Is All You Need

All example outputs in [examples/attention_is_all_you_need/](examples/attention_is_all_you_need/) were generated by ScholarFlow using MiniMax M2.7.
