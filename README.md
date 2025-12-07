# Kwiga BDD Framework (Python + Selenium)

Simple educational BDD-style test framework for the Kwiga website.

## Structure

- `framework/` – core framework code
- `tests/features/` – BDD scenarios in custom DSL (`*.kwiga`)
- `requirements.txt` – Python dependencies

## Quick start

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run all feature files in tests/features
python -m framework.core.runner
```

Note: by default, `base_url` is set to `https://kwiga.com/` in `framework/core/config.py`.
Change it if your test environment is different.
