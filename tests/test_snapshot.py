"""以隔離暫存目錄驗證唯讀、失敗偵測與匯出不覆寫的行為。"""

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPECIFICATION = importlib.util.spec_from_file_location(
    "snapshot_checker", ROOT / "scripts/check_snapshot.py"
)
CHECKER = importlib.util.module_from_spec(SPECIFICATION)
SPECIFICATION.loader.exec_module(CHECKER)


class SnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="engineering-standards-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.manifest = self.root / "manifest.json"
        entries = []
        for relative in sorted(CHECKER.required_paths("backend")):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            content = f"測試文件：{relative}\n".encode("utf-8")
            target.write_bytes(content)
            entries.append({
                "path": relative,
                "source_path": relative,
                "sha256": hashlib.sha256(content).hexdigest(),
            })
        self.document = {
            "schema_version": 1,
            "source": {
                "repository": "https://github.com/twinatrick/engineering-standards",
                "version": "0.1.0-draft.1",
                "status": "draft",
                "commit": None,
            },
            "profile": "backend",
            "files": entries,
            "checker_source_path": "scripts/check_snapshot.py",
            "checker_sha256": hashlib.sha256(
                (ROOT / "scripts/check_snapshot.py").read_bytes()
            ).hexdigest(),
        }
        self.save()

    def save(self) -> None:
        self.manifest.write_text(json.dumps(self.document), encoding="utf-8")

    def test_valid_draft_is_read_only(self) -> None:
        before = {
            path: (path.read_bytes(), path.stat().st_mtime_ns)
            for path in self.root.rglob("*") if path.is_file()
        }
        self.assertEqual(CHECKER.verify_manifest(self.manifest), [])
        after = {
            path: (path.read_bytes(), path.stat().st_mtime_ns)
            for path in self.root.rglob("*") if path.is_file()
        }
        self.assertEqual(before, after)

    def test_tampered_file_fails(self) -> None:
        (self.root / "standards/common.md").write_text("異動", encoding="utf-8")
        self.assertTrue(CHECKER.verify_manifest(self.manifest))

    def test_missing_file_fails(self) -> None:
        (self.root / "standards/common.md").unlink()
        self.assertTrue(CHECKER.verify_manifest(self.manifest))

    def test_removed_manifest_entry_fails(self) -> None:
        self.document["files"].pop()
        self.save()
        self.assertTrue(CHECKER.verify_manifest(self.manifest))

    def test_duplicate_entry_fails(self) -> None:
        self.document["files"].append(self.document["files"][0])
        self.save()
        self.assertTrue(CHECKER.verify_manifest(self.manifest))

    def test_untracked_snapshot_file_fails(self) -> None:
        (self.root / "standards/extra.md").write_text("未列管", encoding="utf-8")
        self.assertTrue(CHECKER.verify_manifest(self.manifest))

    def test_unsafe_paths_fail(self) -> None:
        for relative in ("../secret", "C:/secret", "/secret", "standards\\common.md", ""):
            with self.subTest(relative=relative):
                with self.assertRaises(ValueError):
                    CHECKER.confined_path(self.root, relative)

    def test_unknown_profile_fails(self) -> None:
        self.document["profile"] = "other"
        self.save()
        with self.assertRaises(ValueError):
            CHECKER.verify_manifest(self.manifest)

    def test_source_field_must_be_object(self) -> None:
        self.document["source"] = 123
        self.save()
        self.assertTrue(CHECKER.verify_manifest(self.manifest))

    def test_source_repository_must_match(self) -> None:
        self.document["source"]["repository"] = "https://example.invalid/other"
        self.save()
        self.assertTrue(CHECKER.verify_manifest(self.manifest))

    def test_source_paths_must_match(self) -> None:
        self.document["files"][0]["source_path"] = "different.md"
        self.save()
        self.assertTrue(CHECKER.verify_manifest(self.manifest))

    def test_bad_digest_fails(self) -> None:
        self.document["files"][0]["sha256"] = "invalid"
        self.save()
        self.assertTrue(CHECKER.verify_manifest(self.manifest))

    def test_checker_digest_fails(self) -> None:
        self.document["checker_sha256"] = "0" * 64
        self.save()
        self.assertTrue(CHECKER.verify_manifest(self.manifest))

    def test_draft_cannot_be_formal_adoption(self) -> None:
        self.assertTrue(CHECKER.verify_manifest(self.manifest, require_published=True))

    def test_published_requires_release_gates(self) -> None:
        self.document["source"].update({
            "version": "0.1.0", "status": "published", "commit": "a" * 40
        })
        self.save()
        self.assertTrue(CHECKER.verify_manifest(self.manifest))

    def test_published_metadata_with_completed_gates(self) -> None:
        self.document["source"].update({
            "version": "0.1.0", "status": "published", "commit": "a" * 40
        })
        self.document["release_gates"] = {
            "license_review": "approved", "conflicts": "resolved", "public_redaction": "approved"
        }
        self.save()
        # 此測試只證明格式可接受，不宣稱虛構 SHA 真正存在。
        self.assertEqual(CHECKER.verify_manifest(self.manifest, True), [])

    def test_bad_schema_fails(self) -> None:
        self.document["schema_version"] = 99
        self.save()
        with self.assertRaises(ValueError):
            CHECKER.verify_manifest(self.manifest)

    def test_invalid_json_cli_returns_failure(self) -> None:
        self.manifest.write_text("{", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable, str(ROOT / "scripts/check_snapshot.py"),
                "--manifest", str(self.manifest),
            ],
            capture_output=True,
        )
        self.assertEqual(result.returncode, 1)

    def test_export_refuses_different_existing_file_before_writing(self) -> None:
        project = self.root / "project"
        project.mkdir()
        (project / "AGENTS.md").write_text("測試專案", encoding="utf-8")
        target = project / "docs/engineering-standards/standards/common.md"
        target.parent.mkdir(parents=True)
        target.write_text("不可覆寫", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable, str(ROOT / "scripts/export_snapshot.py"),
                "--profile", "backend", "--project", str(project),
            ],
            capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(target.read_text(encoding="utf-8"), "不可覆寫")
        self.assertFalse((project / "docs/engineering-standards/manifest.json").exists())

    def test_export_allows_update_when_flag_provided(self) -> None:
        project = self.root / "project-update"
        project.mkdir()
        (project / "AGENTS.md").write_text("測試專案", encoding="utf-8")
        target = project / "docs/engineering-standards/standards/common.md"
        target.parent.mkdir(parents=True)
        target.write_text("既有舊內容", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable, str(ROOT / "scripts/export_snapshot.py"),
                "--profile", "backend", "--project", str(project), "--update",
            ],
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotEqual(target.read_text(encoding="utf-8"), "既有舊內容")
        manifest = project / "docs/engineering-standards/manifest.json"
        self.assertEqual(CHECKER.verify_manifest(manifest), [])

    def test_export_roundtrip_both_profiles_and_repeated_export(self) -> None:
        for profile in sorted(CHECKER.PROFILES):
            with self.subTest(profile=profile):
                project = self.root / profile
                project.mkdir()
                (project / "AGENTS.md").write_text("測試專案", encoding="utf-8")
                command = [
                    sys.executable, str(ROOT / "scripts/export_snapshot.py"),
                    "--profile", profile, "--project", str(project),
                ]
                for attempt in range(2):
                    result = subprocess.run(command, capture_output=True)
                    self.assertEqual(result.returncode, 0, (attempt, result.stderr))
                manifest = project / "docs/engineering-standards/manifest.json"
                self.assertEqual(CHECKER.verify_manifest(manifest), [])
                exported = CHECKER.read_document(manifest)
                catalog = CHECKER.read_document(ROOT / "catalog.json")
                self.assertEqual(exported["source"]["status"], catalog["source"]["status"])
                self.assertEqual(exported["source"]["version"], catalog["source"]["version"])
                # 工作草案匯出應完整可讀，但不能因此取得正式採用資格。
                strict_errors = CHECKER.verify_manifest(manifest, True)
                if catalog["source"]["status"] == "published":
                    self.assertEqual(strict_errors, [])
                else:
                    self.assertIn("目前仍為未發布草案", strict_errors)


if __name__ == "__main__":
    unittest.main()
