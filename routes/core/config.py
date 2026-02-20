# core/config.py  (or wherever you keep settings)
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str
    mongodb_url: str
    database_name: str = "mikrotik"                  # default ok
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        # Try these in order – pick ONE that works for you
        env_file = ".env",                             # simple – good if CWD is project root
        # env_file = Path(__file__).parent.parent / ".env",   # if config.py is in src/core/
        # env_file = Path.cwd() / ".env",                # explicit current dir
        env_file_encoding="utf-8",
        extra="ignore",                                # ignore unknown .env keys
        case_sensitive=False,                          # SECRET_KEY == secret_key
    )


settings = Settings()