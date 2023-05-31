import structlog


async def not_handled_updates_func(func, *args):
    if args is None:
        await log.ainfo(f"Не пойманны updates для функции {func.__name__}")


log = structlog.get_logger()


def logger_decor(func):
    async def wrapper(*args, **kwargs):
        await log.ainfo(f"Запущенна функция {func.__name__}", args=args, kwargs=kwargs)
        await log.ainfo(f"Получено обновление: args = {args}, kwargs = {kwargs}")
        await not_handled_updates_func(func, *args)
        return await func(*args, **kwargs)

    return wrapper
