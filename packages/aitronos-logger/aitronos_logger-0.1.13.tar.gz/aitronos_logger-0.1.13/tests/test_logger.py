import json
import os
import pytest
import time
from aitronos_logger.logger import Logger

def safe_remove_file(file_path):
    """Safely remove a file with retries."""
    max_retries = 5
    retry_delay = 0.2
    
    for attempt in range(max_retries):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return
        except (OSError, IOError):
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            continue
        except Exception:
            pass

def cleanup_test_files():
    """Clean up test files."""
    safe_remove_file(Logger.LOG_FILE)

@pytest.fixture(autouse=True)
def unique_log_files(request):
    """Create unique log files for each test."""
    # Save original log file name
    original_log = Logger.LOG_FILE
    
    # Create unique name for this test
    test_name = request.node.name.replace("[", "_").replace("]", "_")
    Logger.LOG_FILE = f"test_{test_name}_log.json"
    
    yield
    
    # Clean up test files
    cleanup_test_files()
    
    # Restore original name
    Logger.LOG_FILE = original_log

@pytest.fixture
def logger(unique_log_files):
    """Create a logger instance for testing."""
    logger_instance = Logger(automation_execution_id="test-automation-001")
    # Wait for initialization to complete
    time.sleep(0.1)
    return logger_instance

def wait_for_log_write(expected_entries=1, timeout=1.0):
    """Wait for log write to complete and verify file exists."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            if os.path.exists(Logger.LOG_FILE):
                with open(Logger.LOG_FILE, 'r') as f:
                    data = json.load(f)
                    if len(data.get("entries", [])) >= expected_entries:
                        return True
        except (json.JSONDecodeError, IOError):
            pass
        time.sleep(0.05)
    return False

def read_log_file():
    """Read the log file with retries."""
    max_retries = 3
    retry_delay = 0.05
    
    for _ in range(max_retries):
        try:
            if not os.path.exists(Logger.LOG_FILE):
                return {"entries": [], "automation_execution_id": None}
            with open(Logger.LOG_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict) and "entries" in data:
                    return data
        except Exception:
            if _ < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise
    return {"entries": [], "automation_execution_id": None}

def test_logger_initialization(logger):
    """Test logger initialization and file structure"""
    assert os.path.exists(Logger.LOG_FILE)
    data = read_log_file()
    assert "id" in data
    assert data["automation_execution_id"] == "test-automation-001"
    assert "entries" in data
    assert isinstance(data["entries"], list)
    assert "metadata" in data
    assert isinstance(data["metadata"], dict)

def test_queue_processing(logger):
    """Test that the queue processes logs in order"""
    messages = [f"Message {i}" for i in range(5)]
    expected_entries = len(messages) + 1  # +1 for initialization entry
    
    # Send all messages quickly
    for msg in messages:
        logger.info(msg)
    
    # Wait for all messages to be processed
    assert wait_for_log_write(expected_entries=expected_entries, timeout=2.0)
    
    # Verify messages are in order
    data = read_log_file()
    logged_messages = [entry["message"] for entry in data["entries"][1:]]  # Skip init entry
    assert logged_messages == messages

def test_queue_shutdown(logger):
    """Test that the queue processes remaining logs on shutdown"""
    messages = [f"Shutdown message {i}" for i in range(3)]
    expected_entries = len(messages) + 1  # +1 for initialization entry
    
    # Send all messages
    for msg in messages:
        logger.info(msg)
    
    # Wait for messages to be queued
    time.sleep(0.1)
    
    # Force logger cleanup
    logger.__del__()
    
    # Wait a bit for shutdown processing
    time.sleep(0.2)
    
    # Verify all messages were processed
    data = read_log_file()
    logged_messages = [entry["message"] for entry in data["entries"][1:]]  # Skip init entry
    
    # Check that all messages are present and in order
    assert logged_messages == messages

def test_info_logging_with_auto_component(logger):
    """Test info logging with automatic component detection"""
    logger.info("Test info message")
    assert wait_for_log_write(expected_entries=2)  # Init entry + new entry
    data = read_log_file()
    
    # Verify log file has entries
    assert len(data["entries"]) >= 2
    latest_log = data["entries"][-1]
    
    assert latest_log["type"] == "info"
    assert latest_log["message"] == "Test info message"
    assert latest_log["component"] == "test_logger"  # Auto-detected from filename
    assert latest_log["severity"] == 1  # Default severity for info
    assert "stack_trace" in latest_log
    assert "file_name" in latest_log["stack_trace"]
    assert "line_number" in latest_log["stack_trace"]
    assert "function_name" in latest_log["stack_trace"]
    assert "progress" in latest_log
    assert "progress_percentage" in latest_log["progress"]
    assert "elapsed_time_seconds" in latest_log["progress"]
    assert "remaining_time_seconds" in latest_log["progress"]

def test_info_logging_with_custom_severity(logger):
    """Test info logging with custom severity"""
    logger.info("Test info message", severity=3)
    assert wait_for_log_write(expected_entries=2)
    data = read_log_file()
    latest_log = data["entries"][-1]
    assert latest_log["severity"] == 3

def test_info_logging_with_manual_component(logger):
    """Test info logging with manually specified component"""
    logger.info("Test info message", component="TestComponent")
    assert wait_for_log_write(expected_entries=2)
    data = read_log_file()
    latest_log = data["entries"][-1]
    
    assert latest_log["type"] == "info"
    assert latest_log["message"] == "Test info message"
    assert latest_log["component"] == "TestComponent"
    assert latest_log["severity"] == 1

def test_info_logging_with_metadata(logger):
    """Test info logging with metadata"""
    metadata = {"key1": "value1", "key2": "value2"}
    logger.info("Test info message", metadata=metadata)
    assert wait_for_log_write(expected_entries=2)
    data = read_log_file()
    latest_log = data["entries"][-1]
    
    assert "metadata" in latest_log
    assert latest_log["metadata"] == metadata

class TestLoggerInClass:
    def test_component_from_class(self, logger):
        """Test component auto-detection from class"""
        logger.info("Test message from class")
        assert wait_for_log_write(expected_entries=2)
        data = read_log_file()
        latest_log = data["entries"][-1]
        assert latest_log["component"] == "TestLoggerInClass"

def test_error_logging_with_auto_component(logger):
    """Test error logging with automatic component detection"""
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.error("Test error message", exc=e)
    
    assert wait_for_log_write(expected_entries=2)
    data = read_log_file()
    latest_log = data["entries"][-1]
    assert latest_log["type"] == "error"
    assert latest_log["message"] == "Test error message"
    assert latest_log["component"] == "test_logger"
    assert latest_log["severity"] == 5
    assert "stack_trace" in latest_log
    assert "metadata" in latest_log
    assert "exception_type" in latest_log["metadata"]
    assert latest_log["metadata"]["exception_type"] == "ValueError"

def test_error_logging_with_manual_component(logger):
    """Test error logging with manually specified component"""
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.error("Test error message", component="TestComponent", exc=e)
    
    assert wait_for_log_write(expected_entries=2)
    data = read_log_file()
    latest_log = data["entries"][-1]
    assert latest_log["type"] == "error"
    assert latest_log["message"] == "Test error message"
    assert latest_log["component"] == "TestComponent"
    assert latest_log["severity"] == 5
    assert "stack_trace" in latest_log
    assert "metadata" in latest_log
    assert "exception_type" in latest_log["metadata"]
    assert latest_log["metadata"]["exception_type"] == "ValueError"

def test_alert_logging(logger):
    """Test alert logging"""
    logger.alert("Test alert")
    assert wait_for_log_write(expected_entries=2)
    data = read_log_file()
    latest_log = data["entries"][-1]
    assert latest_log["type"] == "alert"
    assert latest_log["component"] == "test_logger"
    assert latest_log["severity"] == 3

def test_progress_tracking(logger):
    """Test progress tracking functionality with numeric values"""
    # Test with integer progress and remaining time
    logger.info("Progress check 1", progress=25, remaining_time_seconds=300)
    assert wait_for_log_write(expected_entries=2)
    
    data = read_log_file()
    first_log = data["entries"][-1]
    
    # Test with float progress only (auto-calculated remaining time)
    logger.info("Progress check 2", progress=50.5)
    assert wait_for_log_write(expected_entries=3)
    
    data = read_log_file()
    second_log = data["entries"][-1]
    
    # Test with only remaining time
    logger.info("Progress check 3", remaining_time_seconds=150)
    assert wait_for_log_write(expected_entries=4)
    
    data = read_log_file()
    third_log = data["entries"][-1]
    
    # Check first log (explicit progress and time)
    assert first_log["progress"]["progress_percentage"] == 25
    assert first_log["progress"]["remaining_time_seconds"] == 300
    assert first_log["progress"]["elapsed_time_seconds"] >= 0
    
    # Check second log (auto-calculated remaining time)
    assert second_log["progress"]["progress_percentage"] == 50.5
    assert second_log["progress"]["elapsed_time_seconds"] >= 0
    assert second_log["progress"]["remaining_time_seconds"] >= 0
    
    # Check third log (auto-calculated progress)
    assert third_log["progress"]["remaining_time_seconds"] == 150
    assert third_log["progress"]["elapsed_time_seconds"] >= 0
    assert 0 <= third_log["progress"]["progress_percentage"] <= 100

def test_progress_bounds(logger):
    """Test that progress values are properly bounded between 0 and 100"""
    # Test negative progress
    logger.info("Test negative progress", progress=-10)
    assert wait_for_log_write(expected_entries=2)
    
    # Test progress > 100
    logger.info("Test high progress", progress=150)
    assert wait_for_log_write(expected_entries=3)
    
    data = read_log_file()
    assert data["entries"][-2]["progress"]["progress_percentage"] == 0  # Should be bounded to 0
    assert data["entries"][-1]["progress"]["progress_percentage"] == 100  # Should be bounded to 100

def test_progress_with_no_value(logger):
    """Test progress when no value is provided"""
    logger.info("Test no progress")
    assert wait_for_log_write(expected_entries=2)
    
    data = read_log_file()
    latest_log = data["entries"][-1]
    assert latest_log["progress"]["progress_percentage"] == 0
    assert latest_log["progress"]["remaining_time_seconds"] == 0
    assert latest_log["progress"]["elapsed_time_seconds"] >= 0

def test_progress_time_estimation(logger):
    """Test that remaining time is estimated correctly based on progress"""
    # Add a delay to simulate elapsed time
    time.sleep(1)
    
    # Test explicit remaining time
    logger.info("Explicit time", progress=50, remaining_time_seconds=60)
    assert wait_for_log_write(expected_entries=2)
    
    data = read_log_file()
    first_log = data["entries"][-1]
    assert first_log["progress"]["remaining_time_seconds"] == 60
    
    # Test auto-calculated remaining time
    logger.info("Auto time", progress=50)
    assert wait_for_log_write(expected_entries=3)
    
    data = read_log_file()
    second_log = data["entries"][-1]
    
    elapsed = second_log["progress"]["elapsed_time_seconds"]
    remaining = second_log["progress"]["remaining_time_seconds"]
    
    assert elapsed >= 1  # Should be at least our sleep time
    assert remaining >= 0  # Should estimate remaining time based on progress
    # Since we're at 50%, remaining should be approximately equal to elapsed
    assert abs(remaining - elapsed) <= 1  # Allow 1 second tolerance for timing variations

def test_severity_bounds(logger):
    """Test that severity is properly bounded between 0 and 5"""
    logger.info("Test negative severity", severity=-1)
    assert wait_for_log_write(expected_entries=2)
    
    logger.alert("Test high severity", severity=10)
    assert wait_for_log_write(expected_entries=3)
    
    data = read_log_file()
    assert data["entries"][-2]["severity"] == 0  # Should be bounded to 0
    assert data["entries"][-1]["severity"] == 5  # Should be bounded to 5

def test_stack_trace_format(logger):
    """Test that stack trace contains all required fields"""
    logger.info("Test stack trace")
    assert wait_for_log_write(expected_entries=2)
    
    data = read_log_file()
    latest_log = data["entries"][-1]
    stack_trace = latest_log["stack_trace"]
    
    assert "file_name" in stack_trace
    assert "line_number" in stack_trace
    assert "function_name" in stack_trace
    assert isinstance(stack_trace["line_number"], int)
    assert isinstance(stack_trace["file_name"], str)
    assert isinstance(stack_trace["function_name"], str)

def test_metadata_limits(logger):
    """Test metadata size limits"""
    # Create metadata with more than 16 keys and values longer than 512 chars
    large_metadata = {
        f"key_{i}": "x" * 600 for i in range(20)
    }
    
    logger.info("Test metadata limits", metadata=large_metadata)
    assert wait_for_log_write(expected_entries=2)
    data = read_log_file()
    latest_log = data["entries"][-1]
    
    assert len(latest_log["metadata"]) <= 16  # Should be limited to 16 keys
    for value in latest_log["metadata"].values():
        assert len(value) <= 512  # Values should be truncated to 512 chars

def test_multiple_automations():
    """Test handling of multiple automation executions"""
    # Create first logger with its own file
    first_log_file = "test_first_automation_log.json"
    Logger.LOG_FILE = first_log_file
    first_logger = Logger(automation_execution_id="test-automation-001")
    time.sleep(0.1)  # Wait for initialization
    first_logger.info("First automation log")
    assert wait_for_log_write(expected_entries=2)
    
    # Create second logger with its own file
    second_log_file = "test_second_automation_log.json"
    Logger.LOG_FILE = second_log_file
    second_logger = Logger(automation_execution_id="test-automation-002")
    time.sleep(0.1)  # Wait for initialization
    second_logger.info("Second automation log")
    assert wait_for_log_write(expected_entries=2)
    
    # Clean up loggers
    first_logger.__del__()
    second_logger.__del__()
    
    # Verify first logger's data
    Logger.LOG_FILE = first_log_file
    first_data = read_log_file()
    assert first_data["automation_execution_id"] == "test-automation-001"
    assert len(first_data["entries"]) == 2
    assert first_data["entries"][-1]["message"] == "First automation log"
    
    # Verify second logger's data
    Logger.LOG_FILE = second_log_file
    second_data = read_log_file()
    assert second_data["automation_execution_id"] == "test-automation-002"
    assert len(second_data["entries"]) == 2
    assert second_data["entries"][-1]["message"] == "Second automation log"
    
    # Clean up test files
    safe_remove_file(first_log_file)
    safe_remove_file(second_log_file)

def test_queue_error_handling(logger):
    """Test that queue continues processing after errors"""
    # Create a temporary backup of the log file
    if os.path.exists(Logger.LOG_FILE):
        with open(Logger.LOG_FILE, 'r') as f:
            original_content = f.read()
    
    # Corrupt the log file to cause a JSON error
    with open(Logger.LOG_FILE, 'w') as f:
        f.write("invalid json{")
    
    # Try to log a message
    logger.info("Test message after corruption")
    assert wait_for_log_write(expected_entries=1, timeout=2.0)
    
    # Verify the logger recovered and created a new valid log file
    data = read_log_file()
    assert "entries" in data
    assert any(entry["message"] == "Test message after corruption" for entry in data["entries"])

def test_queue_shutdown_timeout(logger):
    """Test queue shutdown with timeout"""
    # Add a lot of messages just before shutdown
    messages = [f"Last minute message {i}" for i in range(100)]
    for msg in messages:
        logger.info(msg)
    
    # Force immediate shutdown
    start_time = time.time()
    logger.__del__()
    shutdown_time = time.time() - start_time
    
    # Verify shutdown completed within reasonable time
    assert shutdown_time < 6.0  # Should respect the 5-second timeout
    
    # Verify at least some messages were processed
    data = read_log_file()
    logged_messages = [entry["message"] for entry in data["entries"]]
    assert any(msg in logged_messages for msg in messages)

def test_progress_status(logger):
    """Test progress information when no progress is provided"""
    logger.info("Test no progress")
    assert wait_for_log_write(expected_entries=2)
    
    data = read_log_file()
    latest_log = data["entries"][-1]
    assert "progress" in latest_log
    assert latest_log["progress"]["progress_percentage"] == 0
    assert latest_log["progress"]["remaining_time_seconds"] == 0
    assert latest_log["progress"]["elapsed_time_seconds"] >= 0

def test_concurrent_writes(logger):
    """Test that concurrent writes are handled properly through the queue"""
    num_messages = 10
    messages = [f"Concurrent message {i}" for i in range(num_messages)]
    
    # Send all messages rapidly
    for msg in messages:
        logger.info(msg)
    
    # Wait for all messages to be processed
    assert wait_for_log_write(expected_entries=num_messages + 1, timeout=3.0)  # +1 for init entry
    
    # Verify all messages were logged in order
    data = read_log_file()
    logged_messages = [entry["message"] for entry in data["entries"][1:]]  # Skip init entry
    assert logged_messages == messages

def test_queue_stress(logger):
    """Test queue under stress with rapid logging"""
    num_messages = 50
    messages = [f"Stress test message {i}" for i in range(num_messages)]
    
    # Rapidly send many messages
    for msg in messages:
        logger.info(msg)
    
    # Wait for all messages to be processed
    assert wait_for_log_write(expected_entries=num_messages + 1, timeout=5.0)
    
    # Verify all messages were processed
    data = read_log_file()
    logged_messages = [entry["message"] for entry in data["entries"][1:]]
    assert len(logged_messages) == num_messages
    assert logged_messages == messages 