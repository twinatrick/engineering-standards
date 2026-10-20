# 0.1.0 正式發布驗證紀錄

本紀錄記載 `engineering-standards` 0.1.0 發布與驗證程序。

## 基準與工作區

| 項目 | 結果 |
| --- | --- |
| 集中庫遠端 | `https://github.com/twinatrick/engineering-standards`（Public） |
| 集中庫主分支 | `master`（原 main 分支已修剪） |
| 後端遠端基準 | `cb0d97685b2d3b8b1aaafa0a08ba858ee31163ae`（origin/master） |
| 前端遠端基準 | `8470f3f8981f1117e942b24e6ed287e89d328c6d`（origin/master） |
| 前端當前進度 | 已提交並推送裁決修訂至 master（`74c2ab1`） |
| 後端當前進度 | 已在分支 `chore/engineering-standards-adoption` 提交裁決修訂（`9acc1f3`）並建立 PR #169 |
| 使用者既有工作 | 後端原有 4 份未追蹤文件完整保留，未受干擾 |

## 已執行檢查與門禁審查

| 項目 | 審查結果 | 說明 |
| --- | --- | --- |
| 單元測試 | **PASS** | 21+ 項測試全部通過，涵蓋草案與正式發布驗證 |
| 快照驗證器 | **PASS** | `check_snapshot.py --catalog catalog.json` 驗證一致 |
| 衝突裁決（`conflicts`） | **resolved** | CF-01、CF-02、CF-03 三項衝突均獲裁決並落實 |
| 授權審查（`license_review`） | **approved** | 原著作權完整保留，文件採 CC BY 4.0，工具採 MIT |
| 脫敏檢驗（`public_redaction`） | **approved** | 集中庫全庫 27 檔脫敏掃描通過，0 洩漏 |

### 規範衝突裁決落地紀錄

- **CF-01 (Query DTO 基底)**：後端《開發規範.md》§6.2.1 雙軌搜尋軌基底筆誤修正為現行架構之 `com.example.BackendArchitectureLab.Dto.Query.BaseSearchQuery`；Java 原始碼維持不動。
- **CF-02 (FQN 完全限定名稱)**：後端《AGENTS.md》同步補充《開發規範.md》§5.12 之同 Simple Name 並存極窄例外條款，確立原則禁止、同名消除歧義時例外之統一標準。
- **CF-03 (any 型別規範)**：前端《review.md》修訂對齊根規範與 Agent 指南，確立為「禁止濫用 any」，優先具體型別與 unknown。
