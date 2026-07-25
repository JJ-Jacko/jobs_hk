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
`config.toml`
```toml
[ollama]
host = "192.168.6.101"
chat_model = "llama3.2:3b"
code_model = "qwen2.5-coder:7b"
```

### 运行
#### 常规
常规爬虫无需配置代理
* 搜索工作信息
    ```sh
    run-search-job
    ```
    ```log
    2026-04-12 20:25:02 - INFO - Processing page: 1
    2026-04-12 20:25:13 - INFO - Processing page: 2
    2026-04-12 20:25:21 - INFO - Processing page: 3
    ```
* 补全工作信息
    ```sh
    run-fill-job
    ```
    ```log
    2026-04-12 20:37:07 - INFO - Processing job: 機械技術員
    2026-04-12 20:37:18 - INFO - Processing job: 電氣技術員
    2026-04-12 20:37:25 - INFO - Processing job: 西醫診所助理
    ```
#### 并发
并发爬虫需要配置代理

配置文件 `config.toml`
```toml
[proxy]
host = "127.0.0.1"
port_start = 10801  # 代理服务器的起始端口
offset = 5          # 代理端口的偏移量
rate = 0.75         # 实际创建的线程占代理端口总数的比
```
* 搜索工作信息
    ```sh
    run-search-job-MT
    ```
    ```log
    2026-07-25 15:38:42 - [Worker-1] - INFO - Processing page: 1
    2026-07-25 15:38:45 - [Worker-2] - INFO - Processing page: 2
    2026-07-25 15:38:48 - [Worker-3] - INFO - Processing page: 3
    2026-07-25 15:38:51 - [Worker-4] - INFO - Processing page: 4
    2026-07-25 15:39:01 - [Worker-2] - INFO - Processing page: 5
    2026-07-25 15:39:02 - [Worker-1] - INFO - Processing page: 6
    ```
* 补全工作信息
    ```sh
    run-fill-job-MT
    ```
    ```log
    2026-07-25 15:41:32 - [Worker-1] - INFO - Processing job: 助理大廈主管 (日更, 柴灣)
    2026-07-25 15:41:35 - [Worker-2] - INFO - Processing job: 福音幹事III兼行政助理(港島東隊教會)
    2026-07-25 15:41:38 - [Worker-3] - INFO - Processing job: 電氣技術員
    2026-07-25 15:41:41 - [Worker-4] - INFO - Processing job: 冷氣技術員
    2026-07-25 15:41:45 - [Worker-1] - INFO - Processing job: 機械技術員
    2026-07-25 15:41:53 - [Worker-3] - INFO - Processing job: 合約工程助理
    ```
