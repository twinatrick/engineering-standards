# 前端 Profile

適用：v3-admin-vite-templete 的 Vue 3／TypeScript／Scss／HTML。須同時讀取共通基準與下列完整來源，不以本頁摘要取代原文。

- [固定 master 完整工程規範](frontend/master-rules.md)：View → Service → 生成 API → Axios → Gateway、RBAC、錯誤回報、Vue／型別／生命週期、UI 與品質規範。
- [固定 master 完整 Agent 指南](frontend/master-agents.md)：pnpm、環境優先權、檢查順序及 Git 安全。
- [固定 master 完整審查合約](frontend/master-review.md)：資安、審查優先級及 HIGH／MEDIUM 阻擋門檻。

工具留在原專案：`package.json`、`pnpm-lock.yaml`、ESLint／TypeScript／Vitest、`scripts/check_local.py`、Husky 與 CI。

## 已裁決一致性說明（0.1.0）

1. **型別安全與 `any` 規範**：生產環境程式碼統一為「**禁止濫用 `any`**」（優先使用明確型別，不確定或邊界資料使用 `unknown` 搭配型別守衛或驗證；嚴禁為圖方便宣告 `any` 或暴力斷言 `(foo as any)` 規避型別設計；若屬第三方套件或生成契約邊界確需使用，須具備充分依據並交代範圍）。審查合約已與根規範及 Agent 指南同步。

本 Profile 已隨 0.1.0 正式發布，已知衝突均已裁決落地；未新增額外覆蓋率門檻，亦不套用後端測試工具。

## 0.2.0 接軌修訂

- 共通 C-10–C-12 適用 Vue／TypeScript 元件、Service、Store、Hooks、Router 與 API 基礎設施；本節參照前端提交 `5985351cc3dfc8f7b99368a2fe660852d3d4de7b` 的《開發規範.md》§4.5。參照提交不隨原專案工作文件自動更新，也不將其他未列變更一併納入。
- 保留既有外部請求流程，不另創 Views → Service → Store → Hooks → API 的必經鏈；Store／Hooks 的依賴角色取決於職責，不按目錄固定分級。
- 共用 Utils、Types、API 傳輸基礎設施不得反向依賴具體頁面；跨模組協作以單向編排或核心契約隔離。Props／Emits、函式簽名、TypeScript 型別皆可表達契約，不強制每個 Service 增加 Interface／Impl。
- 架構審查須提供循環路徑或反向引用證據，區分執行期 import 與 `import type`；候選搜尋不等於完整依賴圖驗證，未新增自動化門禁或套件。
- 固定來源 `frontend/master-*.md` 保留原始 bytes；本版補充仍須經消費端獨立核准升版，不因集中庫發布而覆寫既有快照。
