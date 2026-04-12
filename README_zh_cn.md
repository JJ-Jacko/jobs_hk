# 香港劳工处招聘信息爬虫

**Languages:** [English](README.md) | [繁中](README_zh_hk.md)

## 📋 描述
香港劳工处公开了大量招聘信息，但人工逐一收集效率低下，本项目旨在自动化地集中抓取这些数据，便于统一分析与求职投递。

程序通过 Python 的 `requests` 库获取招聘页面，使用 `BeautifulSoup` 解析 HTML 元素，并借助正则表达式对信息进行清洗与整理，最终将结构化数据存入 `SQLite` 数据库。

> **注意：** 本项目严格遵守该网站 `robots.txt` 的相关规范，如有冒犯，请通过 email 与我联系，本项目的任何 fork 亦须依法合规开发


## 🚀 使用方法
### 激活环境
```sh
uv sync
source .venv/bin/activate
```

### 运行
#### 搜索工作信息
```sh
run-search-job
```
```log
2026-04-12 20:25:02 - INFO - Processing page: 1
2026-04-12 20:25:13 - INFO - Processing page: 2
2026-04-12 20:25:21 - INFO - Processing page: 3
```
#### 补全工作信息
```sh
run-fill-job
```
```log
2026-04-12 20:37:07 - INFO - Processing job: 機械技術員
2026-04-12 20:37:18 - INFO - Processing job: 電氣技術員
2026-04-12 20:37:25 - INFO - Processing job: 西醫診所助理
```
