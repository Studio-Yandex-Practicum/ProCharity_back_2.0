import structlog


async def logging_updates(*args, **kwargs):
    await log.awarning(f"Не пойманны update", args=args, kwargs=kwargs)


log = structlog.get_logger()


def logger_decor(func):
    async def wrapper(*args, **kwargs):
        await log.ainfo(f"Запущенна функция {func.__name__}", args=args, kwargs=kwargs)
        return await func(*args, **kwargs)

    return wrapper
