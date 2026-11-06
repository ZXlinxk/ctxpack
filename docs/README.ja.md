# ctxpack

[English](../README.md) | [Português](README.pt-BR.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [Français](README.fr.md)

プロジェクト全体を、Claude や Gemini、ChatGPT にそのまま貼れる 1 つの Markdown ファイルにまとめる単一の Python スクリプトです。インストール不要、依存関係なし、Python 3.8 以降で動きます。

```
$ python ctxpack.py
12 ファイル、41.3 KB、約 10,870 トークン
サイズの大きいファイル:
      4,837  src/parser.py
      2,104  src/cli.py
context_prompt.md に書き出しました
クリップボードにコピーしました
```

## 入手方法

```bash
curl -O https://raw.githubusercontent.com/ZXlinxk/ctxpack/main/ctxpack.py
```

プロジェクトのディレクトリで実行するか、フォルダパスを渡します:

```bash
python ctxpack.py ~/code/my-app
```

## 動作内容

サブフォルダも含めて `.gitignore` と `.ignore` を適用しながらフォルダ内を走査します。ディレクトリツリーと各ファイルの中身をコードブロックにまとめた `context_prompt.md` を書き出し、推定トークン数とサイズの大きいファイルを端末に表示したうえで、結果をクリップボードにコピーします。

合計が 180,000 トークンを超えている場合は、何を削るか先に確認できるようにファイル出力だけを行い、コピーはしません。この制限は `--max-tokens` で変更するか、`--force` で強制コピーできます。

## 除外されるファイル

- 不要なファイル: `node_modules`、`.git`、`.next`、`dist`、`build`、`assets`、仮想環境、キャッシュ、ロックファイル、minify されたファイル、ソースマップ。
- バイナリファイルおよび 256 KB を超えるファイル。
- シークレット: `.env`、`*.pem`、`id_rsa` など名前で判断されるもの。中身が AWS、GitHub、OpenAI、Stripe、Slack、Google の API キーや秘密鍵に見えるファイルも除外され、端末に出力されます。

シークレット判定は典型的なパターンのみを検出します。機密性の高いプロジェクトの場合は、貼り付ける前に中身を確認してください。

デフォルトの除外設定は、プロジェクト内の `.ignore` ファイルで打ち消すことができます:

```gitignore
!assets/
```

## オプション

| オプション | 内容 |
| --- | --- |
| `-o FILE` | 出力ファイル名、デフォルトは `context_prompt.md` |
| `-x GLOB` | 追加で除外するパス（gitignore 構文、複数指定可） |
| `--only GLOB` | 一致するパスのみ含める（複数指定可） |
| `--max-tokens N` | N トークン超ならコピーしない（`0` で無制限） |
| `--max-size KB` | このサイズ（KB）より大きいファイルをスキップ、デフォルトは 256 |
| `--top N` | リスト表示する大きいファイルの数、デフォルトは 5 |
| `--dry-run` | 数値の確認のみ、書き出しもコピーもしない |
| `--no-copy` | ファイルは書き出すがクリップボードにはコピーしない |
| `--force` | トークン上限を超えていてもコピーする |
| `--no-defaults` | 組み込みのデフォルト除外リストを無効化する |
| `--allow-secrets` | シークレットと判定されたファイルも除外しない |
| `--lang CODE` | 表示言語（`en`, `pt`, `es`, `de`, `fr`, `ja`）、デフォルトはシステム設定 |

使用例:

```bash
python ctxpack.py --only src/ --only README.md
python ctxpack.py -x "*.test.ts" -x docs/
python ctxpack.py --dry-run
```

## トークン数について

カウントは概算で、Python や JS/TS コードでは約 20% の誤差に収まります。コンテキストウィンドウに収まるかどうかの判断には十分ですが、課金計算用ではありません。`tiktoken` がインストールされていれば自動でそちらを使います。どちらも各モデル固有のトークナイザーと完全に一致するわけではありません。

## クリップボード

Windows では `clip`、macOS では `pbcopy`、Linux では `wl-copy`、`xclip`、`xsel` を使います。Termux や WSL にも対応しています。対応コマンドが見つからない場合でも、ファイル自体は正常に出力されます。

## テスト

```bash
python -m unittest discover -s tests
```

## サポート

自由に使用・改変できます。時間の節約になったら、[こちらから支援できます](https://buymeacoffee.com/samaritansli)。

- Lightning: `inborngrease4665@cake.cash`
- Bitcoin: `bc1qm2j0l9zy7npnhfctf80p3ukuj2ksffwlvum3c5`

## ライセンス

パブリックドメインです。[LICENSE](../LICENSE) を参照してください。
