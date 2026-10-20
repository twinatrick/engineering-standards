"""從已核對的 Git 提交產生來源副本與草案清單，不更新分支或連線。"""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from check_snapshot import PROFILES, required_paths


ROOT = Path(__file__).resolve().parents[1]
REVISIONS = {
    "backend": "cb0d97685b2d3b8b1aaafa0a08ba858ee31163ae",
    "frontend": "8470f3f8981f1117e942b24e6ed287e89d328c6d",
}
REPOSITORIES = {
    "backend": "https://github.com/twinatrick/Backend-Architecture-Lab",
    "frontend": "https://github.com/twinatrick/v3-admin-vite-templete",
}


def git_bytes(repository: Path, *arguments: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments], check=True, capture_output=True
    ).stdout


def write_json(path: Path, document: dict) -> None:
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", type=Path, required=True)
    parser.add_argument("--frontend", type=Path, required=True)
    arguments = parser.parse_args()
    sources = []
    for profile in sorted(PROFILES):
        repository = getattr(arguments, profile)
        revision = REVISIONS[profile]
        current_remote = git_bytes(repository, "rev-parse", "origin/master").decode().strip()
        if current_remote != revision:
            raise ValueError(f"{profile} 遠端追蹤分支已變更，必須重新審查來源")
        review_path = ".github/AI_REVIEW.md" if profile == "backend" else "review.md"
        source_files = (
            ("開發規範.md", "master-rules.md"),
            ("AGENTS.md", "master-agents.md"),
            (review_path, "master-review.md"),
        )
        for name, destination in source_files:
            content = git_bytes(repository, "show", f"{revision}:{name}")
            output = ROOT / "standards" / profile / destination
            if output.exists() and output.read_bytes() != content:
                raise ValueError(f"拒絕覆寫不同內容：{output}")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(content)
            sources.append({
                "profile": profile,
                "repository": REPOSITORIES[profile],
                "branch": "master",
                "commit": revision,
                "local_master_at_import": git_bytes(
                    repository, "rev-parse", "master"
                ).decode().strip(),
                "path": name,
                "imported_path": output.relative_to(ROOT).as_posix(),
                "sha256": hashlib.sha256(content).hexdigest(),
                "transformation": "none; byte-for-byte Git blob",
                "license_review": "pending",
            })
    write_json(ROOT / "sources.json", {
        "schema_version": 1,
        "baseline_review_date": "2026-10-20",
        "sources": sources,
    })
    paths = set().union(*(required_paths(profile) for profile in PROFILES))
    write_json(ROOT / "catalog.json", {
        "schema_version": 1,
        "source": {
            "repository": "https://github.com/twinatrick/engineering-standards",
            "version": "0.1.0-draft.1",
            "commit": None,
            "status": "draft",
        },
        "release_gates": {
            "license_review": "pending",
            "conflicts": "pending",
            "public_redaction": "pending",
        },
        "files": [
            {"path": relative, "sha256": hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()}
            for relative in sorted(paths)
        ],
    })
    print("已產生來源副本與草案清單；尚未發布。")


if __name__ == "__main__":
    main()
