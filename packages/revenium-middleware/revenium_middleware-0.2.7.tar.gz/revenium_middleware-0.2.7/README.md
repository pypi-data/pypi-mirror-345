# 🔄 Revenium Core Middleware

[![PyPI version](https://img.shields.io/pypi/v/revenium-middleware-core.svg)](https://pypi.org/project/revenium-middleware-core/)
[![Python Versions](https://img.shields.io/pypi/pyversions/revenium-middleware-core.svg)](https://pypi.org/project/revenium-middleware-core/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

A foundational library that provides core metering functionality shared across all Revenium AI provider-specific middleware implementations (OpenAI, Anthropic, Ollama, etc). 🐍✨

## ✨ Features

- **🧠 Shared Core Functionality**: Provides the essential metering infrastructure used by all Revenium middleware implementations
- **🔄 Asynchronous Processing**: Background thread management for non-blocking metering operations
- **🛑 Graceful Shutdown**: Ensures all metering data is properly sent even during application shutdown
- **🔌 Provider Agnostic**: Designed to work with any AI provider through specific middleware implementations

## 📥 Installation

```bash
pip install revenium-middleware
```

## 🔧 Usage

### 🔄 Direct Usage

While this package is primarily intended as a dependency for provider-specific middleware, you can use it directly:

```python
from revenium_middleware import client, run_async_in_thread, shutdown_event

# Record usage directly
client.record_usage(
    model="gpt-4o",
    prompt_tokens=500,
    completion_tokens=200,
    user_id="user123",
    session_id="session456"
)

# Run async metering tasks in background threads
async def async_metering_task():
    await client.async_record_usage(
        model="gpt-3.5-turbo",
        prompt_tokens=300,
        completion_tokens=150,
        user_id="user789"
    )

thread = run_async_in_thread(async_metering_task())

# Application continues while metering happens in background
```

### 🏗️ Building Provider-Specific Middleware

This library is designed to be extended by provider-specific middleware implementations:

```python
from revenium_middleware import client, run_async_in_thread

# Example of how a provider-specific middleware might use the core
def record_provider_usage(response_data, metadata):
    # Extract token counts from provider-specific response format
    prompt_tokens = response_data.usage.prompt_tokens
    completion_tokens = response_data.usage.completion_tokens
    
    # Use the core client to record the usage
    run_async_in_thread(
        client.async_record_usage(
            model=response_data.model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            **metadata
        )
    )
```

## 🔄 Compatibility

- 🐍 Python 3.8+
- 🤝 Compatible with all Revenium provider-specific middleware implementations

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

## 📚 Documentation

For more detailed documentation, please refer to the docstrings in the code or visit our GitHub repository.

## 👥 Contributing

Contributions are welcome! Please check out our contributing guidelines for details.

1. 🍴 Fork the repository
2. 🌿 Create your feature branch (`git checkout -b feature/amazing-feature`)
3. 💾 Commit your changes (`git commit -m 'Add some amazing feature'`)
4. 🚀 Push to the branch (`git push origin feature/amazing-feature`)
5. 🔍 Open a Pull Request

## 📄 License

This project is licensed under the Apache Software License - see the LICENSE file for details.

## 🙏 Acknowledgments

- 💖 Built with ❤️ by the Revenium team
