# 000 骨架執行證據

- 日期：2026-11-01；執行者：Codex；環境：Windows、Python 3.12.10，專案 .venv。
- 安裝：`.venv\Scripts\python.exe -m pip install -c course/01-上課/05-constraints.txt -e ".[dev]"` 成功；初次被沙箱網路權限阻擋，經授權後重跑，未變更 constraints。
- 實際版本：fastapi 0.162.0、uvicorn 0.54.0、httpx 0.28.1、pytest 9.1.1、starlette 1.10.0、pydantic 2.14.1、anyio 4.15.1。

## TDD 與測試

1. 先建只有 FastAPI 的入口及 health 測試，尚無 health 路由。
2. `.venv\Scripts\python.exe -m pytest backend/tests/acceptance/test_health.py`：1 failed；要求 200、實際 404，是路由缺少的預期紅燈。
3. 加 health 與靜態頁，同一測試：1 passed、1 warning（0.27 秒），未放寬測試。
4. `.venv\Scripts\python.exe -m pytest`：完整目前專案 1 passed、1 warning（0.27 秒）。不代表員工或請假業務通過。

警告為 StarletteDeprecationWarning：課程套件組合 TestClient 提示 httpx 棄用。保留警告，不擅加白名單外的 httpx2；屬未來相容性限制。

## 服務與瀏覽器

- 實際命令：`.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000`，startup complete。
- Playwright 開 http://127.0.0.1:8000/，首頁、JS、CSS、health 均 200，顯示「服務連線正常」。
- 停止後在已載入頁面按「重新檢查」，顯示「無法連線到服務，請確認服務已啟動後重新檢查。」，按鈕恢復可用。
- 相同命令重啟成功，重新載入並按「重新檢查」恢復正常；最後導覽 console 0 errors、0 warnings。初始 favicon 404 已用空 data favicon 修正。
- [首頁快照](000-home.yml)、[網路請求](000-network.txt) 是重啟後實際工具輸出。
- 路由列確認 health 在最後的靜態 Mount 前；importlib.resources 找到三個靜態檔。
- 交付時保留服務運行供驗收，uvicorn PID 14448。使用者人工驗收尚待完成；未開始 001，未 commit／push。
