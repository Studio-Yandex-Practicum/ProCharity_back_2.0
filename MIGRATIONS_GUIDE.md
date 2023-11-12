# Восстановление базы данных и применение миграций

Этот README-файл содержит инструкции по восстановлению базы данных из дампа и применению миграций с использованием Docker и Alembic.

## Шаги по восстановлению базы данных

1. Запустите Docker-контейнер с PostgreSQL.

2. Создайте пользователя procharity:

   ```
   docker exec -it infra-postgres-1 psql -U postgres -d procharity_back_db_local -c "CREATE ROLE procharity;"
   ```

3. Предоставьте пользователю procharity права доступа к базе данных procharity_back_db_local:

   ```
   docker exec -it infra-postgres-1 psql -U postgres -d procharity_back_db_local -c "GRANT ALL PRIVILEGES ON DATABASE procharity_back_db_local TO procharity;"
   ```
   > Если БД не создана docker exec -it infra-postgres-1 psql -U postgres -d procharity_back_db_local -c "CREATE DATABASE procharity_back_db_local;"


## Шаги по восстановлению данных из дампа

1. Очистите существующие данные и таблицы в базе данных:

   ```
   docker exec -it infra-postgres-1 psql -U postgres -d procharity_back_db_local -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
   ```

2. Загрузите данные из дампа SQL:

   ```
   docker exec -i infra-postgres-1 psql -U postgres procharity_back_db_local < name_dump.sql
   ```

## Шаги по применению миграций с использованием Alembic

1. Удалите таблицу alembic_version из базы данных:

   ```
   docker exec -it infra-postgres-1 psql -U postgres -d procharity_back_db_local -c "DROP TABLE alembic_version;"
   ```
   

2. Примените миграции с помощью Alembic:

   ```
   alembic upgrade head
   ```

3. Восстановление базы данных и применение миграций завершено.