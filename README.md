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
      <a href="#установка-и-запуск">Установка и запуск</a>
      <ul>
        <li><a href="#установка-приложения">Установка приложения</a></li>
        <li><a href="#запуск">Запуск</a></li>
      </ul>
    </li>
    <li><a href="#использование">Использование</a></li>
    <li>
      <a href="#полезная-информация">Полезная информация</a>
      <ul>
        <li><a href="#регистрация-бота-telegram">Регистрация бота Telegram</a></li>
        <li>
          <a href="#режимы-работы-бота">Режимы работы бота</a>
          <ul>
            <li><a href="#запуск-без-api-приложения">Запуск без API приложения</a></li>
            <li><a href="#polling">Polling</a></li>
            <li><a href="#webhook">Webhook</a></li>
          </ul>
        </li>
        <li>
          <a href="#работа-с-базой-данных">Работа с базой данных</a>
          <ul>
            <li><a href="#создание-миграций">Создание миграций</a></li>
            <li><a href="#откат-миграций">Откат миграций</a></li>
          </ul>
        </li>
        <li>
          <a href="#работа-с-poetry">Работа с Poetry</a>
          <ul>
            <li><a href="#активировать-виртуальное-окружение">Активировать виртуальное окружение</a></li>
            <li><a href="#добавить-зависимость">Добавить зависимость</a></li>
            <li><a href="#запустить-скрипт-без-активации-виртуального-окружения">Запустить скрипт без активации виртуального окружения</a></li>
          </ul>
        </li>
        <li><a href="#использование-ngrok">Использование Ngrok</a></li>
        <li><a href="#переменные-окружения-env">Переменные окружения (.env)</a></li>
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

## Установка и запуск

### Установка приложения

1. Клонировать репозиторий.

    ```shell
    git clone https://github.com/Studio-Yandex-Practicum/ProCharity_back_2.0.git
    cd ProCharity_back_2.0
    ```

2. Установить зависимости и активировать виртуальное окружение.

    ```shell
    poetry install
    poetry shell
    ```

    > **Note**
    > [Документация по установке Poetry](https://python-poetry.org/docs/#installation)

3. Переименовать [`.env.example`](.env.example) в `.env` и задать переменные окружения.

    ```dotenv
    BOT_TOKEN=<Токен аутентификации бота>
    ```

    > **Note**
    > Полный список переменных окружения проекта находится в 
    > разделе "[Переменные окружения (.env)](#переменные-окружения-env)".

    > **Note**
    > Для получения токена аутентификации бота обратитесь к 
    > разделу "[Регистрация бота Telegram](#регистрация-бота-telegram)".

### Запуск

1. Применить миграции базы данных.

    ```shell
    alembic upgrade head
    ```

2. Запустить сервер приложения.

    ```shell
    uvicorn src:app --reload
    ```

## Использование

После выполнения инструкций, описанных в разделе "[Установка и Запуск](#установка-и-запуск)", 
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

### Режимы работы бота

#### Запуск без API приложения

Выполнить скрипт запуска.

```shell
python src/run.py
```

> **Warning**:
> Возможно только в режиме [polling](#polling).

#### Polling

Задать значение переменной окружения (`.env`).

```dotenv
BOT_WEBHOOK_MODE=False
```

#### Webhook

Задать значение переменным окружения (`.env`).

```dotenv
BOT_WEBHOOK_MODE=True
APPLICATION_URL=http://example.com  # Пример
```

> **Note**
> [Подробнее о webhooks](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks)

> **Note**
> Для теста через HTTPS можно использовать [Ngrok](https://ngrok.com/) 
> (см. раздел "[Использование Ngrok](#использование-ngrok)").

### Работа с базой данных

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

Откатить последнюю миграцию:

```shell
alembic downgrade -1
```

### Работа с Poetry

В этом разделе представлены наиболее часто используемые команды.

Подробнее: https://python-poetry.org/docs/cli/

#### Активировать виртуальное окружение

```shell
poetry shell
```

#### Добавить зависимость

```shell
poetry add <package_name>
```

> **Note**
> Использование флага `--dev (-D)` позволяет установить зависимость,
> необходимую только для разработки.
> Это полезно для разделения develop и prod зависимостей.

#### Запустить скрипт без активации виртуального окружения

```shell
poetry run <script_name>.py
```

### Команды для работы с Docker

#### _Установка Docker на Linux:_
```
# Установка утилиты для скачивания файлов
sudo apt install curl
# Эта команда скачает скрипт для установки докера
curl -fsSL https://get.docker.com -o get-docker.sh
# Эта команда запустит его
sh get-docker.sh
```

Для удаления старых версий Docker выполните команду:
```sudo apt remove docker docker-engine docker.io containerd runc```

Обновить список пакетов можно командой:
```sudo apt update```

Установите пакеты для работы через протокол https, это нужно для получения доступа к репозиторию докера:
```
sudo apt install \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg-agent \
  software-properties-common -y
```

Добавьте ключ GPG для подтверждения подлинности в процессе установки:

```curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -```

Добавьте репозиторий Docker в пакеты ```apt``` и обновите индекс пакетов:

```
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

sudo apt update
```

Установите Docker и вместе с ним Docker Compose:

```sudo apt install docker-ce docker-compose -y```

Убедитесь, что Docker работает:

```sudo systemctl status docker```

#### _Команды для работы с образами и контейнерами:_

Для просмотра всех хранящихся образов используйте команду:

```docker image ls```

Узнать ID образов можно с помощью команды:

```docker images -a```

Для удаления образа используется команда:

```docker image rm <ID_образа> ```


Для создания контейнера используйте команду:

```docker run <имя_образа> ```

Список запущенных контейнеров можно посмотреть с помощью команды:

``` docker container ls ```

При использовании следующей команды все процессы в контейнере останавливаются:

``` docker stop <ID_контейнера> ```

Окончательное удаление контейнера выполняется с помощью команды:

``` docker rm <ID_контейнера> ```

В директории, где сохранён Dockerfile выполните команду сборки образа:

``` docker build -t <имя_образа> . ```

Запустить контейнер локально можно командой:

```docker run --name <имя_контейнера> -it -p 8000:8000 <образ_,_из_которого_будет_запущен_контейнер> ```

Для остановки контейнера используется команда:

```docker container stop <ID_контейнера>```

Остановленный контейнер запускается с помощью команды:

```docker container start <ID_контейнера>```

Для входа в контейнер используется команда:

```docker exec -it <ID_контейнера> bash ```


Docker-compose запускается и останавливается командами:

```docker-compose up``` и ```docker-compose stop```/сочетание клавиш Ctrl+C

Пересборка контейнеров выполняется с помощью команды:

```docker-compose up -d --build ```

Команды внутри контейнеров выполняют посредством подкоманды ```docker-compose exec```.
Выполнение миграций, создание суперпользователя и сбор статики выполняется с помощью следующих команд:

```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```

Остановить собранные контейнеры можно командой:

```docker-compose down -v```

Посмотреть логи можно с помощью команды:

```docker logs --follow <имя_контейнера> ```

Сохранение логов в файл выполняется командой:

```docker logs <имя_контейнера> > docker.log```

Мониторинг запущенных контейнеров:

```docker stats```

Неактивные (остановленные) контейнеры удаляются с помощью команды:

```docker container prune```

Ненужные образы, которые, возможно, использовались как промежуточные, удаляются командой:

```docker image prune```

Удалить вообще всё, что не используется (неиспользуемые образы, остановленные контейнеры, тома, которые не использует ни один контейнер, билд-кеш), можно командой:

```docker system prune```


### Использование Ngrok

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

3. Задать значение переменной окружения (.env).

    ```dotenv
    APPLICATION_URL=https://1234-56-78-9.eu.ngrok.io  # Пример
    ```

### Переменные окружения (.env)

```dotenv
# Переменные приложения
APPLICATION_URL=  # Домен, на котором развернуто приложение
DEBUG=False  # Включение(True) | Выключение(False) режима отладки
ROOT_PATH=/api/  # Для корректной работы без прокси ставится пустая строка, для работы с прокси "/api/"
BOT_TOKEN=  # Токен аутентификации бота
BOT_WEBHOOK_MODE=False  # Запустить бота в режиме webhook(True) | polling(False)
# Переменные базы данных
POSTGRES_DB=procharity_back_db_local  # Название базы данных
POSTGRES_USER=postgres  # Логин для подключения к базе данных
POSTGRES_PASSWORD=postgres  # Пароль для подключения к базе данных
DB_HOST=localhost  # Название сервиса (контейнера)
DB_PORT=5432  # Порт для подключения к базе данных
```

<!-- MARKDOWN LINKS & BADGES -->

[FastAPI-url]: https://fastapi.tiangolo.com/
[FastAPI-badge]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi

[Python-telegram-bot-url]: https://github.com/python-telegram-bot/python-telegram-bot
[Python-telegram-bot-badge]: https://img.shields.io/badge/python--telegram--bot-2CA5E0?style=for-the-badge

[Postgres-url]: https://www.postgresql.org/
[Postgres-badge]: https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white

[Nginx-url]: https://nginx.org
[Nginx-badge]: https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white~~
