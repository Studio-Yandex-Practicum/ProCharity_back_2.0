from src.bot.bot import start_bot

from .application import create_app

app = create_app()


@app.on_event("startup")
async def startup():
    await start_bot()
