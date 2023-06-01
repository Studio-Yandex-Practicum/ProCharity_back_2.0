import sys

from pyngrok import ngrok

from src.core.logging.setup import setup_logging
from src.settings import settings


def set_ngrok():
    if settings.USE_NGROK:
        port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 8000

        ngrok.connect(port).public_url
        setup_logging()
