"""Main entry"""

import uvicorn

from src.app.setup import app
from src.config.config import get_config

config = get_config()


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=config.http_port)
