# ctxpack

[English](../README.md) | [Português](README.pt-BR.md) | [Español](README.es.md) | [Français](README.fr.md) | [日本語](README.ja.md)

Eine einzige Python-Datei, die ein Projekt in ein Markdown-Dokument verwandelt, das du direkt in Claude, Gemini oder ChatGPT einfügen kannst. Nichts zu installieren, keine Abhängigkeiten, Python 3.8 oder neuer.

```
$ python ctxpack.py
12 Dateien, 41.3 KB, ~10,870 Tokens
größte Dateien:
      4,837  src/parser.py
      2,104  src/cli.py
geschrieben: context_prompt.md
in die Zwischenablage kopiert
```

## Download

```bash
curl -O https://raw.githubusercontent.com/ZXlinxk/ctxpack/main/ctxpack.py
```

Starte es in deinem Projektordner oder übergib den Pfad:

```bash
python ctxpack.py ~/code/my-app
```

## Was es macht

Geht rekursiv durch das Verzeichnis und beachtet `.gitignore` sowie `.ignore` (auch verschachtelte). Schreibt `context_prompt.md` mit Ordnerbaum und jeder Datei im Codeblock. Zeigt eine Token-Schätzung und die größten Dateien an und kopiert das Ergebnis in die Zwischenablage.

Liegt das Ergebnis über 180.000 Tokens, wird die Datei geschrieben, aber nicht kopiert, damit du zuerst siehst, was gekürzt werden sollte. Ändern lässt sich das mit `--max-tokens` oder mit `--force`.

## Was ausgelassen wird

- Ballast: `node_modules`, `.git`, `.next`, `dist`, `build`, `assets`, virtuelle Umgebungen, Caches, Lockfiles, minifizierte Dateien, Source-Maps.
- Binärdateien und alles über 256 KB.
- Secrets: `.env`, `*.pem`, `id_rsa` und Ähnliches nach Namen. Dateien, deren Inhalt wie Keys von AWS, GitHub, OpenAI, Stripe, Slack, Google oder wie ein privater Schlüssel aussieht, werden ebenfalls weggelassen und im Output gemeldet.

Die Secret-Prüfung deckt nur die offensichtlichen Fälle ab. Sieh dir den Inhalt vor dem Einfügen an, wenn das Projekt sensible Daten enthält.

Jeder Eintrag der Standardliste lässt sich über eine `.ignore`-Datei im Projekt wieder freigeben:

```gitignore
!assets/
```

## Optionen

| Option | Funktion |
| --- | --- |
| `-o FILE` | Ausgabedatei, Standard `context_prompt.md` |
| `-x GLOB` | Weitere Pfade ausschließen, gitignore-Syntax, wiederholbar |
| `--only GLOB` | Nur passende Pfade berücksichtigen, wiederholbar |
| `--max-tokens N` | Über N Tokens nicht kopieren, `0` schaltet das Limit aus |
| `--max-size KB` | Größere Dateien überspringen, Standard 256 |
| `--top N` | Wie viele große Dateien aufgelistet werden, Standard 5 |
| `--dry-run` | Zahlen anzeigen, nichts schreiben und nichts kopieren |
| `--no-copy` | Datei schreiben, Zwischenablage unberührt lassen |
| `--force` | Auch bei Überschreitung des Limits kopieren |
| `--no-defaults` | Eingebaute Ausschlussliste verwerfen |
| `--allow-secrets` | Dateien mit erkannten Secrets trotzdem behalten |
| `--lang CODE` | Sprache der Meldungen: `en`, `pt`, `es`, `de`, `fr` oder `ja`, Standard aus dem System |

Beispiele:

```bash
python ctxpack.py --only src/ --only README.md
python ctxpack.py -x "*.test.ts" -x docs/
python ctxpack.py --dry-run
```

## Tokens

Die Angabe ist eine Schätzung mit einer Genauigkeit von etwa 20% für Python- und JS/TS-Code. Das reicht völlig, um zu sehen, ob der Prompt passt, nicht für Rechnungen. Wenn `tiktoken` installiert ist, wird es stattdessen verwendet. Keines von beiden entspricht exakt dem Tokenizer jedes Modells.

## Zwischenablage

Windows nutzt `clip`, macOS `pbcopy`, Linux `wl-copy`, `xclip` oder `xsel`. Termux und WSL funktionieren ebenfalls. Wenn kein Tool vorhanden ist, wird die Datei trotzdem ganz normal geschrieben.

## Tests

```bash
python -m unittest discover -s tests
```

## Unterstützung

Frei nutzbar und veränderbar. Wenn es dir Zeit gespart hat, [kannst du hier etwas beitragen](https://buymeacoffee.com/samaritansli).

- Lightning: `inborngrease4665@cake.cash`
- Bitcoin: `bc1qm2j0l9zy7npnhfctf80p3ukuj2ksffwlvum3c5`

## Lizenz

Public Domain, siehe [LICENSE](../LICENSE).
