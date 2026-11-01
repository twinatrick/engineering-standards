# engineering-standards

共通、後端與前端工程規範的集中權威來源。公開儲存庫為 <https://github.com/twinatrick/engineering-standards>。

最新正式版本：`0.1.0`。目前工作目錄為 `0.2.0-draft.1`（未發布），含使用者於 2026-11-01 核准的共通、前端與後端 ADP／SDP／SAP 規範修訂。消費端仍鎖定 `0.1.0`，本次不發布、不自動匯出或升版。原始基準來源見 [來源清單](sources.json)，固定匯入原文不直接修改。

## 閱讀入口

- [共通基準](standards/common.md)、[後端 Profile](standards/backend.md)、[前端 Profile](standards/frontend.md)
- [採用、版本、例外與發布治理](governance/adoption.md)
- [完整盤點與分類](docs/inventory.md)、[衝突／落實缺口裁決](docs/findings.md)
- [正式發布驗證紀錄](docs/verification.md)
- [待核准改善提案](proposals/backlog.md)、[授權與來源聲明](LICENSES.md)
- [治理詞彙](CONTEXT.md)、[架構決策](docs/adr/0001-central-authority-with-pinned-snapshots.md)

## 範圍與權威

本庫為前後端專案工程規範之共同權威來源；消費端專案保留鎖定版本（`0.1.0`）的共通規範、技術 Profile 及完整來源副本，不自動追隨最新版。`pom.xml`、ESLint、CI、hooks、檢查器與業務 CONTEXT／ADR 仍留原專案。

第一版保留既有 master 要求與原始措辭，不把落實缺口偽裝成規範變更；來源原文所稱「唯一規則來源」指匯入前的專案關係，正式採用後由本庫治理流程與鎖定快照取代。三項已知衝突（CF-01 BaseSearchQuery 路徑、CF-02 FQN 極窄例外、CF-03 any 規範）均已獲使用者正式裁決並落實。

消費端透過鎖定快照接軌：專案目錄下 `docs/engineering-standards/` 保存完整副本，`manifest.json` 明確鎖定集中庫發布版本與 Commit SHA。

## 離線工具

從標準庫目錄執行：

```powershell
python scripts/check_snapshot.py --catalog catalog.json
python -m unittest discover -s tests -v
```

匯出正式快照至消費端專案：

以下為正式發布後的操作說明；目前工作目錄為未發布草案，本次不執行匯出，亦不可使用工作草案覆蓋消費端 `0.1.0` 快照。

```powershell
python scripts/export_snapshot.py --profile backend --project ../Backend-Architecture-Lab --update
python scripts/export_snapshot.py --profile frontend --project ../v3-admin-vite-templete --update
```

消費端唯讀檢查：`python scripts/check_engineering_standards.py`。
加上 `--require-published` 可嚴格驗證發布狀態與門禁，`0.1.0` 正式快照將放行通過。初期不接 CI／hooks，不自動拉取、更新或修復。

SHA-256 只能偵測檔案相對本地清單的變動；同時竄改檔案與清單仍可能通過。匯入與升版必須另比對可信來源 commit，不能把雜湊當來源認證。

## 0.1.0 歷史發布門禁審查結果

以下僅記錄已發布 `0.1.0`，不認證目前工作草案。`0.2.0-draft.1` 的內容核准不等於完成發布審查；清單的衝突與公開脫敏門禁維持待審，後續須核對新來源、遷移影響與真實提交後另行核准發布。

1. **來源與授權審查（`license_review`）**：`approved`。原專案版權與授權聲明完整保留，本庫整理文件依 CC BY 4.0、工具依 MIT 發布。
2. **規範衝突裁決（`conflicts`）**：`resolved`。三項衝突經使用者明確裁決，雙端與集中庫說明一致。
3. **公開脫敏檢驗（`public_redaction`）**：`approved`。全庫 27 檔脫敏掃描通過，無私網 IP、內部主機、本機絕對路徑或機密外洩。
