# logthis

> logthis is a simple yet powerful Python logging utility for cleaner, more readable, and color-coded output.  
> Designed for developers who want better logs without the complexity of the `logging` module.

![PyPI - Version](https://img.shields.io/pypi/v/logthis?style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/laxyny/logthis?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/laxyny/logthis?style=for-the-badge)
![GitHub pull requests](https://img.shields.io/github/issues-pr/laxyny/logthis?style=for-the-badge)
![GitHub license](https://img.shields.io/github/license/laxyny/logthis?style=for-the-badge)

---

## About

logthis is a minimal and universal logging tool that:
- Replaces boring `print()` statements
- Makes logs colorful, clear, and timestamped
- Works out of the box for any Python project

**Why the name?**  
Because sometimes, you just want to... `logthis()`.

---

## Main Features

- Timestamped logs
- Color-coded log levels (INFO, WARN, ERROR)
- Easy to use: `log_info("Hello world")`
- CLI preview: `logthis --test`
- Lightweight, no external dependencies

---

## Installation

Install with pip:
```bash
pip install logthis
```	

---

## Usage

Import and use:
```python
from logthis import log_info, log_warn, log_error

log_info("All systems go.")
log_warn("Caution: approaching limits.")
log_error("Something broke.")
```

Exemple output:
```bash
[2025-05-04 14:03:25] [INFO] All systems go.
[2025-05-04 14:03:26] [WARN] Caution: approaching limits.
[2025-05-04 14:03:27] [ERROR] Something broke.
```

### CLI Mode

You can test the output in terminal:

```bash
logthis --test
```

---

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Developed and maintained by [Kevin Gregoire](https://github.com/laxyny).