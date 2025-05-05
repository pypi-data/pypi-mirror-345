![PyPI](https://img.shields.io/pypi/v/charfinder)
![Python](https://img.shields.io/pypi/pyversions/charfinder)
![License](https://img.shields.io/github/license/berserkhmdvhb/charfinder)
![Tests](https://github.com/berserkhmdvhb/charfinder/actions/workflows/tests.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/berserkhmdvhb/charfinder/badge.svg?branch=main)](https://coveralls.io/github/berserkhmdvhb/charfinder?branch=main)


# 🔎 charfinder

**charfinder** is a terminal and Python-based tool to search Unicode characters by name—strictly or fuzzily—with normalization, caching, logging, and colorful output.  

Ever tried to find an emoji using name of it, or more technically, the Unicode character for "shrug" or "grinning face"? `charfinder` helps you locate them effortlessly from the command line or programmatically.

---

## ✨ Features

- 🔍 Search Unicode characters by name (strict or fuzzy match)
- ⚡ Multiple fuzzy matching algorithms:
  - `difflib.SequenceMatcher` (standard lib)
  - [`rapidfuzz`](https://github.com/maxbachmann/RapidFuzz)
  - [`python-Levenshtein`](https://github.com/ztane/python-Levenshtein)
- 📚 Unicode NFKD normalization for accurate comparison
- 💾 Local cache to speed up repeated lookups
- 🎨 CLI color support via `colorama`
- 🧪 Full test suite: unit tests + CLI tests via `pytest`
- 🐍 Usable both as CLI and as Python library
- 📦 Modern `pyproject.toml`-based packaging (PEP 621)

---

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install charfinder
```

### From GitHub (Development Version)

```bash
pip install git+https://github.com/berserkhmdvhb/charfinder.git
```

---

## 🚀 Usage

### 🖥 CLI Mode

```bash
charfinder -q heart
```

Example:

```bash
$ charfinder -q snowman
☃  U+2603  SNOWMAN
```

You can also run directly from source:

```bash
python -m charfinder -q smile
```

#### Common CLI Options

| Option            | Description                                                 |
|-------------------|-------------------------------------------------------------|
| `--fuzzy`         | Enable fuzzy match fallback                                 |
| `--threshold`     | Fuzzy match threshold (0.0–1.0, default: `0.7`)             |
| `--fuzzy-algo`    | `sequencematcher`, `rapidfuzz`, or `levenshtein`           |
| `--match-mode`    | `single` or `hybrid` (aggregated fuzzy scoring)            |
| `--quiet`         | Suppress logging                                           |
| `--color`         | `auto`, `never`, or `always`                               |

Example:

```bash
charfinder -q grnning --fuzzy --threshold 0.6 --fuzzy-algo rapidfuzz
```

### 🐍 Python Library Mode

```python
from charfinder.core import find_chars

for line in find_chars("snowman"):
    print(line)

# Enable fuzzy search with threshold and algorithm
find_chars("snwmn", fuzzy=True, threshold=0.6, algo="rapidfuzz")
```

---

## 📂 Project Structure

```
charfinder/
├── src/charfinder/
│   ├── __init__.py
│   ├── __main__.py         # Entry point
│   ├── cli.py              # CLI interface
│   ├── core.py             # Core logic: search, normalize, cache
│   └── fuzzymatchlib.py    # Multiple fuzzy matching algorithms
├── tests/
│   ├── test_cli.py         # CLI subprocess tests
│   ├── test_lib.py         # Library function tests
│   └── manual/demo.ipynb   # Interactive exploration notebook
├── Makefile
├── pyproject.toml
├── unicode_name_cache.json  # Auto-generated at runtime
└── README.md
```

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests -v
```

Or use the Makefile (if available):

```bash
make test
```

### Manual Exploration

Use [`demo.ipynb`](https://github.com/berserkhmdvhb/charfinder/blob/main/tests/manual/demo.ipynb) to explore CLI and core functionality interactively.

---

## 🛠 For Developers

To contribute or test locally:

```bash
git clone https://github.com/berserkhmdvhb/charfinder.git
cd charfinder
make install
```

If `make` is not available (e.g. on Windows), run manually:

```bash
python -m venv .venv
. .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -e .[dev]
```

### Makefile Commands

| Command         | Description                      |
|----------------|----------------------------------|
| `make install` | Install with dev dependencies    |
| `make test`    | Run all tests                    |
| `make build`   | Build distribution               |
| `make publish-test` | Upload to TestPyPI         |
| `make publish` | Upload to PyPI (requires config) |

---

## 📦 Dependencies

- [`colorama`](https://pypi.org/project/colorama/)
- [`argcomplete`](https://pypi.org/project/argcomplete/)
- [`rapidfuzz`](https://pypi.org/project/rapidfuzz/)
- [`python-Levenshtein`](https://pypi.org/project/python-Levenshtein/)
- `pytest` (for development)

Install all with:

```bash
pip install -e .[dev]
```

---

## 📌 Roadmap

| Feature                                         | Status |
|------------------------------------------------|--------|
| Strict Unicode name matching                   | ✅     |
| Unicode normalization (NFKD)                   | ✅     |
| Caching for fast repeated lookup               | ✅     |
| Fuzzy search: difflib / rapidfuzz / Levenshtein| ✅     |
| CLI: quiet mode, color modes                   | ✅     |
| Type hints, logging, clean code                | ✅     |
| Unit tests + CLI test coverage                 | ✅     |
| `charfinder` CLI entry point                   | ✅     |
| Fuzzy score shown in results                   | ✅     |
| `demo.ipynb` interactive interface             | ✅     |
| Hybrid fuzzy matching strategy                 | ✅     |
| Docker container support                       | 🔜     |
| JSON output format (for scripting)             | 🔜     |

---

## 🧾 License

MIT License © 2025 [Hamed V / GitHub Handle]
