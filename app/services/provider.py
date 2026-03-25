from datetime import datetime

from app.config import settings
from app.services.provider_variflight_mcp import query_variflight_mcp


def _query_lowest_price_mock(task: dict) -> dict:
    seed = f"{task['travel_date']}-{task['origin']}-{task['destination']}"
    base = abs(hash(seed)) % 2200 + 600
    wave = datetime.now().minute * 2
    price = max(200, base - wave)
    flight_no = f"HU{abs(hash(task['origin'] + task['destination'])) % 9000 + 1000}"
    return {
        "price": float(price),
        "currency": "CNY",
        "flight_no": flight_no,
        "provider": "mock",
    }


def query_lowest_price(task: dict) -> dict:
    provider = settings.price_provider.lower().strip()
    if provider == "variflight_mcp":
        return query_variflight_mcp(task)
    return _query_lowest_price_mock(task)
