# 001｜員工可提交請假並查看自己的待審核假單

- 狀態：實作與 Agent 驗證完成，等待使用者人工驗收；未 commit／push。
- 大小：大，估計 90–150 分鐘，含 TDD、畫面與證據；12 個 TC 有多個變體，不是只跑 12 次。
- 真正依賴：[000 骨架](000-skeleton.md) 已驗收，提供套件、應用、靜態頁與測試入口。
- 時間風險：加上 000 約 110–190 分鐘，可能超過教材 13:30–15:00 的 90 分鐘。使用者已確認此估計；不以趕時間為由刪已定案例。落後 15 分鐘請講師協助調整時程或依教材取得快照，不自行擴範圍或改規格。

## 建置前提與必讀段落

- 沿用 000 已實測的 Python 3.12 與虛擬環境，不另加框架、直接套件或服務。
- [AGENTS.md](../AGENTS.md) 全文；[WORKFLOW](../course/01-上課/02-WORKFLOW.md)「每階段的節奏」、卡 H 第二段；[STACK](../course/01-上課/04-STACK.md)「表單票 001 的邊界」。
- [PRD](../docs/02-prd.md) US-01～03、全部 AC 與補充決策；[SRS](../docs/03-srs.md) FR-01～10、規則字典、NFR-01～03。
- [SAD](../docs/04-sad.md) 信任邊界、交易故障、ADR-01／02；[SDS](../docs/05-sds.md) 資料模型、API-02～04、共通錯誤、UI、公開模組、注入與接縫補充。
- [測試計畫](../docs/06-test-plan.md) TC-01～12、M-01～06、進入／退出條件與追溯表；[LESSONS](../docs/LESSONS.md) 既有紀錄。
- 進入實作前完成小組 SAD／SDS 審查；已確認測試預期，延後矩陣／極端情境的課堂可接受性仍依測試計畫由講師確認。這些為審查前提，不虛構成已完成。

## 可檢查成果

- [x] API-02 員工名單：教學 A／B／C，明確資料初始化，可重複啟動且不覆寫現有資料。
- [x] API-03 提交：嚴格輸入、必填、合法員工／假別／時段、日期先後、理由處理；非法拒絕不新增。
- [x] 程式算天數：含首尾、扣週末；半天限單一工作日；零工作日拒絕；接受過去日期。
- [x] SQLite 交易與參數 SQL；後端固定 pending 及 day_units，客戶端 days／status／day_units 依契約拒絕；commit 成功後才回 201。
- [x] API-04 依員工 WHERE 條件查詢，id 降冪，空列表／不存在員工／讀取故障明確區分；重新整理後資料仍在。
- [x] 單頁表單與我的假單，理由選填最多 200 碼位，純文字呈現；送出中鎖定、完成解鎖、錯誤可修正。
- [x] 連線結果未知顯示先查假單提示，不自動重送；不把可能已存說成未存；成功提交後列表失敗不改說提交失敗。
- [x] 切換員工清掉舊列表，遲到的舊回應不覆寫目前員工；重複合法送出另建假單。
- [x] create_app 暫存 DB 與時鐘注入；每請求連線關閉、明確唯一 commit 責任、import 不連開發 DB；API 先登記最後才掛靜態頁。
- [x] TC 各變體、M-01～06、SQL／文字安全審查有真實證據；README、追溯與 LESSONS 更新。

主線之外不加主管核准、額度、同組提醒、國定假日、附件、登入、部署或 LLM。進階挑戰等使用者另行要求再開票。

## TC 歸屬與逐項 TDD

**全部業務 TC 歸本票。** TC-01 的 health 可沿用 000 證據與測試，員工名單與完整 TC-01 驗收在此完成；不得把 000 health 成功當成 TC-01 全組通過。

建議順序如下；每個可自動化的 TC／變體先寫預期測試，跑出正確業務原因的紅燈，再做最小綠燈，必要時重構並回歸。不得先把全部功能寫完才補測試，也不以實作函式算出預期答案。

1. TC-01 員工名單，搭明確暫存 DB／種子與固定時鐘。
2. TC-02 最薄成功提交、pending、持久化與列表接通。
3. TC-03 必填／非法值，TC-04 日期錯誤。
4. TC-05 半天，TC-06 週末／零工作日，必要純函式單元測試。
5. TC-07 理由／碼位與必要單元測試，TC-08 拒絕客戶端狀態／天數。
6. TC-09 員工隔離／空列表，TC-10 修正與重複提交。
7. TC-11 可控制資料故障，TC-12 文字安全；補齊對應 UI，操作 M-01～06。

TC-12 畫面部分及 M 流程使用實際人工證據，不冒充自動化 TDD。業務自動測試標 @pytest.mark.req("TC-xx", "對應 AC/FR")，參數變體均保留獨立執行結果；任何變體未通過／未執行不得將整群標通過。

## 驗收命令與操作

以下為可重做的命令範例；本次實際執行結果見票末證據。可於根目錄逐檔／逐 node 驗證：

```powershell
.venv\Scripts\python.exe -m pytest backend/tests/acceptance/test_basics.py
.venv\Scripts\python.exe -m pytest backend/tests/acceptance/test_submit_leave.py
.venv\Scripts\python.exe -m pytest backend/tests/acceptance/test_leave_validation.py
.venv\Scripts\python.exe -m pytest backend/tests/unit
.venv\Scripts\python.exe -m pytest backend/tests/acceptance/test_my_leaves.py
.venv\Scripts\python.exe -m pytest backend/tests/acceptance/test_storage_failures.py
.venv\Scripts\python.exe -m pytest backend/tests/acceptance/test_text_safety.py
.venv\Scripts\python.exe -m pytest
```

自動測試各用 tmp_path 與 create_app 注入 DB／時鐘；不將 LEAVEBOT_DB 指向開發 DB 跑測試。人工驗收另用獨立檔案，以下環境變數僅影響該終端機，驗收後移除設定：

```powershell
$env:LEAVEBOT_DB = 'backend/data/leavebot-acceptance.db'
$env:LEAVEBOT_TODAY = '2026-10-14'
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

瀏覽器開 http://127.0.0.1:8000/，依測試計畫 M-01～06 完整操作，記錄版本／網址／操作人與證據。port 占用改 8001 並記錄。獨立人工資料庫不進版控；此處不安排刪除或覆寫現有檔案。停止服務後清除該終端機設定：

```powershell
Remove-Item Env:LEAVEBOT_DB
Remove-Item Env:LEAVEBOT_TODAY
```

## 完成、證據與停止條件

- 本票全部納入的自動化變體實際通過，000 health 回歸仍通過；貼實際命令、日期、版本、通過／失敗數與紅綠摘要。
- M-01～06 與 SQL／文字審查有結果；沒有瀏覽器工具則由人操作，尚未完成不得宣稱完整驗收通過。
- 更新 docs/06-test-plan.md AC／FR／NFR 的真正證據；已確認延後的完整錯誤矩陣、極端日期、損毀恢復、所有並行情境與效能，保留限制與講師範圍處理，不宣稱全覆蓋。
- 錯天數、非法存檔、員工混淆、狀態／天數可覆寫、拒絕殘留、文字執行或結果未知時誤稱未存，均阻塞交付。
- README 提供可重做操作；LESSONS 只記真實偏差與處理。預期規格有錯先提證據請人確認，不刪、跳過或放寬測試。
- 完成本票即停止，不自動做需求變更票或進階功能；提交前 git status、git diff，只加入本次明確路徑，排除 DB／秘密／虛擬環境；不自動推送或合併。

目前證據：[001 執行紀錄](../docs/evidence/001-submit-leave.md)、[完整 pytest 輸出](../docs/evidence/001-pytest.txt)。2026-11-01 完整目前 pytest 58 passed、1 warning；M-01～06 經 Agent 瀏覽器操作通過。服務保留於 http://127.0.0.1:8000/，使用獨立驗收 DB；使用者人工驗收待完成。TDD 實際紅綠與既有行為回歸的界線、延後風險已記錄，未開始進階票。

