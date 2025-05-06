# create-tg-bot

[![PyPI version](https://img.shields.io/pypi/v/create-tg-bot.svg)](https://pypi.org/project/create-tg-bot/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI/CD](https://github.com/emilastanov/create-tg-bot/actions/workflows/publish.yml/badge.svg)](https://github.com/emilastanov/create-tg-bot/actions)

📖 Данный README доступен также на [🇬🇧 English](README.md)

`create-tg-bot` — это CLI-инструмент для быстрого создания архитектурно чистых Telegram-ботов на Python.

---

## 🚀 Возможности

- Быстрое создание структуры проекта
- Поддержка SQLite и PostgreSQL
- Управление переменными окружения и `.env` файлами
- Генерация Dockerfile и GitHub Actions workflows
- Автоматическая миграция базы данных с Alembic
- Поддержка токенов для продакшена и разработки
- Готов к публикации на PyPI
- Встроенные тесты через `pytest`

---

## 📦 Установка

```bash
pip install create-tg-bot
```

---

## 🛠️ Использование

```bash
create-tg-bot <project_name>
```

### Пример

```bash
create-tg-bot my_bot_project
```

Будет создана структура проекта, настроено окружение, установлены зависимости, применены миграции и инициализирован Git-репозиторий.

---

## 📁 Структура проекта

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

## 🧪 Примечания для разработки

- Используется `setuptools_scm` для автоматического управления версиями
- Все шаблоны находятся в `create_tg_bot/templates`
- CLI-интерфейс построен на базе `Click`

---

## 📄 Лицензия

Проект распространяется под лицензией [MIT License](LICENSE).

---

## 👤 Автор

[Emil Astanov](mailto:emila1998@yandex.ru)
