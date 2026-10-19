<div align="center">

# Vellum

### 本地优先的知识库与检索引擎 · 纯 Python · 零依赖 · 开箱即用

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen.svg)](#)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](#)

**把散落各处的笔记、片段与灵感，沉淀成一个可检索、可浏览、可成长的本地知识库。**

[快速开始](#-快速开始) · [架构](#-架构) · [API](#-http-api) · [路线图](#-路线图)

</div>

---

## ✨ 为什么是 Vellum

知识不该被锁在互相割裂的文档和笔记应用里，更不该为了「存几条笔记」就引入一整套数据库与大模型服务。
**Vellum** 把知识管理收敛到最小可行内核：用一份本地 JSON 文件持久化笔记，用经典 **BM25** 算法做中英混合全文检索，再附带一个零依赖的 Web 控制台，让知识真正「存得下、找得到、看得爽」。

无需联网、无需安装第三方库、无需配置数据库——一台装着 Python 的笔记本即可运行。

## 🚀 特性

- **纯本地 · 零依赖** — 仅依赖 Python 标准库，不连网、不装包、不依赖外部服务。
- **BM25 中英混合检索** — 中文按 bigram 切分、英文小写归一，标题额外加权，结果稳定可解释。
- **分层而完整的工程结构** — 笔记模型 / 索引层 / 检索层 / CLI / Web UI 各司其职，代码易读易改。
- **零依赖 Web 控制台** — 基于标准库 `http.server` 自托管前端，支持实时搜索与即时添加。
- **工程化就绪** — 内置单元测试与 GitHub Actions CI，开箱即跑、可测、可扩展。

## 📦 安装

```bash
# 可编辑安装（推荐）
pip install -e .

# 或直接以模块方式运行，连安装都不需要
python -m vellum --help
```

> 要求 Python 3.8+，无任何第三方依赖。

## ⚡ 快速开始

```bash
# 添加一条笔记（标题 / 内容 / 标签）
vellum add "如何系统学习 Python" -c "从变量、函数到面向对象" -t python 学习

# 列出全部笔记
vellum list

# 用 BM25 检索
vellum search "python 函数"

# 启动 Web 控制台（浏览器打开 http://127.0.0.1:8000）
vellum serve --port 8000
```

数据默认写入 `~/.vellum/store.json`，可用环境变量 `VELLUM_PATH` 自定义存储路径。

```
$ vellum search "python"
[0.82] 如何系统学习 Python        tags: python 学习
       匹配片段：…从变量、函数到面向对象…
```

## 🏗️ 架构

Vellum 分为四层，请求自上而下流动，存储与索引在最底层被复用：

```
┌─────────────────────────────────────────────────┐
│              CLI  /  Web 控制台                  │
│           (cli.py · server.py · web/)            │
└───────────────┬───────────────────┬─────────────┘
                │                   │
         ┌──────▼──────┐     ┌──────▼──────┐
         │  检索入口    │     │  笔记读写    │
         │ (search.py) │     │ (models.py) │
         └──────┬──────┘     └──────┬──────┘
                │                   │
         ┌──────▼───────────────────▼──────┐
         │        BM25 索引 (index.py)       │
         │   中文 bigram · 英文归一 · 标题加权  │
         └──────────────┬──────────────────┘
                        │
         ┌──────────────▼──────────────────┐
         │      JSON 持久化 (models.py)      │
         │        ~/.vellum/store.json       │
         └──────────────────────────────────┘
```

- **存储层** — `Note` 以 dataclass 描述，序列化为 JSON 落盘；读写带原子保护，进程退出不丢数据。
- **索引层** — 经典 BM25 实现，针对中文做 bigram 切分、英文做小写 + 词正则，排序可解释。
- **检索 / 服务层** — 检索入口负责打分与摘要高亮；`http.server` 零框架托管前端与 REST API。

## 🔌 HTTP API

启动 `vellum serve` 后可用：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/api/notes` | 列出全部笔记 |
| POST | `/api/notes` | 新增笔记（Body：`{title, content, tags}`） |
| GET  | `/api/search?q=关键词` | BM25 检索并返回高亮摘要 |

## 🧭 路线图

- [ ] 存储后端可插拔（默认 JSON，可选 SQLite 支撑更大规模）
- [ ] Markdown 渲染与代码高亮（前端 `marked.js` + `highlight.js`）
- [ ] 语义检索模式（本地嵌入模型 `sentence-transformers` 与 BM25 混合排序）
- [ ] 多空间 / 多知识库隔离

## 🤝 贡献

欢迎提 Issue 与 PR。本地开发：

```bash
python -m unittest discover -s tests   # 运行测试
```

## 📄 许可证

[MIT](LICENSE) — 自由使用、修改与分发。
