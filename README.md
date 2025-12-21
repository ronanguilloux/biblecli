# Bible CLI Tool

A command-line interface for reading the Bible in Greek (N1904), English, and French (TOB).

## Post-installation

Add `biblecli` to your `$PATH` in your shell config file (e.g. `.zshrc`, `.bashrc`, `.bash_profile`):
```sh
export PATH=$PATH:[YOUR-PATH-TO]/biblecli/bin
```

## Usage

You can use the `biblecli` script to execute commands. It will automatically set up the environment if needed.

### Basic Commands

Display a verse (Greek and French are default):
```sh
biblecli "Jn 1:1"
```

Display a verse range:
```sh
biblecli "Mt 5:1-10"
```

Display an entire chapter:
```sh
biblecli "Mt 5"
```

List all available books:
```sh
biblecli list books
```

### Translations

Use the `-t` or `--tr` option to specify translations. Supported: `en` (English), `fr` (French TOB), `gr` (Greek N1904).

Show only English:
```sh
biblecli "Jn 3:16" -t en
```

Show both English and French:
```sh
biblecli "Jn 3:16" -t en fr
```

### Cross-references

The tool supports verse-level cross-references from OpenBible data.

Show cross-reference list:
```sh
biblecli "Jn 1:1" -c
```

Show cross-references with full verse text:
```sh
biblecli "Jn 1:1" -f
```

Filter cross-references by source (e.g., only TOB notes):
```sh
biblecli "Mk 1:1" -f -s tob
```

### Shortcuts

For convenience, you can use the `tob` command to quickly access TOB notes. It is equivalent to `biblecli ... -f -s tob`.

```sh
tob "Mk 1:1"
```

### Abbreviations

Many common abbreviations are supported in both English and French:
- `Gn`, `Gen`, `Genèse`, `Genesis`
- `Mt`, `Matt`, `Matthieu`, `Matthew`
- `Jn`, `Jean`, `John`
- etc.

## Manual Setup

If you prefer to run `src/main.py` directly, you must install the dependencies:

```bash
pip install -r requirements.txt
```

Or use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 src/main.py "Jn 3:16"
```
