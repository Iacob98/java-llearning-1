import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Server
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/plantmon.db")

    # Sensor API Key
    SENSOR_API_KEY: str = os.getenv("SENSOR_API_KEY", "change-me-to-random-string")

    # LLM (Ollama)
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3.2:3b")
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "120"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "500"))

    # Monitoring
    CHECK_INTERVAL_MINUTES: int = int(os.getenv("CHECK_INTERVAL_MINUTES", "30"))
    SENSOR_OFFLINE_THRESHOLD_MINUTES: int = int(
        os.getenv("SENSOR_OFFLINE_THRESHOLD_MINUTES", "30")
    )

    # Default Plant Thresholds
    DEFAULT_MOISTURE_MIN: int = int(os.getenv("DEFAULT_MOISTURE_MIN", "30"))
    DEFAULT_MOISTURE_MAX: int = int(os.getenv("DEFAULT_MOISTURE_MAX", "70"))

    @property
    def database_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.DATABASE_PATH}"

    def ensure_data_dir(self) -> None:
        Path(self.DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
