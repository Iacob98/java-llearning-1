import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.care_log import CareLog
from src.models.plant import Plant
from src.models.reading import SensorReading
from src.models.recommendation import Recommendation
from src.models.sensor import Sensor
from src.services.llm_service import LLMService
from src.services.moisture_analyzer import MoistureAnalyzer

logger = logging.getLogger(__name__)


class RecommendationEngine:
    def __init__(self, llm: LLMService, session: AsyncSession):
        self.llm = llm
        self.session = session
        self.analyzer = MoistureAnalyzer()

    async def _get_plant_with_data(
        self, plant_id: int
    ) -> tuple[Optional[Plant], list[SensorReading], list[CareLog]]:
        result = await self.session.execute(
            select(Plant).where(Plant.id == plant_id)
        )
        plant = result.scalar_one_or_none()
        if not plant:
            return None, [], []

        # Get sensor IDs for this plant
        sensor_result = await self.session.execute(
            select(Sensor.id).where(Sensor.plant_id == plant_id)
        )
        sensor_ids = [row[0] for row in sensor_result.all()]

        readings = []
        if sensor_ids:
            since = datetime.now(timezone.utc) - timedelta(hours=24)
            readings_result = await self.session.execute(
                select(SensorReading)
                .where(
                    SensorReading.sensor_id.in_(sensor_ids),
                    SensorReading.timestamp >= since,
                )
                .order_by(SensorReading.timestamp.asc())
            )
            readings = list(readings_result.scalars().all())

        care_result = await self.session.execute(
            select(CareLog)
            .where(CareLog.plant_id == plant_id)
            .order_by(CareLog.timestamp.desc())
            .limit(10)
        )
        care_logs = list(care_result.scalars().all())

        return plant, readings, care_logs

    def _build_analysis_prompt(
        self, plant: Plant, readings: list[SensorReading], care_logs: list[CareLog]
    ) -> str:
        trend = self.analyzer.calculate_trend(readings)
        trend_desc = self.analyzer.format_trend_description(trend)

        current_moisture = (
            f"{readings[-1].moisture_percent:.1f}%" if readings else "нет данных"
        )
        current_temp = (
            f"{readings[-1].temperature:.1f}°C"
            if readings and readings[-1].temperature
            else "нет данных"
        )

        # Format recent readings as a compact trend line
        recent = readings[-12:] if len(readings) > 12 else readings
        trend_line = ", ".join(f"{r.moisture_percent:.0f}%" for r in recent)

        # Format care logs
        care_text = "нет записей"
        if care_logs:
            care_entries = []
            for log in care_logs[:5]:
                ts = log.timestamp.strftime("%d.%m %H:%M") if log.timestamp else "?"
                care_entries.append(f"  - {ts}: {log.action}")
            care_text = "\n".join(care_entries)

        return f"""Растение: {plant.name} (вид: {plant.species or 'неизвестен'})
Оптимальный диапазон влажности: {plant.optimal_moisture_min}% - {plant.optimal_moisture_max}%

Текущие показания:
- Влажность: {current_moisture}
- Температура: {current_temp}
- Тренд: {trend_desc}

Последние показания влажности (от старого к новому):
{trend_line or 'нет данных'}

Последние действия по уходу:
{care_text}

Заметки владельца: {plant.notes or 'нет'}

Проанализируй состояние растения и дай конкретную рекомендацию.
Если полив необходим — укажи примерный объём воды.
Если всё хорошо — кратко подтверди."""

    async def analyze_plant(self, plant_id: int) -> Optional[Recommendation]:
        """Analyze a plant and generate recommendation if needed."""
        plant, readings, care_logs = await self._get_plant_with_data(plant_id)
        if not plant:
            return None

        # Quick threshold check — skip LLM if everything is fine
        if readings:
            alert = self.analyzer.check_thresholds(
                readings[-1].moisture_percent, plant
            )
            trend = self.analyzer.calculate_trend(readings)
            if alert is None and trend in ("stable", "rising"):
                return None  # All good, no need to bother the LLM

        prompt = self._build_analysis_prompt(plant, readings, care_logs)
        answer = await self.llm.generate(prompt)

        # Determine recommendation type
        rec_type = "info"
        if readings:
            alert = self.analyzer.check_thresholds(
                readings[-1].moisture_percent, plant
            )
            if alert:
                rec_type = alert
            elif "полив" in answer.lower() or "полить" in answer.lower():
                rec_type = "water"

        recommendation = Recommendation(
            plant_id=plant_id,
            message=answer,
            rec_type=rec_type,
            source="auto",
        )
        self.session.add(recommendation)
        await self.session.commit()
        await self.session.refresh(recommendation)

        logger.info(
            "Generated %s recommendation for plant %s (#%d)",
            rec_type, plant.name, plant.id,
        )
        return recommendation

    async def ask_about_plant(
        self, plant_id: int, question: str
    ) -> tuple[str, Optional[Recommendation]]:
        """Answer a user question about a specific plant."""
        plant, readings, care_logs = await self._get_plant_with_data(plant_id)
        if not plant:
            return "Растение не найдено.", None

        context = self._build_analysis_prompt(plant, readings, care_logs)
        full_prompt = f"{context}\n\nВопрос от пользователя: {question}"

        answer = await self.llm.generate(full_prompt)

        recommendation = Recommendation(
            plant_id=plant_id,
            message=answer,
            rec_type="info",
            source="user",
        )
        self.session.add(recommendation)
        await self.session.commit()
        await self.session.refresh(recommendation)

        return answer, recommendation
