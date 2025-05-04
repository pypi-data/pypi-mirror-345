# ObservAI

![PyPI](https://img.shields.io/pypi/v/observai)
![License](https://img.shields.io/pypi/l/observai)
![Python Versions](https://img.shields.io/pypi/pyversions/observai)

Lightweight SDK for capturing and buffering LLM calls (OpenAI for now) for audit, compliance, and analytics.

## Why ObservAI?

LLMs like ChatGPT are powerful but opaque. ObservAI adds transparency and observability to your AI systems by:

* Capturing every prompt/response made to OpenAI
* Logging metadata such as latency, timestamp, route, and user
* Supporting crash-safe local buffering with SQLite
* Sending logs to a remote collector or local file
* Providing optional background flushing with low overhead

Ideal for:

* Auditing LLM usage
* Debugging hallucinations or failure cases
* Proving compliance (e.g., GDPR, HIPAA)
* Generating analytics on prompt effectiveness

## Features

* Capture prompts/responses from OpenAI automatically
* SQLite fallback for crash resilience
* Easy integration with `openai` SDK
* Local log file or remote collector
* Optional background flushing

## Installation

```bash
pip install observai
```

## Quick Start

```python
import observai as oai

# initialize with defaults (no background flusher)
oai.init(
    user_id="alice@example.com",
    log_path="observai_events.log",
    endpoint="http://localhost:9000/events/batch",
    headers={"X-Observai-Key": "dev-secret-key"},
    flush_interval=2.0,
    background=True,  # enables automatic flush
)

# optionally tag with a user id if not set above
oai.set_user("alice@example.com")

# ... then anywhere in your code, whenever you call OpenAI:
from openai import OpenAI
client = OpenAI(api_key="YOUR_API_KEY")
resp = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role":"user","content":"Hello"}]
)

# at process exit we auto‐flush; you can also manually:
oai.flush(final=True)
```

## Configuration

You can override defaults in `init()`:

| Parameter        | Default                                      | Description                                          |
| ---------------- | -------------------------------------------- | ---------------------------------------------------- |
| `log_path`       | `"observai_events.log"`                    | Local fallback file for JSON-lines dumps             |
| `truncate`       | `500`                                        | Max chars for prompt/response (None = no truncation) |
| `flush_interval` | `2.0`                                        | Seconds between auto flushes                         |
| `db_path`        | `"observai_buffer.sqlite"`                 | SQLite path for crash-safe buffering                 |
| `endpoint`       | `https://collector.example.com/events/batch` | HTTP endpoint for batch POST’ing events              |
| `headers`        | `{}`                                         | HTTP headers to include on each POST                 |
| `background`     | `False`                                      | Whether to spawn the background thread               |

## Adapters

By default, ObservAI auto-detects and patches all supported SDKs (currently: OpenAI).

An adapter patches a third-party SDK (like OpenAI) to automatically intercept API calls.

To explicitly specify only the OpenAI adapter:

```python
from observai.adapters.openai import OpenAIChatAdapter

observai.init(adapters=[OpenAIChatAdapter()])
```

✅ Compatible with `openai>=1.0.0`

## Packaging & Tests

* **Source layout**: follows the `src/` layout best practice
* **Package metadata**: see [`pyproject.toml`](./pyproject.toml)
* **Example script**: [`example.py`](./example.py)
* **Smoke test**: [`tests/test_integration.py`](./tests/test_integration.py)
* **Pre-commit**: run `pre-commit install && pre-commit run --all-files`

## What gets captured?

For each LLM call:

* API route (e.g. `chat.completions.create`)
* Model name
* Input prompt (truncated if configured)
* Output response (truncated if configured)
* Latency (ms)
* Timestamp
* User ID (if configured)
* SHA256 hash of prompt + response

## Flush Modes

* `flush(final=True)` sends events to the configured collector endpoint.
* `flush(final=False)` writes events to a local JSON-lines fallback file.
* Auto-flush mode (enabled via `background=True`) periodically calls `flush()` in a background thread.
* All buffered events are flushed on process exit via `atexit`.

## Roadmap

* Anthropic adapters ??
