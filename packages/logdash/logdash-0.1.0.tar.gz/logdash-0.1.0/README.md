# LogDash Python SDK

This is the official Python SDK for LogDash - a simple and powerful logging and metrics service.

## Installation

```bash
pip install logdash
```

## Usage

### Basic Usage

```python
from logdash import create_logdash

# Initialize LogDash with your API key
logdash = create_logdash(params={
    "api_key": "your-api-key-here",
    "host": "https://api.logdash.io",  # optional, default value shown
    "verbose": False  # optional, default value shown
})

# Access the logger
logger = logdash["logger"]
logger.info("This is an info message")
logger.error("This is an error message")
logger.debug("This is a debug message")

# Log levels supported:
# - error
# - warn
# - info (also available as log())
# - http
# - verbose
# - debug
# - silly

# Access metrics
metrics = logdash["metrics"]
metrics.set("page_views", 100)  # Set a metric value
metrics.mutate("user_count", 1)  # Change a metric by a value (increment/decrement)
```

### Local Development

If you don't provide an API key, logs will only be output locally and metrics will not be tracked:

```python
from logdash import create_logdash

# Local only logger
logdash = create_logdash()
logdash["logger"].info("This will only be logged locally")
```

## License

MIT
