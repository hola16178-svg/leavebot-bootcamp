# LeaveBot — 第二天的空白學生專案

## 目前可執行：請假表單主線（001）

變更狀態：已確認 [002](issues/002-reason-limit.md) 將新提交理由改為最多 100 碼位，舊假單保留原文、DB 儲存上限維持 200；**目前程式與畫面仍為 200，尚未實作新上限**。下述 001 功能與證據屬原版；另有 [TRACE 格式已知紅燈](docs/evidence/002-method-error-red.md) 尚未修復，58 passed 是該診斷前的歷史結果。

已提供員工選擇、請假表單、後端驗證、SQLite 存檔與我的假單。使用教學員工 A／B／C，無登入；新申請固定待審核。只計週一至週五，半天限單一工作日，接受補登；理由選填，去除前後空白後最多 200 Unicode 碼位。

選員工 → 填日期、假別與時段 → 送出 → 在我的假單查看內容／天數／待審核；重新整理後選回同一員工仍可查。錯誤輸入不存檔；結果未知時先查看假單，不自動重送；再次合法送出相同內容會另建一張。

Windows PowerShell 在 repo 根目錄執行（已有 .venv 則跳過建立）：

```powershell
python --version
python -m venv .venv
.venv\Scripts\python.exe -m pip install -c course/01-上課/05-constraints.txt -e ".[dev]"
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

確認 python 為 3.12；若不是，改用正確的 Python 3.12 執行檔或 py -3.12。本機 py launcher 無法辨識安裝，但 python 實際為 3.12.10，故使用後者建立環境。

開啟 http://127.0.0.1:8000/，應顯示「服務連線正常」；按「重新檢查」可重讀 health。http://127.0.0.1:8000/api/health 回 `{"status":"ok"}`。Ctrl+C 停止，再用相同命令重啟；port 占用加 --port 8001 並改開對應網址。

另開終端機測試，不需啟用 venv：

```powershell
.venv\Scripts\python.exe -m pytest backend/tests/acceptance/test_health.py
.venv\Scripts\python.exe -m pytest
```

2026-11-01 實測 Windows／Python 3.12.10、FastAPI 0.162.0、uvicorn 0.54.0、httpx 0.28.1、pytest 9.1.1、Starlette 1.10.0：1 passed、1 warning。警告為課程套件 TestClient 的 httpx 棄用提示，未改白名單。[實際紀錄](docs/evidence/000-skeleton.md)。

上述 1 passed 是 000 歷史紀錄；001 最新完整測試為 **58 passed、1 warning**，六條畫面流程已經 Agent 實際瀏覽器操作。見 [001 證據](docs/evidence/001-submit-leave.md)；使用者人工驗收待完成。

開發資料預設 `backend/data/leavebot.db`；可用 `LEAVEBOT_DB` 指定其他路徑。`LEAVEBOT_TODAY` 若設置須為 YYYY-MM-DD，未設使用真實本機日期，啟動紀錄會標明模式；不以今天限制補登。測試自行注入暫存 DB 與固定時鐘，不使用開發資料。

本次保留運行的驗收服務使用獨立檔案，若要重現同一環境，可在新終端機啟動前設定：

```powershell
$env:LEAVEBOT_DB = 'backend/data/leavebot-acceptance-001.db'
$env:LEAVEBOT_TODAY = '2026-10-14'
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

服務若已運行，不需再啟動；驗收資料包含先前操作假單，不代表測試資料污染開發 DB。SQLite 與虛擬環境不進版控；關閉專用終端機即可移除該終端機的環境設定。

第一天在獨立資料夾體驗 Vibe Coding、比較結果並練習 PRD；第二天用這個 repo，學習如何用規格、通用 skills、測試與人工驗收穩定交付。

**今天做一條完整路徑：選員工 → 填請假單 → 驗證 → 存檔 → 我的假單顯示待審核。** 主管核准、額度與一句話 AI 解析是延伸。

## 從這裡開始

1. Fork 本 repo 的 `main`，clone 自己的 fork。只複製 main 即可；checkpoint 從講師 upstream 取得。
2. 準備 Git、Python 3.12、能正常登入的 Claude Code 或 Codex，以及瀏覽器。Archify 使用 Node（套件最低 18；課前用受支援版本試跑），應用程式主線不需要 Node 或 LLM API key。
3. 從 [課程資料入口](course/README.md) 依序找到當前階段；在 repo 根目錄開工具，讀 [上課流程](course/01-上課/02-WORKFLOW.md) 的開場提示。Claude Code 用 `/技能`，Codex 用 `$技能`。
4. 依工作流程逐步產出文件、票與程式，不先複製空模板占位。需要同組已完成決策時先讀文件。

Windows 使用 Codex 共用技能前，確認 `.agents/skills` 是指向 `../.claude/skills` 的連結；無法建立連結時請講師協助，不能只以設定檔存在當成工具已接通。

`course/` 分成 [01-上課](course/01-上課/01-SETUP.md) 與 [02-補充](course/02-補充/01-HARNESS.md)。上課依編號讀目前需要的檔案與提示卡；工具說明、保底快照、範例及維護紀錄在補充區。[通用技能清單](.claude/skills/README.md)可按需要查。

`main` 只有教材與工具設定；`docs/`、`issues/`、`backend/`、`pyproject.toml` 由學生產生。checkpoint 是另外的教學快照。

講義與講師教材在 [ai-vibe-coding-beginner](https://github.com/Zenobia000/SDD-agent-coding-beginner)。技能與 guard 的來源及授權見 [THIRD-PARTY-NOTICES](.claude/THIRD-PARTY-NOTICES.md)。
