# 診斷：不支援 HTTP 方法的錯誤格式不一致

- 日期：2026-11-01；狀態：已穩定重現，已展示失敗證據，尚未修復。
- 類別：實作錯誤（介面契約），不是套件缺少或環境故障；規格已有明確預期，無須改規格。
- 依據：docs/05-sds.md「共通錯誤契約」規定方法不支援回 405 METHOD_NOT_ALLOWED，JSON 為 error.code／message／field，不使用預設 detail。

## 一條可重做指令

```powershell
.venv\Scripts\python.exe -m pytest backend/tests/acceptance/test_method_errors.py -q --tb=short
```

兩次獨立執行皆 **1 failed、1 warning，0.09 秒**。測試有 TC-03／FR-08 marker；使用既有 client fixture 的 tmp_path 資料庫、固定時鐘與種子，不碰開發或畫面驗收資料庫。

最小操作：TRACE /api/leaves，無請求 body。

- HTTP 預期／實際：均為 405。
- 預期：`{"error":{"code":"METHOD_NOT_ALLOWED","message":"不支援此操作方法","field":null}}`。
- 實際：`{"detail":"Method Not Allowed"}`。
- 失敗位置：test_method_errors.py 的回應 JSON 相等斷言；不是 import、連線或資料庫初始化錯誤。
- 資料不變斷言位於格式斷言之後，本次未抵達，不冒稱此測試已驗證資料不變。

## 單一原因與對照

假說：api.py 的兜底路由只列出 GET／POST／PUT／PATCH／DELETE／OPTIONS／HEAD，TRACE 無法進入自訂 DomainError 處理，而由框架直接產生預設 405。

對照在另一個暫存 DB 呼叫 DELETE /api/leaves，結果 405、METHOD_NOT_ALLOWED。相同網址與環境，僅換 HTTP 方法即走不同錯誤格式；配合 TRACE 未列入兜底方法與 main.py 沒有統一 HTTPException 處理，支持上述原因。

目前影響：一般表單 GET／POST 不受此重現影響，但不支援方法的客戶端無法一致讀取 error.code。先前 58 passed 是已測案例通過，不能推論未完整測遍的 HTTP 錯誤矩陣都正確。

## 下一步（尚未執行）

使用者看過失敗證據後，修正共通 HTTP 錯誤處理，保留原測試與預期，不以放寬斷言或修改 SDS 通過；再跑此測試與完整 pytest。修復前未宣稱已解決，未 commit／push。
