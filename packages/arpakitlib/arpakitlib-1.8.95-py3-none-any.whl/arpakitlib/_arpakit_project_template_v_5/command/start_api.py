import uvicorn

from project.core.settings import get_cached_settings
from project.core.util import setup_logging


def __command():
    setup_logging()
    uvicorn.run(
        "project.api.asgi:app",
        port=get_cached_settings().api_port,
        host="localhost",
        workers=1,
        reload=False
    )


if __name__ == '__main__':
    __command()
