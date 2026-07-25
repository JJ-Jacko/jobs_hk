# Hong Kong Labour Department Job Listing Scraper

**Languages:** [简中](README_zh_cn.md) | [繁中](README_zh_hk.md)

## 📋 Description
The Hong Kong Labour Department publishes a large number of job listings publicly, but manually collecting them one by one is highly inefficient. This project aims to automatically aggregate this data in one place, making it easier to analyse and apply for jobs.

The scraper fetches job listing pages via Python's `requests` library, parses HTML elements with `BeautifulSoup`, and cleans and organises the extracted information using regular expressions. The structured data is then stored in a `SQLite` database.

> **Note:** This project strictly complies with the site's `robots.txt` rules. If you have any concerns, please contact me via email. Any fork of this project must also be developed in accordance with applicable laws and regulations.


## 🚀 Usage
### Activate Environment
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

### Run
#### Common
Common web scrapering don't need to configure proxy.
* Search Job Listings
    ```sh
    run-search-job
    ```
    ```log
    2026-04-12 20:25:02 - INFO - Processing page: 1
    2026-04-12 20:25:13 - INFO - Processing page: 2
    2026-04-12 20:25:21 - INFO - Processing page: 3
    ```
* Fill Job Details
    ```sh
    run-fill-job
    ```
    ```log
    2026-04-12 20:37:07 - INFO - Processing job: 機械技術員
    2026-04-12 20:37:18 - INFO - Processing job: 電氣技術員
    2026-04-12 20:37:25 - INFO - Processing job: 西醫診所助理
    ```
#### Concurrent
Concurrent web scrapering need to configure proxy.

Configuration file `config.toml`
```toml
[proxy]
host = "127.0.0.1"
port_start = 10801  # Start port of the proxy servers
offset = 5          # The offset of the proxy ports
rate = 0.75         # The percentage of threads actually created out of the total number of proxy ports
```
* Search Job Listings
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
* Fill Job Details
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
