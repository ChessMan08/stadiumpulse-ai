from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: str = "mock"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_embed_model: str = "gemini-embedding-001"

    ops_api_key: str = "DEMO-OPS-KEY-2026"
    allowed_origins: str = "*"
    env: str = "development"

    @property
    def cors_origins(self) -> list[str]:
        if self.allowed_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def active_llm_provider(self) -> str:
        if self.llm_provider == "gemini" and not self.gemini_api_key:
            return "mock"
        return self.llm_provider


@lru_cache
def get_settings() -> Settings:
    return Settings()
