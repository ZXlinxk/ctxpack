# ctxpack

One Python file that turns a project into a single markdown file you can paste into Claude, Gemini or ChatGPT. Nothing to install, no dependencies, Python 3.8 or newer.

```
$ python ctxpack.py
12 files, 41.3 KB, ~10,870 tokens
heaviest files:
      4,837  src/parser.py
      2,104  src/cli.py
wrote context_prompt.md
copied to clipboard
```

## Why

Copying files one by one into a web chat is slow, and an agent or an IDE plugin is a lot of setup when you only want to ask about your code. This is the smallest thing I could make that solves that: one file you can read in a few minutes.

If you want more output formats, use Repomix or code2prompt. They do more. ctxpack stays small on purpose.

## Get it

```bash
curl -O https://raw.githubusercontent.com/ZXlinxk/ctxpack/main/ctxpack.py
```

Run it from your project, or pass the folder:

```bash
python ctxpack.py ~/code/my-app
```

On macOS and Linux, use `python3` if `python` is not found.

## What it does

Walks the folder and respects `.gitignore` and `.ignore`, nested ones included. Writes `context_prompt.md` with the folder tree and every file in a fenced block. Shows a token estimate and the heaviest files, then copies the result to the clipboard.

If the result is over 180,000 tokens it writes the file but doesn't copy it, so you can see what to cut first. Change that with `--max-tokens`, or use `--force`.

## What gets left out

- Junk: `node_modules`, `.git`, `.next`, `dist`, `build`, `assets`, virtualenvs, caches, lock files, minified files, source maps.
- Binary files and anything over 256 KB.
- Secrets: `.env`, `*.pem`, `id_rsa` and similar by name. Files whose content looks like an AWS, GitHub, OpenAI, Stripe, Slack or Google key, or a private key, are dropped too and named in the output.

The secret check catches the obvious cases and nothing more. Read what you paste if the project is sensitive.

Everything in the default list can be undone from a `.ignore` file in your project:

```gitignore
!assets/
```

## Options

| Option | What it does |
| --- | --- |
| `-o FILE` | Output file, default `context_prompt.md` |
| `-x GLOB` | Leave out more paths, gitignore syntax, repeatable |
| `--only GLOB` | Keep only matching paths, repeatable |
| `--max-tokens N` | Don't copy above N tokens, `0` turns the limit off |
| `--max-size KB` | Skip files bigger than this, default 256 |
| `--top N` | How many heavy files to list, default 5 |
| `--dry-run` | Show the numbers, write and copy nothing |
| `--no-copy` | Write the file, leave the clipboard alone |
| `--force` | Copy even over the limit |
| `--no-defaults` | Drop the built-in ignore list |
| `--allow-secrets` | Keep files flagged as holding secrets |
| `--lang CODE` | Messages in `en`, `pt`, `es`, `de`, `fr` or `ja`, default comes from your system |

Examples:

```bash
python ctxpack.py --only src/ --only README.md
python ctxpack.py -x "*.test.ts" -x docs/
python ctxpack.py --dry-run
```

## Tokens

The count is an estimate, good to about 20% on Python and JS/TS code. That's enough to know if a paste fits, not enough to bill anyone. If `tiktoken` is installed it gets used instead. Neither one is the exact tokenizer of every model.

## Clipboard

Windows uses `clip`, macOS uses `pbcopy`, Linux uses `wl-copy`, `xclip` or `xsel`, and Termux and WSL work too. If none is available the file is still written.

## Known limits

- The `.gitignore` matching is hand written, because of the no dependencies rule. It matched real `git` on 300 random repos, but tell me if a pattern comes out wrong.
- It targets Python 3.8, but I've only run it on 3.12 on Windows. macOS and Linux reports are welcome.
- The secret check is a safety net, not a guarantee.

## Tests

```bash
python -m unittest discover -s tests
```

## Support

Free to use and change. If it saved you time, [you can chip in here](https://buymeacoffee.com/samaritansli).

- Lightning: `inborngrease4665@cake.cash`
- Bitcoin: `bc1qm2j0l9zy7npnhfctf80p3ukuj2ksffwlvum3c5`

## License

Public domain, see [LICENSE](LICENSE).
