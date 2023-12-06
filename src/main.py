from fastapi import FastAPI

from src.core.depends import Container


def main(run_bot: bool = True) -> FastAPI:
    container = Container()
    container.wire(packages=(__package__,))
