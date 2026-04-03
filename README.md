# ScholarFlow 📚

**全网最强的学术论文处理工具** — 一个工具，搞定所有论文处理需求。

输入一篇论文（PDF / 标题 / DOI / arXiv链接），自动生成 **简要介绍 + 汇报PPT + PPT讲解稿 + 学习笔记 + 思维导图 + 学术海报 + 双语翻译** 全套材料。

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
> **现在**: `sf full paper.pdf` — 一个命令，全部搞定。

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

OpenAI GPT-4o | Claude | Gemini | DeepSeek | MiniMax M2.7 | Ollama本地模型 | 任何litellm支持的模型

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

# 方式2: sf命令
sf config set api-key sk-xxx

# 方式3: .env文件
cp .env.example .env  # 编辑填入API Key
```

### 使用

```bash
# 快速筛选 - 这篇论文值不值得读？(最快，几秒)
sf scan --arxiv 1706.03762

# 生成全套材料
sf full --arxiv 1706.03762 --lang zh

# 单独生成PPT
sf slides paper.pdf --theme academic_blue

# 考试复习笔记
sf notes paper.pdf --mode exam

# 批量处理文件夹中所有PDF
sf batch ./papers/
```

---

## 示例: Attention Is All You Need

使用 Transformer 经典论文作为示例:

```bash
sf full --arxiv 1706.03762 --lang zh --output ./examples/attention
```

### 简要介绍输出 (summary.md)

> **一句话总结**: 本文提出了Transformer架构——一种完全基于注意力机制的序列转换模型，彻底摒弃了循环和卷积结构，在机器翻译任务上取得了当时最优结果，并深刻改变了整个深度学习领域的发展方向。
>
> **核心贡献**:
> 1. 提出Transformer架构: 第一个完全基于自注意力机制的序列到序列模型
> 2. 多头注意力机制(Multi-Head Attention): 允许模型同时关注不同位置的不同表示子空间
> 3. 位置编码(Positional Encoding): 用正弦/余弦函数注入序列位置信息
> 4. 大幅提升训练效率: 高度并行化，8个GPU仅需3.5天
> 5. 建立了GPT、BERT、T5等所有大语言模型的基础架构
>
> **推荐指数: ⭐⭐⭐⭐⭐** (5/5)
>
> **推荐理由**: 深度学习领域最重要的论文之一，Transformer已成为现代AI的基石架构，无论做什么方向都值得精读。

完整示例文件见 [examples/attention_is_all_you_need/](examples/attention_is_all_you_need/)

---

## 命令参考

```bash
sf full [PDF] [OPTIONS]      # 生成全部输出
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
- `--title, -t`: 论文标题 (自动搜索下载)
- `--arxiv, -a`: arXiv ID 或链接
- `--doi, -d`: DOI号
- `--model, -m`: LLM模型 (如 `openai/gpt-4o`, `minimax/MiniMax-M2.7`)
- `--lang, -l`: 输出语言 (`zh` 中文 / `en` 英文)
- `--verbosity, -v`: 详细度 (`concise` / `normal` / `detailed`)
- `--output, -o`: 输出目录

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
| 论文标题/DOI输入 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 简要介绍+推荐指数 | ✅ | ❌ | ❌ | 部分 | ❌ |
| 汇报PPT (.pptx) | ✅ | ✅ | ❌ | ❌ | ✅ |
| Beamer幻灯片 | ✅ | ❌ | ✅ | ❌ | ❌ |
| PPT讲解稿 | ✅ | ❌ | ✅ | ❌ | ❌ |
| 学习笔记 (3种模式) | ✅ | ❌ | ❌ | ❌ | ❌ |
| 思维导图 | ✅ | ❌ | ❌ | ✅ | ❌ |
| 学术海报 | ✅ | ✅ | ❌ | ❌ | ✅ |
| 双语翻译 | ✅ | ❌ | ❌ | ✅ | ❌ |
| 一键全部生成 | ✅ | ❌ | ❌ | ❌ | ❌ |
| CLI | ✅ | ✅ | ✅ | ✅ | ❌ |
| Web应用 | ✅ | ❌ | ❌ | ✅ | ❌ |
| 桌面应用 | ✅ | ❌ | ❌ | ❌ | ❌ |
| MCP Server | ✅ | ❌ | ❌ | ❌ | ❌ |
| OpenClaw技能 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 批量处理 | ✅ | ✅ | ❌ | ❌ | ❌ |
| MiniMax M2.7 | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 项目结构

```
scholarflow/
├── scholarflow/          # 核心Python包
│   ├── fetcher/          # 论文获取 (arXiv/Semantic Scholar)
│   ├── parser/           # PDF解析 (PyMuPDF)
│   ├── analyzer/         # LLM分析 (litellm)
│   ├── generator/        # 输出生成 (PPTX/LaTeX/HTML)
│   ├── prompts/          # Prompt模板 (Jinja2)
│   ├── templates/        # 输出模板 (LaTeX/HTML)
│   └── pipeline.py       # 主流水线
├── cli/                  # CLI工具
├── web/                  # Web应用
├── mcp/                  # MCP Server
├── skill/                # OpenClaw Skill
├── docker/               # Docker部署
├── examples/             # 示例输出
└── docs/                 # 文档与教程
```

---

## Contributing

欢迎贡献! 请提交 Issue 或 Pull Request。

## License

MIT License

---

<a id="english"></a>

## English

### What is ScholarFlow?

ScholarFlow is the ultimate all-in-one academic paper processing tool. Give it a paper (PDF, title, DOI, or arXiv link), and it automatically generates:

- **Brief Summary** — Decide if a paper is worth reading in 2 minutes
- **Presentation PPT** — Ready-to-use slides for seminars (.pptx)
- **Beamer Slides** — Academic-style LaTeX PDF slides
- **Speech Script** — Per-slide presentation notes (LaTeX PDF)
- **Study Notes** — 3 modes: deep study / exam review / quick notes (LaTeX PDF)
- **Mind Map** — Interactive HTML visualization
- **Academic Poster** — A0 landscape poster (HTML)
- **Bilingual Translation** — Chinese + English summary

### Quick Start

```bash
pip install scholarflow
export OPENAI_API_KEY=sk-xxx

# Quick scan
sf scan --arxiv 1706.03762

# Generate everything
sf full --arxiv 1706.03762 --lang en

# Just slides
sf slides paper.pdf

# Exam review notes
sf notes paper.pdf --mode exam

# Batch process
sf batch ./papers/
```
