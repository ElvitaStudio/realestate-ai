from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str
    bot_token: str
    mono_token: str = ""
    mono_webhook_secret: str = ""
    jwt_secret: str
    database_url: str = "sqlite+aiosqlite:///./realestate.db"

    class Config:
        env_file = ".env"


settings = Settings()
