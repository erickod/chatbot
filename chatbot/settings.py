from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = ""
    OTEL_SERVICE_NAME: str = ""
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""
    OTEL_COLLECTOR_METRICS_URL: str = ""
    OTEL_COLLECTOR_TRACES_URL: str = ""
    BOTMAKER_AUTH_TOKEN: str = ""
    BOTMAKER_WEBHOOK_URL: str = ""
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASS: str = ""
    DB_HOST: str = ""
    DB_PORT: str = ""
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 0
    STARKBANK_ENVIRONMENT: str = ""
    STARKBANK_PROJECT_ID: str = ""
    STARKBANK_PRIVATE_KEY: str = ""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def build_database_uri(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def retrieve_engine_config(self) -> dict:
        return {"pool_size": self.DB_POOL_SIZE, "max_overflow": self.DB_MAX_OVERFLOW}

    def build_session_config(self) -> dict:
        return {"expire_on_commit": False}


settings = Settings()
