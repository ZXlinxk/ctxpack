import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import ctxpack


def write(root, files):
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8", newline="")


def run(root, *args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = ctxpack.main([str(root), "--no-copy", "--lang", "en", *args])
    packed = root / ctxpack.OUTPUT_NAME
    text = packed.read_text(encoding="utf-8") if packed.exists() else ""
    return code, text, out.getvalue() + err.getvalue()


class Packing(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def test_default_junk_is_left_out(self):
        write(self.root, {
            "src/app.js": "console.log(1)\n",
            "node_modules/x/index.js": "nope\n",
            ".git/config": "nope\n",
            ".next/out.js": "nope\n",
            "dist/app.js": "nope\n",
            "assets/logo.txt": "nope\n",
            "package-lock.json": "{}\n",
        })
        _, text, _ = run(self.root)
        self.assertIn("### src/app.js", text)
        self.assertNotIn("nope", text)

    def test_gitignore_negation_and_nesting(self):
        write(self.root, {
            ".gitignore": "*.txt\n!keep.txt\n",
            "a.txt": "gone\n",
            "keep.txt": "stays\n",
            "sub/.gitignore": "local.py\n",
            "sub/local.py": "gone\n",
            "local.py": "stays\n",
        })
        _, text, _ = run(self.root)
        self.assertIn("### keep.txt", text)
        self.assertIn("### local.py", text)
        self.assertNotIn("### a.txt", text)
        self.assertNotIn("### sub/local.py", text)

    def test_ignore_file_can_undo_a_default(self):
        write(self.root, {".ignore": "!assets/\n", "assets/data.json": "{}\n"})
        _, text, _ = run(self.root)
        self.assertIn("### assets/data.json", text)

    def test_env_files(self):
        write(self.root, {".env": "A=1\n", ".env.local": "A=1\n", ".env.example": "A=\n"})
        _, text, _ = run(self.root)
        self.assertIn("### .env.example", text)
        self.assertNotIn("### .env\n", text)
        self.assertNotIn("### .env.local", text)

    def test_file_with_a_key_is_dropped(self):
        key = "AKIA" + "ABCDEFGHIJKLMNOP"
        write(self.root, {"cfg.py": "key = '" + key + "'\n", "ok.py": "task-with-a-really-long-name-here = 1\n"})
        _, text, report = run(self.root)
        self.assertNotIn(key, text)
        self.assertIn("### ok.py", text)
        self.assertIn("cfg.py", report)

    def test_binary_and_oversized_files(self):
        write(self.root, {"a.bin": b"\x00\x01\x02", "big.txt": "x" * 3000, "ok.txt": "fine\n"})
        _, text, report = run(self.root, "--max-size", "1")
        self.assertEqual(text.count("\n### "), 1)
        self.assertIn("1 binary, 1 too large", report)

    def test_fence_survives_backticks_in_the_file(self):
        write(self.root, {"doc.md": "````\ncode\n````\n"})
        _, text, _ = run(self.root)
        self.assertIn("`````markdown\n````\ncode\n````\n`````", text)

    def test_output_is_not_packed_into_itself(self):
        write(self.root, {"a.py": "x = 1\n"})
        run(self.root)
        _, text, _ = run(self.root)
        self.assertEqual(text.count("### a.py"), 1)
        self.assertNotIn("context_prompt.md", text)

    def test_custom_output_is_not_packed_either(self):
        write(self.root, {"a.py": "x = 1\n"})
        run(self.root, "-o", "out.txt")
        run(self.root, "-o", "out.txt")
        text = (self.root / "out.txt").read_text(encoding="utf-8")
        self.assertEqual(text.count("\n### "), 1)
        self.assertNotIn("### out.txt", text)

    def test_only_and_exclude(self):
        write(self.root, {"src/a.py": "1\n", "src/b.py": "2\n", "docs/c.md": "3\n"})
        _, text, _ = run(self.root, "--only", "src/", "-x", "b.py")
        self.assertIn("### src/a.py", text)
        self.assertNotIn("### src/b.py", text)
        self.assertNotIn("### docs/c.md", text)

    def test_dry_run_writes_nothing(self):
        write(self.root, {"a.py": "x = 1\n"})
        code, text, _ = run(self.root, "--dry-run")
        self.assertEqual((code, text), (0, ""))

    def test_empty_project(self):
        code, _, _ = run(self.root)
        self.assertEqual(code, 1)

    def test_crlf_and_bom(self):
        write(self.root, {"a.txt": b"\xef\xbb\xbfone\r\ntwo\r\n"})
        _, text, _ = run(self.root)
        self.assertIn("```txt\none\ntwo\n```", text)


class Pieces(unittest.TestCase):
    def test_tree(self):
        self.assertEqual(
            ctxpack.render_tree("p", ["src/a.py", "src/lib/b.py", "z.md"]),
            "p/\n├── src/\n│   ├── lib/\n│   │   └── b.py\n│   └── a.py\n└── z.md",
        )

    def test_estimate_counts_cjk_per_character(self):
        self.assertGreaterEqual(ctxpack.estimate_tokens("日本語のテキスト"), 8)

    def test_estimate_scales(self):
        small = ctxpack.estimate_tokens("def f(x): return x\n")
        self.assertLess(small * 90, ctxpack.estimate_tokens("def f(x): return x\n" * 100))

    def test_windows_locale_name(self):
        self.assertEqual(ctxpack.WINDOWS_LOCALES["portuguese"], "pt")

    def test_every_language_has_every_string(self):
        keys = set(ctxpack.STRINGS["en"])
        for lang, strings in ctxpack.STRINGS.items():
            self.assertEqual(set(strings), keys, lang)


if __name__ == "__main__":
    unittest.main()
