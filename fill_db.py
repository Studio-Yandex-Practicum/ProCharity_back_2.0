import asyncio

from datetime import datetime, timedelta
from random import randint, choice
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)

from src.core.db.models import Category, Task
from src.settings import settings

engine = create_async_engine(settings.database_url)

CATEGORIES_TEST_DATA = [
    {"id": "1", "name": "Дизайн и верстка"},
    {"id": "2", "name": "Маркетинг и коммуникации"},
    {"id": "3", "name": "Переводы"},
    {"id": "4", "name": "IT"},
    {"id": "5", "name": "Юридические услуги"},
    {"id": "6", "name": "Стратегический консалтинг"},
    {"id": "7", "name": "Фото и видео"},
    {"id": "8", "name": "Обучение и тренинги"},
    {"id": "9", "name": "Финансы и фандрайзинг"},
    {"id": "10", "name": "Менеджмент"}
    ]
COUNT_CATEGORIES = 10
TEST_LOCATION = [
    "Москва",
    "Санкт-Петербург",
    "Новосибирск",
    "Екатеринбург",
    "Казань",
    "Нижний Новгород",
    "Челябинск",
    "Самара",
    "Омск",
    "Ростов-на-Дону"
]
TEST_ORGANIZATION = [
    "Нефть без границ",
    "Транспортный гигант-2",
    "Российские роботы",
    "Строй Инновация",
    "Медицинский Колос"
]
TEST_TASKS = [
    {"id": "1", "tasks": [
        "Создание макета сайта в графическом редакторе",
        "Изучение основных принципов дизайна: цвет, типографика, композиция",
        "Создание векторной графики для использования на сайте",
        "Создание нескольких вариантов дизайна для выбора наилучшего решения",
        "Разработка дизайна логотипа и фирменного стиля"
    ]},
    {"id": "2", "tasks": [
        "Разработка и продвижение программы лояльности для доноров.",
        "Организация и проведение благотворительного аукциона или лотереи.",
        "Проведение промо-акций в социальных сетях для привлечения доноров.",
        "Организация и проведение благотворительного мероприятия.",
        "Создание PR-кампаний и пресс-релизов."
    ]},
    {"id": "3", "tasks": [
        "Перевод средств на поддержку нуждающихся",
        "Организация благотворительных мероприятий через переводы",
        "Регулярные переводы на улучшение условий жизни нуждающихся",
        "Перевод на медицинскую помощь нуждающимся",
        "Помощь с переводом для мигрантов и беженцев",
    ]},
    {"id": "4", "tasks": [
        "Разработка и поддержка сайта организации",
        "Создание базы данных для учета доноров и получателей помощи",
        "Разработка мобильного приложения для сбора пожертвований",
        "Автоматизация процесса учета и отчетности в организации",
        "Разработка системы онлайн-консультаций для получателей помощи"
    ]},
    {"id": "5", "tasks": [
        "Регистрация благотворительной организации",
        "Разработка устава и другой внутренней документации",
        "Получение статуса НКО",
        "Консультации по налогообложению и отчетности",
        "Правовая поддержка при взаимодействии с государственными органами"
    ]},
    {"id": "6", "tasks": [
        "Определение и разработка концепции долгосрочного развития организации.",
        "Поиск и обеспечение новых источников финансирования.",
        "Разработка стратегии маркетинга и продвижения организации.",
        "Оптимизация деятельности и уменьшение издержек организации.",
        "Оценка эффективности программ благотворительной помощи.",
    ]},
    {"id": "7", "tasks": [
        "Создание промо-видео",
        "Фотоотчет",
        "Создание видеоинструкций",
        "Фотографирование пациентов",
        "Создание коротких видеороликов",
    ]},
    {"id": "8", "tasks": [
        "Развитие навыков лидерства и командной работы",
        "Навыки эффективной коммуникации и делового переговоров",
        "Финансовое планирование и управление бюджетом",
        "Управление проектами и достижение целей организации",
        "Развитие личной эффективности и эмоционального интеллекта"
    ]},
    {"id": "9", "tasks": [
        "Разработка стратегии привлечения доноров на следующий квартал.",
        "Проведение анализа эффективности рекламных кампаний.",
        "Организация благотворительного концерта с участием артистов.",
        "Проведение финансовой аудитории для улучшения финансовой дисциплины.",
        "Разработка системы мотивации для волонтеров."
     ]},
    {"id": "10", "tasks": [
        "Разработать стратегию привлечения новых доноров",
        "Организация гала-вечеринки в поддержку благотворительной программы",
        "Подготовка презентации о деятельности организации.",
        "Провести опрос среди населения для выявления актуальных проблем.",
        "Разработать план волонтерской деятельности для привлечения помощи."
    ]}
]


async def get_task_name_by_id(category_id):
    """Function for selecting tasks from the TEST_TASKS list."""
    for task in TEST_TASKS:
        if int(task["id"]) == category_id:
            return choice(task["tasks"])
    return "Category not found"


async def filling_category_in_db(
        async_session: async_sessionmaker[AsyncSession],
        ) -> None:
    """Filling the database with test data Categories.
    The fields id, name, archive are filled in.
    """
    async with async_session() as session:
        for category in CATEGORIES_TEST_DATA:
            category_obj = Category(
                name=category['name'],
                archive=choice([True, False]),
                id=int(category['id']),
            )
            session.add(category_obj)
        await session.commit()


async def filling_task_in_db(
        async_session: async_sessionmaker[AsyncSession],
        ) -> None:
    """Filling the database with test data: Tasks.
    The fields title, name_organization, deadline, category,
    location, description, archive.
     """
    async with async_session() as session:
        for task_num in range(1, 51):
            category_id = randint(1, COUNT_CATEGORIES)
            title = await get_task_name_by_id(category_id)
            name_organization = f'{choice(TEST_ORGANIZATION)}'
            deadline = datetime.now() + timedelta(days=randint(1, 30))
            bonus = randint(100, 1000)
            location = f'Location {choice(TEST_LOCATION)}'
            link = f'http://example.com/task/{task_num}'
            description = f'Description {title}'
            archive = choice([True, False])
            task = Task(
                name_organization=name_organization,
                deadline=deadline,
                category_id=category_id,
                title=title,
                bonus=bonus,
                location=location,
                link=link,
                description=description,
                archive=archive
            )
            # Check if task with the same title and category_id already exists
            existing_task = await session.execute(
                select(Task).where((Task.title == title))
            )
            while existing_task.fetchone() is not None:
                # If task already exists, generate a new title and category
                category_id = randint(1, COUNT_CATEGORIES)
                title = await get_task_name_by_id(category_id)
                existing_task = await session.execute(select(Task).where(
                    (Task.title == title) &
                    (Task.category_id == category_id)))
            session.add(task)
        await session.commit()


async def delete_all_data(async_session: AsyncSession) -> None:
    """The function deletes data from the tables Category, Tasks."""
    async with async_session() as session:
        await session.execute(
            text("""TRUNCATE TABLE tasks, categories CASCADE""")
        )
        await session.commit()


async def run():
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    await delete_all_data(async_session)
    print("Deleted data from the Tasks, Categories table.")
    await filling_category_in_db(async_session)
    print("The table with the Categories is full.")
    await filling_task_in_db(async_session)
    print("The Tasks table is full.")

if __name__ == "__main__":
    asyncio.run(run())
