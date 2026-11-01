"""準備隔離規範候選，不覆寫有效快照、正式檢查器或規範入口。"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from check_snapshot import (
    VERSION_PATTERN, confined_path, read_document, required_paths, verify_catalog,
    verify_manifest,
)


ROOT = Path(__file__).resolve().parents[1]


def git_output(root: Path, *arguments: str) -> bytes:
    """只讀取 Git 物件；失敗時保留明確錯誤，不退回未驗證內容。"""
    result = subprocess.run(
        ["git", *arguments], cwd=root, capture_output=True, check=False
    )
    if result.returncode:
        raise ValueError(f"Git 核對失敗：{result.stderr.decode('utf-8', errors='replace').strip()}")
    return result.stdout


def committed_contents(root: Path, specified: str | None, paths: set[str]) -> tuple[str, dict[str, bytes]]:
    commit = specified if specified is not None else git_output(root, "rev-parse", "HEAD").decode().strip()
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("發布快照需要完整的 40 位小寫 commit SHA")
    resolved = git_output(root, "rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip()
    if resolved != commit:
        raise ValueError("指定 SHA 必須直接指向提交")
    contents: dict[str, bytes] = {}
    for relative in sorted(paths):
        committed = git_output(root, "show", f"{commit}:{relative}")
        if confined_path(root, relative).read_bytes() != committed:
            raise ValueError(f"列管內容與指定提交不符：{relative}")
        contents[relative] = committed
    return commit, contents


def reject_symlinks(root: Path, target: Path) -> None:
    """隔離位置不得透過符號連結或 junction 指回有效快照。"""
    for path in (target, *target.parents):
        if path == root:
            break
        if path.is_symlink() or path.is_junction():
            raise ValueError(f"目的路徑不得包含連結：{path}")


def prepare_snapshot(root: Path, project: Path, profile: str, preview: bool, commit: str | None) -> Path:
    errors = verify_catalog(root / "catalog.json")
    if errors:
        raise ValueError("；".join(errors))
    catalog = read_document(root / "catalog.json")
    source_info = dict(catalog["source"])
    status = source_info["status"]
    if not preview and status != "published":
        raise ValueError("草案與預發布版本僅供試採用，必須指定 --preview")
    if not project.is_dir() or not (project / "AGENTS.md").is_file():
        raise ValueError("目的地必須是既有專案，不自動建立專案")
    project = project.resolve()
    version = source_info["version"]
    if VERSION_PATTERN.fullmatch(version) is None:
        raise ValueError("候選目錄需要符合 SemVer 的版本識別")
    paths = {entry["path"] for entry in catalog["files"]} | {
        "scripts/check_snapshot.py", "scripts/export_snapshot.py", "catalog.json"
    }
    if status in {"published", "prerelease"}:
        revision, contents = committed_contents(root, commit, paths)
        recorded = source_info.get("commit")
        if recorded is not None and recorded != revision:
            raise ValueError("catalog 記錄與指定提交不符")
        source_info["commit"] = revision
    else:
        if commit is not None:
            raise ValueError("草案預覽不得指定發布 commit")
        contents = {relative: confined_path(root, relative).read_bytes() for relative in paths}

    # 正式候選的準備也不能掩蓋已被修改的有效快照；不執行舊檢查器。
    active = project / "docs/engineering-standards"
    if not preview and active.exists():
        active_errors = verify_manifest(
            active / "manifest.json", True, project / "scripts/check_engineering_standards.py"
        )
        if active_errors:
            raise ValueError("有效快照須先釐清異動：" + "；".join(active_errors))
        if read_document(active / "manifest.json")["profile"] != profile:
            raise ValueError("有效快照的 Profile 與候選不同")

    area = "engineering-standards-preview" if preview else "engineering-standards-candidates"
    output = project / "docs" / area / version / profile
    reject_symlinks(project, output)
    if not output.resolve().is_relative_to(project):
        raise ValueError("候選位置超出專案")
    writes: dict[str, bytes] = {}
    files: list[dict[str, str]] = []
    for relative in sorted(required_paths(profile)):
        content = contents[relative]
        writes[relative] = content
        files.append({"path": relative, "source_path": relative, "sha256": hashlib.sha256(content).hexdigest()})
    writes["check_snapshot.py"] = contents["scripts/check_snapshot.py"]
    manifest = {
        "schema_version": 1, "source": source_info,
        "release_gates": catalog["release_gates"], "profile": profile, "files": files,
        "checker_source_path": "scripts/check_snapshot.py",
        "checker_sha256": hashlib.sha256(writes["check_snapshot.py"]).hexdigest(),
    }
    writes["manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if output.exists():
        for path in output.rglob("*"):
            reject_symlinks(project, path)
        existing = {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()}
        if existing != set(writes) or any(
            confined_path(output, relative).read_bytes() != content for relative, content in writes.items()
        ):
            raise ValueError(f"拒絕覆寫既有不同候選，請保留差異並另行處理：{output}")
        return output
    output.parent.mkdir(parents=True, exist_ok=True)
    # 先完成隔離寫入與驗證，再移入候選位置；任何步驟都不碰有效基準。
    with tempfile.TemporaryDirectory(prefix=".snapshot-", dir=output.parent) as temporary:
        staging = Path(temporary)
        for relative, content in writes.items():
            target = staging / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        errors = verify_manifest(staging / "manifest.json", not preview, staging / "check_snapshot.py")
        if errors:
            raise ValueError("候選驗證失敗：" + "；".join(errors))
        staging.rename(output)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("backend", "frontend"), required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--preview", action="store_true", help="只準備隔離試採用副本")
    parser.add_argument("--commit", help="已發布版本的完整來源提交，未指定時核對 HEAD")
    parser.add_argument("--update", action="store_true", help="已停用；不支援強制覆寫或原位升版")
    arguments = parser.parse_args()
    try:
        if arguments.update:
            raise ValueError("--update 已停用；請準備隔離候選並依治理流程核准切換")
        output = prepare_snapshot(ROOT, arguments.project, arguments.profile, arguments.preview, arguments.commit)
    except (OSError, ValueError, TypeError, KeyError) as exception:
        print(f"匯出失敗：{exception}", file=sys.stderr)
        return 1
    print(f"已準備隔離候選：{output}；未切換有效規範、正式檢查器、hooks 或 CI。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
