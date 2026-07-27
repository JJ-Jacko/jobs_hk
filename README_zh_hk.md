# 香港勞工處招聘資訊爬蟲與智能體

**Languages:** [简体中文](README_zh_cn.md) | [English](README.md)

## 📋 描述
香港勞工處公開了大量招聘資訊，但以人手逐一收集效率偏低，人工分析亦需耗費大量時間及成本。
本專案旨在自動化集中擷取相關資料，並透過內建智能體或提供 `MCP`，方便進行市場研究及統一分析。

> **免責聲明：**
> 1. 本項目嚴格遵守 `robots.txt` 規範及 MIT 開源協議。
> 2. 任何第三方 Fork 或基於本項目二次開發之衍生項目，其行為均屬開發者之個人行為，概與本項目及原作者無關。
> 3. 開發者須自行承擔因使用或修改本代碼而產生之一切法律責任。

## 💡 核心亮點
### 🕷️ 高併發彈性資料擷取：
* **多模式並行擷取**：支援一般`單執行緒`擷取及基於代理的`多執行緒並行`擷取，大幅提升資料擷取效率。
* **動態代理池管理**：
    內建針對 `sing-box` 的`代理池`分配器，
    支援代理可用性檢測、動態評分及智能分配，
    有效解決針對單一 IP 的請求頻率限制，以及代理節點失效時無法有效切換的問題。
### 📊 結構化清洗與持久化
* **高精度資料解析**：
    結合 `BeautifulSoup` 與`正則表達式`對 HTML 進行深度擷取。
    精準清洗及標準化職位名稱、薪酬範圍、工作地點及任職要求等關鍵欄位。
* **輕量化資料庫儲存**：
    將結構化資料自動歸檔至 `SQLite` 資料庫。
    建立索引並提供低延遲的本地資料查詢及持久化儲存能力。
### 🤖 智能體 與 Text-to-SQL：
* **Text-to-SQL 流程**：
    結合本地 `Ollama` LLM 將自然語言轉換為 SQL，
    採用 `SQL 生成器 ➔ 執行器 ➔ 檢查器` 的自動修正機制，
    支援對擷取資料進行精確的多維度統計分析。
* **MCP 整合**：
    開放介面，支援 VSCode Github Copilot、Claude Desktop 等，
    可由具備高效能模型及完整功能的用戶端直接調用。
* **上下文工程**：
    結合資料表定義 `DDL`、提示詞 `prompts` 工程、少樣本 `Few-Shot` 範例，
    為模型建立規範化推理流程及提供完整資料來源。
    最後透過 `Schemas` 結構化約束模型輸出格式，並配合 `pydantic` 的再次驗證及重試機制，
    確保最終輸出的 JSON 格式符合規範。
* **SQL 安全審核與自我修正**：
    模型產生 SQL 後，系統會即時進行安全檢查。
    嚴格攔截 INSERT/UPDATE/DELETE/DROP 等具破壞性的寫入操作，只允許執行 SELECT 查詢。
    若觸發安全違規或語法錯誤，系統會將錯誤內容回饋予模型重新修正及合規重建，
    確保資料庫絕對安全及模型輸出可靠。
* **資料庫安全**：
    系統初始化時，嚴格區分`讀寫`及`唯讀`兩類資料庫連線實例。
    爬蟲寫入資料及智能體讀取資料分別使用兩種明確建立的資料庫連線類型。

## 🏗️ 架構
```mermaid
flowchart
    subgraph User["👤 用戶"]
        CLI[命令行]
        MCP_CLIENT[MCP 客戶端]
    end

    subgraph Scraper["🕷️ 網路爬蟲"]
        search_job[搜索崗位]
        search_job_mt[并發搜索崗位]
        fill_job[填充崗位詳情]
        fill_job_mt[并發填充崗位詳情]
    end

    subgraph ProxyPool["🔀 代理池"]
        check_proxy_availability[測試可用性]
        evaluate_proxy[評分]
        assigner[分配器]
    end

    subgraph SQL_pipline["📊 文本轉 SQL 管綫"]
        SQL_generator[SQL 生成器]
        SQL_runner[SQL 運行器]
        SQL_checker[SQL 檢查器]
    end

    subgraph AI["🤖 智能體"]
        chat[聊天]
        MCP_server[MCP 伺服端]
        SQL_pipline
    end

    subgraph Service["⚙️ 服務"]
        Ollama[Ollama]
        SQLite[(SQLite)]
        proxy_server["sing-box 代理伺服器"]
    end

    subgraph DataSource["🌐 數據源"]
        web_src[香港勞工處官網]
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
### 🛠️ 環境
啟用環境
```sh
uv sync
source .venv/bin/activate
```
### 🕷️ 爬蟲
#### 常規
常規爬蟲無需配置代理
* 搜尋職缺資訊
    ```sh
    run-search-job
    ```
    ```log
    2026-04-12 20:25:02 - INFO - Processing page: 1
    2026-04-12 20:25:13 - INFO - Processing page: 2
    2026-04-12 20:25:21 - INFO - Processing page: 3
    ```
* 補全職缺資訊
    ```sh
    run-fill-job
    ```
    ```log
    2026-04-12 20:37:07 - INFO - Processing job: 機械技術員
    2026-04-12 20:37:18 - INFO - Processing job: 電氣技術員
    2026-04-12 20:37:25 - INFO - Processing job: 西醫診所助理
    ```
#### 并發
并發爬蟲需要配置代理

配置文件 `config.toml`
```toml
[proxy]
host = "127.0.0.1"
port_start = 10801  # 代理伺服器的起始端口
offset = 5          # 代理端口的偏移量
rate = 0.75         # 實際創建的綫程占代理端口總數的比
```
* 搜尋職缺資訊
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
* 補全職缺資訊
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
🤖 智能體
配置文件 `config.toml`
```toml
[ollama]
host = "192.168.6.101"
chat_model = "llama3.2:3b"      # 聊天模型
code_model = "qwen2.5-coder:7b" # 編碼模型
```
#### 詢問
```sh
run-ask
```
> **注意：** 輸出結果過多，已將大部分内容用 `...` 略過
* 基礎查詢
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
* 增强查詢(SQL 語句流)
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
