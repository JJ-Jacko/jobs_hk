# 香港勞工處招聘資訊爬蟲

**Languages:** [简中](README_zh_cn.md) | [English](README.md)

## 📋 描述
香港勞工處公開了大量招聘資訊，但人工逐一收集效率低下，本專案旨在自動化地集中抓取這些資料，便於統一分析與求職投遞。

程式透過 Python 的 `requests` 庫獲取招聘頁面，使用 `BeautifulSoup` 解析 HTML 元素，並借助正則表達式對資訊進行清洗與整理，最終將結構化資料存入 `SQLite` 資料庫。

> **注意：** 本專案嚴格遵守該網站 `robots.txt` 的相關規範，如有冒犯，請透過 email 與我聯繫，本專案的任何 fork 亦須依法合規開發


## 🚀 使用方法
### 啟用環境
```sh
uv sync
source .venv/bin/activate
```

### 執行
#### 搜尋職缺資訊
```sh
run-search-job
```
```log
2026-04-12 20:25:02 - INFO - Processing page: 1
2026-04-12 20:25:13 - INFO - Processing page: 2
2026-04-12 20:25:21 - INFO - Processing page: 3
```
#### 補全職缺資訊
```sh
run-fill-job
```
```log
2026-04-12 20:37:07 - INFO - Processing job: 機械技術員
2026-04-12 20:37:18 - INFO - Processing job: 電氣技術員
2026-04-12 20:37:25 - INFO - Processing job: 西醫診所助理
```
