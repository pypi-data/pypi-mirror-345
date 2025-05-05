# Grimoire Logger

Grimoire Logger is a lightweight Python logging library that outputs logs in a
structured JSON format. It is designed to make log parsing and analysis easier,
especially in distributed systems or environments where structured logging is
essential.

## Features

- **JSON-formatted logs**: Logs are output in a machine-readable JSON format.
- **Multiple log levels**: Supports `info`, `warn`, `error`, and `debug` levels.
- **Timestamped logs**: Each log entry includes a timestamp for better
  traceability.
- **Source identification**: Automatically includes the source file in the log
  output.

## Installation

You can install Grimoire Logger by cloning this repository to a local place or
by using `pip`:

```bash
pip install grimoire_logger
```

## Usage

Here’s a quick example of how to use Grimoire Logger:

```python
from grimoire_logger import Logger

logger = Logger()

logger.info("This is an info message.")
logger.warn("This is a warning message.")
logger.error("This is an error message.")
logger.debug("This is a debug message.")
```

### Example Output

```json
{
  "timestamp": "2023-10-01 12:34:56",
  "level": "info",
  "source": "example.py",
  "message": "This is an info message."
}
```
