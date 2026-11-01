# 002｜新提交理由最多 100 碼位，舊假單保留原文

- 狀態：需求、測試期待與相容策略已由使用者確認；規格／案例已更新，程式與測試程式尚未修改，新案例未執行。
- 日期：2026-11-01；大小：小至中，估計 30–60 分鐘（含紅綠、回歸、畫面與證據），不含獨立 TRACE 問題修復。
- 真正依賴：001 現有提交、列表、暫存 DB fixture 與理由處理；已存在，無須重建骨架或換技術。
- 實作方式：使用者另開新對話，以 `$implement` 指定本票；本次規劃不授權直接實作。

## 已確認需求與來源

使用者確認「兩項都採取建議」：

1. 新提交理由去除前後空白後，最多 **100 Unicode 碼位**；100 成功，101、200、201 都拒絕且資料不新增或改寫。
2. 變更前已存的 101–200 碼位理由原文保留，仍可查閱，不截斷、不刪除；SQLite CHECK 儲存上限維持 200，不遷移 schema。新提交的 100 由後端規則強制。

理由仍選填，空值／純空白合法，中間空白計入，不做組合正規化；空白集合、特殊字元計數、錯誤格式、天數與 pending 規則不變。新上限只影響提交，不用它重新驗證已保存的列表內容。

必讀：

- [AGENTS.md](../AGENTS.md)、[WORKFLOW](../course/01-上課/02-WORKFLOW.md) 卡 J／單票實作節奏、[STACK](../course/01-上課/04-STACK.md)。
- [PRD](../docs/02-prd.md) AC-02.2、AC-03.1 與變更確認紀錄。
- [SRS v0.3](../docs/03-srs.md) FR-02、FR-08、FR-09、NFR-02 與新邊界算例。
- [SAD v0.2](../docs/04-sad.md) ADR-03、[SDS v0.3](../docs/05-sds.md) reason 欄位、API-03／04、REASON_TOO_LONG、UI-01 與相容性規則。
- [測試計畫 v0.3](../docs/06-test-plan.md) TC-07 新邊界、歷史資料相容性、追溯與既有 TRACE 紅燈。

## 受影響位置與明確邊界

| 位置 | 本票工作 |
|---|---|
| `backend/app/rules.py` normalize_reason | 新提交由 200 改 100；沿用去空白與碼位算法，可用明確常數避免散落數字 |
| `backend/app/errors.py` | REASON_TOO_LONG 訊息改「理由最多 100 字」；code、field、HTTP 422 不變 |
| `backend/app/schemas.py` | 核對仍走同一 normalize_reason 入口，不另做第二套驗證；沒有需要不改 |
| `backend/app/static/index.html` | 初始字數提示 /100 |
| `backend/app/static/app.js` | 輸入中字數提示 /100，仍以碼位計數；列表不截斷舊內容 |
| `backend/tests/acceptance/test_leave_validation.py` | 新增獨立 101 拒絕紅燈，再依已核准期待更新 TC-07 參數與錯誤訊息斷言 |
| `backend/tests/unit/test_reason.py` | 必要的 100／101 純函式邊界、先去空白後計數；既有碼位算例保留 |
| 相容性 API 測試（建議 `test_reason_compatibility.py`） | 舊 200 碼位假單啟動、查詢、重建後完整保存；同樣文字新提交拒絕 |
| README、測試計畫、LESSONS | 寫真實生效狀態、指令／結果與限制，不覆蓋舊證據 |
| 流程圖文件 | 現有 submit-leave HTML／candidate 為 SRS v0.2 的 200 上限歷史圖；交付時僅同步規則卡片與版本，拓樸不變，依 repo Archify 流程重產與驗證；不得手改舊工具收據假稱通過 |

**不修改 `backend/app/db.py` 的 CHECK 200**，不重建／清空既有 DB，不截斷資料；不能為「配合新規則」直接改成 CHECK 100。直接 SQL 能儲存歷史 200 是已確認相容策略，不是新 API 接受 200 的理由。沒有核准、額度、LLM 或其他變更。

## 先紅再綠：執行順序

1. 先讀現有 code／tests 與已知失敗證據；原程式仍允許 200。不要先改上限、訊息、畫面或舊測試參數。
2. 新增**一個獨立** TC-07／AC-02.2／FR-02／FR-08 測試：合法員工／假別／工作日，理由為「假」重複 101 次；送出前記完整假單快照；期待 422、REASON_TOO_LONG、reason 與「理由最多 100 字」，送出後全資料不變。資料庫用 tmp_path，今天固定 2026-10-14，不碰開發 DB。
3. 只跑此測試，應在**舊程式回 201 而非 422**處失敗。讓使用者看到命令與實際紅燈後先停下確認，再做綠燈。若不是該原因失敗，先診斷測試／環境，不把 import 或 fixture 錯誤當成有效紅燈；若意外通過，先查版本，不偽造失敗。
4. 確認後按同一個行為逐項循環，修正後端上限與訊息、補邊界與相容性、同步畫面。不要一次寫完全部實作才補測試。
5. 新測試不得放寬。原「200 成功」測試按下列**使用者已核准的規格變更**修訂；不是為通過而刪測試。原 201 拒絕、空值、空白與 Unicode 算例繼續保留。

### 已核准的測試期待修訂

| 案例 | 舊期待 | 新期待與依據 |
|---|---|---|
| TC-07 新提交 200 碼位 | 201 成功保存 | 422 REASON_TOO_LONG、資料不變；依 PRD AC-02.2／SRS FR-02 新上限與使用者確認 |
| TC-07 新提交 201 碼位 | 422 拒絕 | 仍拒絕；若斷言訊息，改為「理由最多 100 字」 |
| TC-07 新提交 100 碼位 | 原規格下合法但未獨立固定新邊界 | 201，原文保存，pending／天數仍由後端決定 |
| TC-07 新提交 101 碼位 | 舊程式可接受 | 新增 422 拒絕、全資料不變，先看到紅燈 |
| 舊 DB 200 碼位理由 | 可查原文 | 繼續可查；重啟／查詢不截斷或改寫，依 ADR-03 |

舊資料測試可用參數 SQL 建立已知歷史 fixture，不能把新 API 暫時放寬來製造資料；讀回要比對獨立固定原文。所有業務測試標 req，維持 TC-07 群組及對應 AC／FR，無須增加第 13 個群組。

## 驗收指令與畫面

以下命令為待執行範例；實際新增 test node 名稱須與程式一致並回填證據：

```powershell
.venv\Scripts\python.exe -m pytest backend/tests/acceptance/test_leave_validation.py::test_101_codepoint_reason_is_rejected_without_saving -q
.venv\Scripts\python.exe -m pytest backend/tests/acceptance/test_leave_validation.py backend/tests/unit/test_reason.py backend/tests/acceptance/test_reason_compatibility.py -q
.venv\Scripts\python.exe -m pytest
```

人工驗收用獨立 SQLite 檔與固定時鐘啟動，不覆寫目前驗收／開發資料。首頁理由提示初始及輸入時均為 /100；100 送出成功，101 顯示上限錯誤，筆數／舊資料不變；已有 200 碼位理由完整顯示。另核對空白與組合 emoji 計數未退回 UTF-16 單元。

## 已知獨立失敗與完成條件

現有 `backend/tests/acceptance/test_method_errors.py` 的 TRACE 錯誤格式已穩定紅燈，見 [診斷證據](../docs/evidence/002-method-error-red.md)。它不是本次變更新增，不是本票真正阻塞依賴；**不刪、不跳過、不放寬，也不順手修復混入本票**。使用者若另外授權修復，另按診斷流程處理與記證據。

- [ ] 101 測試先在舊實作失敗，經使用者確認後才實作。
- [ ] 新提交 100 成功；101／200／201 拒絕、錯誤契約正確且資料不變。
- [ ] 舊 101–200 理由不改寫／不刪除，200 固定算例經啟動、查詢、重啟後仍一致；DB schema 不遷移。
- [ ] 其餘原本有效測試仍通過；只依已核准變更修訂失效期待。
- [ ] 完整 pytest 實際執行，逐項回報結果；若僅剩已知 TRACE 失敗，明列實際數字，可說理由變更案例通過，不能說整體全綠或整體交付驗收通過。
- [ ] 畫面操作與文件／圖卡一致；更新 docs/06-test-plan.md 追溯及 docs/LESSONS.md 真實偏差，保留 001 原歷史證據。
- [ ] git status／git diff 核對範圍；不自動 commit、push、合併或開進階功能，完成後停止等待驗收。

目前執行結果：未建立／執行新測試，未改應用程式，未宣稱 100 上限已生效。
