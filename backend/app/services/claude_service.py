from anthropic import AsyncAnthropic
from app.config import settings

_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
MODEL = "claude-sonnet-4-6"


async def generate_text(prompt: str) -> str:
    message = await _client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
