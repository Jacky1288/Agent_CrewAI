# Deep Research Crew

基于 [CrewAI](https://crewai.com) 构建的**并行深度研究工作流**。给定一个研究问题（`user_query`），由四个分工明确的 Agent 协作完成「规划 → 并行调研 → 事实核查 → 出报告」，最终产出一份带图表和引用的 Markdown 研究报告 `final_report.md`。

---

## 项目结构

```
deep_research_crew/
├── .env                              # 多 provider 配置模板（无真实 key）
├── .env.bak                          # 你本地真实 key（已 gitignore）
├── pyproject.toml                    # 依赖声明
├── knowledge/
│   └── user_preference.txt           # （可选）用户偏好知识源
├── src/deep_research_crew/
│   ├── main.py                       # 入口：定义 user_query 并 kickoff
│   ├── crew.py                       # Crew/Agent/Task 装配
│   ├── utils.py                      # 加载 .env、解析 MODEL 等
│   ├── config/
│   │   ├── agents.yaml               # 4 个 Agent 的 role/goal/backstory
│   │   └── tasks.yaml                # 6 个 Task 的 description/expected_output
│   ├── tools/
│   │   └── chart_generator_tool.py   # 自定义工具：生成 matplotlib/seaborn 图
│   └── guardrails/
│       └── guardrails.py             # write_report_guardrail
└── final_report.md                   # 运行后输出（已 gitignore）
```

### Agent / Task 矩阵

| Agent | 用到的工具 | 对应的 Task |
|---|---|---|
| `research_planner` | — | `create_research_plan` |
| `topic_researcher` | EXASearchTool + ScrapeWebsiteTool | `research_main_topics`、`research_secondary_topics` |
| `fact_checker` | EXASearchTool + ScrapeWebsiteTool | `validate_main_topics`、`validate_secondary_topics` |
| `report_writer` | ChartGeneratorTool（自研） | `write_final_report` |

工作流是顺序执行 6 个 task。原工程把 `research_main_topics` 和 `research_secondary_topics` 设为 `async_execution=True` 想做并行；但目前已**关闭并行**（见 FAQ #5）。

---

## 安装

需要 Python 3.10–3.13。

```bash
# 进项目根目录
cd deep_research_crew

# 创建并激活 venv（推荐用项目自己的 .venv，不要复用别的）
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖（editable mode）
pip install -e .
```

依赖列表（见 `pyproject.toml`）：
- `crewai[tools,anthropic]==1.14.4` — 主框架 + 自带工具 + Anthropic 原生 provider
- `litellm>=1.55.0` — 万能模型适配层（详见下一节）
- `pandas / matplotlib / seaborn` — `ChartGeneratorTool` 用
- `python-dotenv` — 加载 `.env`
- `exa-py` — Exa 搜索 SDK

---

## 配置 `.env`

`deep_research_crew/.env` 是**模板**，所有 key 都是占位符。**实际运行前**：

1. 复制一份本地工作副本：`cp .env .env.bak`（或直接在 `.env` 编辑）
2. 选一个 provider 组（5 个里挑 1），删 `#` 取消注释
3. 把其余组继续用 `#` 注释掉
4. 填入真实 key

### 当前支持的 5 组 provider

| 组号 | Provider | MODEL 示例 | 备注 |
|---|---|---|---|
| [1] | DeepSeek | `deepseek/deepseek-chat` | 便宜，国内可用；模型名只能用 `deepseek-chat`（V3）或 `deepseek-reasoner`（R1），**不存在 v4-flash**（见 FAQ #4） |
| [2] | Anthropic Claude | `anthropic/claude-haiku-4-5` 或 `claude-sonnet-4-6` | 质量高但有 TPM 限速（见 FAQ #7） |
| [3] | OpenAI 官方 | `gpt-4o` / `gpt-4o-mini` | 标准选项 |
| [4] | OpenAI 兼容代理 | `openai/deepseek-chat` + `OPENAI_BASE_URL` | OpenRouter / SiliconFlow / Together / 自建 vLLM 等都走这条 |
| [5] | Ollama 本地 | `ollama/qwen2.5:14b` | 完全免费，需先 `ollama serve` |

切换 provider **只改 `.env` 一处**，代码无需改动。

---

## 运行

```bash
crewai run
```

正常流程：
1. `research_planner` 把 `user_query` 拆成 main / secondary topics
2. `topic_researcher` 顺序调研两组（用 Exa 搜索 + 网页抓取）
3. `fact_checker` 验证两组结果
4. `report_writer` 调用 `ChartGeneratorTool` 生成图表，写 `final_report.md`

修改入参：编辑 `src/deep_research_crew/main.py` 里的 `inputs["user_query"]`。

---

## LiteLLM 是什么

[LiteLLM](https://docs.litellm.ai/) 是一个**统一适配层**，让你用同一套 OpenAI 风格 API 调用 100+ 模型 provider（OpenAI / Anthropic / Gemini / Cohere / Bedrock / OpenRouter / Together / SiliconFlow / Moonshot / Qwen / 自建 vLLM / Ollama 等）。

### 它在这个工程的角色

- CrewAI 1.14 已经**自带**几个原生 provider（`deepseek/`、`anthropic/`、`openai/`、`gemini/` 等），跑这些走的是 CrewAI 直连，**不经过 LiteLLM**
- 你想用**冷门 provider**（如 Moonshot Kimi、阿里 Qwen、SiliconFlow 上的小模型）或**自建端点**时，LiteLLM 会自动接管，把 MODEL 字符串映射到对应 SDK 调用
- 因此装 LiteLLM 是「以备未来灵活切换」，不是当前必需

### 模型名前缀速查（LiteLLM 路由依据）

| 前缀 | 示例 | 走哪条路径 |
|---|---|---|
| `deepseek/` | `deepseek/deepseek-chat` | CrewAI 原生 DeepSeek provider |
| `anthropic/` | `anthropic/claude-sonnet-4-6` | CrewAI 原生 Anthropic provider（需要 `crewai[anthropic]`） |
| `gpt-4o` / 无前缀 | `gpt-4o-mini` | CrewAI 原生 OpenAI provider |
| `openai/` + 其他模型名 | `openai/deepseek-chat` | OpenAI 兼容代理（看 `OPENAI_BASE_URL`） |
| `openrouter/` | `openrouter/anthropic/claude-3-opus` | LiteLLM 路由到 OpenRouter |
| `ollama/` | `ollama/qwen2.5:14b` | LiteLLM 路由到本地 Ollama |
| `gemini/` / `cohere/` / ... | 同上 | LiteLLM 各家 SDK |

---

## 常见问题（FAQ）—— 实战踩坑记录

### #1 `source: no such file or directory: .../venv/activate`

激活路径写错了，正确语法：

```bash
source /path/to/venv/bin/activate
```

注意 `venv` 里有个 `bin/` 子目录。

---

### #2 `warning: VIRTUAL_ENV=xxx does not match the project environment path .venv`

`uv`（CrewAI 内部包管理器）检测到你激活的 venv 不是项目自己的 `.venv`。

**解决**：要么用项目自己的 `.venv`，要么 `unset VIRTUAL_ENV`：

```bash
deactivate
source ./deep_research_crew/.venv/bin/activate
```

---

### #3 `command not found: crewai` 或 `command not found: uv`

新建的 `.venv` 里没有自动装 `crewai` CLI 和 `uv`。

**解决**：

```bash
# 先激活项目 venv
source .venv/bin/activate

# 装项目依赖（包括 crewai CLI）
pip install -e .

# uv 不是必需，需要的话单独装
brew install uv     # 或者 curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

### #4 `Unable to initialize LLM with model 'openai/deepseek-v4-flash'`

两个错误叠加：
1. **`deepseek-v4-flash` 不是真实模型名**。DeepSeek 实际只有 `deepseek-chat`（V3）和 `deepseek-reasoner`（R1），目前没有 V4
2. 用错前缀。原生 provider 用 `deepseek/deepseek-chat`，**不要写成 `openai/...`**

**解决**：

```bash
MODEL=deepseek/deepseek-chat
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_API_BASE=https://api.deepseek.com
```

---

### #5 `tool_use ids were found without tool_result blocks immediately after`（DeepSeek/Anthropic 都会撞）

这是**并行 task + 原生 tool-calling provider 的已知 bug**。CrewAI 在重组消息历史时把含 `tool_use` 的 assistant 消息发回去了，但对应的 `tool_result` 没全部跟上；OpenAI 端容忍这种情况，DeepSeek 和 Anthropic 会严格校验 400 错。

**解决**：把 `crew.py` 里两个 research task 的 `async_execution=True` **改为 `False`**：

```python
@task
def research_main_topics(self) -> Task:
    return Task(
        config=self.tasks_config["research_main_topics"],
        async_execution=False,   # ← 关键
    )
```

代价：顺序执行，耗时翻倍但稳定。等 CrewAI 修复并行模式下的消息重组逻辑后可恢复并行。

---

### #6 `Anthropic native provider not available, to install: uv add "crewai[anthropic]"`

需要 Anthropic 原生 provider 但没装 SDK。

**解决**：在 `pyproject.toml` 把 extras 改成：

```toml
"crewai[tools,anthropic]==1.14.4"
```

然后 `pip install -e .`。**注意**：`crewai[litellm]` 这个 extra **不存在**（CrewAI 1.14 错误信息里写的安装命令是过期的），litellm 要单独装：`pip install litellm`。

---

### #7 `Error code: 429 - rate_limit_error ... 30,000 input tokens per minute`

Anthropic 新账号 Tier 1 的 TPM 限额是 30k，但 research agent 抓多个网页累积 prompt 容易超。

**几种解法**：
1. 换 Haiku 4.5（TPM 和 Sonnet 独立分桶）：`MODEL=anthropic/claude-haiku-4-5`
2. 充值升 Tier 2（$40+，提到 50k TPM）
3. 减少 EXA 搜索结果上限、缩小 max_iter
4. 换非 Anthropic 的 provider

---

### #8 `Error code: 529 - overloaded_error`

Anthropic 服务端临时过载，不是你的问题。

**解决**：等 5–10 分钟重试；查看 https://status.claude.com；或临时换 provider。

---

### #9 `The OPENAI_API_KEY environment variable is not set`（warning，但 task 失败）

`TextFileKnowledgeSource` 默认用 OpenAI embedding（`text-embedding-3-small`）做向量化，与你的 LLM provider 无关。

**解决**：三选一：
1. **注释掉 `knowledge_sources`**（推荐，简单）—— 见 `crew.py` 底部
2. 在 `.env` 同时配 `OPENAI_API_KEY` 仅用于 embedding
3. 改用本地 embedder（Ollama / sentence-transformers），需额外配置 CrewAI 的 `embedder=` 参数

---

### #10 `'latin-1' codec can't encode characters in position 0-4`（Exa 工具）

HTTP 请求头要求 latin-1 编码，但你的 `EXA_API_KEY` 里有非 ASCII 字符（典型场景：占位符里有中文）。

**解决**：把 `.env` 的 `EXA_API_KEY` 改成真实的 Exa key（去 https://dashboard.exa.ai/api-keys 拿）。Exa key 形如 `ee74c90f-xxxx-xxxx-xxxx-xxxxxxxxxxxx`。

---

### #11 `KeyError: 'create_research_plan'`（或其他 task 名）

`tasks.yaml` 里没定义这个 task 名，但 `crew.py` 引用了它。常见原因：
- `tasks.yaml` 被误填成 agents 配置（内容和 `agents.yaml` 一样）
- 工程从顺序版（4 task）升级到并行版（6 task），但 yaml 没更新

**解决**：确保 `config/tasks.yaml` 里有 `crew.py` 用到的所有 task key：`create_research_plan`、`research_main_topics`、`research_secondary_topics`、`validate_main_topics`、`validate_secondary_topics`、`write_final_report`。

---

### #12 提交前如何防止真实 key 泄漏

经验做法：
- `.env` 只放占位符（如 `sk-your-key-here`），**真实 key 放 `.env.bak`**
- `.gitignore` 包含 `.env.bak`
- 万一 key 已经写进过 `.env` 并 commit，**立刻去后台 revoke + 生成新 key**——光是 `git rm` 不够，历史里还在
- 提交前用 `grep -E "sk-[A-Za-z0-9]{20,}|[a-f0-9]{8}-[a-f0-9]{4}"` 扫描即将 staged 的文件

---

## Support

- CrewAI 文档：https://docs.crewai.com
- CrewAI 仓库：https://github.com/crewAIInc/crewAI
- LiteLLM 文档：https://docs.litellm.ai
- Exa 文档：https://docs.exa.ai
- DeepSeek 控制台：https://platform.deepseek.com
- Anthropic 控制台：https://console.anthropic.com
