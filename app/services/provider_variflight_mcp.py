import asyncio
import json
import re
from typing import Any

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from app.config import settings


def _extract_price_from_text(text: str) -> float | None:
    patterns = [
        r"最低价\s*[:：]\s*(\d+(?:\.\d+)?)\s*元",
        r"价格\s*[:：]\s*(\d+(?:\.\d+)?)\s*元",
        r"(\d+(?:\.\d+)?)\s*元",
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return float(m.group(1))
    return None


def _extract_flight_no_from_text(text: str) -> str:
    m = re.search(r"([A-Z]{2}\d{3,4})", text)
    return m.group(1) if m else "-"


def _parse_tool_result(result: Any) -> dict:
    text_parts: list[str] = []

    content = getattr(result, "content", None)
    if content:
        for item in content:
            txt = getattr(item, "text", None)
            if txt:
                text_parts.append(txt)

    merged = "\n".join(text_parts).strip()

    price = None
    flight_no = "-"

    if merged:
        try:
            data = json.loads(merged)
            if isinstance(data, dict):
                # Case 1: price fields directly in dict
                for key in ["minPrice", "lowestPrice", "price"]:
                    if key in data:
                        price = float(data[key])
                        break
                if price is not None:
                    flight_no = str(data.get("flightNo") or data.get("flight_number") or "-")

                # Case 2: price info buried inside a natural-language "data" field
                if price is None:
                    data_field = data.get("data", "")
                    if isinstance(data_field, str) and data_field:
                        price = _extract_price_from_text(data_field)
                        flight_no = _extract_flight_no_from_text(data_field)
        except Exception:
            # Not JSON at all — try regex directly on raw text
            price = _extract_price_from_text(merged)
            flight_no = _extract_flight_no_from_text(merged)

    if price is None:
        raise RuntimeError(f"无法从MCP返回中解析价格，原始返回: {merged[:300]}")

    return {
        "price": float(price),
        "currency": "CNY",
        "flight_no": flight_no,
        "provider": "variflight_mcp",
        "raw": merged,
    }


async def _query_with_stdio(task: dict) -> dict:
    if not settings.variflight_api_key:
        raise RuntimeError("VARIFLIGHT_API_KEY 未配置")

    args = settings.variflight_mcp_args.split(" ")
    server_params = StdioServerParameters(
        command=settings.variflight_mcp_command,
        args=args,
        env={"X_VARIFLIGHT_KEY": settings.variflight_api_key},
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            payload = {
                "depCityCode": task["origin"],
                "arrCityCode": task["destination"],
                "depDate": task["travel_date"],
            }

            tool_names = ["searchFlightItineraries", "searchFlightltineraries"]
            last_err: Exception | None = None
            for tool_name in tool_names:
                try:
                    result = await session.call_tool(tool_name, payload)
                    return _parse_tool_result(result)
                except Exception as exc:
                    last_err = exc

            raise RuntimeError(f"MCP工具调用失败: {last_err}")


def query_variflight_mcp(task: dict) -> dict:
    return asyncio.run(_query_with_stdio(task))
