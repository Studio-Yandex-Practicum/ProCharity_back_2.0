import locale

locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")


def display_tasks(task):
    deadline = task.deadline.strftime("%d.%m.%y")
    bonus_link = "https://help.procharity.ru/article/10053"
    return (
        f"От фонда: {task.name_organization}\n\n"
        f"Категория: {task.category.name}\n\n"
        f"Срок: {deadline}\n"
        f"Бонусы: <a href='{bonus_link}'>{task.bonus * '💎'}</a>\n"
        f"<a href='<Сделать ссылку на задание>'>{'Посмотреть задание'}</a>"
    )
