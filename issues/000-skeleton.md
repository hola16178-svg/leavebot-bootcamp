# 000｜可啟動的 FastAPI 與首頁連線檢查

- 狀態：骨架實作與 Agent 驗證完成，等待使用者驗收；未開始 001。
- 大小：小，估計 20–40 分鐘；為規劃估計，非完成承諾。
- 真正依賴：無前置工作票；需要以下建置環境。
- 解鎖成果：001 可沿用同一套件、應用入口、靜態頁與測試配置。

## 建置前提與必讀段落

- Git、Python 3.12、可建立虛擬環境與安裝指定套件、可用瀏覽器；本階段尚未驗證。
- 讀 [AGENTS.md](../AGENTS.md) 全文、[WORKFLOW](../course/01-上課/02-WORKFLOW.md)「每階段的節奏」及卡 H 第一段。
- 讀 [STACK](../course/01-上課/04-STACK.md)「骨架票 000 的要求」「安裝與執行」、課程 constraints。
- 讀 [SDS](../docs/05-sds.md) API-01、main.create_app 與靜態頁路由順序；本票只做骨架，DB 初始化、員工與業務模組留 001。
- 讀 [測試計畫](../docs/06-test-plan.md) TC-01：本票僅做 health 部分，不把完整 TC-01 標通過。

## 可檢查成果與範圍

- [ ] 根目錄 pyproject.toml：requires-python ≥3.12；直接套件限 fastapi、uvicorn、httpx，dev 加 pytest，安裝套用課程 constraints。
- [ ] 明確 package discovery：package-dir 指 backend、find where 為 backend，包含 app 靜態檔 package data，不將 course／issues 當套件。
- [ ] pytest：testpaths 指 backend/tests、pythonpath 指 backend、import-mode=importlib，註冊 req marker。
- [ ] 建立 backend/app/__init__.py、main.py、static/index.html、app.js、style.css；main 保留 app 入口，可使用 create_app 組裝；import 不開 DB。
- [ ] GET /api/health 回 200 與 `{"status":"ok"}`；health 不探測 DB。
- [ ] 先登記 API，最後掛 `/` 靜態頁；首頁 fetch('/api/health') 並顯示成功或連線失敗，無 CORS。
- [ ] health 測試先看到預期原因的失敗，再以最小實作通過；預定 backend/tests/acceptance/test_health.py。這是骨架檢查，不承接員工或業務 TC。
- [ ] README 補可重做的 Windows 安裝、啟動、測試及停止方式；記錄實際驗證的 Python／套件版本。

不建立員工 API、請假表單、驗證規則、資料庫、LLM、登入或進階挑戰。不得為了套用完整 SDS 提前把 001 做掉。

## 實作節奏與驗收

以新對話指定本票並使用 `$implement`。先建必要測試配置，再對 health 看到預期失敗與通過；不能以套件缺少、語法錯誤當作行為紅燈。保留簡要紅／綠證據。

以下是後續實作時的命令，本次拆票未執行；既有 venv 先確認版本與可用性，不覆寫現有使用者工作。

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -c course/01-上課/05-constraints.txt -e ".[dev]"
.venv\Scripts\python.exe -m pytest backend/tests/acceptance/test_health.py
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

服務與測試分開終端機。瀏覽器開 http://127.0.0.1:8000/，核對首頁連線結果與 /api/health JSON；Ctrl+C 停止，再啟動一次確認能正常使用。若 8000 被占用，改 --port 8001 並記錄實際網址。沒有瀏覽器工具則交由人操作，不冒稱已驗。

## 完成條件、證據與停止

- 專案測試實際通過，貼實際命令、版本、日期、通過／失敗數；首頁與重啟有實際結果。
- 更新 docs/06-test-plan.md：只記 TC-01 health 子項的真實結果，員工名單子項仍未執行，整組不得標通過；不提前標業務 AC／FR 通過。
- 在 docs/LESSONS.md 記有證據的偏差或工具問題；未發生不虛構。
- 完成骨架即停止，不開始 001。超過預定進度 15 分鐘找講師，不自行切 checkpoint。
- 提交前 git status、git diff，僅加入本票明確檔案；不自動推送、合併。

目前證據：[2026-11-01 執行紀錄](../docs/evidence/000-skeleton.md)。health 與完整目前 pytest 各 1 passed、1 warning；紅燈 404→綠燈 200、瀏覽器首頁與重新檢查、停止／重啟已核對。使用者驗收尚待確認。
