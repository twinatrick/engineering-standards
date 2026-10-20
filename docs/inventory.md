# 來源盤點與分類

盤點基準：2026-10-20，兩端 fetch 後的遠端 master；實際 SHA、來源路徑與原始檔 SHA-256 記錄於 `sources.json`。後端本地 master 落後遠端 2 個提交，前端相同；未 reset／merge 本地 master，改從 origin/master 建立工作分支。

## 主要工程規範：完整匯入與適用對照

| 來源 | 分類 | 集中位置與處理 |
| --- | --- | --- |
| 後端 `開發規範.md` §1 | 後端專屬；分層原則可共通 | `standards/backend/master-rules.md` 全文；共通 C-01、C-03 |
| 同上 §2 | 後端權限、BOLA | 後端全文；共通 C-02，不把專案權限字典變通用字典 |
| 同上 §3 | OpenAPI、模型、路由、批次快取 | 後端全文；契約原則共通 C-03；Query 路徑待裁決 |
| 同上 §4 | Python 專屬 | 後端全文；例外原則共通 C-04，不套用 Python 格式至前端 |
| 同上 §5.1–5.11 | 品質原則；含後端檢查表 | 全文保留；僅交集整理為 C-05，不能將全套檢查表直接升為前端新要求 |
| 同上 §5.12–5.13 | FQN／Java Markdown 專屬 | 全文保留；FQN 例外待裁決 |
| 同上 §6 | 雙軌搜尋、SSE、遷移燃盡 | 全文保留；不把專案白名單提升為永久例外 |
| 同上 §7 | 稽核指令 | 全文保留，實際工具與運行設定留原專案 |
| 同上 §8 | Liquibase、H2、樂觀鎖 | 全文保留，不擴大實施對象 |
| 同上 §9 | 韌性與權限近端快取 | 全文保留，不套用於前端本機狀態 |
| 同上 §10 | 提交及單行程測試 | 全文保留；提交檢查原則共通 C-07 |
| 後端 `AGENTS.md` | 環境、執行及 Git 安全 | `standards/backend/master-agents.md` 全文；共通 C-06–C-09 |
| 後端 `.github/AI_REVIEW.md` | 審查合約、信任邊界及 AI Gate | `standards/backend/master-review.md` 全文；不混同本地門檻 |
| 前端 `開發規範.md` §1 | 單向分層、環境、RBAC、錯誤與死碼 | `standards/frontend/master-rules.md` 全文；共通 C-01–C-05 |
| 同上 §2 | Vue、TypeScript、生命週期 | 前端全文；不以後端實作替換 |
| 同上 §3 | UnoCSS／Scss、Element Plus、繁中 UI | 前端全文；共通 C-06 只整理語言原則 |
| 同上 §4 | SRP／DRY／KISS／YAGNI／Boy Scout | 前端全文；共通 C-05，不將建議行數改為強制門檻 |
| 同上 §5 | 稽核指令 | 全文保留；工具仍留前端 |
| 前端 `AGENTS.md` | pnpm、三道品質防線及 Git 安全 | `standards/frontend/master-agents.md` 全文；共通 C-06–C-09 |
| 前端 `review.md` | 正式審查合約，不是臨時 review 輸出 | `standards/frontend/master-review.md` 全文；`any` 措辭差異列衝突 |

上述六份來源均逐位元組保留，不修改文字以掩蓋既有問題。來源授權仍待確認；完整匯入不等於已完成公開散布授權。

## 補充材料：保留原地、提煉治理、不批搬

| 來源候選 | 分類與決定 |
| --- | --- |
| 後端 `.github/ai-review/README.md` | 檢查系統與 CI 信任邊界操作說明，工具維護文件留原專案；合約要求已由完整 AI_REVIEW 匯入 |
| 後端 `docs/adr/0002-trusted-ai-review-boundary-and-target-resolution.md` | 工程治理決策證據，見 12–27 行；不重新編號搬移，後續提案引用 |
| 後端 ADR `0004-sonarqube-code-quality-and-coverage-gate` | 品質門禁決策證據，見 19–35 行；對照實際工具落差，不直接宣稱已阻擋合併 |
| 後端 ADR `0008-precommit-compliance-gate-and-local-linting` | 20–39 行記錄確定性檢查取捨；不把沒裝 Checkstyle／Spotless 視為缺陷 |
| 後端 ADR `0012-model-spec-dual-batching-and-legacy-debt-governance`、`0014-deterministic-local-quality-gate-and-dead-code-audit` | 技術債燃盡、交易／強型別與死碼治理證據；保留專案特定實作及白名單 |
| 後端 ADR `0021-po-dto-vo-bo-separation-and-controller-contract-traversal` | 31–58 行為公開契約遍歷理由，現行要求已由根規範匯入 |
| 前端 ADR `0006-frontend-engineering-standards-and-precommit-gate` | 18–38 行說明規範與三道防線；原地保留，工具落差見 findings |
| 後端 `backend-ai-py/PYTHON_RULES.md` | 舊重複材料，根唯一規範已整合；不另升為平行現行權威 |
| 兩端 `CONTEXT.md` | 工程詞彙可作查證，業務詞彙與模型不搬；本庫 CONTEXT 僅定義治理語言 |
| 前端 `docs/API_GENERATION.md`、`docs/SWAGGER_API_INTEGRATION.md` | 產碼操作留原專案；舊直連範例與環境資訊不得原封變成新標準 |
| 後端 `docs/archive/` | 歷史資料，不恢復為與根規範平行的現行來源 |
| 前端 `require.md`、兩端業務 ADR | 業務待辦／設計，不屬工程標準庫 |

## 可執行落實點：不搬移、不修改

後端：`pom.xml`、`.github/workflows/ci.yml`、`.github/ai-review/`、`.githooks/pre-commit`、GitLab CI、Docker／Liquibase／測試設定。

前端：`package.json`、`pnpm-lock.yaml`、`.eslintrc.js`、TypeScript／Vitest 設定、`scripts/check_local.py`、`.husky/pre-commit`、`.gitlab-ci.yml`。

本次只新增與本地快照相關的唯讀檢查器，不修改上列檔案、不執行自動修復 lint、不更改測試或門禁要求。規範與工具不同步須分別記錄，不能以工具為準刪除既有要求。

## 公開前脫敏檢查範圍

不搬 `.env`／`.run` 或內部 remote。兩端 README、部署／compose、壓測與產碼文件可能含連線、帳密環境說明或本機路徑，均未整份匯入。前端模板上游來源為 `un-pany/v3-admin-vite`，須核對衍生權利。人工審查仍待完成，搜尋未命中不能作為沒有機密的證明。
