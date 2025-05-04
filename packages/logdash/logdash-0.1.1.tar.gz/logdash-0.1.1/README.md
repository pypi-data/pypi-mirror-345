# LogDash Python SDK

The official Python SDK for LogDash - a simple and powerful logging and metrics service.

## Installation

```bash
pip install logdash
```

## Features

- Colorized console logging
- Remote log aggregation
- Metrics tracking
- Support for multiple log levels
- Fully Pythonic implementation

## Usage

### Basic Usage

```python
from logdash import create_logdash

# Initialize LogDash with your API key
logdash = create_logdash({
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

### Complete Example

Check out the examples directory for more detailed examples.

```python
#!/usr/bin/env python3
import time
from logdash import create_logdash

# Initialize LogDash
logdash = create_logdash({
    "api_key": "your-api-key",  # Replace with your actual API key
    "verbose": True,  # Enable verbose mode for development
})

logger = logdash["logger"]
metrics = logdash["metrics"]

# Log at different levels
logger.info("Application started")
logger.debug("Debug information")
logger.warn("Warning message")
logger.error("Error occurred")

# Track metrics
metrics.set("active_users", 100)
metrics.mutate("requests_count", 1)
```

## Requirements

- Python 3.7+
- requests
- colorama

## Development

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e .
```

## License

MIT
