# 前端 Profile

適用：v3-admin-vite-templete 的 Vue 3／TypeScript／Scss／HTML。須同時讀取共通基準與下列完整來源，不以本頁摘要取代原文。

- [固定 master 完整工程規範](frontend/master-rules.md)：View → Service → 生成 API → Axios → Gateway、RBAC、錯誤回報、Vue／型別／生命週期、UI 與品質規範。
- [固定 master 完整 Agent 指南](frontend/master-agents.md)：pnpm、環境優先權、檢查順序及 Git 安全。
- [固定 master 完整審查合約](frontend/master-review.md)：資安、審查優先級及 HIGH／MEDIUM 阻擋門檻。

工具留在原專案：`package.json`、`pnpm-lock.yaml`、ESLint／TypeScript／Vitest、`scripts/check_local.py`、Husky 與 CI。

## 已裁決一致性說明（0.1.0-draft.1）

1. **型別安全與 `any` 規範**：生產環境程式碼統一為「**禁止濫用 `any`**」（優先使用明確型別，不確定或邊界資料使用 `unknown` 搭配型別守衛或驗證；嚴禁為圖方便宣告 `any` 或暴力斷言 `(foo as any)` 規避型別設計；若屬第三方套件或生成契約邊界確需使用，須具備充分依據並交代範圍）。審查合約已與根規範及 Agent 指南同步。

本 Profile 為草案，沒有新增覆蓋率門檻，也不為了共通化套用後端測試工具。
