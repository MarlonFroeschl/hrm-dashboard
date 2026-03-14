import httpx
import logging

logger = logging.getLogger(__name__)


async def trigger(webhook_url: str, payload: dict) -> None:
    """Sendet einen HTTP POST an eine externe n8n Webhook-URL."""
    if not webhook_url:
        return  # Webhook nicht konfiguriert → still ignorieren
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            await client.post(webhook_url, json=payload)
        except httpx.RequestError as e:
            logger.warning("Webhook to %s failed: %s", webhook_url, e)
