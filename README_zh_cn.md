# 香港劳工处招聘信息爬虫与智能体

**Languages:** [English](README.md) | [繁體中文](README_zh_hk.md)

## 📋 描述
香港劳工处公开了大量招聘信息，但人工逐一收集效率低下，本项目旨在自动化地集中抓取这些数据，便于统一分析与求职投递。

程序通过 Python 的 `requests` 库获取招聘页面，使用 `BeautifulSoup` 解析 HTML 元素，并借助正则表达式对信息进行清洗与整理，最终将结构化数据存入 `SQLite` 数据库。

> **免责声明：**
> 1. 本项目严格遵守 `robots.txt` 规范及 MIT 开源协议。
> 2. 任何第三方 Fork 或基于本项目二次开发的衍生项目，其行为均属开发者个人行为，与本项目及原作者无关。
> 3. 开发者须自行承担因使用或修改本代码而产生的法律责任。

## 🏗️ 架构
```mermaid
flowchart
    subgraph User["👤 用户"]
        CLI[命令行]
        MCP_CLIENT[MCP 客户端]
    end

    subgraph Scraper["🕷️ 网络爬虫"]
        search_job[搜索岗位]
        search_job_mt[并发搜索岗位]
        fill_job[填充岗位详情]
        fill_job_mt[并发填充岗位详情]
    end

    subgraph ProxyPool["🔀 代理池"]
        check_proxy_availability[测试可用性]
        evaluate_proxy[评分]
        assigner[分配器]
    end

    subgraph SQL_pipline["📊 文本转 SQL 管线"]
        SQL_generator[SQL 生成器]
        SQL_runner[SQL 运行器]
        SQL_checker[SQL 检查器]
    end

    subgraph AI["🤖 智能体"]
        chat[聊天]
        MCP_server[MCP 服务端]
        SQL_pipline
    end

    subgraph Service["⚙️ 服务"]
        Ollama[Ollama]
        SQLite[(SQLite)]
        proxy_server["sing-box 代理服务器"]
    end

    subgraph DataSource["🌐 数据源"]
        web_src[香港劳工处官网]
    end

    CLI <--> chat
    MCP_CLIENT <--> MCP_server

    chat <--> Ollama
    chat --> SQL_generator

    MCP_server --> SQL_generator

    SQL_generator --> SQL_runner
    SQL_generator <--> Ollama

    SQL_runner --> SQL_checker
    SQL_runner <--> SQLite

    SQL_checker --> chat
    SQL_checker --> MCP_server

    web_src --> search_job
    web_src --> search_job_mt

    search_job --> fill_job
    search_job_mt --> fill_job_mt

    fill_job --> SQLite
    fill_job_mt --> SQLite

    assigner --> search_job_mt
    assigner --> fill_job_mt
    assigner --> check_proxy_availability
    assigner --> evaluate_proxy
    assigner <--> proxy_server
```

## 🚀 使用方法
### 🛠️ 环境
激活环境
```sh
uv sync
source .venv/bin/activate
```
### 🕷️ 爬虫
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
### 🤖 智能体
配置文件 `config.toml`
```toml
[ollama]
host = "192.168.6.101"
chat_model = "llama3.2:3b"      # 聊天模型
code_model = "qwen2.5-coder:7b" # 编程模型
```
#### 询问
```sh
run-ask
```
> **注意：** 输出结果过多，已将大部分内容用 `...` 略过
* 基础查询
    ```txt
    >>> I want to know the basic infomation about the scrapered jobs
    ```
    ```md
    Here is a sample of recently scraped jobs from the project database:

    | Job Position | Salary Type | Monthly Range (HKD) | Location |
    | :--- | :--- | :--- | :--- |
    | 助理大廈主管 (日更, 柴灣) | 月薪 | HK$22,000 - 22,500 | 柴灣 |

    ...

    | 公司司機(東涌) | 月薪 | HK$18,000 - 18,500 | 東涌 |

    Would you like to see more details about specific roles or filter the results further?
    ```
* 增强查询(SQL 语句流)
    ```txt
    >>> Find all jobs with salary type as monthly salary and min salary above 30000.
    ```
    ```md
    Here are the jobs matching your criteria (Monthly Salary with minimum of HK$30,001 or above):

    | Job Name | Min Monthly Salary | Max Monthly Salary | Location |
    | :--- | :---: | :---: | :--- |
    | **中港跨境貨車司機** (Cross-border truck driver) | $38,000 | $38,000 | 葵涌，內地 |

    ...
    
    | **註冊安全主任** (Registered Safety Officer) - repeat entry | $35,000 | $45,000 | 元朗 |

    Would you like me to filter results further by a specific job title or company?
    ```
#### MCP
```json
"Jobs HongKong": {
    "type": "stdio",
    "command": "uv",
    "args": [
        "run",
        "-m",
        "jobs_hk.server"
    ]
}
```
