# Aitronos Logger

A sophisticated logging module that provides JSON-based logging with insights and time estimation capabilities. The logger stores all logs in a structured JSON format, making it easy to analyze and process log data programmatically.

## Features

- JSON-based logging with structured data
- Time-based progress tracking with remaining time estimation
- Smart stack trace detection
- Multiple log types (info, alert, error)
- Automatic component detection from caller
- Customizable severity levels (0-5)
- Thread-safe file operations
- Support for metadata in logs
- Support Stream Handler for Real-Time Logs

## Installation

```bash
pip install aitronos-logger
```

## Usage

### Basic Usage

```python
from aitronos_logger import Logger

# Initialize the logger (all parameters optional)
logger = Logger(
    automation_execution_id="my-execution-123",
    metadata={"environment": "production"}
)

# Basic logging with progress and time estimation
logger.info(
    "Processing started",
    progress=25,  # 25% complete
    remaining_time_seconds=300  # 5 minutes remaining
)

# Alert with progress update
logger.alert(
    "Important notification",
    severity=3,
    progress=50,  # 50% complete
    remaining_time_seconds=150  # 2.5 minutes remaining
)

# Error logging with progress
try:
    result = 1 / 0
except Exception as e:
    # Stack trace and error details are automatically captured
    logger.error(
        "Division error occurred",
        progress=75,  # 75% complete
        remaining_time_seconds=60,  # 1 minute remaining
        exc=e
    )

# Add custom metadata to any log
logger.info(
    "User action completed",
    severity=1,
    metadata={"user_id": "123", "action": "login"},
    progress=90,  # 90% complete
    remaining_time_seconds=30  # 30 seconds remaining
)
```

### Progress and Time Tracking

The logger provides flexible ways to track progress and remaining time:

```python
# Set progress with remaining time
logger.info(
    "Processing batch 1",
    progress=25,
    remaining_time_seconds=300
)

# Progress only (remaining time will be auto-calculated)
logger.info(
    "Processing batch 2",
    progress=50
)

# Only remaining time (progress will be auto-calculated)
logger.info(
    "Processing batch 3",
    remaining_time_seconds=150
)

# Final completion
logger.info(
    "Process completed",
    progress=100,
    remaining_time_seconds=0
)
```

### Log File Structure

The logger creates a JSON file (`execution_log.json`) with structured log entries:

```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "automation_execution_id": "my-execution-123",
    "entries": [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "timestamp": 1706062800000,
            "progress": {
                "elapsed_time_seconds": 120,
                "progress_percentage": 50,
                "remaining_time_seconds": 150
            },
            "type": "info",
            "message": "Processing batch 2",
            "component": "MainApp",  // Automatically detected
            "severity": 1,
            "stack_trace": {
                "file_name": "main.py",
                "line_number": 10,
                "function_name": "process_batch"
            }
        }
    ],
    "metadata": {
        "environment": "production"
    }
}
```

### Log Types and Severity

Each log type supports severity levels (0-5) for fine-grained control:

- `info(message, severity=1)`: General information (default severity 1)
- `alert(message, severity=3)`: Important notifications (default severity 3)
- `error(message, severity=5)`: Error messages (default severity 5)

Common parameters for all log methods:
- `message`: The log message
- `severity`: Optional severity level (0-5)
- `component`: Optional component name (auto-detected if not provided)
- `metadata`: Optional dictionary of additional data
- `progress`: Optional progress value (0-100)
- `remaining_time_seconds`: Optional estimate of remaining time in seconds

Features automatically handled by the logger:
- Time-based progress tracking
- Automatic remaining time calculation when only progress is provided
- Automatic progress calculation when only remaining time is provided
- Stack trace capture for errors
- Component detection from caller
- Timestamp and log ID generation
- File locking for thread safety
- JSON-formatted logs prefixed with `log:` for easy parsing

### Insights and Monitoring

Get real-time insights into your logging:

```python
logger.display_insights()
```

Output:
```
---- Log Insights ----
Total Logs: 5
Info Logs: 3
Alerts: 1
Errors: 1
Estimated Time Remaining: ~150 seconds remaining
-----------------------
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install in development mode:
   ```bash
   pip install -e .
   ```

### Version Management

The project includes a version management script that handles version bumping, package building, and publishing:

```bash
# Bump patch version (0.1.0 -> 0.1.1)
python scripts/update_version.py patch

# Bump minor version (0.1.0 -> 0.2.0)
python scripts/update_version.py minor

# Bump major version (0.1.0 -> 1.0.0)
python scripts/update_version.py major

# Test upload to TestPyPI
python scripts/update_version.py patch --test

# Skip git operations
python scripts/update_version.py patch --no-git
```

The script will:
1. Bump the version in `pyproject.toml`
2. Clean build directories
3. Build the package (sdist and wheel)
4. Commit all code changes and create a git tag
5. Upload to PyPI (or TestPyPI with `--test`)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
