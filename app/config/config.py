import os
from dotenv import load_dotenv
import logging

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_HTTP = os.getenv("BASE_HTTP")
DB_FOLDER = os.path.join('/'.join(os.getcwd().split('/')[:-1]), 'db')

def setup_logger():
    logger = logging.getLogger("VK-Teams")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = setup_logger()