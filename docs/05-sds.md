# 05 SDS — LeaveBot 請假系統

- 版本：0.3；日期：2026-11-01；狀態：100 碼位變更已確認，待 002 實作／測試，現行程式仍為 200。
- 審查者：小組使用者代表。
- 上游：[SAD](04-sad.md)、[SRS v0.2](03-srs.md)、[PRD](02-prd.md)、[STACK](../course/01-上課/04-STACK.md)。契約變更須同步後續測試案例。

## 目錄

- [資料模型與不變量](#資料模型與不變量)
- [API 契約](#api-契約)
- [UI 與模組契約](#ui-與模組契約)
- [變更與未決](#變更與未決)

## 資料模型與不變量

員工是唯讀名單，假單只新增與查詢，不做修改、刪除或審核。日期、員工等輸入通過後端驗證後，才能寫入；天數、申請識別值與 `pending` 由後端決定。空理由統一保存空字串，API 亦回空字串。

| 欄位 | 型別、格式與可空性 | 預設／約束 | 來源 |
|---|---|---|---|
| `employees.id` | SQLite INTEGER，非空 | 主鍵，正整數；API 同名為 `id` | FR-01 |
| `employees.name` | TEXT，非空 | 教學顯示名稱，不作識別主鍵 | FR-01 |
| `leave_requests.id` | INTEGER，非空 | 主鍵，自動配置；重送得到不同 id | FR-05、07 |
| `leave_requests.employee_id` | INTEGER，非空 | 外鍵指向 `employees.id` | FR-01、09 |
| `leave_requests.leave_type` | TEXT，非空 | CHECK：`annual`、`personal`、`sick` | FR-01 |
| `leave_requests.start_date` | TEXT，非空 | ISO `YYYY-MM-DD`，有效日曆日由程式驗證 | FR-03、04 |
| `leave_requests.end_date` | TEXT，非空 | 同格式，CHECK：不早於 start_date | FR-03 |
| `leave_requests.period` | TEXT，非空 | CHECK：`full`、`am`、`pm` | FR-01、04 |
| `leave_requests.reason` | TEXT，非空 | 新提交去前後空白後最多 100 碼位，空值轉 `""`；DB CHECK length ≤ 200 保留舊資料相容性，非新提交許可上限 | FR-02、ADR-03 |
| `leave_requests.day_units` | INTEGER，非空 | 正整數，單位 0.5 天；full 為正偶數，am／pm 為 1 且起訖同日 | FR-04、05 |
| `leave_requests.status` | TEXT，非空 | DEFAULT `pending`，CHECK 只能為 `pending` | FR-05 |

不接受客戶端設定資料庫 id、day_units、days、status。API 假單物件使用 `days` 數字表示天數，不公開 day_units；1 與 1.0 語意相同。建索引 `(employee_id, id)`；讀取必須使用 `WHERE employee_id = ? ORDER BY id DESC`，不先取全部再由瀏覽器過濾。排序是本版介面設計，非新增業務規則。

### 初始化、交易與生命週期

- `init_db(path, employees)` 建立缺少的表及索引；啟用外鍵。新增範例員工使用按 id 不重複新增，不清空或覆寫既有資料；可重複初始化，新增既有表不代表支援任意 schema 升級。
- 教材未附本組正式名單；本版指定**教學範例**：`1/員工A`、`2/員工B`、`3/員工C`，不代表真實員工。全新資料庫只有名單，無預建假單。測試自行明確注入名單及案例，不依賴開發資料。
- 每個請求開自己的 sqlite3 連線，`PRAGMA foreign_keys = ON`，設定 timeout＝5 秒，finally 關閉；不使用全域長連線。5 秒是鎖等待配置，非效能承諾。
- POST 在單一交易內查員工、驗證業務規則、計算、INSERT、取得回應資料並 commit；驗證失敗不執行 INSERT；交易失敗 rollback，成功 commit 後才回 201。SELECT 不新增假單。
- 沒有重複內容 UNIQUE 約束、重送鍵或自動重試。同一合法內容送兩次，預期新增兩張。
- 一般查詢／寫入已確定失敗且回滾：503；commit 階段若無法確定結果：結果未知錯誤。不得把可能已提交的情境寫成「保證未存」。分類詳見 API。

## API 契約

全部 API 使用同來源相對路徑 `/api/...`，JSON 回應 `Content-Type: application/json`；POST 請求為 JSON 物件。以下為**設計範例**，不是執行紀錄。除 health 外，資料庫故障均按共通錯誤處理。

### API-01｜GET /api/health

用途：骨架票確認服務存活。成功 200：`{"status":"ok"}`。不探測資料庫，不將存活宣稱為所有功能可用；服務未啟動是連線失敗，無 HTTP 成功回應。

### API-02｜GET /api/employees（FR-01）

- 無 query 或 body；未知 query 回 422 `UNKNOWN_FIELD`。
- 成功 200：`{"employees":[{"id":1,"name":"員工A"},{"id":2,"name":"員工B"},{"id":3,"name":"員工C"}]}`；按 id 升冪，沒有資料回 `{"employees":[]}`。
- 讀取失敗 503 `DB_UNAVAILABLE`，不新增假單；畫面不得把讀取失敗當成名單為空。

### API-03｜POST /api/leaves（FR-01～08）

請求：

```json
{"employee_id":1,"leave_type":"annual","start_date":"2026-10-12","end_date":"2026-10-12","period":"full","reason":" 補登 "}
```

- 五個必填欄位：employee_id、leave_type、start_date、end_date、period；不得缺漏或 null。reason 可省略、null 或字串，省略／null 轉 `""`；拒絕其他型別。
- employee_id 為嚴格正整數（不將 true、`"1"` 或 1.5 自動轉整數）；leave_type 僅 annual／personal／sick；period 僅 full／am／pm。日期為精確 `YYYY-MM-DD` 字串且日曆有效，不接受時間戳或自動修補。
- 額外欄位一律 422 `UNKNOWN_FIELD`，包括 status、days、day_units、id；不得新增。未傳 JSON content type 回 415；損壞 JSON 回 400。
- reason 先去除兩端 Unicode White_Space 字元，再按 Unicode 碼位計數；集合固定為 U+0009～000D、0020、0085、00A0、1680、2000～200A、2028、2029、202F、205F、3000。中間空白保留；不移除 U+200B、U+FEFF，不做組合正規化。前後端共用此明確語意，避免各語言預設 trim 的差異；後端結果為準。
- 處理後最多 100 碼位；101、200、201 碼位的新提交均回下列 REASON_TOO_LONG，資料不新增、不改寫。HTTP 欄位／路徑與錯誤代碼不變，僅限制與訊息更新。GET 列表須允許歷史 101–200 碼位理由原文，不套用此輸入驗證。
- 業務算法完全依 SRS：接受補登；反向日期拒絕；半天限同一工作日；含首尾只算週一至週五；W＝0 拒絕。不得因時鐘日期而拒絕過去日期。

成功 201，**只有 commit 成功才回傳**：

```json
{"leave":{"id":1,"employee_id":1,"leave_type":"annual","start_date":"2026-10-12","end_date":"2026-10-12","period":"full","reason":"補登","days":1,"status":"pending"}}
```

失敗按下表；驗證拒絕無新增資料。相同合法請求再次成功時，取得另一 id；無去重。

### API-04｜GET /api/leaves?employee_id=1（FR-09、10）

- 必填 query employee_id，單一正整數十進位字串；缺少、重複或非正整數回 422。只接受 employee_id，其他 query 回 422；不使用 body。
- 不存在的員工回 404 `EMPLOYEE_NOT_FOUND`，與合法員工沒有申請不同。
- 成功 200：`{"leaves":[假單物件]}`；假單物件欄位同 API-03 回應，依 id 降冪；空列表為 `{"leaves":[]}`。不得包含其他員工假單。
- 讀取本身無新增；503 是讀取失敗，不得轉成 200 空列表。

### 共通錯誤契約

```json
{"error":{"code":"REVERSE_DATES","message":"結束日期不得早於開始日期","field":"end_date"}}
```

固定為單一 error，code 為下表穩定代碼、message 為可理解繁體中文、field 為欄位名稱或 null；不回傳使用者原始輸入、SQL、堆疊或本機路徑。FastAPI 輸入驗證錯誤也轉成此結構，不直接回預設 detail 陣列。

| HTTP／code | 條件與 message | 資料副作用 |
|---|---|---|
| 400 `INVALID_JSON` | JSON 無法解析／「請提供有效的 JSON」 | 不新增 |
| 415 `UNSUPPORTED_MEDIA_TYPE` | POST 非 application/json／「請使用 JSON 格式送出」 | 不新增 |
| 422 `UNKNOWN_FIELD` | 未知欄位／「包含不支援的欄位」 | 不新增 |
| 422 `REQUIRED_FIELD` | 必填缺漏、null 或空字串／「請填寫必要欄位」 | 不新增 |
| 422 `INVALID_VALUE` | 型別、正整數或允許值不合法；含重複 query／「欄位值不合法」 | 不新增 |
| 422 `INVALID_DATE` | 日期格式或日曆日無效／「請填寫有效日期 YYYY-MM-DD」 | 不新增 |
| 422 `REASON_TOO_LONG` | 新提交理由處理後超過 100 碼位／「理由最多 100 字」；field 為 reason | 不新增、不改寫 |
| 404 `EMPLOYEE_NOT_FOUND` | 合法 id 但名單無此人／「找不到所選員工」 | 不新增 |
| 422 `REVERSE_DATES` | 結束早於開始／「結束日期不得早於開始日期」 | 不新增 |
| 422 `HALF_DAY_SINGLE_DATE` | am／pm 起訖不同日／「半天假限同一天」 | 不新增 |
| 422 `NO_WORKDAYS` | W＝0／「申請期間沒有工作日」 | 不新增 |
| 503 `DB_UNAVAILABLE` | 開啟／讀取失敗或確定回滾的寫入故障／「資料庫暫時無法使用，請稍後再試」 | GET 無新增；POST 確定未提交 |
| 503 `SUBMISSION_UNKNOWN` | POST commit 結果無法確認／「無法確認是否送出成功，請先查看我的假單，再決定是否重送」 | 可能已提交，不保證無新增 |
| 404 `NOT_FOUND` | 未知 /api 路徑／「找不到此 API」 | 不新增 |
| 405 `METHOD_NOT_ALLOWED` | 方法不支援／「不支援此操作方法」 | 不新增 |
| 500 `INTERNAL_ERROR` | 未預期例外／「系統暫時無法處理」 | POST 若無法確認提交，改用 SUBMISSION_UNKNOWN；不得假稱未存 |

多錯誤只回第一個：媒體型別 → JSON 解析 → body 物件型別 → 未知欄位 → 欄位結構驗證（employee_id、leave_type、start_date、end_date、period、reason 順序）→ 員工存在 → 日期先後 → 半天單日 → 工作日。reason 超長屬 reason 欄位驗證；同類未知欄位按名稱排序選首個。錯誤 field：對應欄位；半天為 period、零工作日為 start_date、媒體／JSON／整體型別／資料庫／系統錯誤為 null。body 不是物件用 INVALID_VALUE；空白必填字串不能自動修成合法值。

## UI 與模組契約

### UI-01｜單頁表單與我的假單

- `index.html`、`style.css`、`app.js` 放於 `backend/app/static/`。初始呼叫 API-01 與 API-02；未選員工時不查假單、不允許送出；名單載入失敗顯示錯誤，名單空則提示無可選員工。
- 選員工呼叫 API-04，立即清除舊列表並顯示載入中；每次讀取帶前端序號，只有最新序號且回應員工仍等於目前選取值才渲染，避免舊回應覆寫。列表錯誤顯示「無法讀取假單」，不冒充空列表。空陣列顯示「目前沒有申請」。重新整理後可重新選取員工，不承諾記住選項。
- 假別選單顯示中文對應 annual／personal／sick，時段對應 full／am／pm；日期欄位傳精確日期字串。理由可用相同計數作輔助提示，不能以 HTML maxlength 的 UTF-16 計數取代後端規則。
- 初始及輸入中理由提示改為 `/ 100 字`；101 送出須能由後端拒絕並顯示「理由最多 100 字」。查詢顯示歷史長理由不得截斷，不以 maxlength 改變碼位算法。
- submit handler 先檢查 submitting，再立刻設 true 並鎖住送出、員工與輸入欄位，擷取該次輸入快照，僅送 API-03，不附 days／status。進行中不允許重入。
- 201 顯示成功與待審核，解鎖後重新呼叫 API-04；若隨後查詢失敗，保留「送出成功」回饋，另顯示「無法讀取假單」，不能將成功提交改說成失敗。
- 確定驗證／資料庫錯誤顯示 error.message，保留原填內容便於修正。finally 解除 submitting 與欄位鎖；不清除使用者輸入，允許完成後再次送出相同合法內容。
- fetch 失敗、成功回應無法解析或 POST 結果無法確認，顯示 SRS 指定的「無法確認是否送出成功，請先查看我的假單，再決定是否重送」，解鎖、不自動重送；取得 SUBMISSION_UNKNOWN 同理。提供「查看我的假單」操作，只讀不寫。
- 員工名稱、理由與伺服器錯誤一律用 textContent 建立，不用使用者資料組 innerHTML。沒有核准、額度、撤回或模型入口。

### Python 公開模組接縫（均為待實作契約）

以下型別名稱為契約名稱，型別細節放 schemas；業務錯誤使用 `DomainError(code, field)`，資料故障使用 `StorageUnavailable` 或 `SubmissionUnknown`，HTTP 對應由 API 層處理。

| 模組／公開入口 | 輸入與輸出 | 責任與限制 |
|---|---|---|
| `main.create_app(*, db_path=None, today_provider=None, seed_employees=None) -> FastAPI` | keyword overrides；回新 app | 建立設定、掛錯誤處理器、註冊 API；lifespan 才 init_db。保留 `app = create_app()` 供 uvicorn；import 不建立 DB。 |
| `settings.load_settings() -> Settings` | env → 絕對 db_path 與今天設定 | db_path override 優先；其次 LEAVEBOT_DB，最後專案根目錄 backend/data/leavebot.db；相對設定以專案根定位。 |
| `clock.build_today_provider(value: str \| None) -> Callable[[], date]` | ISO 日期或 None → 日期提供者 | 有值固定回該日，格式錯誤啟動失敗；None 回本機 date.today。注入函式優先於環境。 |
| `db.init_db(path: Path, employees: Sequence[Employee]) -> None` | 明確路徑與名單 | 建目錄、表、索引、範例種子；可重複呼叫；失敗中止啟動。 |
| `db.connect(path: Path) -> context manager[Connection]` | 每次新連線 | 外鍵、row factory、timeout，finally close；未提交交易離開時回滾。 |
| `rules.normalize_reason(value: str \| None) -> str` | 理由 → 處理後文字 | 按上述明確空白集合處理、計碼位，超長 DomainError；不做 HTML 轉換或字元正規化。 |
| `rules.calculate_day_units(start: date, end: date, period: str) -> int` | 已解析日期、合法時段 → 正整數 | 反向、半天跨日、零工作日拋對應 DomainError；不連 DB、不讀今天；用完整週數與餘日算 W，避免長日期區間逐日耗時。 |
| `repository.list_employees(conn) -> list[Employee]` | 連線 → id 升冪資料 | 參數 SQL／固定 SQL，唯讀。 |
| `repository.employee_exists(conn, employee_id: int) -> bool` | id → 是否存在 | 以參數查詢，不以名稱比對。 |
| `repository.insert_leave(conn, validated_leave) -> LeaveRecord` | 合法欄位、後端 day_units → 物件 | INSERT 固定 pending，回新 id；不自行 commit、不接受客戶端 status。 |
| `repository.list_leaves(conn, employee_id: int) -> list[LeaveRecord]` | id → id 降冪列表 | SQL 中限定 employee_id；不新增。 |
| `leave_service.submit_leave(conn, request: LeaveInput) -> LeaveRecord` | 嚴格型別輸入 → 新假單 | 擁有上述 POST 交易與業務流程；提交成功才返回；確定回滾拋 StorageUnavailable，提交無法確認拋 SubmissionUnknown。 |
| `leave_service.get_leaves(conn, employee_id: int) -> list[LeaveRecord]` | 正整數 → 假單列表 | 先確認員工存在，否則 DomainError；結果轉換 days。 |
| `api.register_routes(app, settings, today_provider) -> None` | 應用依賴 → 註冊 API-01～04 | HTTP 契約、錯誤映射、取得每請求連線；先完成 API 與未知 /api 路由處理，再掛 `/` StaticFiles(html=True)。 |

schemas 定義嚴格 `LeaveInput`（僅六個輸入欄位）、`Employee`（id/name）、`LeaveRecord`（API 假單物件）及 `ErrorResponse`（error）。repository 寫入參數使用獨立 validated_leave（包含 day_units，不含客戶端 status）；不把 HTTP body 直接展開寫入 SQL。API 不回 DB 的 day_units。

接縫補充（0.2 核對）：

- `ValidatedLeave` 的固定欄位為 employee_id:int、leave_type:str、start_date:date、end_date:date、period:str、reason:str、day_units:int；這是服務內部資料，不是 API 可直接接收的型別。repository 以日期的 ISO 字串寫入，將 day_units 除以 2 後建立 LeaveRecord。
- LeaveInput 的 reason 在欄位驗證階段呼叫 normalize_reason，日期在同階段解析為 date，再交服務；因此理由超長優先於員工存在性錯誤，符合上方錯誤順序。服務不重新採用另一套文字處理規則。
- `db.connect` 只管理連線開啟、未完成交易回滾及關閉，**不得在離開 context 時自動提交**；唯一 POST commit 擁有者是 submit_leave，repository 不提交。服務用明確交易包住查員工至新增，回應物件在 commit 前建立，避免提交後因物件轉換失敗誤報未保存。
- 同一請求的 connect、服務呼叫、repository 與 close 必須在同一執行緒完成；可用同步 API handler 在自身 context 內開關連線，不將 sqlite3 連線跨執行緒傳遞。
- `seed_employees=None` 才使用上述三位教學員工；明確傳入空序列表示不播種，不能因空序列被當成 false 而偷偷使用預設名單。明確注入 db_path／today_provider 時，不再解析對應的環境值，讓測試不受本機環境影響。

### 測試資料庫與時鐘注入

- 每個測試用 pytest tmp_path 下的獨立 sqlite 檔案，傳給 create_app(db_path=...)，並傳明確 seed_employees；不使用 `:memory:`，避免每請求新連線看到不同資料庫。
- 在 TestClient context 內啟動／結束 lifespan，進入時初始化、離開時完成資源清理；每次請求及錯誤路徑均關閉連線，測試結束可移除暫存檔。
- 測試傳 today_provider 固定回 2026-10-14，補登請求為 2026-10-12。課堂一般執行可設定 LEAVEBOT_TODAY=2026-10-12，兩者是不同情境，不互相覆寫。
- 主線不依「今天」拒絕任何日期；時鐘接縫供可重現情境，不能為了用它而增加日期限制。若未指定使用真實本機日期，啟動紀錄註明時鐘模式與日期，不輸出秘密。
- rules 純函式可獨立測邊界；API 測試核對回應與資料庫筆數／內容；SQL／文字安全做案例及審查；前端人工核對連點、員工快速切換與網路中斷。以上均為計畫，尚未執行。

## 變更與未決

版本 0.3／002：使用者確認新提交 100、101／200／201 拒絕，舊假單保留。下述「首次建表」為 001 設計背景；目前已有 001 的儲存 schema，因此本變更明確**不遷移**、不改 db.py 的 CHECK 200。normalize_reason 改新提交上限，錯誤訊息與 UI 同步；讀取路徑照原文回傳。測試預期修訂已由人確認，新邊界尚未實作／執行。

目前無既有 app／資料表，不需遷移舊資料；本版只設計首次建表與可重複初始化。未來改契約／schema 必須另列遷移與相容性方案，不能靠 init_db 偷改既有資料。不新增設計以外的 API。

版本 0.2：重複設計請求時沿用既有成果，補明內部 ValidatedLeave 型別、正規化順序、唯一提交責任、連線執行緒與明確空種子／設定覆寫語意；不修改 PRD、SRS 或公開 API。

未決核心產品規則：無。教學名單、錯誤優先序、嚴格未知欄位及 SQL 排序為本版明訂的設計選擇，待人工審查；不是現有程式事實。具體套件版本沿用課程 constraints，須在實作環境實測後才報相容；效能仍待量測，不捏造數字門檻。

### FR／NFR 設計落點

| 需求 | 設計落點 |
|---|---|
| FR-01 | 員工表與範例種子、API-02／03、嚴格 schemas、員工存在性查詢 |
| FR-02 | reason 欄位、normalize_reason、API-03、textContent |
| FR-03 | 日期格式／先後錯誤、calculate_day_units；過去日期不比較今天 |
| FR-04 | day_units、不變量、calculate_day_units、API 日期錯誤契約 |
| FR-05 | 單一交易、commit 後 201、固定 pending、拒絕額外 days／status |
| FR-06 | UI submitting／finally、API 共通錯誤、結果未知提示且不重送 |
| FR-07 | 無內容唯一限制，每次合法 POST 新增並產生新 id |
| FR-08 | 驗證優先序、DomainError、無 INSERT 拒絕分支、修正後重送 |
| FR-09 | API-04 WHERE employee_id、持久 SQLite、UI 避免舊回應覆寫 |
| FR-10 | API 空陣列與未知員工／故障分開、UI 空狀態及清除舊列表 |
| NFR-01 | 參數 SQL、textContent、安全錯誤格式與不記理由 |
| NFR-02 | 交易與回滾、commit 後成功、實體檔案重讀、拒絕前後資料核對 |
| NFR-03 | create_app overrides、tmp_path、TestClient lifespan、固定 today_provider |

沒有設計落點的 FR／NFR：無。人工 Gate 須核對請求／回應、錯誤優先序、資料副作用、教學名單、理由字元例子、交易故障與結果未知區別，以及模組能否各自依契約實作。停止於設計文件；未建立程式、測試計畫或工作票，未安裝或執行服務。
