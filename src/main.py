from fastapi import FastAPI

from src.core.depends.container import Container


def main(run_bot: bool = True) -> FastAPI:
    container = Container()
    container.wire(packages=(__package__,))
    return container.applications_container.fastapi_app(run_bot=run_bot)
