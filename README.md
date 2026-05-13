# CrewAI Content Creation Lab

这是一个基于 CrewAI 的实验项目，用于生成一周的 YouTube Shorts 内容规划。

主流程在 [C1M1_Lab_1_content_creation.ipynb](C1M1_Lab_1_content_creation.ipynb) 中完成：
- 加载 `.env` 配置
- 创建 `LLM`
- 定义 `Agent`
- 定义 `Task`
- 创建 `Crew`
- 执行 `crew.kickoff()` 并输出结果

## 项目结构

- `C1M1_Lab_1_content_creation.ipynb`：主实验 Notebook
- `utils.py`：环境变量加载工具
- `.env`：当前生效的配置文件
- `.env.deepseek`：DeepSeek 官方接口配置模板
- `.env.openrouter`：OpenRouter 配置模板
- `.env.provider`：额外 provider 配置备份文件
- `requirements.txt`：项目依赖

## 1. 创建虚拟环境

建议使用 `python -m venv` 创建独立虚拟环境。

如果你已经有可用的 Python 虚拟环境，也可以直接复用，不必重新创建。

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

如果你的系统里 `python3` 不可用，也可以使用：

```bash
python -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 2. 安装依赖

激活虚拟环境后执行：

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

当前项目依赖已包含 `crewai-tools`，用于 [C1M1_Lab_2_automatic_deep_research_solution.ipynb](C1M1_Lab_2_automatic_deep_research_solution.ipynb) 中的 `EXASearchTool` 和 `ScrapeWebsiteTool`。

如果你要运行 [C1M1_Lab_2_automatic_deep_research_solution.ipynb](C1M1_Lab_2_automatic_deep_research_solution.ipynb)，还需要安装 `exa-py`。该包为 Exa 搜索工具提供底层客户端，安装名是 `exa-py`，导入模块名是 `exa_py`。

如果你要把当前虚拟环境注册为 Notebook 内核，可执行：

```bash
python -m ipykernel install --user --name ppt-crewai --display-name "Python (.venv)"
```

然后在 VS Code/Jupyter 中选择对应内核。

## 3. 配置 API Provider

本项目不会直接读取 `.env.deepseek` 或 `.env.openrouter`。

`utils.py` 只会加载当前名为 `.env` 的文件，因此：
- `.env` 是唯一生效的运行配置
- `.env.deepseek` 和 `.env.openrouter` 是模板文件

### 方式一：直接编辑 `.env`

确保 `.env` 至少包含以下变量：

```dotenv
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=your_base_url
OPENAI_MODEL_NAME=your_model_name
```

### 方式二：用模板覆盖 `.env`

#### 使用 DeepSeek 官方接口

将 `.env.deepseek` 的内容复制到 `.env`，或直接覆盖：

```bash
cp .env.deepseek .env
```

#### 使用 OpenRouter

将 `.env.openrouter` 的内容复制到 `.env`：

```bash
cp .env.openrouter .env
```

> 切换 provider 后，务必重启 Notebook 内核再重新运行，否则旧的环境变量可能仍然留在当前会话中。

## 4. 运行 Notebook

1. 打开 `C1M1_Lab_1_content_creation.ipynb`
2. 选择刚才创建的 `.venv` 内核
3. 从上到下依次运行所有单元
4. 成功后会看到当前使用的模型和 API Base，并输出一周内容规划结果

## 5. 常见问题

### 1) `Missing OPENAI_MODEL_NAME`

说明 `.env` 中没有设置 `OPENAI_MODEL_NAME`。

### 2) `Missing OPENAI_API_KEY`

说明 `.env` 中没有设置 `OPENAI_API_KEY`，或当前内核没有正确加载 `.env`。

### 3) 日志里显示的 API Base 不是当前想要的 provider

通常是因为切换 `.env` 后没有重启 Notebook 内核。由于当前 Python 进程可能保留旧的 `OPENAI_*` 环境变量，建议：
- 重启内核
- 从第 1 个代码单元开始重新运行

### 4) 配置明明改成 DeepSeek，但仍然走 OpenRouter

请确认当前生效文件确实是 `.env`，而不是仅修改了 `.env.deepseek`。

### 5) `crew.kickoff()` 报鉴权错误

请检查以下三项是否匹配：
- `OPENAI_API_KEY`
- `OPENAI_API_BASE`
- `OPENAI_MODEL_NAME`

例如：
- DeepSeek 官方接口应使用 DeepSeek 对应的 base URL 和模型名
- OpenRouter 应使用 OpenRouter 对应的 base URL 和模型名

## 6. 安全说明

- 不要把真实 API Key 提交到版本库
- 建议只在本地保存包含真实密钥的 `.env`
- 模板文件建议保留占位符，不要保存真实密钥

## 7. 推荐工作流

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.deepseek .env   # 或 cp .env.openrouter .env
```

随后打开 Notebook，选择 `.venv` 内核并运行全部单元。
