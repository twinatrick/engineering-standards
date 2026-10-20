# OpenCode Agent 專案指南

請所有 Agent 在協助開發本專案時，嚴格遵守以下準則。**請務必使用繁體中文與使用者溝通與撰寫說明。**

---

## 🗣️ 語言與溝通準則 (Language & Communication)

- **強制使用繁體中文**：所有向使用者的回應、程式碼註解、Commit 訊息、PR 說明與技術文件，一律強制使用繁體中文。
- **直指核心**：避免冗長鋪墊或無意義的客套，直接報告結果、執行修改或提出關鍵決策。

---

## 📦 套件與執行環境 (Environment & Commands)

- **環境設定與執行優先權 (重要)**：
  - 在執行任何開發伺服器、建置、API 生成或測試指令前，請先檢查當前專案目錄下是否存在 **`.run` 資料夾**。
  - 若存在 `.run` 目錄，必須優先讀取其中的配置檔案 (如 XML)，並將其內嵌的環境變數（如 `.env` 覆寫項目）或啟動參數作為最高優先級應用於後續的執行環境中。
- **套件管理員**：專案已從 npm 遷移至 pnpm，**一律嚴格使用 `pnpm`** 來安裝套件與執行指令。套件鎖定檔案為 `pnpm-lock.yaml`。
- **開發伺服器**：`pnpm dev`
- **建置指令**：`pnpm build:dev`, `pnpm build:stage`, `pnpm build:prod`。
- **API 生成**：`pnpm generate-api`。

---

## 🏗️ 架構與代碼規範 (Architecture & Standards)

- **唯一規則來源**：**絕對必須遵守《`開發規範.md`》**。
- **五層單向架構**：`Views (*.vue)` ➔ `Service (service.ts)` ➔ `Api (Api.ts)` ➔ `Client (Axios)`。
- **組件直連 API 禁令**：視圖組件（`*.vue`）嚴格禁止直接引入或呼叫 API，必須經由該目錄下的 `service.ts` 業務抽象層。
- **連線資訊脫敏**：程式碼中嚴格禁止出現寫死的私有 IP、Tailscale 網域或硬編碼網址，一律透過 `import.meta.env` 讀取。
- **嚴格型別**：生產代碼禁止濫用 `any`。所有資料型別以 `Api.ts` 與 `types/` 為契約準則。
- **生命週期釋放**：定時器、事件監聽與音訊 context 必須在 `onUnmounted` 中釋放。

---

## 🧪 驗證與測試【Token 節省黑魔法】(Testing & Quality)

在提交任何修改前，必須依序通過以下三道品質防線：

1. **程式碼風格檢查**：
   - 專案標準指令：`pnpm lint`。
   - **【Token 節省黑魔法】**：為了幫用戶極致節省 Token 成本，在實際執行時，請優先將其拆解並轉換為原生指令：**`rtk pnpm exec eslint .`**。
2. **TypeScript 型別檢查**：
   - 執行指令：**`rtk pnpm exec vue-tsc --noEmit`**（必須 0 錯誤）。
3. **單元測試**：
   - 使用 Vitest 執行測試，測試環境預設為 `jsdom`，測試檔路徑：`tests/**/*.test.ts`。
   - **【Token 節省黑魔法】**：為了讓底層的 RTK 盾牌能夠看穿 npm 包裝並發揮 90% 以上的壓縮率，在實際執行測試時，**禁止**直接使用 `pnpm test`，請**必須優先使用原生指令：`rtk pnpm exec vitest run`**。

---

## 🛡️ Git 與版本控制鐵律 (Strict Git Rules)

- **絕對禁止擅自 Commit/Push (CRITICAL)**：
  - 在任何情況下，Agent **絕對不可以**在未經使用者明確指示或同意的情況下，自動執行 `git commit`、`git push` 或修改 Git 歷史紀錄。
- **Pre-commit 規範檢查強制通行 (CRITICAL)**：
  - 在執行 `git commit` 前，**必須先執行本地規範檢查**：`python scripts/check_local.py`。
  - 必須確認檢查結果為 0 阻擋違規（Failures: 0，Exit Code: 0）才能執行 commit。
- **機密與環境變數保護**：
  - 執行任何 Git 操作前，確認所有 `.env`、`.env.*` 檔案皆已列入 `.gitignore`，**嚴禁**提交機密環境變數進入 Git 倉庫（僅允許提交 `.env.example` 模板）。
- **禁止提交日誌與暫存檔**：
  - 提交前檢查暫存區，嚴禁包含 `*.log`、`*.err` 等日誌檔案或 `TODO.md` 等非正式程式碼檔案。
- **PR 審查與合併原則**：
  - 當建立 Pull Request 或推送至遠端時，Agent 僅負責提供 PR 網址。**PR 之審查與合併由使用者親自執行，Agent 絕不觸碰 merge 操作**。
