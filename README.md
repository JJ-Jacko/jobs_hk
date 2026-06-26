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
#### Search Job Listings
```sh
run-search-job
```
```log
2026-04-12 20:25:02 - INFO - Processing page: 1
2026-04-12 20:25:13 - INFO - Processing page: 2
2026-04-12 20:25:21 - INFO - Processing page: 3
```
#### Fill Job Details
```sh
run-fill-job
```
```log
2026-04-12 20:37:07 - INFO - Processing job: 機械技術員
2026-04-12 20:37:18 - INFO - Processing job: 電氣技術員
2026-04-12 20:37:25 - INFO - Processing job: 西醫診所助理
```
