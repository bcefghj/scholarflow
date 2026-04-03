# ScholarFlow × OpenClaw（小龙虾）使用指南（保姆级教程）

本教程说明如何安装 **OpenClaw（常被社区称为「小龙虾」）**、通过 **ClawHub** 安装 **ScholarFlow 技能（Skill）**、在对话中使用 ScholarFlow，以及在 **Cursor** 中配置 **MCP Server** 调用 ScholarFlow。

> **前置条件**：已具备可用的 **Python 环境** 与 **大模型 API Key**（见 **01-环境准备.md**）。OpenClaw 本体安装方式可能随版本更新，请以官方文档为准。

---

## 1. OpenClaw（小龙虾）是什么？

**OpenClaw** 是一类 **AI 智能体 / 助手** 运行环境（具体名称与版本以官方为准），可以通过 **技能（Skills）** 扩展能力。**ScholarFlow** 提供了可在 ClawHub 上安装的 Skill，让你在对话里用自然语言完成「读论文、做 PPT、写笔记」等任务。

---

## 2. 安装 OpenClaw

OpenClaw 的安装步骤会随项目迭代变化，建议 **优先阅读官方指南**：

- 中文入门参考（第三方整理，示例）：[OpenClaw Launch 指南](https://openclawlaunch.com/zh/guide)

下面给出常见思路，**若与官方文档冲突，以官方为准**：

1. 根据官方要求准备 **Node.js**、**Python** 或 **Docker** 等依赖。  
2. 按文档完成 **安装、启动、登录**（部分场景需要绑定账号或 Token）。  
3. 确认 OpenClaw 能正常对话、执行基础指令后，再安装 Skill。

> **提示**：若你使用 **云服务器** 部署 OpenClaw，请同时完成 **防火墙 / 安全组** 放行与 **HTTPS**（若对外提供 Web），思路可参考 **03-服务器部署.md**。

---

## 3. 安装 ClawHub CLI 并登录

**ClawHub** 用于搜索、安装、管理 Skills。常见安装方式之一为全局安装 npm 包：

```bash
npm i -g clawhub
```

安装完成后检查：

```bash
clawhub --help
```

### 3.1 登录（若命令行提示需要 Token）

1. 打开 **ClawHub** 网站（社区常用入口示例）：**https://clawhub.ai/**  
2. 使用 **GitHub 等账号** 登录（以网站当前流程为准）。  
3. 在用户设置中创建 **API Token**。  
4. 在终端执行（示例）：

   ```bash
   clawhub login --token 你的Token
   ```

> **注意**：Token 属于敏感信息，勿提交到公开仓库或截图外传。

---

## 4. 通过 ClawHub 安装 ScholarFlow Skill

项目 README 推荐命令：

```bash
clawhub install scholarflow
```

### 4.1 安装成功后的典型效果

- OpenClaw 的技能列表中会出现 **scholarflow** 相关条目；  
- 你可以在对话中用自然语言触发论文分析、生成摘要等能力（具体以 Skill 内定义的指令为准）。

### 4.2 若安装失败或限频

1. 检查网络与 `clawhub login` 是否有效。  
2. 在 ClawHub 网站搜索 **scholarflow**，确认 Skill 名称与 README 一致。  
3. 部分社区文章提到 **国内镜像或手动解压 Skill 到工作区**（路径因 OpenClaw 版本而异，例如 `~/.openclaw/workspace/skills`），若 CLI 不稳定可尝试手动方式。

---

## 5. 对话式使用示例（聊天风格）

安装 Skill 并确保 OpenClaw 已加载该技能后，可以尝试类似指令（**自然语言即可，以下为示例**）：

1. 「请用 ScholarFlow **快速扫一眼**这篇论文是否值得读：Attention Is All You Need。」  
2. 「我桌面上有 `paper.pdf`，请帮我生成 **中文** 的 **汇报要点** 和 **PPT 大纲**。」  
3. 「请对 arXiv **1706.03762** 跑一遍 **全套输出**，输出语言用中文。」

实际效果取决于：

- OpenClaw 是否将请求路由到 ScholarFlow Skill；  
- 本机或服务器上是否已配置 **`sf` 命令** 与 **API Key**；  
- Skill 内部定义的 **触发词与参数**。

若对话无响应，请到 OpenClaw 日志或 Skill 说明中查看 **必填环境变量**（如 `OPENAI_API_KEY`）。

---

## 6. 在 Cursor 中配置 MCP Server

ScholarFlow 仓库提供 **MCP（Model Context Protocol）** 服务端脚本（见项目 `mcp/server.py`）。在 **Cursor** 中可通过 MCP 让编辑器内的 AI 直接调用 ScholarFlow 能力。

### 6.1 依赖安装

MCP 相关依赖在可选组件 **`mcp`** 中，需使用 **包含 `mcp` 包源码或开发安装** 的方式。仓库中 **`mcp` 位于项目根目录**，若仅用 `pip install scholarflow` 默认 wheel **可能不包含** `mcp` 顶层包，因此推荐：

**方式 A：克隆仓库并 editable 安装（推荐开发者）**

```bash
git clone https://github.com/bcefghj/scholarflow.git
cd scholarflow
python -m pip install -e ".[mcp]"
```

**方式 B：在克隆目录下用虚拟环境 + 依赖**

```bash
cd scholarflow
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[mcp]"
```

### 6.2 Cursor 的 MCP 配置示例

在 Cursor 的 MCP 设置中新增服务（路径因 Cursor 版本略有不同，一般在 **Settings → MCP** 或编辑 JSON 配置文件），示例如下：

```json
{
  "mcpServers": {
    "scholarflow": {
      "command": "python",
      "args": ["-m", "mcp.server"],
      "cwd": "/绝对路径/scholarflow"
    }
  }
}
```

请将 **`cwd`** 换成你本机 **克隆下来的 `scholarflow` 仓库根目录**（该目录下应有 `mcp/server.py`）。

若你使用虚拟环境，请将 **`command`** 改为虚拟环境里 Python 的**绝对路径**，例如：

- macOS / Linux：`/path/to/scholarflow/.venv/bin/python`  
- Windows：`C:\\path\\to\\scholarflow\\.venv\\Scripts\\python.exe`

### 6.3 环境变量

MCP 进程需能读取 **API Key**，可在系统环境变量中设置 `OPENAI_API_KEY` 等，或在 Cursor 的 MCP 配置中按文档支持的方式传入（以 Cursor 当前版本说明为准）。

### 6.4 验证

保存配置后 **重启 Cursor**，在 MCP 面板中查看 **scholarflow** 是否显示为已连接；然后在对话中尝试「调用 ScholarFlow 分析某篇 PDF」类指令。

> **提示**：README 中的 MCP 片段为最小示例；实际部署时 **`cwd` 与 Python 解释器路径** 是最容易出错的两项，请逐项核对。

---

## 7. 常见问题

| 现象 | 可能原因 | 处理方向 |
|------|----------|----------|
| `clawhub: command not found` | 未安装或 npm 全局路径未加入 PATH | 重新执行 `npm i -g clawhub` 并检查 PATH |
| `clawhub install` 报错 | 未登录、网络、限频 | `clawhub login`、换网络或稍后重试 |
| Cursor MCP 无法连接 | `cwd` 错误、未装 `[mcp]`、Python 不对 | 按第 6 节逐项检查 |
| 对话不执行论文任务 | API Key 未配置 | 配置环境变量或 `sf config set api-key` |

---

## 8. 相关链接

| 资源 | 地址 |
|------|------|
| ScholarFlow 仓库 | https://github.com/bcefghj/scholarflow |
| ClawHub（示例） | https://clawhub.ai/ |
| 本地 CLI 教程 | **02-本地安装使用.md** |

完成 OpenClaw 侧配置后，若你更习惯 **图形界面**，可继续阅读 **05-桌面应用使用.md**。
