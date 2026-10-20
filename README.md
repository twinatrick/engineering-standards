# engineering-standards

共通、後端與前端工程規範的集中治理草案。預定公開位置為 <https://github.com/twinatrick/engineering-standards>；**目前未建立 GitHub 儲存庫、未 commit、未發布、未正式採用**。

目前版本：`0.1.0-draft.1`。此版本字串只辨識草案，不是已存在的 Git tag。規範來源固定為兩端已 fetch 的遠端 master 提交，詳見 [來源清單](sources.json)。

## 閱讀入口

- [共通基準](standards/common.md)、[後端 profile](standards/backend.md)、[前端 profile](standards/frontend.md)
- [採用、版本、例外與發布流程](governance/adoption.md)
- [完整盤點與分類](docs/inventory.md)、[衝突／落實缺口](docs/findings.md)
- [本次草案驗證紀錄](docs/verification.md)
- [待核准改善提案](proposals/backlog.md)、[授權與來源](LICENSES.md)
- [治理詞彙](CONTEXT.md)、[架構決策](docs/adr/0001-central-authority-with-pinned-snapshots.md)

## 範圍與權威

正式發布後，本庫為共同權威來源；專案保留鎖定版本的共通規範、技術 profile 及完整來源副本，不追隨最新版。`pom.xml`、ESLint、CI、hooks、檢查器與業務 CONTEXT／ADR 仍留原專案。

第一版保留既有 master 要求與原始措辭，不把落實缺口偽裝成規範變更；來源原文所稱「唯一規則來源」指匯入前的專案關係，正式採用後由本庫治理流程與鎖定快照取代。尚未裁決的原文差異不得靠重寫消失。

目前消費端只有接軌預覽：其原 `開發規範.md` 仍有效，草案不新增門禁。授權及衝突完成裁決、標準庫有不可變 commit SHA 且通過發布審查後，才可啟用採用。

## 離線工具

從標準庫目錄執行：

```powershell
python scripts/check_snapshot.py --catalog catalog.json
python -m unittest discover -s tests -v
```

建立接軌預覽（明確寫入操作，不是檢查）：

```powershell
python scripts/export_snapshot.py --profile backend --project ../Backend-Architecture-Lab
python scripts/export_snapshot.py --profile frontend --project ../v3-admin-vite-templete
```

消費端唯讀檢查：`python scripts/check_engineering_standards.py`。加上 `--require-published` 可在發布前檢查採用條件，草案應失敗。初期不接 CI／hooks，不自動拉取、更新或修復。

SHA-256 只能偵測檔案相對本地清單的變動；同時竄改檔案與清單仍可能通過。匯入與升版必須另比對可信來源 commit，不能把雜湊當來源認證。

## 完成發布前的阻擋項

1. 確認來源文件作者、第三方衍生關係及重新散布／授權權限。
2. 裁決 `docs/findings.md` 的真正規範衝突；工具落差另列改善，不混為衝突。
3. 完成人工脫敏與來源核對，審查本庫內容。
4. 經使用者另行授權後建立公開遠端、commit 與發布；記錄真實 tag／commit。
5. 更新消費端鎖定清單並明確核准採用，重新核對快照及例外。
