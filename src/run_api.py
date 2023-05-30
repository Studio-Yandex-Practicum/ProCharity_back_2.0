
import argparse
from application import create_app
import uvicorn


def configure_argument_parser():
    parser = argparse.ArgumentParser(description='Запуск API ProCharity')
    parser.add_argument(
        '--with-bot',
        action='store_true',
        default=False,
        help='Запуск API ProCharity с ботом'
    )
    return parser


def start_api():
    arg_parser = configure_argument_parser()
    args = arg_parser.parse_args()
    app = create_app(run_bot=args.with_bot)
    uvicorn.run(app, host="localhost", port=8000)


if __name__ == "__main__":
    start_api()
