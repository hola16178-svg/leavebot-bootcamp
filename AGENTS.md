# LeaveBot — 課程專案規則

Claude Code 經 `CLAUDE.md` 載入本檔；Codex 直接讀本檔。通用 skills 提供方法，本檔與 `course/` 定義本課的限制。

## 先讀哪裡

- **開始第二天、詢問下一步或呼叫課程技能前，先讀 `course/01-上課/02-WORKFLOW.md`。** 依當前階段讀必要材料，不一次產出整套文件。
- 題目與範圍：`course/01-上課/03-LEAVEBOT.md`；技術與執行方式：`course/01-上課/04-STACK.md`；工具設定：`course/02-補充/01-HARNESS.md`。
- `course/02-補充/04-PLAN.json` 與 `course/01-上課/prompts/` 是兩邊教材同步的來源。模板在 `course/01-上課/templates/`，產出寫到根目錄 `docs/`，工作票寫到 `issues/`。
- 第一天的臨摹、塔羅與動畫在**獨立的 D1 練習資料夾**執行，不放進本專案。本專案從第二天開始。

## 範圍與決策

本分支是一個空白學生起點：沒有 app、`docs/` 或 `issues/`。第二天先規格，再讓 Agent 生成骨架與功能。
全班基本路徑是「選員工 → 填表 → 後端驗證 → SQLite 存檔 → 我的假單顯示待審核」。主線兩張票：`issues/000-skeleton.md`、`issues/001-submit-leave.md`。

`course/` 固定課程邊界；已確認的 `docs/` 定義邊界內的產品行為。兩者衝突或必要決策未定時，列出問題請人決定，不能改規格來配合程式。偏差記進 `docs/LESSONS.md`。

## 實作與驗收

- 一次處理指定票。使用 `/implement`（Codex：`$implement`）；可測行為使用 TDD，逐一看到預期原因的紅燈，再做綠燈。
- 不刪除、跳過或放寬測試來通過。測試規格本身有錯時，先提出證據，由人確認修訂。
- 每個業務測試標註 `@pytest.mark.req("TC-xx", "AC/FR 編號")`；票結束時更新 `docs/06-test-plan.md` 的追溯表，未執行不能標通過。
- 使用虛擬環境執行：macOS/Linux `.venv/bin/python -m pytest`；Windows `.venv\Scripts\python.exe -m pytest`。不可假設 shell 已啟用 venv。
- 說完成前跑專案測試並貼出結果，操作核心畫面（可用瀏覽器工具，沒有則交由人操作），回報未驗證事項。
- 提交前查看 `git status`、`git diff`，只加入本次明確路徑。不自動推送、合併或切換 checkpoint。

## 技術邊界

- 依 `course/01-上課/04-STACK.md`：FastAPI 提供 HTML/CSS/原生 JavaScript，SQLite 與 pytest；主線不加前端框架、登入、部署或 LLM 呼叫。
- 前端呼叫相對路徑 `/api/...`；不開 CORS。驗證在後端；SQL 用參數；使用者文字以 `textContent` 或安全跳脫呈現。
- 天數由程式計算。測試使用暫存資料庫及固定時鐘，不讀寫開發資料庫。
- 金鑰不進版控，不讀出或印出秘密；進階模型設定只從環境載入。應用程式不可把 Agent CLI 當後端服務。

## 本專案決策（D2 拆票時由小組補充）

只記本組已確認且可檢查的規則，例如「半天假只接受同一天」。引用對應 SRS/SDS，避免複寫整份規格。

- 理由選填：002 已確認規格為新提交去除前後空白後最多 100 Unicode 碼位，中間空白計入；只含空白視為未填，不作組合正規化。既有 101–200 碼位理由保留原文，SQLite 儲存 CHECK 200 不改。程式尚待 002 實作，不把文件更新當成已生效；依 `docs/03-srs.md` FR-02、`docs/05-sds.md` API-03 與 `docs/04-sad.md` ADR-03。
- 接受過去日期補登，不以「今天」拒絕；日期先後、半天限單一工作日、扣週末與零工作日拒絕依 `docs/03-srs.md` FR-03、FR-04，計算契約依 SDS。
- 不自動去重：送出期間鎖住按鈕、顯示送出中；完成後再次提交相同合法內容可另建假單。依 `docs/03-srs.md` FR-06、FR-07 與 `docs/05-sds.md` UI-01。
- 網路中斷且無法確認結果時，解除按鈕鎖定，顯示「無法確認是否送出成功，請先查看我的假單，再決定是否重送」，不自動重送，不宣稱未存；與驗證拒絕不新增分開處理。依 SRS FR-06、FR-08 與 SDS 共通錯誤契約。
