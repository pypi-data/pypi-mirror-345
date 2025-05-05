# 🤖 Revenium Middleware for Anthropic

[![PyPI version](https://img.shields.io/pypi/v/revenium-middleware-anthropic.svg)](https://pypi.org/project/revenium-middleware-anthropic/)
[![Python Versions](https://img.shields.io/pypi/pyversions/revenium-middleware-anthropic.svg)](https://pypi.org/project/revenium-middleware-anthropic/)
[![Documentation Status](https://readthedocs.org/projects/revenium-middleware-anthropic/badge/?version=latest)](https://revenium-middleware-anthropic.readthedocs.io/en/latest/?badge=latest)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

[//]: # ([![Build Status]&#40;https://github.com/revenium/revenium-middleware-anthropic/actions/workflows/ci.yml/badge.svg&#41;]&#40;https://github.com/revenium/revenium-middleware-anthropic/actions&#41;)

A middleware library for metering and monitoring Anthropic API usage in Python applications. 🐍✨

## ✨ Features

- **📊 Precise Usage Tracking**: Monitor tokens, costs, and request counts across all Anthropic API endpoints
- **🔌 Seamless Integration**: Drop-in middleware that works with minimal code changes
- **⚙️ Flexible Configuration**: Customize metering behavior to suit your application needs

## 📥 Installation

```bash
pip install revenium-middleware-anthropic
```

## 🔧 Usage

### 🔄 Zero-Config Integration

Simply export your REVENIUM_METERING_API_KEY and import the middleware.
Your Anthropic calls will be metered automatically:

```python
import anthropic
import revenium_middleware_anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=20000,
    temperature=1,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                     "text": "What is the meaning of life, the universe and everything?",
                }
            ]
        }
    ]
)
print(message.content)
```

The middleware automatically intercepts Anthropic API calls and sends metering data to Revenium without requiring any
changes to your existing code. Make sure to set the `REVENIUM_METERING_API_KEY` environment variable for authentication
with the Revenium service.

### 📈 Enhanced Tracking with Metadata

For more granular usage tracking and detailed reporting, add the `usage_metadata` parameter:

```python
import anthropic
import revenium_middleware_anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=20000,
    temperature=1,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What is the meaning of life, the universe and everything?",
                }
            ]
        }
    ],
    usage_metadata={
        "trace_id": "conv-28a7e9d4-1c3b-4e5f-8a9b-7d1e3f2c1b4a",
        "task_id": "chat-summary-af23c910",
        "task_type": "text-classification",
        "subscriber_email": "customer-email@example.com",
        "organization_id": "acme-corporation-12345",
        "subscription_id": "startup-plan-quarterly-2025-Q1",
        "product_id": "intelligent-document-processor-v3",
        "agent": "customer-support-assistant-v2",
    }
)
print(message.content)
```

### 🔄 Streaming Support

The middleware also supports Anthropic's streaming API. For streaming responses, use the `usage_context` to set metadata before making the streaming call. The middleware will automatically track token usage and send metering data when the stream completes.

```python
import anthropic
from revenium_middleware_anthropic import usage_context

usage_context.set({
    "task_id": "task-41921",
    "agent": "network-traffic-analyzer",
    "subscriber_email": "ai@revenium.io",
    "organization_id": "devops-team-emea",
    "response_quality_score": 0.5,
})

with client.messages.stream(
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
    model="claude-3-5-sonnet-latest",
) as stream:
    for text in stream.text_stream:
        print("\n>>>" + text, end="", flush=True)

```


## 🏷️ Metadata Fields

The `usage_metadata` parameter supports the following fields:

| Field                    | Description                                     | Use Case                                                          |
|--------------------------|-------------------------------------------------|-------------------------------------------------------------------|
| `trace_id`               | Unique identifier for a conversation or session | Track multi-turn conversations                                    |
| `task_id`                | Identifier for a specific AI task               | Group related API calls for a single task                         |
| `task_type`              | Classification of the AI operation              | Categorize usage by purpose (e.g., classification, summarization) |
| `subscriber_email`       | The email address of the subscriber             | Track usage by individual users                                   |
| `subscriber_credential_name` | The name of the credential associated with the subscriber | Track usage by individual users                     |
| `subscriber_credential`  | The credential associated with the subscriber   | Track usage by individual users                                   |
| `organization_id`        | Customer or department identifier               | Allocate costs to business units                                  |
| `subscription_id`        | Reference to a billing plan                     | Associate usage with specific subscriptions                       |
| `product_id`             | The product or feature using AI                 | Track usage across different products                             |
| `agent`                  | Identifier for the specific AI agent            | Compare performance across different AI agents                    |
| `response_quality_score` | The quality of the AI response (0..1)           | Track AI response quality                                         |

All metadata fields are optional. Adding them enables more detailed reporting and analytics in Revenium.

## 🔄 Compatibility

- 🐍 Python 3.8+
- 🤖 Anthropic Python SDK
## 🔍 Logging

This module uses Python's standard logging system. You can control the log level by setting the `REVENIUM_LOG_LEVEL` environment variable:

```bash
# Enable debug logging
export REVENIUM_LOG_LEVEL=DEBUG

# Or when running your script
REVENIUM_LOG_LEVEL=DEBUG python your_script.py
```

Available log levels:
- `DEBUG`: Detailed debugging information
- `INFO`: General information (default)
- `WARNING`: Warning messages only
- `ERROR`: Error messages only
- `CRITICAL`: Critical error messages only

## 👥 Contributing

Contributions are welcome! Please check out our [contributing guidelines](CONTRIBUTING.md) for details.

1. 🍴 Fork the repository
2. 🌿 Create your feature branch (`git checkout -b feature/amazing-feature`)
3. 💾 Commit your changes (`git commit -m 'Add some amazing feature'`)
4. 🚀 Push to the branch (`git push origin feature/amazing-feature`)
5. 🔍 Open a Pull Request

## 📄 License

This project is licensed under the Apache Software License - see the LICENSE file for details.

## 🙏 Acknowledgments

- 🔥 Thanks to the Anthropic team for creating an excellent API
- 💖 Built with ❤️ by the Revenium team
