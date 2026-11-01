# engineering-standards

共通、後端與前端工程規範的集中權威來源。公開儲存庫為 <https://github.com/twinatrick/engineering-standards>。

最新正式版本：`0.2.1`，僅修正快照檢查器的超長程式行並補充回歸測試，沿用 `0.2.0` 規範與檢查語意；授權、衝突與公開審查門禁已通過。版本與提交對應以 `0.2.1` tag 為準，不自動匯出或升級任何消費端。原始基準來源見 [來源清單](sources.json)，固定匯入原文不直接修改。

## 閱讀入口

- [共通基準](standards/common.md)、[後端 Profile](standards/backend.md)、[前端 Profile](standards/frontend.md)
- [採用、版本、例外與發布治理](governance/adoption.md)
- [完整盤點與分類](docs/inventory.md)、[衝突／落實缺口裁決](docs/findings.md)
- [正式發布驗證紀錄](docs/verification.md)
- [0.2.1 版本說明](docs/release-notes-0.2.1.md)、[0.2.1 發布前審查紀錄](docs/release-review-0.2.1.md)
- [0.2.0 歷史版本說明](docs/release-notes-0.2.0.md)、[0.2.0 發布前審查紀錄](docs/release-review-0.2.0.md)
- [待核准改善提案](proposals/backlog.md)、[授權與來源聲明](LICENSES.md)
- [治理詞彙](CONTEXT.md)、[集中權威決策](docs/adr/0001-central-authority-with-pinned-snapshots.md)、[發布生命週期與相容性決策](docs/adr/0003-release-lifecycle-and-compliance-compatibility.md)

## 範圍與權威

本庫為前後端專案工程規範之共同權威來源；消費端專案保留鎖定版本（`0.1.0`）的共通規範、技術 Profile 及完整來源副本，不自動追隨最新版。`pom.xml`、ESLint、CI、hooks、檢查器與業務 CONTEXT／ADR 仍留原專案。

第一版保留既有 master 要求與原始措辭，不把落實缺口偽裝成規範變更；來源原文所稱「唯一規則來源」指匯入前的專案關係，正式採用後由本庫治理流程與鎖定快照取代。三項已知衝突（CF-01 BaseSearchQuery 路徑、CF-02 FQN 極窄例外、CF-03 any 規範）的適用規則與處理結果見各 Profile 及衝突紀錄。

消費端透過鎖定快照接軌：專案目錄下 `docs/engineering-standards/` 保存完整副本，`manifest.json` 明確鎖定集中庫發布版本與 Commit SHA。

## 離線工具

從標準庫目錄執行：

```powershell
python scripts/check_snapshot.py --catalog catalog.json
python -m unittest discover -s tests -v
```

在隔離位置準備候選（Python 3.12 以上）：

以下為操作範例，本次不向消費端執行匯出。草案與預發布必須使用 `--preview`；副本位於 `docs/engineering-standards-preview/<版本>/<Profile>/`，不覆蓋消費端 `0.1.0`。正式版本不加 `--preview`，只準備 `docs/engineering-standards-candidates/<版本>/<Profile>/`，不自動切換採用。

```powershell
python scripts/export_snapshot.py --profile backend --project ../Backend-Architecture-Lab --preview
python scripts/export_snapshot.py --profile frontend --project ../v3-admin-vite-templete --preview
```

`--update` 已停用，不提供強制覆寫；已發布候選還須核對指定提交的列管內容。隔離候選使用其自帶檢查器，明確指定同目錄 `manifest.json`；正式採用另依[受控切換程序](governance/adoption.md#隔離準備與受控切換)完成。

消費端既有唯讀檢查：`python scripts/check_engineering_standards.py`。
加上 `--require-published` 可嚴格驗證發布狀態與門禁，完整且未異動的 `0.1.0` 正式快照仍可驗證。檢查採逐位元組比對，換行轉換也會報不符，不自動正規化或修復。初期不接 CI／hooks，不自動拉取或更新。

新版檢查器核對歷史快照時，可用 `--checker-file scripts/check_engineering_standards.py` 指定該快照對應的檢查器，只核對雜湊而不執行；不改寫歷史快照。預發布不可通過正式採用檢查，即使其發布門禁已完成。

SHA-256 只能偵測檔案相對本地清單的變動；同時竄改檔案與清單仍可能通過。匯入與升版必須另比對可信來源 commit，不能把雜湊當來源認證。

## 0.1.0 歷史發布門禁審查結果

以下僅記錄已發布 `0.1.0`，不代替 `0.2.1` 的[本版審查紀錄](docs/release-review-0.2.1.md)。本版三項門禁已通過，清單狀態為 `published`；實際發布提交須核對 `0.2.1` tag 指向的完整 SHA，不以本地清單作遠端來源認證。

1. **來源與授權審查（`license_review`）**：`approved`。原專案版權與授權聲明完整保留，本庫整理文件依 CC BY 4.0、工具依 MIT 發布。
2. **規範衝突裁決（`conflicts`）**：`resolved`。三項衝突的適用規則已統一，雙端與集中庫說明一致。
3. **公開脫敏檢驗（`public_redaction`）**：`approved`。全庫 27 檔脫敏掃描通過，無私網 IP、內部主機、本機絕對路徑或機密外洩。
