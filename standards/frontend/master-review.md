# 前端代碼審查合約 (Frontend Code Review Contract)

> 本文件定義前端專案的代碼審查標準（Code Review Contract）。
> 專案唯一規則來源為《`開發規範.md`》；本合約規定審查優先級、違規等級與阻擋門檻。

---

## 1. 審查優先級 (Review Priorities)

進行代碼審查時，必須嚴格依照以下優先級依序檢驗：

1. **機密與敏感資訊 (Credentials & Secrets)**：
   - 檢查是否包含任何私有 IP、Tailscale 節點、未脫敏的伺服器金鑰、硬編碼 Token 或未被 `.gitignore` 排除之 `.env` 檔案。
2. **安全性 (Security)**：
   - **XSS 防護**：嚴格檢查 `v-html` 或 DOM 直接操作（如 `innerHTML`），禁止未經轉義與消毒的使用者字串注入。
   - **Token 處理**：JWT Token 僅允許儲存於安全 Cookie 或授權管理模組中，嚴禁輸出至 console 或掛載於全域 window。
3. **架構邊界與反模式 (Architecture & Boundaries)**：
   - 檢查視圖組件（`*.vue`）是否嚴格經由 `service.ts` 呼叫 API，嚴禁直連 API 或 Axios。
   - 檢查業務邏輯是否正確封裝於 Service 層，避免 God Component。
4. **權限與存取控制 (RBAC & Route Guards)**：
   - 動態路由 `name` 是否正確對齊後端 `role_function` 權限樹（如 `VoiceUpload:View`）。
   - 禁止在組件內部自行解構 Token 進行特權判定。
5. **型別完整度與靜態品質 (Type Safety & Standards)**：
   - 生產代碼禁止 `any` 或過度 `as` 強制斷言。
   - `vue-tsc --noEmit` 必須為 0 錯誤。
   - `eslint .` 必須為 0 錯誤 0 警告。
6. **資源釋放與生命週期 (Resource Lifecycle)**：
   - 定時器、全域監聽器、音訊 Worklet/Context 是否在 `onUnmounted` 中徹底銷毀。
7. **單元測試與功能正確性 (Tests & Correctness)**：
   - 關聯之 Service 業務邏輯必須具備單元測試，`vitest run` 必須全數通過。

---

## 2. 違規等級與門檻 (Severity Levels & Merge Gate)

| 等級              | 定義                                                                                       | 處理動作                                        |
| :---------------- | :----------------------------------------------------------------------------------------- | :---------------------------------------------- |
| **HIGH (阻擋)**   | 機密外洩、XSS 漏洞、直連 API 反模式、硬編碼連線資訊、型別檢查失敗、測試失敗、ESLint 報錯。 | **禁止合併 (Merge Blocked)**，必須修正至 0 項。 |
| **MEDIUM (阻擋)** | 記憶體未在 `onUnmounted` 釋放、靜默吞噬例外（`catch {}`）、Props/Emits 缺少型別定義。      | **禁止合併 (Merge Blocked)**，必須修正至 0 項。 |
| **LOW (建議)**    | 變數命名不夠直觀、繁體中文潤飾、樣式建議。                                                 | 不阻擋合併，建議後續優化。                      |

---

## 3. 本地確定性通行門檻 (Local Pre-commit Gate)

所有提交與 PR 必須在本地端執行守門腳本：

```bash
python scripts/check_local.py
```

當且僅當結果為 `Failures: 0` 且 `Exit Code: 0` 時，方可放行提交。
