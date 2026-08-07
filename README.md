# 🔧 PromptForge

**AI Prompt Engineering Toolkit**

[English](#english) | [中文](#中文)

---

## English

> Inspired by GitHub trending AI projects: prompts.chat (151k⭐), caveman (83.8k⭐), system-prompts-and-models-of-ai-tools (130k⭐)

### Introduction

PromptForge is an all-in-one AI prompt engineering toolkit that helps you **optimize, test, and manage** prompts.

Key differentiators from existing projects:
- **prompts.chat** only provides static template library → PromptForge adds AI-driven token optimization engine
- **caveman** only does token compression → PromptForge offers three optimization strategies (minimal/balanced/aggressive)
- **system-prompts** only collects and displays → PromptForge supports multi-model A/B testing and effectiveness scoring

### Features

#### 1. Prompt Management
- Create, edit, delete, search prompts
- Version control, track every modification
- Category and tag system
- Automatic token counting

#### 2. Token Optimization Engine
Inspired by caveman (83.8k⭐) and ponytail (73.8k⭐).

Three optimization strategies:
| Strategy | Effect | Description |
|----------|--------|-------------|
| minimal | ~15% compression | Remove redundant phrases and filler words |
| balanced | ~30% compression | Compress instruction format + normalize whitespace |
| aggressive | ~45% compression | Merge short sentences + remove articles |

#### 3. Multi-Model Test Bench
- Support OpenAI (GPT-4o, GPT-4o-mini, etc.)
- Support Anthropic Claude (Claude Sonnet, Claude Haiku)
- Mock mode (no API key required)
- Latency, token usage statistics

#### 4. Effectiveness Scoring
Four-dimensional scoring (0-10):
- **Clarity** - Sentence length and readability
- **Specificity** - Constraints and format specifications
- **Structure** - Organization and formatting
- **Token Efficiency** - Token usage efficiency

#### 5. Curated Template Library
10+ curated prompt templates covering:
- Coding (code review, API design, debugging)
- Writing (blog, story)
- Productivity (meeting notes, project planning)
- AI/ML (prompt engineering, data analysis)
- System prompts (general assistant, coding assistant)

### Quick Start

#### Docker (Recommended)

```bash
git clone https://github.com/Eileenes/promptforge.git
cd promptforge
cp .env.example .env  # Optional: configure API keys
docker-compose up -d
# Visit http://localhost:8777
```

#### Local

```bash
pip install -r requirements.txt
python main.py
# Visit http://localhost:8777
```

### API Documentation

Visit `http://localhost:8777/docs` for Swagger UI after starting.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/prompts` | List all prompts |
| POST | `/api/prompts` | Create a prompt |
| PUT | `/api/prompts/{id}` | Update a prompt |
| DELETE | `/api/prompts/{id}` | Delete a prompt |
| POST | `/api/optimize` | Optimize a prompt |
| POST | `/api/optimize/save` | Optimize and save as new version |
| GET | `/api/test/providers` | List LLM providers |
| POST | `/api/test/run` | Run a test |
| POST | `/api/test/benchmark` | Effectiveness scoring |
| GET | `/api/library` | Get template library |
| POST | `/api/library/import` | Import a template |

### Tech Stack

- **Backend**: Python 3.13 + FastAPI + SQLite
- **Frontend**: Native HTML/CSS/JS (no build step)
- **Deployment**: Docker + docker-compose

### License

MIT

---

## 中文

> 灵感来源于 GitHub 热门 AI 项目：prompts.chat (151k⭐)、caveman (83.8k⭐)、system-prompts-and-models-of-ai-tools (130k⭐)

### 简介

PromptForge 是一个一站式的 AI 提示词工程工具，帮助你**优化、测试、管理**提示词。

与现有项目的差异化：
- **prompts.chat** 只提供静态模板库 → PromptForge 还提供 AI 驱动的 token 优化引擎
- **caveman** 只做 token 压缩 → PromptForge 提供三级优化策略 (minimal/balanced/aggressive)
- **system-prompts** 只是收集展示 → PromptForge 支持多模型 A/B 测试和效果评分

### 功能

#### 1. 提示词管理
- 创建、编辑、删除、搜索提示词
- 版本管理，追踪每次修改
- 分类和标签系统
- 自动 token 计数

#### 2. Token 优化引擎
灵感来自 caveman (83.8k⭐) 和 ponytail (73.8k⭐) 项目。

三级优化策略：
| 策略 | 效果 | 说明 |
|------|------|------|
| minimal | ~15% 压缩 | 移除冗余短语和填充词 |
| balanced | ~30% 压缩 | 压缩指令格式 + 规范空白 |
| aggressive | ~45% 压缩 | 合并短句 + 去除冠词 |

#### 3. 多模型测试台
- 支持 OpenAI (GPT-4o, GPT-4o-mini 等)
- 支持 Anthropic Claude (Claude Sonnet, Claude Haiku)
- Mock 模式（无需 API key 即可体验）
- 延迟、token 用量统计

#### 4. 效果评分系统
四个维度评分 (0-10)：
- **清晰度** - 句子长度和可读性
- **具体性** - 约束条件和格式规范
- **结构性** - 组织层次和格式化
- **Token 效率** - token 使用效率

#### 5. 精选模板库
内置 10+ 精选提示词模板，覆盖：
- 编程开发 (代码审查、API设计、调试)
- 写作创作 (博客、故事)
- 工作效率 (会议纪要、项目规划)
- AI/ML (提示词工程、数据分析)
- 系统提示词 (通用助手、编程助手)

### 快速开始

#### Docker 部署 (推荐)

```bash
git clone https://github.com/Eileenes/promptforge.git
cd promptforge
cp .env.example .env  # 可选：配置 API Key
docker-compose up -d
# 访问 http://localhost:8777
```

#### 本地运行

```bash
pip install -r requirements.txt
python main.py
# 访问 http://localhost:8777
```

### API 文档

启动后访问 `http://localhost:8777/docs` 查看 Swagger UI。

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

### 技术栈

- **后端**: Python 3.13 + FastAPI + SQLite
- **前端**: 原生 HTML/CSS/JS (无构建步骤)
- **部署**: Docker + docker-compose

### License

MIT
