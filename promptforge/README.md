# PromptForge - AI 提示词锻造工具

> 灵感来源于 GitHub 热门 AI 项目：prompts.chat (151k⭐)、caveman (83.8k⭐)、system-prompts-and-models-of-ai-tools (130k⭐)

## 简介

PromptForge 是一个一站式的 AI 提示词工程工具，帮助你**优化、测试、管理**提示词。

与现有项目的差异化：
- **prompts.chat** 只提供静态模板库 → PromptForge 还提供 AI 驱动的 token 优化引擎
- **caveman** 只做 token 压缩 → PromptForge 提供三级优化策略 (minimal/balanced/aggressive)
- **system-prompts** 只是收集展示 → PromptForge 支持多模型 A/B 测试和效果评分

## 功能

### 1. 提示词管理
- 创建、编辑、删除、搜索提示词
- 版本管理，追踪每次修改
- 分类和标签系统
- 自动 token 计数

### 2. Token 优化引擎
灵感来自 caveman (83.8k⭐) 和 ponytail (73.8k⭐) 项目。

三级优化策略：
| 策略 | 效果 | 说明 |
|------|------|------|
| minimal | ~15% 压缩 | 移除冗余短语和填充词 |
| balanced | ~30% 压缩 | 压缩指令格式 + 规范空白 |
| aggressive | ~45% 压缩 | 合并短句 + 去除冠词 |

### 3. 多模型测试台
- 支持 OpenAI (GPT-4o, GPT-4o-mini 等)
- 支持 Anthropic Claude (Claude Sonnet, Claude Haiku)
- Mock 模式（无需 API key 即可体验）
- 延迟、token 用量统计

### 4. 效果评分系统
四个维度评分 (0-10)：
- **清晰度** - 句子长度和可读性
- **具体性** - 约束条件和格式规范
- **结构性** - 组织层次和格式化
- **Token 效率** - token 使用效率

### 5. 精选模板库
内置 10+ 精选提示词模板，覆盖：
- 编程开发 (代码审查、API设计、调试)
- 写作创作 (博客、故事)
- 工作效率 (会议纪要、项目规划)
- AI/ML (提示词工程、数据分析)
- 系统提示词 (通用助手、编程助手)

## 快速开始

### Docker 部署 (推荐)

```bash
# 克隆仓库
git clone https://github.com/Eileenes/promptforge.git
cd promptforge

# 配置 API Key (可选，不配置则使用 Mock 模式)
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 启动
docker-compose up -d

# 访问 http://localhost:8777
```

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动
python main.py

# 访问 http://localhost:8777
```

## API 文档

启动后访问 `http://localhost:8777/docs` 查看 Swagger UI。

主要端点：
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/prompts` | 列出所有提示词 |
| POST | `/api/prompts` | 创建提示词 |
| PUT | `/api/prompts/{id}` | 更新提示词 |
| DELETE | `/api/prompts/{id}` | 删除提示词 |
| POST | `/api/optimize` | 优化提示词 |
| POST | `/api/optimize/save` | 优化并保存为新版本 |
| GET | `/api/test/providers` | 列出 LLM 提供商 |
| POST | `/api/test/run` | 运行测试 |
| POST | `/api/test/benchmark` | 效果评分 |
| GET | `/api/library` | 获取模板库 |
| POST | `/api/library/import` | 导入模板 |

## 技术栈

- **后端**: Python 3.13 + FastAPI + SQLite
- **前端**: 原生 HTML/CSS/JS (无构建步骤)
- **Token 计数**: tiktoken
- **部署**: Docker + docker-compose

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `OPENAI_API_KEY` | OpenAI API Key | (空，使用 Mock 模式) |
| `ANTHROPIC_API_KEY` | Anthropic API Key | (空，使用 Mock 模式) |

## License

MIT
