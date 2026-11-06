# ctxpack

[English](../README.md) | [Português](README.pt-BR.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [日本語](README.ja.md)

Un seul fichier Python qui transforme un projet en un fichier markdown que tu peux coller dans Claude, Gemini ou ChatGPT. Rien à installer, aucune dépendance, Python 3.8 ou plus récent.

```
$ python ctxpack.py
12 fichiers, 41.3 KB, ~10,870 tokens
fichiers les plus lourds :
      4,837  src/parser.py
      2,104  src/cli.py
écrit dans context_prompt.md
copié dans le presse-papiers
```

## Téléchargement

```bash
curl -O https://raw.githubusercontent.com/ZXlinxk/ctxpack/main/ctxpack.py
```

Lance-le depuis ton projet, ou passe le dossier en argument :

```bash
python ctxpack.py ~/code/my-app
```

## Ce qu'il fait

Parcourt le dossier en respectant `.gitignore` et `.ignore`, y compris les fichiers imbriqués. Écrit `context_prompt.md` avec l'arborescence des dossiers et chaque fichier dans un bloc de code. Affiche une estimation des tokens et les fichiers les plus lourds, puis copie le résultat dans le presse-papiers.

Si le résultat dépasse 180 000 tokens, il écrit le fichier mais ne le copie pas, pour que tu puisses d'abord voir ce qu'il faut couper. Tu peux modifier cela avec `--max-tokens`, ou utiliser `--force`.

## Ce qui est exclu

- Les trucs inutiles : `node_modules`, `.git`, `.next`, `dist`, `build`, `assets`, virtualenvs, caches, lockfiles, fichiers minifiés, source maps.
- Les fichiers binaires et tout ce qui dépasse 256 Ko.
- Les secrets : `.env`, `*.pem`, `id_rsa` et similaires par leur nom. Les fichiers dont le contenu ressemble à une clé AWS, GitHub, OpenAI, Stripe, Slack ou Google, ou à une clé privée, sont aussi exclus et signalés dans la sortie.

La détection de secrets repère les cas évidents et rien de plus. Relis ce que tu colles si le projet est sensible.

Tout ce qui se trouve dans la liste par défaut peut être réactivé via un fichier `.ignore` dans ton projet :

```gitignore
!assets/
```

## Options

| Option | Ce qu'elle fait |
| --- | --- |
| `-o FILE` | Fichier de sortie, par défaut `context_prompt.md` |
| `-x GLOB` | Exclure d'autres chemins, syntaxe gitignore, répétable |
| `--only GLOB` | Ne garder que les chemins correspondants, répétable |
| `--max-tokens N` | Ne pas copier au-delà de N tokens, `0` désactive la limite |
| `--max-size KB` | Ignorer les fichiers plus gros que ça, par défaut 256 |
| `--top N` | Nombre de fichiers lourds à lister, par défaut 5 |
| `--dry-run` | Afficher les chiffres, sans rien écrire ni copier |
| `--no-copy` | Écrire le fichier, sans toucher au presse-papiers |
| `--force` | Copier même au-dessus de la limite |
| `--no-defaults` | Ignorer la liste d'exclusions intégrée |
| `--allow-secrets` | Conserver les fichiers signalés comme contenant des secrets |
| `--lang CODE` | Messages en `en`, `pt`, `es`, `de`, `fr` ou `ja`, par défaut selon ton système |

Exemples :

```bash
python ctxpack.py --only src/ --only README.md
python ctxpack.py -x "*.test.ts" -x docs/
python ctxpack.py --dry-run
```

## Tokens

Le décompte est une estimation, fiable à environ 20 % sur du code Python et JS/TS. C'est suffisant pour savoir si ce que tu colles rentre dans le contexte, pas pour facturer qui que ce soit. Si `tiktoken` est installé, il est utilisé à la place. Aucun des deux ne correspond au tokenizer exact de chaque modèle.

## Presse-papiers

Windows utilise `clip`, macOS utilise `pbcopy`, Linux utilise `wl-copy`, `xclip` ou `xsel`. Termux et WSL fonctionnent aussi. Si aucun outil n'est disponible, le fichier est quand même écrit.

## Tests

```bash
python -m unittest discover -s tests
```

## Soutien

Libre à utiliser et à modifier. Si ça t'a fait gagner du temps, [tu peux participer ici](https://buymeacoffee.com/samaritansli).

- Lightning: `inborngrease4665@cake.cash`
- Bitcoin: `bc1qm2j0l9zy7npnhfctf80p3ukuj2ksffwlvum3c5`

## Licence

Domaine public, voir [LICENSE](../LICENSE).
