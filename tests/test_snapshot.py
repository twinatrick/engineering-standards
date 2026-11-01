"""以隔離暫存目錄驗證唯讀、失敗偵測與匯出不覆寫的行為。"""

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPECIFICATION = importlib.util.spec_from_file_location(
    "snapshot_checker", ROOT / "scripts/check_snapshot.py"
)
CHECKER = importlib.util.module_from_spec(SPECIFICATION)
SPECIFICATION.loader.exec_module(CHECKER)
EXPORT_SPECIFICATION = importlib.util.spec_from_file_location(
    "snapshot_exporter", ROOT / "scripts/export_snapshot.py"
)
EXPORTER = importlib.util.module_from_spec(EXPORT_SPECIFICATION)
with patch.dict(sys.modules, {"check_snapshot": CHECKER}):
    EXPORT_SPECIFICATION.loader.exec_module(EXPORTER)


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

    def test_line_endings_are_not_silently_normalized(self) -> None:
        path = self.root / "standards/common.md"
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
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

    def test_export_rejects_update_even_when_flag_provided(self) -> None:
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
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(target.read_text(encoding="utf-8"), "既有舊內容")
        manifest = project / "docs/engineering-standards/manifest.json"
        self.assertFalse(manifest.exists())

    def test_draft_export_roundtrip_both_profiles_and_repeated_export(self) -> None:
        source = self.root / "draft-source"
        catalog = CHECKER.read_document(ROOT / "catalog.json")
        catalog["source"].update({
            "version": "0.0.0-test.1", "status": "draft", "commit": None,
        })
        # 草案往返使用隔離資料，不依賴本庫工作目錄是否已正式提交。
        for relative in [entry["path"] for entry in catalog["files"]] + [
            "scripts/check_snapshot.py", "scripts/export_snapshot.py",
        ]:
            target = source / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / relative).read_bytes())
        (source / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
        for profile in sorted(CHECKER.PROFILES):
            with self.subTest(profile=profile):
                project = self.root / profile
                project.mkdir()
                (project / "AGENTS.md").write_text("測試專案", encoding="utf-8")
                command = [
                    sys.executable, str(source / "scripts/export_snapshot.py"),
                    "--profile", profile, "--project", str(project), "--preview",
                ]
                for attempt in range(2):
                    result = subprocess.run(command, capture_output=True)
                    self.assertEqual(result.returncode, 0, (attempt, result.stderr))
                manifest = project / "docs/engineering-standards-preview" / catalog["source"]["version"] / profile / "manifest.json"
                self.assertEqual(CHECKER.verify_manifest(manifest), [])
                exported = CHECKER.read_document(manifest)
                self.assertEqual(exported["source"]["status"], catalog["source"]["status"])
                self.assertEqual(exported["source"]["version"], catalog["source"]["version"])
                # 草案匯出應完整可讀，但不能因此取得正式採用資格。
                strict_errors = CHECKER.verify_manifest(manifest, True)
                self.assertIn("目前仍為未發布草案或僅供試採用的預發布版本", strict_errors)

    def test_prerelease_is_not_formal_even_with_completed_gates(self) -> None:
        self.document["source"].update({
            "version": "0.2.0-rc.1", "status": "prerelease", "commit": "a" * 40
        })
        self.document["release_gates"] = dict(CHECKER.RELEASE_GATES)
        self.save()
        self.assertEqual(CHECKER.verify_manifest(self.manifest), [])
        self.assertTrue(CHECKER.verify_manifest(self.manifest, True))

    def test_published_rejects_all_prerelease_labels(self) -> None:
        for version in ("0.2.0-rc.1", "0.2.0-beta.1", "0.2.0-DRAFT.1", "0.2.0-alpha.1"):
            with self.subTest(version=version):
                self.document["source"].update({
                    "version": version, "status": "published", "commit": "a" * 40
                })
                self.document["release_gates"] = dict(CHECKER.RELEASE_GATES)
                self.save()
                self.assertTrue(CHECKER.verify_manifest(self.manifest))

    def test_semver_rejects_invalid_released_versions(self) -> None:
        for version in ("0.02.0", "0.2", "0.2.0-01", "v0.2.0", "../0.2.0"):
            with self.subTest(version=version):
                self.document["source"].update({
                    "version": version, "status": "published", "commit": "a" * 40
                })
                self.document["release_gates"] = dict(CHECKER.RELEASE_GATES)
                self.save()
                self.assertTrue(CHECKER.verify_manifest(self.manifest))

    def test_prerelease_requires_marker_and_gates(self) -> None:
        self.document["source"].update({
            "version": "0.2.0", "status": "prerelease", "commit": "a" * 40
        })
        self.save()
        self.assertTrue(CHECKER.verify_manifest(self.manifest))

    def test_old_published_format_with_separate_checker(self) -> None:
        historical = self.root / "old_checker.py"
        historical.write_bytes(b"# historical checker\n")
        self.document["source"].update({
            "version": "0.1.0", "status": "published", "commit": "a" * 40
        })
        self.document["release_gates"] = dict(CHECKER.RELEASE_GATES)
        self.document["checker_sha256"] = hashlib.sha256(historical.read_bytes()).hexdigest()
        self.save()
        self.assertEqual(CHECKER.verify_manifest(self.manifest, True, historical), [])
        historical.write_bytes(b"# changed\n")
        self.assertTrue(CHECKER.verify_manifest(self.manifest, True, historical))


class ExportSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="engineering-export-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.project = self.root / "project"
        self.project.mkdir()
        (self.project / "AGENTS.md").write_text("測試專案", encoding="utf-8")
        self.catalog = CHECKER.read_document(ROOT / "catalog.json")
        self.catalog["source"].update({"version": "0.2.0", "status": "published", "commit": None})
        self.catalog["release_gates"] = dict(CHECKER.RELEASE_GATES)
        for entry in self.catalog["files"]:
            target = self.source / entry["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            content = (ROOT / entry["path"]).read_bytes()
            target.write_bytes(content)
            entry["sha256"] = hashlib.sha256(content).hexdigest()
        for name in ("check_snapshot.py", "export_snapshot.py"):
            target = self.source / "scripts" / name
            target.parent.mkdir(exist_ok=True)
            target.write_bytes((ROOT / "scripts" / name).read_bytes())
        self.save_catalog()
        self.commit = "a" * 40
        # 模擬既定提交的不可變 blob，不建立提交或修改 Git 歷史。
        self.committed = {
            path.relative_to(self.source).as_posix(): path.read_bytes()
            for path in self.source.rglob("*") if path.is_file()
        }

    def save_catalog(self) -> None:
        (self.source / "catalog.json").write_text(json.dumps(self.catalog), encoding="utf-8")

    def git(self, root: Path, *arguments: str) -> bytes:
        self.assertEqual(root, self.source)
        if arguments == ("rev-parse", "HEAD") or arguments == ("rev-parse", "--verify", f"{self.commit}^{{commit}}"):
            return self.commit.encode()
        if arguments[0] == "show":
            revision, relative = arguments[1].split(":", 1)
            if revision == self.commit and relative in self.committed:
                return self.committed[relative]
        raise ValueError("測試提交或 blob 不存在")

    def prepare(self, preview: bool = False, profile: str = "backend") -> Path:
        with patch.object(EXPORTER, "git_output", side_effect=self.git):
            return EXPORTER.prepare_snapshot(self.source, self.project, profile, preview, self.commit)

    def test_formal_candidate_isolated_and_idempotent(self) -> None:
        for profile in ("backend", "frontend"):
            with self.subTest(profile=profile):
                output = self.prepare(profile=profile)
                self.assertEqual(output, self.project / "docs/engineering-standards-candidates/0.2.0" / profile)
                self.assertEqual(CHECKER.verify_manifest(output / "manifest.json", True, output / "check_snapshot.py"), [])
                self.assertEqual(self.prepare(profile=profile), output)
        self.assertFalse((self.project / "docs/engineering-standards").exists())
        self.assertFalse((self.project / "scripts/check_engineering_standards.py").exists())

    def test_wrong_commit_or_missing_blob_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            EXPORTER.committed_contents(self.source, "bad", {"catalog.json"})
        del self.committed["scripts/check_snapshot.py"]
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertFalse((self.project / "docs").exists())

    def test_real_git_missing_commit_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            EXPORTER.committed_contents(ROOT, "f" * 40, {"README.md"})

    def test_real_git_unchanged_file_matches(self) -> None:
        revision = EXPORTER.git_output(ROOT, "rev-parse", "HEAD").decode().strip()
        relative = "standards/frontend/master-rules.md"
        commit, contents = EXPORTER.committed_contents(ROOT, revision, {relative})
        self.assertEqual(commit, revision)
        self.assertEqual(contents[relative], (ROOT / relative).read_bytes())

    def test_other_profile_and_exporter_are_bound_to_commit(self) -> None:
        for relative in ("standards/frontend.md", "scripts/export_snapshot.py", "catalog.json"):
            with self.subTest(relative=relative):
                original = self.committed[relative]
                self.committed[relative] = original + b"\n"
                with self.assertRaises(ValueError):
                    self.prepare()
                self.committed[relative] = original

    def test_unrelated_local_file_does_not_block_export(self) -> None:
        (self.source / "unrelated.txt").write_text("本機異動", encoding="utf-8")
        self.assertTrue(self.prepare().is_dir())

    def test_catalog_commit_mismatch_is_rejected(self) -> None:
        self.catalog["source"]["commit"] = "b" * 40
        self.save_catalog()
        self.committed["catalog.json"] = (self.source / "catalog.json").read_bytes()
        with self.assertRaises(ValueError):
            self.prepare()

    def test_existing_candidate_changes_are_preserved(self) -> None:
        output = self.prepare()
        target = output / "standards/common.md"
        target.write_text("保留異動", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertEqual(target.read_text(encoding="utf-8"), "保留異動")

    def test_modified_active_snapshot_is_preserved(self) -> None:
        active = self.project / "docs/engineering-standards"
        active.mkdir(parents=True)
        target = active / "standards/common.md"
        target.parent.mkdir()
        target.write_text("現場", encoding="utf-8")
        with self.assertRaises(OSError):
            self.prepare()
        self.assertEqual(target.read_text(encoding="utf-8"), "現場")
        self.assertFalse((self.project / "docs/engineering-standards-candidates").exists())

    def test_valid_legacy_active_snapshot_allows_preparation_but_tampering_does_not(self) -> None:
        candidate = self.prepare()
        active = self.project / "docs/engineering-standards"
        shutil.copytree(candidate, active)
        checker = self.project / "scripts/check_engineering_standards.py"
        checker.parent.mkdir()
        checker.write_bytes(b"# historical checker, never executed\n")
        manifest = active / "manifest.json"
        document = CHECKER.read_document(manifest)
        document["source"]["version"] = "0.1.0"
        document["checker_sha256"] = hashlib.sha256(checker.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(document), encoding="utf-8")
        before = {path: path.read_bytes() for path in active.rglob("*") if path.is_file()}
        self.assertEqual(self.prepare(), candidate)
        self.assertEqual(before, {path: path.read_bytes() for path in active.rglob("*") if path.is_file()})
        target = active / "standards/common.md"
        target.write_bytes(b"preserve local changes")
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertEqual(target.read_bytes(), b"preserve local changes")
        self.assertEqual(checker.read_bytes(), b"# historical checker, never executed\n")

    def test_profile_change_requires_explicit_handling(self) -> None:
        candidate = self.prepare()
        active = self.project / "docs/engineering-standards"
        shutil.copytree(candidate, active)
        checker = self.project / "scripts/check_engineering_standards.py"
        checker.parent.mkdir()
        checker.write_bytes((candidate / "check_snapshot.py").read_bytes())
        with self.assertRaises(ValueError):
            self.prepare(profile="frontend")

    def test_candidate_path_cannot_alias_active_snapshot(self) -> None:
        active = self.project / "docs/engineering-standards"
        active.mkdir(parents=True)
        alias = self.project / "docs/engineering-standards-preview"
        try:
            if os.name == "nt":
                subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(alias), str(active)],
                    capture_output=True, check=True,
                )
            else:
                alias.symlink_to(active, target_is_directory=True)
        except (OSError, subprocess.CalledProcessError) as exception:
            self.skipTest(f"環境不允許建立測試符號連結：{exception}")
        with self.assertRaises(ValueError):
            self.prepare(preview=True)
        self.assertEqual(list(active.iterdir()), [])

    def test_candidate_checker_cannot_be_modified_or_removed(self) -> None:
        output = self.prepare()
        checker = output / "check_snapshot.py"
        checker.write_bytes(b"changed checker")
        with self.assertRaises(ValueError):
            self.prepare()
        checker.unlink()
        with self.assertRaises(ValueError):
            self.prepare()

    def test_draft_and_prerelease_require_preview(self) -> None:
        for status in ("draft", "prerelease"):
            with self.subTest(status=status):
                self.catalog["source"].update({"status": status, "version": "0.2.0-rc.1"})
                self.save_catalog()
                with self.assertRaises(ValueError):
                    self.prepare()

    def test_prerelease_preview_has_no_formal_qualification(self) -> None:
        self.catalog["source"].update({"status": "prerelease", "version": "0.2.0-rc.1"})
        self.save_catalog()
        self.committed["catalog.json"] = (self.source / "catalog.json").read_bytes()
        output = self.prepare(preview=True)
        self.assertIn("engineering-standards-preview", output.parts)
        self.assertEqual(CHECKER.verify_manifest(output / "manifest.json", False, output / "check_snapshot.py"), [])
        self.assertTrue(CHECKER.verify_manifest(output / "manifest.json", True, output / "check_snapshot.py"))

    def test_preview_does_not_touch_active_snapshot_or_checker(self) -> None:
        active = self.project / "docs/engineering-standards/standards/common.md"
        checker = self.project / "scripts/check_engineering_standards.py"
        for path in (active, checker):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"unchanged")
        self.prepare(preview=True)
        self.assertEqual(active.read_bytes(), b"unchanged")
        self.assertEqual(checker.read_bytes(), b"unchanged")

    def test_failed_preparation_does_not_publish_partial_candidate(self) -> None:
        with patch.object(EXPORTER, "verify_manifest", return_value=["測試失敗"]):
            with self.assertRaises(ValueError):
                self.prepare()
        base = self.project / "docs/engineering-standards-candidates/0.2.0"
        self.assertFalse((base / "backend").exists())
        self.assertEqual(list(base.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
