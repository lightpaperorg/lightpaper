"""Email sending via Resend API."""

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def send_otp_email(to: str, code: str) -> bool:
    """Send a 6-digit OTP code via Resend. Returns True on success."""
    if not settings.resend_api_key:
        logger.warning("RESEND_API_KEY not configured — OTP email not sent to %s", to)
        return False

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                json={
                    "from": "lightpaper.org <auth@lightpaper.org>",
                    "to": [to],
                    "subject": f"Your lightpaper code: {code}",
                    "text": (
                        f"Your verification code is: {code}\n\n"
                        "Expires in 10 minutes.\n\n"
                        "\u2014 lightpaper.org"
                    ),
                },
            )
        return resp.status_code == 200
    except httpx.HTTPError:
        logger.exception("Failed to send OTP email to %s", to)
        return False
