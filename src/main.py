from fastapi import FastAPI

from src.core.depends import Container


def main(run_bot: bool = True) -> FastAPI:
    container = Container()
    container.wire(packages=(__package__,))
    return container.applications_container.fastapi_app(run_bot=run_bot)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(main(), host="0.0.0.0", port=8000)
