# Qwen Cloud Global AI Hackathon Proof Bundle

## Project
**Poly Autopilot Workforce for Qwen Cloud**, Autopilot Agent track.

Poly is a governed digital workforce pattern for real business operations. A Qwen-backed planner turns an operator objective into tasks, routes work to specialized workers and tools, verifies source evidence, persists a receipt, and holds external sends or spend behind human approval.

This directory is a bounded proof bundle. It does not claim a live Qwen deployment without credentials. The integration seam is executable when `QWEN_API_KEY` and `QWEN_BASE_URL` are supplied by the operator.

## Evidence map

- [`qwen_integration.py`](qwen_integration.py): OpenAI-compatible Qwen Cloud adapter. Fails closed when credentials are absent.
- [`deployment_proof.md`](deployment_proof.md): placeholder-safe live deployment receipt template. It remains explicitly unverified until a real provider response exists.
- [`architecture.svg`](architecture.svg): rendered architecture diagram.
- [`demo_script.md`](demo_script.md): three-minute recording plan.
- [`../LICENSE`](../LICENSE): MIT license for the repository.

## Run the integration proof

```bash
export QWEN_API_KEY='your-key-from-a-secret-store'
export QWEN_BASE_URL='https://your-qwen-compatible-endpoint/v1'
export QWEN_MODEL='qwen-plus'  # optional
python hackathon/qwen_integration.py
```

Do not commit credentials. A live run requires a valid Qwen Cloud endpoint, API key, network access, and the OpenAI-compatible Python client. No such credentials are included in this repository.

## Architecture and claims boundary

The demo is designed to show: planning, tool routing, source grounding, durable artifact creation, verification, and a human checkpoint before external action. It does not claim that this repository alone contains Poly's production runtime, CRM, or cloud deployment. Those are described as integration targets in the submission packet and must be demonstrated with separate, verifiable links before Devpost submission.

## Local validation

```bash
python -m py_compile hackathon/qwen_integration.py
```

Expected behavior without credentials is a clear `QwenCloudError`, not a fabricated response. This is intentional receipt-first behavior. See [`deployment_proof.md`](deployment_proof.md) for the exact evidence still required for a live claim.
