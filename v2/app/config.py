import os
from functools import lru_cache


class Settings:
    app_name: str = "AyeSpy v2"
    environment: str = os.getenv("ENV", "dev")

    db_engine_choice: str = os.getenv("DB_ENGINE", "sqlite")  # sqlite | postgres
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./v2_ayespy.db")

    # Embeddings / LLM (optional)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    embeddings_provider: str = os.getenv("EMBEDDINGS_PROVIDER", "local")  # local | openai

    # Rate limits (simple caps)
    chat_daily_limit: int = int(os.getenv("CHAT_DAILY_LIMIT", "50"))


@lru_cache()
def get_settings() -> Settings:
    return Settings()


