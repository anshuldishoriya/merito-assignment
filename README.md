# Heartbeat Monitoring System

A simple heartbeat monitoring system that detects when services fail to send expected heartbeat signals. If a service misses 3 consecutive heartbeats, the system triggers an alert.

## Requirements

- Python 3.7 or higher
- No external dependencies required

## File Structure

```
.
├── events.json
├── main.py
├── test_heartbeat_monitor.py
├── requirements.txt
└── README.md
```

## Setup

No installation is required. The project uses only Python's standard library.

Ensure you have Python 3.7 or higher installed:

```bash
python --version
```

## Running the Main Program

To run the heartbeat monitor on the provided events.json file:

```bash
python main.py
```

This will load events from events.json and print any alerts in JSON format.

Example output:

```json
[
  {
    "service": "email",
    "alert_at": "2025-08-04T10:05:00Z"
  }
]
```

## Running Tests

To run all unit tests:

```bash
python -m unittest test_heartbeat_monitor.py
```

To run tests with verbose output:

```bash
python -m unittest test_heartbeat_monitor.py -v
```

## Test Cases

The test suite includes the following required test cases:

1. Working Alert Case - Service misses 3+ consecutive heartbeats and alert is generated
2. Near-Miss Case - Service misses only 2 consecutive heartbeats, no alert generated
3. Unordered Input - Events arrive out of chronological order, system sorts correctly
4. Malformed Events - Invalid events are skipped gracefully without crashing

## Algorithm

The system processes heartbeat events using the following steps:

1. Filter out malformed events (missing fields or invalid timestamps)
2. Group events by service name
3. Sort events chronologically per service
4. Detect gaps between consecutive heartbeats
5. Generate alerts when a service misses 3 or more consecutive expected heartbeats

## Configuration

Default parameters in main.py:
- expected_interval_seconds: 60 (heartbeats expected every 60 seconds)
- allowed_misses: 3 (alert after 3 consecutive misses)

To change these values, edit the configuration section in main.py.
