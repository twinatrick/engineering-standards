"""明確匯出完整工程規範快照，拒絕覆蓋任何不同內容，不修改既有規範。"""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

from check_snapshot import read_document, required_paths, verify_catalog


ROOT = Path(__file__).resolve().parents[1]


def resolve_commit(specified: str | None) -> str:
    if specified:
        if not re.fullmatch(r"[0-9a-f]{40}", specified):
            raise ValueError(f"指定的 commit SHA 格式不正確：{specified}")
        return specified
    try:
        commit = (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT)
            .decode("utf-8")
            .strip()
        )
        if re.fullmatch(r"[0-9a-f]{40}", commit):
            return commit
    except Exception:
        pass
    raise ValueError("正式發布快照匯出需要有效的 40 位 commit SHA（可指定 --commit）")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("backend", "frontend"), required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--update", action="store_true", help="確認更新既有快照，覆寫不同內容")
    parser.add_argument(
        "--commit",
        help="指定集中庫 40 位 commit SHA，未指定時若為 published 則自動讀取當前 git HEAD",
    )
    arguments = parser.parse_args()
    catalog_path = ROOT / "catalog.json"
    errors = verify_catalog(catalog_path)
    if errors:
        raise ValueError("；".join(errors))
    catalog = read_document(catalog_path)
    status = catalog["source"].get("status")
    source_info = dict(catalog["source"])
    if status == "draft":
        source_info["commit"] = catalog["source"].get("commit")
    elif status == "published":
        source_info["commit"] = resolve_commit(arguments.commit)
    else:
        raise ValueError(f"未知的發布狀態：{status}")
    if not arguments.project.is_dir() or not (arguments.project / "AGENTS.md").is_file():
        raise ValueError("目的地必須是既有專案，不自動建立專案")
    output = arguments.project.resolve() / "docs" / "engineering-standards"
    checker = arguments.project.resolve() / "scripts" / "check_engineering_standards.py"
    files = []
    writes = {}
    for relative in sorted(required_paths(arguments.profile)):
        content = (ROOT / relative).read_bytes()
        writes[output / relative] = content
        files.append({
            "path": relative,
            "source_path": relative,
            "sha256": hashlib.sha256(content).hexdigest(),
        })
    manifest = {
        "schema_version": 1,
        "source": source_info,
        "release_gates": catalog["release_gates"],
        "profile": arguments.profile,
        "files": files,
        "checker_source_path": "scripts/check_snapshot.py",
        "checker_sha256": hashlib.sha256(
            (ROOT / "scripts/check_snapshot.py").read_bytes()
        ).hexdigest(),
    }
    writes[output / "manifest.json"] = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    writes[checker] = (ROOT / "scripts/check_snapshot.py").read_bytes()
    # 先檢查所有目的地，避免後段衝突導致只寫入一半。
    for target, content in writes.items():
        if (
            target.exists()
            and not arguments.update
            and (not target.is_file() or target.read_bytes() != content)
        ):
            raise ValueError(f"拒絕覆寫既有不同內容（如需確認更新請加 --update）：{target}")
        if not target.resolve().is_relative_to(arguments.project.resolve()):
            raise ValueError(f"目的地超出專案：{target}")
    for target, content in writes.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    desc = "正式快照" if status == "published" else "接軌預覽"
    print(f"已匯出 {arguments.profile} {desc}；未修改有效規範、hooks 或 CI。")


if __name__ == "__main__":
    main()
