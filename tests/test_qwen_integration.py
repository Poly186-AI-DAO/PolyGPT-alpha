import os
import subprocess
import sys
from pathlib import Path

import pytest

from hackathon.qwen_integration import QwenCloudError, qwen_chat


ROOT = Path(__file__).resolve().parents[1]


def test_qwen_chat_fails_closed_without_credentials(monkeypatch):
    monkeypatch.delenv("QWEN_API_KEY", raising=False)
    monkeypatch.delenv("QWEN_BASE_URL", raising=False)

    with pytest.raises(QwenCloudError, match="not configured"):
        qwen_chat([{"role": "user", "content": "READY"}])


def test_cli_fails_closed_without_credentials():
    env = os.environ.copy()
    env.pop("QWEN_API_KEY", None)
    env.pop("QWEN_BASE_URL", None)

    result = subprocess.run(
        [sys.executable, "hackathon/qwen_integration.py"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "qwen_cloud_proof_failed" in result.stderr
    assert "QWEN_API_KEY" in result.stderr
    assert "{'" not in result.stdout
