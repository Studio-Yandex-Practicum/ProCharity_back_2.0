from telegram import Update


def delete_previous(coroutine):
    """Для функций, отправляющих сообщения с inline-кнопками.
    Удаляет сообщение с кнопками, приведшее к вызову функции."""

    async def wrapper(*args, **kwargs):
        result = await coroutine(update: Update, *args, **kwargs)
        if "update" in kwargs and isinstance(kwargs["update"], Update):
            update = kwargs["update"]
        else:
            for arg in args:
                if isinstance(arg, Update):
                    update = arg
                    break
            else:
                return result  # если нет update, просто возвращаем результат работы
        await update.callback_query.message.delete()
        return result

    return wrapper
