# create-tg-bot

[![PyPI version](https://img.shields.io/pypi/v/create-tg-bot.svg)](https://pypi.org/project/create-tg-bot/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI/CD](https://github.com/emilastanov/create-tg-bot/actions/workflows/publish.yml/badge.svg)](https://github.com/emilastanov/create-tg-bot/actions)

📖 This README is also available in [🇷🇺 Russian](README.ru.md)

`create-tg-bot` is a CLI tool for rapidly creating clean-architecture Telegram bots using Python.

---

## 🚀 Features

- Quickly scaffold a new project structure
- SQLite and PostgreSQL support
- Environment variable and `.env` management
- Generates Dockerfile and GitHub Actions workflows
- Automatic database migrations (Alembic)
- Optional development and production bot tokens
- Ready for PyPI publishing
- Includes testing with `pytest`

---

## 📦 Installation

```bash
pip install create-tg-bot
```

---

## 🛠️ Usage

```bash
create-tg-bot <project_name>
```

### Example

```bash
create-tg-bot my_bot_project
```

This creates a fully-structured bot project and initializes it with environment setup, dependency installation, migrations, and Git repository initialization.

---

## 📁 Project Structure

```
project/
├── .env
├── alembic.ini
├── config.py
├── main.py
├── models/
├── services/
├── crud/
├── migrations/
├── templates/
├── requirements.txt
└── .github/workflows/
```

---

## 🧪 Development Notes

- Uses `setuptools_scm` for automatic versioning
- Templates live in `create_tg_bot/templates`
- CLI interface powered by `Click`

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 👤 Author

[Emil Astanov](mailto:emila1998@yandex.ru)
