# PROJECT_NAME

https://pypi.org/project/app-toolkit-package/

1. bages here
2. short description here

<br>


## Оглавление
- [Технологии](#технологии)
- [Описание работы](#описание-работы)
- [Установка приложения](#установка-приложения)
- [Виртуальное окружение](#виртуальное-окружение)
- [Разработка в Docker](#разработка-в-Docker)
- [Удаление приложения](#удаление-приложения)
- [Автор](#автор)

<br>


## Технологии
<details><summary>Подробнее</summary><br>

[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue?logo=python)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3-blue?logo=aiogram)](https://aiogram.dev/)
[![FastAPI](https://img.shields.io/badge/-FastAPI-464646?logo=fastapi)](https://fastapi.tiangolo.com/)
[![FastAPI_Users](https://img.shields.io/badge/-FastAPI--Users-464646?logo=fastapi-users)](https://fastapi-users.github.io/fastapi-users/)
[![Pydantic](https://img.shields.io/badge/pydantic-2-blue?logo=Pydantic)](https://docs.pydantic.dev/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?logo=PostgreSQL)](https://www.postgresql.org/)
[![asyncpg](https://img.shields.io/badge/-asyncpg-464646?logo=PostgreSQL)](https://pypi.org/project/asyncpg/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2-blue?logo=sqlalchemy)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/-Alembic-464646?logo=alembic)](https://alembic.sqlalchemy.org/en/latest/)
[![Uvicorn](https://img.shields.io/badge/-Uvicorn-464646?logo=Uvicorn)](https://www.uvicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?logo=docker)](https://www.docker.com/)
[![docker_compose](https://img.shields.io/badge/-Docker%20Compose-464646?logo=docker)](https://docs.docker.com/compose/)
[![docker_hub](https://img.shields.io/badge/-Docker_Hub-464646?logo=docker)](https://hub.docker.com/)
[![GitHub_Actions](https://img.shields.io/badge/-GitHub_Actions-464646?logo=GitHub)](https://docs.github.com/en/actions)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?logo=NGINX)](https://nginx.org/en/docs/)
[![SWAG](https://img.shields.io/badge/-SWAG-464646?logo=swag)](https://docs.linuxserver.io/general/swag)
[![httpx](https://img.shields.io/badge/-httpx-464646?logo=httpx)](https://www.python-httpx.org/)
[![Pytest](https://img.shields.io/badge/-Pytest-464646?logo=Pytest)](https://docs.pytest.org/en/latest/)
[![Pytest-asyncio](https://img.shields.io/badge/-Pytest--asyncio-464646?logo=Pytest-asyncio)](https://pypi.org/project/pytest-asyncio/)
[![pytest-cov](https://img.shields.io/badge/-pytest--cov-464646?logo=codecov)](https://pytest-cov.readthedocs.io/en/latest/)
[![deepdiff](https://img.shields.io/badge/-deepdiff-464646?logo=deepdiff)](https://zepworks.com/deepdiff/6.3.1/diff.html)
[![pre-commit](https://img.shields.io/badge/-pre--commit-464646?logo=pre-commit)](https://pre-commit.com/)

[⬆️Оглавление](#оглавление)

---

</details>
<br>


## Описание работы:


</details>


[⬆️Оглавление](#оглавление)

<br>


## Установка приложения:
Клонируйте репозиторий с GitHub и введите данные для переменных окружения (значения даны для примера, но их можно оставить):

```bash
git clone https://github.com/<proj_name>.git
cd <proj_name>
cp .env.example .env
nano .env
```
Все последующие команды производятся из корневой директории проекта.

[⬆️Оглавление](#оглавление)

<br>


## Виртуальное окружение:
<details><summary>Среда разработки</summary><br>

1. Создайте и активируйте виртуальное окружение:
   * Если у вас Linux/macOS:
   ```bash
    python -m venv venv && source venv/bin/activate
   ```
   * Если у вас Windows:
   ```bash
    python -m venv venv && source venv/Scripts/activate
   ```

```bash
where python
```

<br>

2. Установите в виртуальное окружение необходимые зависимости:
```bash
python -m pip install --upgrade pip && pip install pre-commit && \
pre-commit install && pre-commit autoupdate && pre-commit run --all-files
```

```bash
python.exe -m pip install --upgrade pip
python -m pip install -e .
```
<br>


## Разработка в Docker:

1. Запуск тестов - после прохождения тестов в консоль будет выведен отчет `pytest` и `coverage`(**xx%**):
```bash
docker compose -f docker/test.docker-compose.yaml --env-file .env up --build --abort-on-container-exit && \
docker compose -f docker/test.docker-compose.yaml --env-file .env down --volumes && docker system prune -f
```
<br>


## Удаление приложения:
```bash
cd .. && rm -fr <proj_name>
```

[⬆️Оглавление](#оглавление)

<br>


## Автор:
[Aleksei Proskuriakov](https://github.com/alexpro2022)

[⬆️В начало](#project_name)
