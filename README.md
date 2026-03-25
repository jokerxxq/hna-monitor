<div align="center">

# ✈ HNA Flight Monitor

**海南航空机票价格监控 · HNA Flight Price Watcher**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

[🇨🇳 中文](#-中文文档) · [🇺🇸 English](#-english-docs)

</div>

---

## 🇨🇳 中文文档

### 项目简介

基于 FastAPI 的航班价格监控 Web 应用，自动轮询机票价格，低于设定阈值时通过微信（Server酱）推送提醒。

### 功能特性

- ✅ 创建 / 删除 / 启用 / 停用监控任务
- ⏱ 后台定时轮询（可配置间隔）
- 🔔 价格阈值提醒，自动去重防骚扰
- 💬 微信推送（Server酱）
- 🗄 SQLite 持久化 + Web 日志界面
- 🛫 变飞 MCP stdio 数据源（推荐）
- 📱 响应式设计，支持移动端浏览

### 本地快速启动

```bash
# 1. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux
# 编辑 .env，填入 API Key

# 4. 启动
uvicorn app.main:app --reload
```

浏览器访问 `http://127.0.0.1:8000`

### 变飞 MCP 配置

1. 安装 [Node.js](https://nodejs.org)（`npx` 运行依赖）
2. 在 `.env` 中填写：

```env
PRICE_PROVIDER=variflight_mcp
VARIFLIGHT_API_KEY=你的Key
VARIFLIGHT_MCP_COMMAND=npx
VARIFLIGHT_MCP_ARGS=-y @variflight-ai/variflight-mcp
```

3. 在网页表单中输入城市三字码（如 `SZX` → `HAK`）和日期即可。

### Mock 模式（无需 API Key）

本地测试时可跳过 MCP 配置：

```env
PRICE_PROVIDER=mock
```

### Ubuntu 服务器一键部署

```bash
# 1. 克隆代码
git clone https://github.com/jokerxxq/hna-monitor.git ~/apps/hna-monitor
cd ~/apps/hna-monitor

# 2. 填写配置
cp .env.example .env
nano .env   # 填入 SERVERCHAN_SENDKEY 和 VARIFLIGHT_API_KEY

# 3. 一键部署（自动安装依赖、配置 systemd + Nginx）
bash deploy.sh
```

部署完成后访问 `http://服务器IP`

<details>
<summary>📋 部署脚本说明（点击展开）</summary>

`deploy.sh` 自动完成以下步骤：

| 步骤 | 内容 |
|------|------|
| 1 | 安装系统依赖（Python / Node.js / Nginx） |
| 2 | 创建 Python 虚拟环境并安装依赖 |
| 3 | 复制 `.env.example` → `.env`（若不存在） |
| 4 | 注册并启动 systemd 服务（开机自启） |
| 5 | 配置 Nginx 反向代理 |
| 6 | 开放 UFW 防火墙端口 |

</details>

### 后续更新

```bash
cd ~/apps/hna-monitor
git pull
sudo systemctl restart hna-monitor
```

### 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `POLL_INTERVAL_MINUTES` | 轮询间隔（分钟） | `30` |
| `WECHAT_PROVIDER` | 推送渠道 | `serverchan` |
| `SERVERCHAN_SENDKEY` | Server酱 SendKey | — |
| `PRICE_PROVIDER` | 价格数据源 | `variflight_mcp` |
| `VARIFLIGHT_API_KEY` | 变飞 API Key | — |
| `DATABASE_URL` | 数据库路径 | `sqlite:///./data/app.db` |

---

## 🇺🇸 English Docs

### Overview

A FastAPI-based web application that monitors flight prices and sends WeChat alerts via Server酱 when prices drop below your threshold.

### Features

- ✅ Create / delete / enable / disable monitoring tasks
- ⏱ Background scheduler with configurable polling interval
- 🔔 Price threshold alerts with de-duplication
- 💬 WeChat push notifications via Server酱
- 🗄 SQLite persistence + web log viewer
- 🛫 Variflight MCP stdio provider (recommended)
- 📱 Responsive UI with mobile browser support

### Quick Start (Local)

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux
# Edit .env and fill in your API keys

# 4. Run
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`

### Variflight MCP Configuration

1. Install [Node.js](https://nodejs.org) (required for `npx`)
2. Set in `.env`:

```env
PRICE_PROVIDER=variflight_mcp
VARIFLIGHT_API_KEY=your_key_here
VARIFLIGHT_MCP_COMMAND=npx
VARIFLIGHT_MCP_ARGS=-y @variflight-ai/variflight-mcp
```

3. Use city IATA codes in the form (e.g. `SZX` → `HAK`) with a departure date.

### Mock Mode (No API Key)

For local testing without an API key:

```env
PRICE_PROVIDER=mock
```

### Ubuntu One-Click Deployment

```bash
# 1. Clone the repo
git clone https://github.com/jokerxxq/hna-monitor.git ~/apps/hna-monitor
cd ~/apps/hna-monitor

# 2. Configure
cp .env.example .env
nano .env   # Fill in SERVERCHAN_SENDKEY and VARIFLIGHT_API_KEY

# 3. Deploy (installs deps, configures systemd + Nginx automatically)
bash deploy.sh
```

Then visit `http://your-server-ip`

<details>
<summary>📋 What deploy.sh does (click to expand)</summary>

| Step | Action |
|------|--------|
| 1 | Install system packages (Python / Node.js / Nginx) |
| 2 | Create Python virtualenv and install pip deps |
| 3 | Copy `.env.example` → `.env` if not present |
| 4 | Register and start systemd service (auto-start on boot) |
| 5 | Configure Nginx reverse proxy |
| 6 | Open UFW firewall ports |

</details>

### Updating

```bash
cd ~/apps/hna-monitor
git pull
sudo systemctl restart hna-monitor
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `POLL_INTERVAL_MINUTES` | Polling interval in minutes | `30` |
| `WECHAT_PROVIDER` | Notification channel | `serverchan` |
| `SERVERCHAN_SENDKEY` | Server酱 SendKey | — |
| `PRICE_PROVIDER` | Price data source | `variflight_mcp` |
| `VARIFLIGHT_API_KEY` | Variflight API key | — |
| `DATABASE_URL` | Database path | `sqlite:///./data/app.db` |

---

<div align="center">

Made with ❤️ · 数据来源 Variflight · 推送 Server酱

</div>
