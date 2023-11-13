# Восстановление базы данных и применение миграций

Этот README-файл содержит инструкции по восстановлению базы данных из дампа и применению миграций с использованием Docker и Alembic.


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