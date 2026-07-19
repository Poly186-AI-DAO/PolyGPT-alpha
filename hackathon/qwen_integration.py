"""Minimal Qwen Cloud integration proof for the hackathon demo.

This adapter uses an OpenAI-compatible endpoint, which keeps model routing
separate from the worker runtime. It intentionally fails closed when the
credentials are absent; no fake completion is returned.
"""

from __future__ import annotations

import logging
import os
from typing import Any


logger = logging.getLogger(__name__)


class QwenCloudError(RuntimeError):
    """Raised when Qwen Cloud is not configured or the request fails."""


def qwen_chat(messages: list[dict[str, str]], *, model: str | None = None) -> dict[str, Any]:
    """Call Qwen Cloud through its OpenAI-compatible API.

    Required environment variables:
      QWEN_API_KEY: API key (never committed)
      QWEN_BASE_URL: OpenAI-compatible base URL

    The function is a small, auditable proof seam for the Poly worker runtime.
    It does not claim a live deployment until a real key and endpoint are used.
    """
    api_key = os.getenv("QWEN_API_KEY")
    base_url = os.getenv("QWEN_BASE_URL")
    if not api_key or not base_url:
        raise QwenCloudError(
            "Qwen Cloud is not configured. Set QWEN_API_KEY and QWEN_BASE_URL "
            "to run the live proof; no credentials are bundled."
        )

    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise QwenCloudError("Install the OpenAI-compatible client before running the live proof") from exc

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model or os.getenv("QWEN_MODEL", "qwen-plus"),
        messages=messages,
        temperature=0,
    )
    return response.model_dump() if hasattr(response, "model_dump") else response.to_dict()


def main() -> int:
    """Run the bounded proof entry point with structured, non-secret logging."""
    try:
        response = qwen_chat([{"role": "user", "content": "Return the word READY."}])
    except QwenCloudError as exc:
        logger.error("qwen_cloud_proof_failed", extra={"reason": str(exc)})
        return 1

    logger.info(
        "qwen_cloud_proof_succeeded",
        extra={"response_keys": sorted(response.keys())},
    )
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(main())
