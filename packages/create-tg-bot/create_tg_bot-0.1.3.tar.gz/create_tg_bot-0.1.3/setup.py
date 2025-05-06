from setuptools import setup, find_packages

setup(
    name="create-tg-bot",
    use_scm_version=True,
    setup_requires=[
        "setuptools-scm"
    ],
    description = "A modular, CLI-first Python boilerplate for building Telegram bots. Fast setup, clean architecture, and open-source ready.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Emil Astanov",
    author_email="emila1998@yandex.ru",
    url="https://github.com/emilastanov/create-tg-bot",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "click",
        "jinja2"
    ],
    entry_points={
        "console_scripts": [
            "create-tg-bot=create_tg_bot.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Topic :: Software Development :: Build Tools",
    ],
    keywords=[
        "telegram", "bot", "telegram-bot", "cli", "command-line",
        "python", "boilerplate", "template", "starter-kit",
        "open-source", "asyncio", "telegram-cli", "modular",
        "framework", "python3", "telegram-api", "telegram-bot-api"
    ]
)