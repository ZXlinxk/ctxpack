# ctxpack

[English](../README.md) | [Português](README.pt-BR.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [日本語](README.ja.md)

Un solo archivo Python que convierte un proyecto en un archivo markdown para pegar en Claude, Gemini o ChatGPT. Sin instalaciones ni dependencias, solo Python 3.8 o superior.

```
$ python ctxpack.py
12 archivos, 41.3 KB, ~10,870 tokens
archivos más pesados:
      4,837  src/parser.py
      2,104  src/cli.py
escrito en context_prompt.md
copiado al portapapeles
```

## Descarga

```bash
curl -O https://raw.githubusercontent.com/ZXlinxk/ctxpack/main/ctxpack.py
```

Ejecútalo desde tu proyecto o pasa la carpeta como argumento:

```bash
python ctxpack.py ~/code/my-app
```

## Qué hace

Recorre la carpeta respetando `.gitignore` y `.ignore`, incluyendo subcarpetas. Escribe `context_prompt.md` con el árbol de directorios y cada archivo dentro de un bloque de código. Muestra un estimado de tokens junto a los archivos más pesados y copia el resultado al portapapeles.

Si pasa de 180.000 tokens escribe el archivo pero no lo copia, para que veas qué recortar primero. Puedes cambiar el tope con `--max-tokens` o usar `--force`.

## Qué deja fuera

- Basura: `node_modules`, `.git`, `.next`, `dist`, `build`, `assets`, entornos virtuales, cachés, lockfiles, archivos minificados y mapas de código.
- Archivos binarios y cualquier archivo que supere los 256 KB.
- Secretos: `.env`, `*.pem`, `id_rsa` y similares por nombre. Archivos con patrones que parecen claves de AWS, GitHub, OpenAI, Stripe, Slack, Google o claves privadas también se omiten y se avisan en la salida.

La detección de secretos cubre lo evidente. Revisa lo que pegas si el proyecto tiene datos sensibles.

Cualquier regla de la lista predeterminada se puede desactivar desde un archivo `.ignore` en tu proyecto:

```gitignore
!assets/
```

## Opciones

| Opción | Qué hace |
| --- | --- |
| `-o FILE` | Archivo de salida, por defecto `context_prompt.md` |
| `-x GLOB` | Omite más rutas, sintaxis gitignore, repetible |
| `--only GLOB` | Conserva solo rutas que coincidan, repetible |
| `--max-tokens N` | No copia si supera N tokens, `0` desactiva el límite |
| `--max-size KB` | Salta archivos mayores a esto, por defecto 256 |
| `--top N` | Cuántos archivos pesados listar, por defecto 5 |
| `--dry-run` | Muestra los números sin escribir ni copiar nada |
| `--no-copy` | Escribe el archivo sin tocar el portapapeles |
| `--force` | Copia incluso si supera el límite |
| `--no-defaults` | Descarta la lista de exclusiones por defecto |
| `--allow-secrets` | Conserva archivos marcados con secretos |
| `--lang CODE` | Mensajes en `en`, `pt`, `es`, `de`, `fr` o `ja`, por defecto según el sistema |

Ejemplos:

```bash
python ctxpack.py --only src/ --only README.md
python ctxpack.py -x "*.test.ts" -x docs/
python ctxpack.py --dry-run
```

## Tokens

El conteo es un estimado con un margen cercano al 20% en código Python y JS/TS. Sirve para saber si cabe en el contexto, no para facturación. Si tienes `tiktoken` instalado lo usará en su lugar. Ninguno de los dos coincide con el tokenizer exacto de cada modelo.

## Portapapeles

Windows usa `clip`, macOS usa `pbcopy`, Linux usa `wl-copy`, `xclip` o `xsel`. Termux y WSL también funcionan. Si no hay herramienta disponible, el archivo se genera de todos modos.

## Pruebas

```bash
python -m unittest discover -s tests
```

## Apoyo

Libre para usar y modificar. Si te ahorró tiempo, [puedes colaborar aquí](https://buymeacoffee.com/samaritansli).

- Lightning: `inborngrease4665@cake.cash`
- Bitcoin: `bc1qm2j0l9zy7npnhfctf80p3ukuj2ksffwlvum3c5`

## Licencia

Dominio público, consulta [LICENSE](../LICENSE).
