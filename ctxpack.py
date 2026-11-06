#!/usr/bin/env python3
"""Pack a project into one markdown file you can paste into an LLM."""

import argparse
import locale
import math
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

__version__ = "0.1.0"

OUTPUT_NAME = "context_prompt.md"

# Same syntax as .gitignore. A project can undo any of these from its own
# .ignore, e.g. "!assets/".
DEFAULT_IGNORE = """
.git
.hg
.svn
node_modules/
bower_components/
.next/
.nuxt/
.turbo/
.svelte-kit/
.cache/
.parcel-cache/
dist/
build/
out/
target/
coverage/
vendor/
assets/
__pycache__/
*.pyc
.venv/
venv/
.tox/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.egg-info/
.idea/
.vscode/
.DS_Store
Thumbs.db

package-lock.json
yarn.lock
pnpm-lock.yaml
bun.lockb
poetry.lock
uv.lock
Pipfile.lock
Cargo.lock
Gemfile.lock
composer.lock
go.sum

*.min.js
*.min.css
*.map
*.svg
*.log
context_prompt.md

.env
.env.*
!.env.example
!.env.sample
*.pem
*.key
*.p12
*.pfx
id_rsa
id_ed25519
.npmrc
.pypirc
.aws/
.ssh/
"""

SECRET_RE = re.compile(
    r"\bAKIA[0-9A-Z]{16}\b"
    r"|\bgh[pousr]_[A-Za-z0-9]{36}"
    r"|\bsk-[A-Za-z0-9_-]{20,}"
    r"|\bsk_live_[0-9a-zA-Z]{24,}"
    r"|\bxox[baprs]-[0-9A-Za-z-]{10,}"
    r"|\bAIza[0-9A-Za-z_-]{35}"
    r"|-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----"
)

LANGUAGES = {
    ".py": "python", ".js": "javascript", ".jsx": "jsx", ".ts": "typescript",
    ".tsx": "tsx", ".rb": "ruby", ".rs": "rust", ".kt": "kotlin", ".cs": "csharp",
    ".sh": "bash", ".yml": "yaml", ".md": "markdown", ".h": "c", ".hpp": "cpp",
}
LANGUAGES_BY_NAME = {"Dockerfile": "dockerfile", "Makefile": "makefile"}

STRINGS = {
    "en": {
        "summary": "{files} files, {size}, ~{tokens} tokens",
        "heaviest": "heaviest files:",
        "skipped": "skipped: {binary} binary, {large} too large, {secret} with secrets",
        "secret": "possible secret, left out: {path}",
        "wrote": "wrote {path}",
        "copied": "copied to clipboard",
        "no_clipboard": "no clipboard tool found, use the file instead",
        "over": "over the limit of {limit} tokens, not copied. Trim the files above or use --force",
        "empty": "nothing to pack in {path}",
        "not_found": "folder not found: {path}",
    },
    "pt": {
        "summary": "{files} arquivos, {size}, ~{tokens} tokens",
        "heaviest": "arquivos mais pesados:",
        "skipped": "ignorados: {binary} binários, {large} grandes demais, {secret} com segredos",
        "secret": "possível segredo, deixado de fora: {path}",
        "wrote": "gravado em {path}",
        "copied": "copiado para a área de transferência",
        "no_clipboard": "nenhuma ferramenta de clipboard encontrada, use o arquivo",
        "over": "passou do limite de {limit} tokens, não copiei. Corte os arquivos acima ou use --force",
        "empty": "nada para empacotar em {path}",
        "not_found": "pasta não encontrada: {path}",
    },
    "es": {
        "summary": "{files} archivos, {size}, ~{tokens} tokens",
        "heaviest": "archivos más pesados:",
        "skipped": "omitidos: {binary} binarios, {large} demasiado grandes, {secret} con secretos",
        "secret": "posible secreto, omitido: {path}",
        "wrote": "escrito en {path}",
        "copied": "copiado al portapapeles",
        "no_clipboard": "no hay herramienta de portapapeles, usa el archivo",
        "over": "supera el límite de {limit} tokens, no se copió. Recorta los archivos de arriba o usa --force",
        "empty": "nada que empaquetar en {path}",
        "not_found": "carpeta no encontrada: {path}",
    },
    "de": {
        "summary": "{files} Dateien, {size}, ~{tokens} Tokens",
        "heaviest": "größte Dateien:",
        "skipped": "übersprungen: {binary} binär, {large} zu groß, {secret} mit Secrets",
        "secret": "mögliches Secret, ausgelassen: {path}",
        "wrote": "geschrieben: {path}",
        "copied": "in die Zwischenablage kopiert",
        "no_clipboard": "kein Clipboard-Tool gefunden, nimm die Datei",
        "over": "über dem Limit von {limit} Tokens, nicht kopiert. Kürze die Dateien oben oder nutze --force",
        "empty": "nichts zu packen in {path}",
        "not_found": "Ordner nicht gefunden: {path}",
    },
    "fr": {
        "summary": "{files} fichiers, {size}, ~{tokens} tokens",
        "heaviest": "fichiers les plus lourds :",
        "skipped": "ignorés : {binary} binaires, {large} trop gros, {secret} avec secrets",
        "secret": "secret possible, exclu : {path}",
        "wrote": "écrit dans {path}",
        "copied": "copié dans le presse-papiers",
        "no_clipboard": "aucun outil de presse-papiers trouvé, utilise le fichier",
        "over": "au-dessus de la limite de {limit} tokens, non copié. Allège les fichiers ci-dessus ou utilise --force",
        "empty": "rien à empaqueter dans {path}",
        "not_found": "dossier introuvable : {path}",
    },
    "ja": {
        "summary": "{files} ファイル、{size}、約 {tokens} トークン",
        "heaviest": "サイズの大きいファイル:",
        "skipped": "スキップ: バイナリ {binary}、サイズ超過 {large}、シークレット {secret}",
        "secret": "シークレットの可能性があるため除外: {path}",
        "wrote": "{path} に書き出しました",
        "copied": "クリップボードにコピーしました",
        "no_clipboard": "クリップボードのコマンドが見つかりません。ファイルを使ってください",
        "over": "上限の {limit} トークンを超えたのでコピーしていません。上のファイルを減らすか --force を使ってください",
        "empty": "{path} に対象ファイルがありません",
        "not_found": "フォルダが見つかりません: {path}",
    },
}

# Windows reports names like "Portuguese_Brazil" instead of "pt_BR".
WINDOWS_LOCALES = {
    "english": "en", "portuguese": "pt", "spanish": "es",
    "german": "de", "french": "fr", "japanese": "ja",
}


def detect_language():
    names = [os.environ.get(k) for k in ("LC_ALL", "LC_MESSAGES", "LANG")]
    try:
        names.append(locale.getlocale()[0])
    except ValueError:
        pass
    for name in names:
        if not name:
            continue
        name = name.lower()
        code = WINDOWS_LOCALES.get(name.split("_")[0], name[:2])
        if code in STRINGS:
            return code
    return "en"


def glob_to_regex(glob):
    out = []
    i = 0
    while i < len(glob):
        c = glob[i]
        if c == "\\" and i + 1 < len(glob):
            out.append(re.escape(glob[i + 1]))
            i += 2
        elif glob.startswith("**/", i) and (i == 0 or glob[i - 1] == "/"):
            out.append("(?:.*/)?")
            i += 3
        elif glob[i:] == "/**":
            out.append("/.*")
            i += 3
        elif c == "*":
            while glob.startswith("*", i):
                i += 1
            out.append("[^/]*")
        elif c == "?":
            out.append("[^/]")
            i += 1
        elif c == "[":
            end = glob.find("]", i + 2)
            if end == -1:
                out.append(r"\[")
                i += 1
            else:
                body = glob[i + 1:end].replace("\\", "\\\\")
                if body[0] in "!^":
                    body = "^" + body[1:]
                out.append("[" + body + "]")
                i = end + 1
        else:
            out.append(re.escape(c))
            i += 1
    return "".join(out)


def parse_rule(line, base=""):
    line = re.sub(r"(?<!\\)\s+$", "", line)
    if not line or line.startswith("#"):
        return None
    negate = line.startswith("!")
    if negate:
        line = line[1:]
    dir_only = line.endswith("/")
    line = line.rstrip("/")
    anchored = "/" in line
    line = line.lstrip("/")
    if not line:
        return None
    prefix = "" if anchored else "(?:.*/)?"
    return base, re.compile("^" + prefix + glob_to_regex(line) + "$"), negate, dir_only


def parse_rules(text, base=""):
    rules = (parse_rule(line, base) for line in text.splitlines())
    return [rule for rule in rules if rule]


def load_rules(directory, base):
    rules = []
    for name in (".gitignore", ".ignore"):
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            with open(path, encoding="utf-8", errors="replace") as f:
                rules += parse_rules(f.read(), base)
    return rules


def is_ignored(path, is_dir, rules):
    # Last match wins, like git.
    ignored = False
    for base, regex, negate, dir_only in rules:
        if dir_only and not is_dir:
            continue
        target = path
        if base:
            if not path.startswith(base + "/"):
                continue
            target = path[len(base) + 1:]
        if regex.match(target):
            ignored = not negate
    return ignored


def walk(directory, rel, rules, extra):
    rules = rules + load_rules(directory, rel)
    try:
        entries = list(os.scandir(directory))
    except OSError:
        return
    entries.sort(key=lambda e: (not e.is_dir(follow_symlinks=False), e.name.lower()))
    for entry in entries:
        if entry.is_symlink():
            continue
        path = rel + "/" + entry.name if rel else entry.name
        is_dir = entry.is_dir()
        # --exclude goes last so it beats anything in the project's own files.
        if is_ignored(path, is_dir, rules + extra):
            continue
        if is_dir:
            yield from walk(entry.path, path, rules, extra)
        else:
            yield path


def matches_only(path, only):
    parts = path.split("/")
    candidates = ["/".join(parts[:i]) for i in range(1, len(parts) + 1)]
    return any(rule[1].match(c) for rule in only for c in candidates)


def read_text(path, max_bytes):
    """Return (text, reason); reason is set when the file can't be used."""
    if os.path.getsize(path) > max_bytes:
        return None, "large"
    with open(path, "rb") as f:
        data = f.read()
    if b"\0" in data[:8192]:
        return None, "binary"
    try:
        return data.decode("utf-8-sig").replace("\r\n", "\n"), None
    except UnicodeDecodeError:
        return None, "binary"


WORD_RE = re.compile(r"[぀-ヿ㐀-鿿가-힯]|[^\W\d_]+|\d+|[^\w\s]")


def estimate_tokens(text):
    # Tuned against cl100k on Python and JS/TS sources. Good to about 20%,
    # which is enough to tell whether a paste will fit.
    total = 0
    for word in WORD_RE.findall(text):
        total += 1 + (len(word) - 1) // 6
    return math.ceil(total * 0.95)


def token_counter():
    """Use tiktoken when it's around, otherwise the estimate."""
    try:
        import tiktoken

        enc = tiktoken.get_encoding("cl100k_base")
        return lambda text: len(enc.encode(text, disallowed_special=()))
    except Exception:
        return estimate_tokens


def fence_for(text):
    runs = re.findall(r"`{3,}", text)
    return "`" * (max(map(len, runs), default=2) + 1)


def language_for(path):
    name = path.rsplit("/", 1)[-1]
    if name in LANGUAGES_BY_NAME:
        return LANGUAGES_BY_NAME[name]
    ext = os.path.splitext(name)[1].lower()
    return LANGUAGES.get(ext, ext[1:])


def render_tree(name, paths):
    tree = {}
    for path in paths:
        node = tree
        for part in path.split("/"):
            node = node.setdefault(part, {})
    lines = [name + "/"]

    def add(node, prefix):
        items = sorted(node.items(), key=lambda kv: (not kv[1], kv[0].lower()))
        for i, (part, children) in enumerate(items):
            last = i == len(items) - 1
            lines.append(prefix + ("└── " if last else "├── ") + part + ("/" if children else ""))
            add(children, prefix + ("    " if last else "│   "))

    add(tree, "")
    return "\n".join(lines)


def render(name, files):
    parts = ["# " + name, "", "## Tree", "", "```text", render_tree(name, [p for p, _ in files]), "```", "", "## Files", ""]
    for path, text in files:
        fence = fence_for(text)
        parts += ["### " + path, "", fence + language_for(path), text.rstrip("\n"), fence, ""]
    return "\n".join(parts)


def clipboard_commands():
    if sys.platform == "win32":
        return [["clip"]]
    if sys.platform == "darwin":
        return [["pbcopy"]]
    commands = []
    if os.environ.get("WAYLAND_DISPLAY"):
        commands.append(["wl-copy"])
    commands += [
        ["xclip", "-selection", "clipboard"],
        ["xsel", "--clipboard", "--input"],
        ["termux-clipboard-set"],
        ["clip.exe"],  # WSL
    ]
    return commands


def copy_to_clipboard(text):
    for command in clipboard_commands():
        if not shutil.which(command[0]):
            continue
        # clip mangles anything non-ASCII unless it's UTF-16, and a BOM would
        # end up pasted as well.
        encoding = "utf-16-le" if command[0].startswith("clip") else "utf-8"
        try:
            subprocess.run(
                command,
                input=text.encode(encoding),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
                timeout=10,
            )
            return True
        except (OSError, subprocess.SubprocessError):
            continue
    return False


def human_size(size):
    for unit in ("B", "KB", "MB"):
        if size < 1024 or unit == "MB":
            return "{:.0f} {}".format(size, unit) if unit == "B" else "{:.1f} {}".format(size, unit)
        size /= 1024


def parse_args(argv):
    p = argparse.ArgumentParser(prog="ctxpack", description=__doc__)
    p.add_argument("path", nargs="?", default=".", help="project folder (default: current folder)")
    p.add_argument("-o", "--output", default=OUTPUT_NAME, help="output file, relative to the project (default: %(default)s)")
    p.add_argument("-x", "--exclude", action="append", default=[], metavar="GLOB", help="extra pattern to leave out, gitignore syntax, repeatable")
    p.add_argument("--only", action="append", default=[], metavar="GLOB", help="keep only matching paths, repeatable")
    p.add_argument("--max-tokens", type=int, default=180000, metavar="N", help="don't copy above this many tokens (default: %(default)s, 0 = no limit)")
    p.add_argument("--max-size", type=int, default=256, metavar="KB", help="skip files bigger than this (default: %(default)s)")
    p.add_argument("--top", type=int, default=5, metavar="N", help="how many heavy files to list (default: %(default)s)")
    p.add_argument("--dry-run", action="store_true", help="show the numbers, write and copy nothing")
    p.add_argument("--no-copy", action="store_true", help="write the file but leave the clipboard alone")
    p.add_argument("--force", action="store_true", help="copy even over --max-tokens")
    p.add_argument("--no-defaults", action="store_true", help="drop the built-in ignore list, .gitignore and .ignore still apply")
    p.add_argument("--allow-secrets", action="store_true", help="keep files that look like they hold keys or tokens")
    p.add_argument("--lang", choices=sorted(STRINGS), help="message language (default: from the system locale)")
    p.add_argument("--version", action="version", version="ctxpack " + __version__)
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    # Windows defaults to the ANSI codepage when output is piped, Git Bash included.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    t = STRINGS[args.lang or detect_language()]

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(t["not_found"].format(path=root), file=sys.stderr)
        return 2
    name = root.name or "project"
    output = root / args.output
    try:
        output_rel = output.resolve().relative_to(root).as_posix()
    except ValueError:
        output_rel = None

    rules = [] if args.no_defaults else parse_rules(DEFAULT_IGNORE)
    extra = parse_rules("\n".join(args.exclude))
    only = parse_rules("\n".join(g.rstrip("/") for g in args.only))
    count = token_counter()

    files = []
    skipped = Counter()
    for path in walk(str(root), "", rules, extra):
        if path == output_rel or (only and not matches_only(path, only)):
            continue
        try:
            text, reason = read_text(str(root / path), args.max_size * 1024)
        except OSError:
            continue
        if reason:
            skipped[reason] += 1
            continue
        if not args.allow_secrets and SECRET_RE.search(text):
            skipped["secret"] += 1
            print(t["secret"].format(path=path), file=sys.stderr)
            continue
        files.append((path, text))

    if not files:
        print(t["empty"].format(path=root), file=sys.stderr)
        return 1

    document = render(name, files)
    tokens = count(document)
    size = len(document.encode("utf-8"))

    print(t["summary"].format(files=len(files), size=human_size(size), tokens="{:,}".format(tokens)))
    if args.top > 0:
        print(t["heaviest"])
        heavy = sorted(((count(text), path) for path, text in files), reverse=True)
        for weight, path in heavy[: args.top]:
            print("  {:>9,}  {}".format(weight, path))
    if skipped:
        print(t["skipped"].format(binary=skipped["binary"], large=skipped["large"], secret=skipped["secret"]))

    if args.dry_run:
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8", newline="\n") as f:
        f.write(document)
    print(t["wrote"].format(path=args.output))

    if args.no_copy:
        return 0
    if args.max_tokens and tokens > args.max_tokens and not args.force:
        print(t["over"].format(limit="{:,}".format(args.max_tokens)))
    elif copy_to_clipboard(document):
        print(t["copied"])
    else:
        print(t["no_clipboard"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
