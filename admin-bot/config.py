import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.environ["ADMIN_BOT_TOKEN"]
ADMIN_IDS: list[int] = [int(x.strip()) for x in os.environ["ADMIN_IDS"].split(",")]
DB_PATH: str = os.environ.get("DB_PATH", "/root/realestate-ai/backend/realestate.db")

NEW_USER_POLL_INTERVAL: int = 60
BROADCAST_DELAY: float = 0.05
USERS_PER_PAGE: int = 10
