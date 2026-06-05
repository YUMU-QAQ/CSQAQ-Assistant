# CSQAQ Assistant — CS2 饰品数据分析助手

基于 [CSQAQ API](https://csqaq.com/home) 的 CS2 饰品数据分析 Web 应用，帮助玩家进行饰品搜索、比价、持仓管理、挂刀分析和 AI 智能问答。

## 功能模块

| 模块 | 功能 |
|------|------|
| 数据看板 | 饰品指数、涨跌榜、热门饰品 |
| 饰品搜索 | 模糊搜索 + 详情页 + 多平台价格 K 线图 |
| 排行榜 | 涨幅/跌幅/成交量/市值/热度/挂刀收益排行 |
| 关注列表 | 收藏饰品，自动刷新价格 |
| 持仓管理 | 持仓记录、盈亏计算、持仓分布 |
| 价格提醒 | 价格阈值/涨跌幅提醒 |
| 挂刀分析 | 跨平台汇率、套利机会 |
| 武器箱 | ROI 排名、期望值分析 |
| AI 助手 | Claude 流式对话 + 市场/持仓上下文注入 |

## 技术栈

- **后端**: Python FastAPI + SQLAlchemy + SQLite
- **前端**: React + TypeScript + Vite + Tailwind CSS + ECharts
- **AI**: Anthropic Claude API

## 快速开始

### 1. 获取 API Token

- 注册 https://csqaq.com/home，在个人中心获取 API Token
- 在个人中心 → API 设置中绑定本机 IP 白名单

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入:
#   CSQAQ_API_TOKEN=你的token
#   ANTHROPIC_API_KEY=你的claude_key
```

### 3. 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 4. 启动

```bash
# Terminal 1 - 后端 (port 8000)
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2 - 前端 (port 5173)
cd frontend
npm run dev
```

访问 `http://localhost:5173`

## 项目结构

```
CSQAQ/
├── backend/app/
│   ├── main.py           # FastAPI 入口
│   ├── config.py         # 配置管理
│   ├── database.py       # SQLite 异步引擎
│   ├── models/           # ORM 模型
│   ├── schemas/          # Pydantic 请求/响应
│   ├── services/         # 业务逻辑层
│   │   ├── csqaq_client.py   # CSQAQ API 客户端 (限流/缓存/重试)
│   │   ├── ai_service.py     # Claude AI 集成
│   │   └── ...
│   ├── routers/          # API 路由
│   └── prompts/          # AI 提示词模板
├── frontend/src/
│   ├── App.tsx           # 路由配置
│   ├── pages/            # 10 个页面组件
│   ├── components/       # 通用组件
│   ├── api/              # API 调用层
│   └── types/            # TypeScript 类型
└── .env.example          # 环境变量模板
```

## License

MIT
