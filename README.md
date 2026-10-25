# 智能数据 Agent

一个基于**大模型 + 数据库**的前后端分离智能数据分析系统。支持上传结构化表格与文本文档入库，用户通过与 Agent 对话，由 Agent 基于数据库中的数据自动生成 SQL 查询、检索相关文档并给出分析回答，支持表格与图表可视化。

## 核心特性

- **前后端分离**：FastAPI 后端 + Vue 3 前端，接口 RESTful，聊天采用 SSE 流式输出。
- **用户与权限**：登录 / 注册，分**管理员**与**客户端**两种角色。
  - 管理员：可上传数据（数据管理）+ 智能对话。
  - 客户端：仅智能对话，可基于全部已上传数据分析问答。
- **数据入库**：支持结构化表格（CSV / Excel）与文本文档（txt / md / pdf / docx）两种类型。
- **智能分析（SQL + RAG 混合）**：
  - 结构化数据：Agent 自动生成 SELECT 查询并执行，返回结果表格。
  - 文本数据：TF-IDF + 中文分词（jieba）检索相关文档片段作为参考（RAG）。
  - 回答由大模型综合 SQL 结果与文档片段生成，支持柱状图 / 折线图 / 饼图可视化。
- **大模型可配置**：默认 **Mock 模式**即可跑通全流程演示；配置好密钥后自动切换为真实大模型（OpenAI 兼容接口）。

## 技术栈 / 框架

| 端 | 技术 |
|---|---|
| 后端 | Python 3.10+、FastAPI、Uvicorn、SQLAlchemy、PyMySQL、pandas、scikit-learn、jieba |
| 前端 | Vue 3、Vite、Vue Router、Pinia、Element Plus、ECharts、Axios |
| 数据库 | MySQL 8（业务表），文本向量索引使用本地 TF-IDF（无需额外向量库） |
| 大模型 | OpenAI 兼容 API（可配置 base_url / api_key / model），内置 Mock 模式 |

## 系统架构

```
┌─────────────────────────┐        ┌──────────────────────────────┐
│        前端 (Vue3)       │  REST  │          后端 (FastAPI)       │
│ ┌───────────┬─────────┐ │ ─────► │ ┌──────────────────────────┐ │
│ │ 数据管理    │  Agent对话│ │        │ │ 上传入库 / 认证 / 聊天 SSE │ │
│ │(仅管理员) │ (所有用户)│ │ ◄───── │ │ SQL Agent + RAG + LLM     │ │
│ └───────────┴─────────┘ │ SSE    │ └──────────┬───────────────┘ │
└─────────────────────────┘        └────────────┼────────────────┘
                                                │
                                    ┌───────────┴──────────┐
                                    │        MySQL         │
                                    │  datasets / 数据表     │
                                    │  document_chunks      │
                                    │  users / chat_messages│
                                    └──────────────────────┘
```

### 数据流转

1. **上传**：管理员上传文件 → 后端解析。
   - 表格：pandas 推断类型 → 在 MySQL 建表（`dataset_{id}`）并批量写入，登记列结构与表名。
   - 文档：提取文本 → 切分片段（`document_chunks`），后续由 TF-IDF 检索。
2. **对话**：用户提问 → 后端同时做两件事：
   - **结构化侧**：Agent 依据已登记的表结构生成 SELECT SQL 并执行，得到结果集。
   - **文本侧（RAG）**：jieba 分词 + TF-IDF 相似度检索最相关的文档片段。
   - **汇总**：大模型综合 SQL 结果 + 检索片段生成自然语言回答，SSE 流式返回；结果表格/图表在对话中渲染。

## 目录结构

```
移动云杯/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口（路由、CORS、建库、种子管理员）
│   │   ├── config.py            # 配置（MySQL、LLM、JWT 密钥）
│   │   ├── database.py          # 数据库连接与建表
│   │   ├── models.py            # ORM 模型（Dataset/Chunk/Message/User）
│   │   ├── schemas.py           # Pydantic 模型
│   │   ├── deps.py              # 登录/管理员鉴权依赖
│   │   ├── routers/
│   │   │   ├── auth.py          # 注册 / 登录
│   │   │   ├── upload.py        # 数据上传（仅管理员）
│   │   │   ├── datasets.py      # 数据集列表
│   │   │   └── chat.py          # 聊天 SSE 接口（SQL + RAG）
│   │   ├── services/
│   │   │   ├── ingest.py        # CSV/Excel/文档解析入库
│   │   │   ├── vector_store.py  # TF-IDF + jieba 文本检索
│   │   │   ├── sql_agent.py     # SQL 生成与安全执行、图表建议
│   │   │   └── llm.py           # OpenAI 兼容客户端 + Mock 模式
│   │   └── utils/
│   │       └── auth.py          # 密码哈希 + JWT 工具
│   ├── run.py                   # 后端启动入口
│   ├── requirements.txt
│   ├── .env.example             # 配置样例
│   └── sample_data/             # 演示样例数据
├── frontend/
│   ├── src/
│   │   ├── App.vue              # 布局 + 角色菜单
│   │   ├── router/index.js      # 路由 + 登录守卫
│   │   ├── stores/auth.js       # 登录态 Pinia store
│   │   ├── api/index.js         # Axios 封装（Token 注入）
│   │   ├── views/
│   │   │   ├── LoginView.vue    # 登录/注册
│   │   │   ├── UploadView.vue   # 数据上传（管理员）
│   │   │   └── ChatView.vue     # Agent 对话
│   │   └── components/
│   │       ├── DataTable.vue    # 结果表格
│   │       └── DataChart.vue    # ECharts 图表
│   ├── package.json
│   └── vite.config.js           # dev 代理到后端
├── start.bat                    # 一键启动脚本
└── README.md
```

## 数据库表设计（MySQL `data_agent` 库）

| 表 | 说明 |
|---|---|
| `users` | 用户（username 唯一，密码哈希存储，role 为 admin/client） |
| `datasets` | 数据集元信息（类型 table/doc、状态、表名、列结构 JSON、分块数） |
| `dataset_{id}` | 每个表格数据源动态创建的实际数据表 |
| `document_chunks` | 文本文档分块后的片段（用于 TF-IDF 检索） |
| `chat_messages` | 对话历史（role、内容、结构化结果 extra JSON） |

## 快速开始

### 1. 环境准备

- Python 3.10+（本项目使用 3.12）
- Node.js 16+
- MySQL 8（本地已启动）

### 2. 后端

```bash
cd backend

# 创建虚拟环境并安装依赖（依赖安装在本项目虚拟环境中，非全局）
python -m venv .venv
.\.venv\Scripts\activate         # Windows
pip install -r requirements.txt

# 配置连接与参数
copy .env.example .env           # 按需修改 MySQL / LLM / 端口

# 启动后端（自动建库、建表、创建默认管理员）
python run.py                    # http://localhost:8000
```

### 3. 前端

```bash
cd frontend
npm install
npm run dev                      # http://localhost:5173
```

浏览器访问 `http://localhost:5173`，进入登录页。

> 说明：前端 dev 服务器已通过 Vite 代理把 `/api` 转发到后端 `http://localhost:8000`，无需额外跨域配置。

### 4. 使用流程

1. 使用**默认管理员**登录：`admin` / `admin123`（首次启动自动创建）。
2. 进入「数据管理」，上传样例数据（可用 `backend/sample_data/` 下的 `sales.csv` 与 `年度报告.txt`）。
3. 进入「Agent 对话」，提问，例如：
   - 「哪个地区销售额最高？」
   - 「各区域的总销售额与占比如何？」
   - 「根据报告总结一下今年业务情况？」

> 可用「注册」创建客户端账号，登录后仅能进入对话页，无数据上传入口。

## 配置说明

### 切换真实大模型

默认 `LLM_MOCK=true`，无需密钥即可演示。接入真实大模型，编辑 `backend/.env`：

```ini
LLM_MOCK=false
LLM_BASE_URL=https://api.openai.com/v1   # 或其它 OpenAI 兼容服务地址
LLM_API_KEY=你的密钥
LLM_MODEL=gpt-3.5-turbo                  # 或对应模型名
```

### MySQL

```ini
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123
MYSQL_DB=data_agent
```

启动后后端会自动创建 `data_agent` 数据库与全部业务表，并在无管理员时创建默认管理员。

### 安全说明

- 密码使用 PBKDF2-SHA256 加盐哈希存储，不会明文保存。
- 接口使用基于 HMAC-SHA256 签名的 JWT 进行鉴权（默认 24 小时有效）。
- Agent 生成的 SQL 仅允许执行只读 `SELECT`，避免数据被修改或破坏。
- 密钥、数据库密码仅存放于 `.env`，已在 `.gitignore` 中排除，不会提交到仓库。

## 常见问题

- **后端报 401**：未登录或 Token 失效，请重新登录。
- **客户端无法上传**：上传权限仅开放给管理员。
- **聊天无内容**：请确认已登录，且后端在 `LLM_MOCK` 下可正常返回（Mock 模式下为演示性回答）。
- **文档解析失败（pdf/docx）**：需安装 `pypdf` / `python-docx` 后上传对应格式。

## 后续可扩展方向

- 引入独立向量数据库（如 Milvus / pgvector）提升海量文档检索性能。
- 自动图表生成规则增强（更多图表类型与字段语义识别）。
- 多用户数据隔离（每个用户仅可见自己上传的数据）。
- 对话历史持久化与多会话管理。
