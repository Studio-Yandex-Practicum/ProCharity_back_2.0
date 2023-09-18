# ProCharity_back_2.0

<details>
  <summary>Оглавление</summary>
  <ol>
    <li>
      <a href="#описание">Описание</a>
      <ul>
        <li><a href="#технологии">Технологии</a></li>
      </ul>
    </li>
    <li>
    <a href="#запуск-бота-локально">Запуск бота локально</a>
    </li>
    <li>
      <a href="#для-разработки">Для разработки</a>
      <ul>
        <li><a href="#установка-и-настройка-приложения">Установка и настройка приложения</a></li>
        <li><a href="#запуск">Запуск</a></li>
      </ul>
    </li>
    <li><a href="#использование">Использование</a></li>
    <li>
      <a href="#полезная-информация">Полезная информация</a>
      <ul>
        <li><a href="#регистрация-бота-telegram">Регистрация бота Telegram</a></li>
        <li><a href="#режимы-работы-бота">Режимы работы бота</a></li>
        <li><a href="#работа-с-базой-данных">Работа с базой данных</a></li>
        <li><a href="#работа-с-poetry">Работа с Poetry</a></li>
        <li><a href="#использование-ngrok">Использование Ngrok</a></li>
      </ul>
    </li>
  </ol>
</details>

### Описание

Создание чат-бота в Telegram для платформы интеллектуального волонтерства
ProCharity (НКО Фонд Друзья).

Сайт [https://procharity.ru/](https://procharity.ru/)

Чат-бот @ProCharity_bot

Платформа представляет собой агрегатор волонтерских заданий от различных
благотворительных проектов - любой желающий согласно своим желаниям и
умениям может откликаться на конкретные предложения благотворительных
проектов о волонтерской помощи, в свою очередь благотворительный проект/фонд
выбирает из всех откликов подходящих кандидатов.

Чат-бот реализует функционал волонтерской платформы в приложении Telegram -
с помощью JSON рассылает подписчикам новые появляющиеся задания от фондов.

### Технологии

[![FastAPI][FastAPI-badge]][FastAPI-url]
[![Python-telegram-bot][Python-telegram-bot-badge]][Python-telegram-bot-url]
[![Postgres][Postgres-badge]][Postgres-url]
[![Nginx][Nginx-badge]][Nginx-url]

## Запуск бота локально

1. Создайте и заполните файл `.env`:

    ```dotenv
    # Переменные приложения
    BOT_TOKEN=<your_token_from_botfather>  # Токен аутентификации бота
    ```
    > **Note**
    > [Полный пример переменных окружения](env.example).

    > **Note**
    > Для получения токена аутентификации бота обратитесь к
    разделу [Регистрация бота Telegram](#регистрация-бота-telegram).


2. Собрать и запустить контейнеры из файла infra/docker-compose.local.yml.

    ```shell
    docker compose -f infra/docker-compose.local.yml up
    ```
    Эта команда создаст и запустит все необходимые контейнеры, включая базу данных и бэкенд.

3. После успешного запуска контейнеров, выполните следующую команду, которая войдет в контейнер, выполнит миграции и наполнит тестовую базу данных:

    ```shell
    docker exec -it procharity_bot_backend sh -c "alembic upgrade head && python3 fill_db.py"
    ```

## Для разработки

### Установка и настройка приложения

1. Клонировать репозиторий.

    ```shell
    git clone https://github.com/Studio-Yandex-Practicum/ProCharity_back_2.0.git
    cd ProCharity_back_2.0
    ```

2. Установить зависимости и активировать виртуальное окружение.

    ```shell
    poetry env use python3.11
    poetry install
    poetry shell
    ```

    > **Note**
   > [Документация по установке Poetry](https://python-poetry.org/docs/#installation)
3. Настроить pre-commit.
В режиме ```poetry shell```
   ```
   pre-commit install
   ```
   > **Note**
   > Перед каждым коммитом будет запущен линтер и форматтер,
   который автоматически отформатирует код согласно принятому в команде codestyle.

4. Создайте и заполните файл `.env`:

    ```dotenv
    BOT_TOKEN=  # Токен аутентификации бота
    # Переменные базы данных
    POSTGRES_DB=procharity_back_db_local  # Название базы данных
    POSTGRES_USER=postgres  # Логин для подключения к базе данных
    POSTGRES_PASSWORD=postgres  # Пароль для подключения к базе данных
    DB_HOST=localhost  # Название сервиса (контейнера)
    DB_PORT=5432  # Порт для подключения к базе данных
    ```

    > **Note**
    > [Полный пример переменных окружения](env.example).

    > **Note**
    > Для получения токена аутентификации бота обратитесь к
    разделу [Регистрация бота Telegram](#регистрация-бота-telegram).

### Запуск

1. Запустить Docker с БД.

    ```shell
    sudo docker compose -f infra/docker-pg.yml up -d
    ````

2. Применить миграции базы данных.

    ```shell
    alembic upgrade head

3. Выполнить скрипт наполнения тестовой базы.

    ```shell
    python3 fill_db.py
    ```

4. Запустить сервер приложения.

    ```shell
    uvicorn src:app --reload
    ```

## Использование

После выполнения инструкций, описанных в разделе "[Для разработки](#для-разработки)",

будет запущен FastAPI-сервер по адресу http://localhost:8000.

Также по адресу http://localhost:8000/docs доступна полная документация API.

## Полезная информация

Данный раздел содержит информацию, которая может быть полезна для разработчиков.
Настоятельно рекомендуем каждому прочитать его хотя бы один раз.

### Регистрация бота Telegram

1. Найдите в Telegram бота [@BotFather](https://t.me/botfather) и откройте с ним чат.

2. Напишите ему `/newbot`.

3. Придумайте и напишите название бота. Оно будет отображаться в контактах и
чатах. Например: `My Dev Bot`.

4. Придумайте и напишите юзернейм. Он используется для упоминания бота и в
ссылках. Юзернейм должен быть на латинице и обязательно заканчиваться на
«bot». Например: `my_dev_bot`.

5. Готово. [@BotFather](https://t.me/botfather) пришлет токен бота — его нужно
скопировать в переменную окружения `BOT_TOKEN` (см. в разделе "[Установка и Запуск](#установка-и-запуск)").

    > **Note**
    > [Документация о боте BotFather](https://core.telegram.org/bots/features#botfather)

<details>
  <summary><h3>Режимы работы бота</h3></summary>

1. Запуск без API приложения

    Выполнить скрипт запуска.

    ```shell
    python src/run.py
    ```

    > **Warning**:
         Возможно только в режиме [polling](#polling).

2. Polling

    Задать значение переменной окружения (`.env`).

    ```dotenv
    BOT_WEBHOOK_MODE=False
    ```

3. Webhook

    Задать значение переменным окружения (`.env`).

    ``` dotenv
    BOT_WEBHOOK_MODE=True
    APPLICATION_URL=http://example.com  # Пример
    ```

    > **Note**
    > [Подробнее о webhooks](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks)

    > **Note**
    > Для теста через HTTPS можно использовать [Ngrok](https://ngrok.com/)
    > (см. раздел "[Использование Ngrok](#использование-ngrok)").
</details>

<details>
  <summary><h3>Работа с базой данных</h3></summary>

#### Создание миграций

1. Применить существующие миграции:

    ```shell
    alembic upgrade head
    ```

2. Создать новую миграцию:

    ```shell
    alembic revision --autogenerate -m "<Название миграции>"
    ```

    В название миграции указывается
    для какого поля или модели внесены изменения, например:

    * add_shift_model
    * shift_add_field_title
    * shift_remove_field_title

3. Повторить пункт 1, для применения созданной миграции.

#### Откат миграций

1. Откатить последнюю миграцию:

    ```shell
    alembic downgrade -1
    ```
</details>

<details>
  <summary><h3>Работа с Poetry</h3></summary>

В этом разделе представлены наиболее часто используемые команды.

Подробнее: https://python-poetry.org/docs/cli/

1. Настройка окружения проекта
Установку необходимо выполнять через curl, как в документации.

    ```shell
    poetry env use python3.11; poetry install
    ```

2. Активировать виртуальное окружение

    ```shell
    poetry shell
    ```

3. Добавить зависимость

    ```shell
    poetry add <package_name>
    ```

    > **Note**
    > Использование флага `--dev (-D)` позволяет установить зависимость,
    необходимую только для разработки.
    Это полезно для разделения develop и prod зависимостей.

#### Запустить скрипт без активации виртуального окружения

```shell
poetry run <script_name>.py
```
</details>

<details>
  <summary><h3>Использование Ngrok</h3></summary>

Этот раздел будет полезен, если у вас нет доменного имени с установленным
SSL-сертификатом.

[Ngrok](https://ngrok.com/) — это инструмент, который позволяет создавать временный общедоступный
адрес (туннель) для вашего локального сервера, находящимся за NAT или
брандмауэром.

Подробнее: https://ngrok.com/

1. Установить, следуя официальным инструкциям.

    https://ngrok.com/download

2. Запустить туннель.

    ```shell
    ngrok http 80
    ```
    > **Note**
        > Если задать переменную в следующем пункте 3, то пункт два можно пропустить.

3. Задать значение переменной окружения (.env).

    ```dotenv
    APPLICATION_URL=https://1234-56-78-9.eu.ngrok.io  # Пример
    USE_NGROK=True
    ```
</details>



<!-- MARKDOWN LINKS & BADGES -->

[FastAPI-url]: https://fastapi.tiangolo.com/
[FastAPI-badge]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi

[Python-telegram-bot-url]: https://github.com/python-telegram-bot/python-telegram-bot
[Python-telegram-bot-badge]: https://img.shields.io/badge/python--telegram--bot-2CA5E0?style=for-the-badge

[Postgres-url]: https://www.postgresql.org/
[Postgres-badge]: https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white

[Nginx-url]: https://nginx.org
[Nginx-badge]: https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white~~
