# 本次草案驗證紀錄

本紀錄只描述本地草案檢查，不是發布核准、來源認證、授權證明或業務品質報告。

## 基準與工作區

| 項目 | 結果 |
| --- | --- |
| 後端遠端 master | `cb0d97685b2d3b8b1aaafa0a08ba858ee31163ae`；fetch 後本地 master 落後 2 筆，未移動本地 master |
| 前端遠端 master | `8470f3f8981f1117e942b24e6ed287e89d328c6d`；與本地 master 相同 |
| 兩端工作分支 | `chore/engineering-standards-adoption`，均由上述遠端 master 建立 |
| 集中庫工作分支 | `chore/engineering-standards-bootstrap`；尚無 commit／tag／遠端 |
| 使用者既有工作 | 後端原有 4 份未追蹤文件保留；未 stash、reset、merge、commit 或 push |

## 已執行檢查

以下 Python 指令使用標準函式庫；測試循序執行，沒有啟動 Maven、Java、Docker 或應用程式。

| 位置／指令 | 結果 |
| --- | --- |
| 集中庫：`python -X utf8 -m unittest discover -s tests -v` | 21 個測試全部通過（含 --update 覆寫測試），1.290 秒 |
| 集中庫：`python -X utf8 scripts/check_snapshot.py --catalog catalog.json` | exit 0，完整清單一致，conflicts gate 標記已裁決 |
| 後端：`python -X utf8 scripts/check_engineering_standards.py` | exit 0，完整快照一致 |
| 前端：`python -X utf8 scripts/check_engineering_standards.py` | exit 0，完整快照一致 |
| 兩端各執行：`python -X utf8 scripts/check_engineering_standards.py --require-published` | 均依預期 exit 1：缺正式來源 commit、仍為草案、發布審查未完成 |
| 兩端各執行：`git diff --check` | 均 exit 0；此指令不涵蓋未追蹤檔案 |
| 集中庫文字快速掃描 | 未命中 Windows 絕對路徑、常見私網位址、`.local`／`.internal` URL 與簡單硬編碼敏感值模式；不能取代人工脫敏 |

測試包含兩個 Profile 匯出與重跑、不同既有內容預設拒絕覆寫但支援 --update、唯讀前後內容與修改時間不變、異動／缺檔／清單刪項／重複項／額外檔案拒絕、不安全路徑拒絕、來源欄位／路徑／檢查器雜湊驗證、草案拒絕正式採用、正式中繼資料缺審查標記時拒絕。

來源匯入使用固定提交的 `git show` 原始位元組產生六份全文，逐檔記錄於 `sources.json`；匯出前檢查集中清單，消費端保留適用 Profile 全文與共同規範。新增快照檢查器不接現有 CI／hooks，不改變既有品質工具設定。

### 規範衝突裁決落地（0.1.0-draft.1）

- **CF-01 (Query DTO 基底)**：後端《開發規範.md》§6.2.1 雙軌搜尋軌基底筆誤修正為現行存在之 `com.example.BackendArchitectureLab.Dto.Query.BaseSearchQuery`；Java 原始碼維持不動。
- **CF-02 (FQN 完全限定名稱)**：後端《AGENTS.md》同步補充《開發規範.md》§5.12 之同 Simple Name 並存極窄例外條款，確立原則禁止、同名消除歧義時例外之統一標準。
- **CF-03 (any 型別規範)**：前端《review.md》修訂對齊根規範與 Agent 指南，確立為「禁止濫用 any」，優先具體型別與 unknown。

## 未驗證或尚未完成

- 尚未跑兩端業務測試／建置，因本次只更動文件並新增獨立快照工具；不得宣稱應用程式測試已通過。
- 未發布、未核准正式採用、未建立 GitHub 遠端、未 commit／tag／push。
- 原始來源權利、目標授權與第三方聲明仍待核對；人工公開脫敏仍未完成。
- 雜湊只檢查本地一致性。正式來源認證、真實不可變 commit 與升版審查仍需另行完成；目前匯出工具刻意只提供草案接軌。
