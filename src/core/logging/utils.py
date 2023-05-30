import structlog


log = structlog.get_logger()


def logger_decor(func):
    def wrapper(update, context):
        log.info(f'Получено обновление: Update - {update}; Context - {context}')
        return func(update, context)
    return wrapper
