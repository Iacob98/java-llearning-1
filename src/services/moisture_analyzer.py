from typing import Optional

from src.models.plant import Plant
from src.models.reading import SensorReading


class MoistureAnalyzer:
    @staticmethod
    def calculate_trend(readings: list[SensorReading]) -> str:
        """Determine moisture trend: 'rising', 'falling', 'stable', or 'insufficient_data'."""
        if len(readings) < 3:
            return "insufficient_data"

        values = [r.moisture_percent for r in readings]
        n = len(values)

        # Simple linear regression slope
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n

        numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        # Threshold: 0.5% per reading interval
        if slope > 0.5:
            return "rising"
        elif slope < -0.5:
            return "falling"
        return "stable"

    @staticmethod
    def check_thresholds(moisture: float, plant: Plant) -> Optional[str]:
        """Quick threshold check. Returns alert type or None."""
        if moisture < plant.optimal_moisture_min * 0.5:
            return "critical"
        elif moisture < plant.optimal_moisture_min:
            return "warning"
        elif moisture > plant.optimal_moisture_max:
            return "info"
        return None

    @staticmethod
    def format_trend_description(trend: str) -> str:
        descriptions = {
            "rising": "растёт (почва увлажняется)",
            "falling": "падает (почва высыхает)",
            "stable": "стабильная",
            "insufficient_data": "недостаточно данных",
        }
        return descriptions.get(trend, trend)
