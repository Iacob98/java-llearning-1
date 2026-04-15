import logging
from datetime import datetime

import httpx

from src.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    SYSTEM_PROMPT = """Ты - эксперт по уходу за комнатными растениями. Ты анализируешь данные
с датчиков влажности почвы и даёшь рекомендации по поливу и уходу.

Правила:
- Отвечай ТОЛЬКО на русском языке
- Будь конкретным: указывай количество воды, частоту полива
- Учитывай время года (сейчас {current_season})
- Если влажность критически низкая (<15%), отмечай это как СРОЧНО
- Учитывай вид растения и его особенности
- Если данных недостаточно, скажи об этом честно
- Давай краткие, практичные советы
"""

    @staticmethod
    def _get_season() -> str:
        month = datetime.now().month
        if month in (3, 4, 5):
            return "весна"
        elif month in (6, 7, 8):
            return "лето"
        elif month in (9, 10, 11):
            return "осень"
        else:
            return "зима"

    async def generate(self, prompt: str) -> str:
        system = self.SYSTEM_PROMPT.format(current_season=self._get_season())

        try:
            async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT) as client:
                response = await client.post(
                    f"{settings.OLLAMA_URL}/api/chat",
                    json={
                        "model": settings.LLM_MODEL,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": prompt},
                        ],
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "num_predict": settings.LLM_MAX_TOKENS,
                        },
                    },
                )
                response.raise_for_status()
                return response.json()["message"]["content"]
        except httpx.ConnectError:
            logger.error("Cannot connect to Ollama at %s", settings.OLLAMA_URL)
            return (
                "ИИ-сервис недоступен. Проверьте, что Ollama запущена. "
                "Базовая рекомендация: проверьте влажность почвы вручную."
            )
        except Exception as e:
            logger.error("LLM error: %s", e)
            return f"Ошибка ИИ-сервиса: {e}"

    async def check_health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{settings.OLLAMA_URL}/api/tags")
                models = resp.json().get("models", [])
                return any(
                    m["name"].startswith(settings.LLM_MODEL) for m in models
                )
        except Exception:
            return False
