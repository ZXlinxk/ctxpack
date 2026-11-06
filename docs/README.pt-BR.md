# ctxpack

[English](../README.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [日本語](README.ja.md)

Um único arquivo Python que transforma um projeto em um arquivo markdown para colar no Claude, Gemini ou ChatGPT. Nada para instalar, sem dependências, Python 3.8 ou superior.

```
$ python ctxpack.py
12 arquivos, 41.3 KB, ~10,870 tokens
arquivos mais pesados:
      4,837  src/parser.py
      2,104  src/cli.py
gravado em context_prompt.md
copiado para a área de transferência
```

## Como obter

```bash
curl -O https://raw.githubusercontent.com/ZXlinxk/ctxpack/main/ctxpack.py
```

Rode dentro do projeto ou passe a pasta:

```bash
python ctxpack.py ~/code/my-app
```

## O que ele faz

Percorre a pasta respeitando `.gitignore` e `.ignore`, inclusive em subpastas. Salva `context_prompt.md` com a árvore de diretórios e cada arquivo em um bloco de código. Mostra uma estimativa de tokens e os arquivos mais pesados, copiando o resultado para a área de transferência.

Se passar de 180.000 tokens, grava o arquivo mas não copia, para você ver antes o que cortar. Mude isso com `--max-tokens` ou use `--force`.

## O que fica de fora

- Lixo: `node_modules`, `.git`, `.next`, `dist`, `build`, `assets`, virtualenvs, caches, lockfiles, arquivos minificados e source maps.
- Binários e arquivos com mais de 256 KB.
- Segredos: `.env`, `*.pem`, `id_rsa` e similares pelo nome. Arquivos cujo conteúdo parece uma chave da AWS, GitHub, OpenAI, Stripe, Slack, Google ou chave privada também são deixados de fora e avisados no terminal.

A detecção de segredos pega os casos óbvios. Revise o que for colar se o projeto for sensível.

Qualquer item da lista padrão pode ser reativado criando um `.ignore` no seu projeto:

```gitignore
!assets/
```

## Opções

| Opção | O que faz |
| --- | --- |
| `-o FILE` | Arquivo de saída, padrão `context_prompt.md` |
| `-x GLOB` | Ignora outros caminhos, sintaxe de gitignore, repetível |
| `--only GLOB` | Mantém apenas caminhos compatíveis, repetível |
| `--max-tokens N` | Não copia acima de N tokens, `0` desativa o limite |
| `--max-size KB` | Pula arquivos maiores que isso, padrão 256 |
| `--top N` | Quantos arquivos pesados listar, padrão 5 |
| `--dry-run` | Mostra os números sem gravar nem copiar nada |
| `--no-copy` | Grava o arquivo sem mexer na área de transferência |
| `--force` | Copia mesmo acima do limite |
| `--no-defaults` | Desativa a lista padrão de bloqueio |
| `--allow-secrets` | Mantém arquivos sinalizados com segredos |
| `--lang CODE` | Mensagens em `en`, `pt`, `es`, `de`, `fr` ou `ja`, padrão vem do sistema |

Exemplos:

```bash
python ctxpack.py --only src/ --only README.md
python ctxpack.py -x "*.test.ts" -x docs/
python ctxpack.py --dry-run
```

## Tokens

A contagem é uma estimativa, com precisão de cerca de 20% para Python e JS/TS. É suficiente para saber se cabe na janela de contexto, não para tarifar ninguém. Se o `tiktoken` estiver instalado, ele é usado no lugar. Nenhum dos dois é idêntico ao tokenizer de todos os modelos.

## Área de transferência

No Windows usa `clip`, no macOS `pbcopy`, no Linux `wl-copy`, `xclip` ou `xsel`. Termux e WSL também funcionam. Se nenhuma ferramenta estiver disponível, o arquivo ainda é gerado normalmente.

## Testes

```bash
python -m unittest discover -s tests
```

## Apoie

Livre para usar e modificar. Se economizou seu tempo, [você pode apoiar aqui](https://buymeacoffee.com/samaritansli).

- Lightning: `inborngrease4665@cake.cash`
- Bitcoin: `bc1qm2j0l9zy7npnhfctf80p3ukuj2ksffwlvum3c5`

## Licença

Domínio público, veja [LICENSE](../LICENSE).
