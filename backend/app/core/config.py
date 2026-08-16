from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    app_name: str = "BuildKit"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg2://user:password@localhost:5432/buildkit"
    max_upload_size: int = 10_485_760
    allowed_upload_extensions: list[str] = [
        ".txt",
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".csv",
        ".json",
    ]


settings = Settings()
