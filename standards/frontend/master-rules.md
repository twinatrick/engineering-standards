# 開發規範（唯一規則文件）

> 本文件為前端專案唯一規則來源。
> 所有 Vue 3 / TypeScript / Scss / HTML 程式碼（新增與修改）都必須遵守。

---

## 1. 架構分層與職責邊界 (Architectural Layers & Boundaries)

### 1.1 五層單向依賴架構

本專案遵循嚴格的單向依賴流向，嚴禁逆向或跨層呼叫：

```
Views (視圖層: *.vue)
  ↓ 呼叫
Service (業務服務層: service.ts)
  ↓ 呼叫
Api (生成的 API Client: src/api/generated/Api.ts)
  ↓ 呼叫
Client (Axios 攔截層: src/api/client.ts)
  ↓
後端 Gateway 閘道
```

- **全域狀態 (Pinia Store)**：`src/store/modules/`（如 `user.ts`、`permission.ts`），負責跨組件共享之使用者資訊與動態路由表，提供只讀 `computed` 或 Action 供 View 層消費。
- **類型契約 (Types)**：`src/types/` 與生成的 `Api.ts`，作為前後端資料溝通的唯一契約。

### 1.2 嚴格禁止的反模式 (Anti-patterns)

1. **視圖直接呼叫 API 禁令 (View-to-API Direct Call Prohibition)**：
   - 視圖組件（`*.vue`）**嚴格禁止**直接 `import` `api`、`axios` 或 `Api.ts` 內的 Controller 實例。
   - 所有外部資料請求必須收斂於該視圖目錄下的 `service.ts`（例如 `src/views/personal-management/skill/service.ts`）。
   - **驗證方式**：`rg 'import.*from ["\x27]@/api' src/views/ --glob "*.vue"` 必須為 0 結果（僅允許引入純 Type 定義）。
2. **寫死連線位址禁令 (Hardcoded URL/IP Prohibition)**：
   - 程式碼中**嚴格禁止**出現具體 IP 位址、Tailscale 私有網域或寫死的主機網址。
   - 伺服器前綴一律自 `import.meta.env` 動態讀取（如 `VITE_BASE_API`、`VITE_PUBLIC_PATH`）。
3. **繞過 RBAC 禁令 (RBAC Bypass Prohibition)**：
   - 禁止在組件內部自行解構 JWT Token 進行角色判定。
   - 頁面存取權限一律交由路由守衛 (`permission.ts`) 與動態路由 `name` 權限樹匹配。
4. **靜默吞噬例外禁令 (Silent Exception Swallowing Prohibition)**：
   - **嚴禁**使用空的 `catch (e) {}` 靜默吞噬非預期例外。
   - Service 層捕捉例外時，必須向外拋出或將錯誤結構標準化；View 層必須給予使用者友善的 `ElMessage.error` 提示。
5. **幽靈 Service 與死代碼禁令 (Dead Service Prohibition)**：
   - `service.ts` 內定義的方法必須具備實質呼叫者，禁止保留無人呼叫的殘留方法。

---

## 2. Vue 3 與 TypeScript 代碼標準

### 2.1 Composition API 與 `<script setup>`

- 全專案一律採用 Vue 3 `<script setup lang="ts">` 語法，**全面禁止**使用 Vue 2 Options API。
- 響應式狀態規範：
  - 單一純量值（數字、字串、布林值、彈窗開關 `visible` 等）一律使用 `ref()`。
  - 表單物件、查詢條件與分頁參數一律使用 `reactive()`。
  - 需要衍生計算的屬性一律使用 `computed()`，嚴禁在 template 內撰寫過於複雜的行內運算。

### 2.2 TypeScript 嚴格型別

- **嚴禁濫用 `any`**：生產環境程式碼（`src/**/*.vue`, `src/**/*.ts`）嚴格禁止為圖方便宣告 `any` 或以 `(foo as any)` 暴力斷言。
- 資料型別一律對齊 `src/api/generated/Api.ts` 所生成的後端 VO（例如 `UserVo`, `BotConfigVo`, `VoiceDiaryVo`）。
- 組件 Props 與 Emits 必須具有完整 TypeScript 定義：
  ```vue
  <script setup lang="ts">
  interface Props {
    title: string
    visible?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    visible: false
  })
  const emit = defineEmits<{
    (e: "success"): void
    (e: "close"): void
  }>()
  </script>
  ```

### 2.3 生命週期與資源清理 (Lifecycle & Memory Leak Prevention)

- 凡在 `onMounted` 或生命週期中建立的非同步資源：
  - 計時器（`setInterval` / `setTimeout`）
  - 全域事件監聽器（`window.addEventListener`）
  - 音訊處理物件（`AudioContext`、`MediaStream`、`AudioWorkletNode`）
- **必須在 `onUnmounted` 中顯式中斷、移除與關閉**，杜絕 SPA 頁面切換後記憶體洩漏或背景任務持續耗電。

---

## 3. UI、樣式與元件規範

### 3.1 樣式技術棧 (UnoCSS + Scss)

- 佈局與通用樣式優先使用 UnoCSS 原子化 class（如 `flex items-center justify-between p-4 mb-2`）。
- 特殊或深層組件樣式採用 `<style lang="scss" scoped>`。
- **嚴禁全域污染**：禁止在沒有 `scoped` 的 style 標籤中編寫常規選擇器；穿透 Element Plus 組件樣式請使用 `:deep(...)`。

### 3.2 Element Plus 語義化使用

- 列表展示優先使用 `<el-table>` 與 `<el-table-column>`。
- 頁面操作使用 `<el-button>`，狀態以 `<el-tag>` 標籤化呈現。
- 明細與表單操作優先採用 `<el-drawer>`（抽屜）或 `<el-dialog>`（對話框）。
- 彈窗確認操作一律使用 `ElMessageBox.confirm`，成功/失敗回饋一律使用 `ElMessage`。
- **全站介面文字與回饋訊息一律強制使用繁體中文**。

---

## 4. 程式碼品質標準 (SOLID / DRY / KISS / YAGNI)

### 4.1 SRP (單一職責原則)

- 單一 `.vue` 檔案行數建議控制在 **300 行以內**。
- 當頁面包含表格、抽屜、彈窗與篩選區時，應將各區塊拆分至子目錄（例如 `data-table/`、`drawer/`、`dialog/`）。

### 4.2 DRY (不重複原則)

- 跨頁面重複使用的業務邏輯必須抽取至 `src/hooks/`（Composables）。
- 通用格式化函式（如日期格式化、檔案大小換算、音訊時長解析）集中於 `src/utils/`。

### 4.3 KISS 與 YAGNI

- 保持邏輯簡明直觀，拒絕過度設計與無實際需求的預留擴充點。
- 嚴禁保留未引用的 import 與 dead code。

### 4.4 Boy Scout Rule

- 每次修改程式碼時，應使該模組比修改前更加乾淨。順手清理未使用的變數、修復過期的型別宣告。

---

## 5. 常見稽核指令 (Audit Commands)

在進行提交前，可使用下列指令進行快速稽核：

```bash
# 1. 檢查 Vue 組件是否違規直連 API 或 Axios
rg 'from ["\x27]@/api["\x27]' src/views/ --glob "*.vue"
rg 'from ["\x27]axios["\x27]' src/views/ --glob "*.vue"

# 2. 檢查原始碼是否殘留寫死之私有連線或具體 IP
rg '100\.64\.|tailscale|192\.168\.' src/

# 3. 檢查生產程式碼是否有濫用 any
rg ': any|as any' src/views/ src/store/

# 4. 執行本地確定性 Pre-commit 守門稽核
python scripts/check_local.py
```
