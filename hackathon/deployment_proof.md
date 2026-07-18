# Qwen Cloud deployment proof record

> **Status: NOT VERIFIED.** This file is a submission-safe template. It contains no API key, endpoint secret, fabricated response, or claim of a live Alibaba Cloud/Qwen deployment.

## What must be recorded before Devpost submission

Complete every field from the actual run and attach the resulting receipt or public evidence. Do not replace `NOT VERIFIED` with `VERIFIED` based on a local compile or a mocked response.

| Field | Value |
| --- | --- |
| Deployment status | `NOT VERIFIED` |
| Qwen service / model | `[record the service and model returned by the provider]` |
| Base URL host | `[record host only, never the API key or query secrets]` |
| Request timestamp (UTC) | `[ISO-8601 timestamp from the real run]` |
| Request receipt / provider request ID | `[provider-returned ID, if available]` |
| Response verification | `[record the observed response and validation method]` |
| Public evidence URL | `[public URL to an accepted proof artifact, or leave NOT AVAILABLE]` |

## Reproducible run

The live proof requires credentials supplied out-of-band. Do not commit them or paste them into an issue, pull request, recording, or this file.

```bash
export QWEN_API_KEY='[from a secret manager; do not commit]'
export QWEN_BASE_URL='[provider-issued OpenAI-compatible endpoint]/v1'
export QWEN_MODEL='qwen-plus'  # optional; use the model enabled for the account
python hackathon/qwen_integration.py
```

A successful local compile proves only that the adapter parses. A run without both required variables must fail closed with `QwenCloudError`; it is not deployment evidence.

## Evidence checklist

- [ ] A real Qwen Cloud endpoint and API key were supplied out-of-band.
- [ ] The request reached the provider and returned a response.
- [ ] The provider response or request ID was saved as an auditable receipt.
- [ ] Secrets were removed from logs, screenshots, and video.
- [ ] The public evidence URL resolves without exposing credentials.
- [ ] The Devpost packet links this record and the public repository.

Until all applicable boxes are checked, retain `Deployment status: NOT VERIFIED` and describe the remaining blocker rather than claiming live deployment.
