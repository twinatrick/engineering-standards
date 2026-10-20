# 衝突與落實缺口

證據皆取自 `sources.json` 的固定來源提交；行號為來源基準，不是後續插入草案入口後的行號。

## 規範衝突與裁決紀錄（已於 0.1.0-draft.1 裁決並落地）

| ID | 互斥／不一致要求與證據 | 裁決結果與落地動作 | 狀態 |
| --- | --- | --- | --- |
| CF-01 | 後端 `開發規範.md` §3.2（159–164 行）Query DTO 在 `Dto/Query/`；§6.2.1（406–410 行）卻指定 `com.example.BackendArchitectureLab.Vo.Search.BaseSearchQuery`。實際基底為 `com.example.BackendArchitectureLab.Dto.Query.BaseSearchQuery`，沒有舊路徑檔案 | **使用者裁決**：以 master 實際類別與新模型分層為準，修訂後端《開發規範.md》§6.2.1 雙軌章節舊路徑筆誤；原始 Java 程式碼維持現狀不動；集中庫後端 Profile 記載一致性說明。 | **已裁決並落實** |
| CF-02 | 後端 `AGENTS.md` 52 行為絕對 FQN 禁令；根規範 §5.12（360–368 行）准許同檔同 Simple Name 的極窄例外；`.github/ai-review/check_java.py` 233–253 行未辨識此例外 | **使用者裁決**：保留根規範的極窄同 Simple Name 例外，後端《AGENTS.md》已同步補充例外條款，確立原則禁止、同名消除歧義時例外之統一標準；檢查器辨識改善另列後續任務。 | **已裁決並落實** |
| CF-03 | 前端根規範 §2.2（59–62 行）及 AGENTS 禁止「濫用 any」；正式 `review.md` 23–24 行卻寫生產程式碼「禁止 any」 | **使用者裁決**：統一為「禁止濫用 any」，優先使用明確型別，外部與未知資料使用 `unknown`；前端《review.md》已同步修訂，消除絕對禁令與根規範／AGENTS 的矛盾。 | **已裁決並落實** |

註：固定提交匯入檔 `standards/*/master-*.md` 維持原始 bytes 作為歷史基準比對，不直接修改原始匯入檔案。

## 過期範例與入口（不是新增規範）

- 前端 `docs/API_GENERATION.md` 163–189 行示範 Vue 直接建立 generated API 並使用 `any`，與現行 Service 分層要求不一致。建議後續更新範例，不將舊範例匯入正式規範；根規範對此已有明確要求，無須創造新禁令。
- 前端 `README.md` 62–64 行的 pnpm 8.x／Node 16+ 與 `package.json` 第 4 行 pnpm 9.15.4、GitLab CI 17／24 行 Node 20／pnpm 9.15.4 不一致。建議以可執行配置核定支援版本，另行更新 README。

## 工具落實差距與驗證邊界

| ID | 證據與現況 | 正確解讀／後續方向 |
| --- | --- | --- |
| G-01 | 前端 AGENTS 56–58 行要求 `check_local.py`，但 `.husky/pre-commit` 1–4 行只有 `pnpm lint-staged`；hooksPath 已設定 `.husky` | 不是沒啟用 Husky，而是未接完整守門；此次不修改 hook |
| G-02 | 前端 `.gitlab-ci.yml` 22–30 行 verify 只有安裝、ESLint、Vitest，未獨立執行型別或架構檢查；build scripts 才含型別檢查 | 不可宣稱每個 MR verify 都完成三道防線 |
| G-03 | 前端 `.eslintrc.js` 28 行關閉 `no-explicit-any`；`scripts/check_local.py` 134–159 行架構 import 正則未涵蓋所有生成 API 路徑 | 文件規則存在，工具覆蓋不完整，不是要求不存在 |
| G-04 | 前端 `scripts/check_local.py` 86–94 行選 staged 檔名，110–118／139–148 行讀 working tree；後端則讀 index blob | 部分暫存可能檢查錯內容，需測試後修正，不在本次變更工具 |
| G-05 | 前端檢查器 199–204 行直接 `eslint .`，沒有 `--max-warnings 0` 卻印 0 warnings；審查合約要求 0 警告 | 顯示成功不證明零警告；不是所有 ESLint 指令等價 |
| G-06 | 後端 `pom.xml` 440–481 行有廣泛覆蓋率排除，483–490 行 BUNDLE LINE 80%，496–505 行未綁 check；GitHub CI 35–36 行明確執行 `test jacoco:check` | 80% 只對納入計算的範圍，單跑 test 不等於驗證門檻 |
| G-07 | 後端 ADR 0004 28–35 行描述 Sonar 門禁，GitHub CI 44–52 行按 token 有無條件掃描，命令未等待 Quality Gate | 未查遠端 required checks／Sonar 設定，不能認定結果必阻擋合併 |
| G-08 | 後端 `.githooks/pre-commit` 21–29 行只有規範檢查；`check_local.py` 174–186 行無變更可直接成功 | Hook 成功不等於 Maven 測試通過；不暫存檔案時不能把零違規當完整驗證 |
| G-09 | 後端 POM 403–418 行 Surefire／Failsafe 已有 forkCount=1 | 單 fork 已落實，不誤報缺失；這不能攔住命令列另加 `-T` |
| G-10 | 後端 `.gitignore` 只明列 `.env`，前端有 `.env.*` 並允許 `.env.example` | 防護模式差異，不代表已發生機密追蹤；兩端追蹤環境檔查核僅見範本 |

後端 AI Review 的 CRITICAL／HIGH＋confidence gate 與本地 HIGH／MEDIUM gate 處理的是不同流程；前端也有自己的 HIGH／MEDIUM 審查門檻。**這是適用範圍差異，不合併成單一分級表，也不算互斥衝突。**

## 授權阻擋

後端沒有找到根授權或 POM licenses；前端只有 package MIT 標示且保留上游模板來源。請權利人確認六份匯入文件的作者、衍生關係、散布及改授權權限，再落實文件 CC BY 4.0／工具 MIT 目標。完整來源及本次新產出都不因草案存在而自動取得重新授權。

來源衝突裁決、授權和人工脫敏完成前，維持接軌預覽；現有原專案規範不被草案取代。
