import uvicorn

from application import create_app


def start_api():
    app = create_app()
    uvicorn.run(app, host="localhost", port=8000)


if __name__ == "__main__":
    start_api()
