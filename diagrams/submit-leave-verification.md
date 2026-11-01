# 提交請假流程圖：交付與驗證紀錄

- 日期：2026-11-01。
- 來源：`docs/03-srs.md` v0.2；此圖是規格視覺化，不是已實作功能或業務測試結果。
- 工具：repo 內 `.claude/skills/archify/bin/archify.mjs`，Archify 3.2.0；實際 Node v26.13.0。
- 候選來源：`diagrams/submit-leave.candidate.json`。
- HTML：`diagrams/submit-leave.html`。
- 完整結果：`diagrams/submit-leave.finalize.json`。
- 精簡結果：`diagrams/submit-leave.finalize-summary.json`。
- 實際瀏覽器結果：`diagrams/submit-leave.browser-check.json`。

實際執行：

```powershell
node .claude/skills/archify/bin/archify.mjs finalize workflow diagrams/submit-leave.candidate.json diagrams/submit-leave.html --quality showcase --json
```

第一次在沙箱內執行失敗，exit code 1：`output/path-identity-indeterminate`，底層 `EPERM`，工具無法安全確認輸出路徑；四項檢查皆未執行，不算通過。取得沙箱外執行授權後，以上同一命令 exit code 0，成功產出 HTML 與工具收據，未安裝或更新套件。

| 檢查 | 實際結果 |
|---|---|
| validate（showcase） | pass |
| deliver | pass |
| check | pass |
| browser-check | pass；requested=true、ran=true |
| 工具診斷 | 0 項 |
| 人工視覺與需求對照審查 | 未執行，交由小組對照 SRS 審圖 |

本次未修改 SRS 或產品需求，未執行應用程式測試。圖含選員工、填表、送出中、後端驗證、通過存檔與待審核、拒絕不存檔與修正、我的假單與空列表、連線結果未知分支。網路中斷分支不聲稱未存檔，不自動重送；未加入核准或 LLM。
