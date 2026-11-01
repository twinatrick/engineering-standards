# 0.2.1 — 快照檢查器行長修正

類型：正式修訂版。比較基準：`0.2.0`，來源提交 `ea3480a2c504773cd083563578c78fbf5eaa6633`。

## 修改摘要

- 將 `scripts/check_snapshot.py` 原第 141 行的 checker SHA-256 比對表達式拆行，從 102 字元改為不超過 100 字元；修正後整份檢查器最長行為 93 字元。
- 保留原有 `or` 短路求值順序，不提前讀取檢查器；與 `0.2.0` 的 AST 比對一致，僅位置資訊不同。
- 新增檢查器行長、來源路徑不符時的短路行為，以及 `--checker-file` 只讀且不執行歷史檢查器的回歸測試。

## 保持不變

- 檔案與 checker 本身均以原始位元組計算 SHA-256，不正規化換行、不修復或覆寫內容。
- `--checker-file` 僅讀取指定檔案，不執行歷史程式。
- 正式發布資格、版本、Profile、來源與檔案集合驗證，以及隔離匯出的提交核對維持不變。
- 沿用 `0.2.0` 的規範要求；不新增合規義務、不放寬消費端品質限制、不新增 CI／hooks。
- 不修改固定匯入 `master-*.md`、來源清單、授權內容、既有發布 tag 或歷史版本說明。

## 驗證與門禁

驗證環境：Python 3.14，僅使用標準函式庫；工具支援需求維持 Python 3.12 以上。

| 項目 | 結果 |
| --- | --- |
| 單元測試 | 47 項通過 |
| 檢查器行長 | 全部不超過 100 字元，最長 93 字元 |
| AST 比對 | 與 `0.2.0` 一致，不含行列位置資訊 |
| 授權審查 | `license_review: approved`；本版未改授權或匯入來源 |
| 衝突審查 | `conflicts: resolved`；未改規範、檢查語意或適用範圍 |
| 公開內容審查 | `public_redaction: approved`；檢視本版變更及敏感資訊候選 |

詳細範圍、證據與限制見 [發布前審查紀錄](release-review-0.2.1.md)。完整性檢查不認證遠端身分、授權、安全性或消費端程式品質。

## 採用影響

checker 的程式語意不變，但來源位元組及其 SHA-256 已改變，消費端須重新匯出 `0.2.1` 候選快照，不得自行拆行後改寫 manifest 雜湊。新 manifest 由匯出器依正式提交產生，同時鎖定 `0.2.1` 版本、完整 commit SHA 與新 checker 雜湊。

在內容對應 `0.2.1` tag 的集中庫目錄，先以可信遠端核對版本與提交關係，再執行：

```powershell
$releaseCommit = (git rev-parse '0.2.1^{commit}').Trim()
python scripts/export_snapshot.py --profile backend --project ../Backend-Architecture-Lab --commit $releaseCommit
```

候選位置為 `docs/engineering-standards-candidates/0.2.1/backend/`；此命令僅準備隔離候選，不切換有效快照或檢查器。若既有有效快照完整性不符，仍拒絕匯出並保留現場，不使用 `--update` 或強制覆寫。

本次發布不修改 Backend-Architecture-Lab 的工作目錄、暫存區或 PR #199，不代表其已採用或完成本地品質驗證。舊版 tag 不變；消費端須依 [採用治理](../governance/adoption.md) 另行核准與受控切換。
