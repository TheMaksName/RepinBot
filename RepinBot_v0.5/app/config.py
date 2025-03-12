import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    DATABASE_URL: str = os.getenv('DB_LITE')
    SMTP_SERVER: str = os.getenv('SMTP_SERVER')
    SMTP_PORT: int = os.getenv("PORT")
    USERNAME: str = os.getenv("SENDER_EMAIL")
    PASSWORD: str = os.getenv("SENDER_PASSWORD")


settings = Settings()