import json
from datetime import datetime, timedelta


def is_valid_event(event):
    """
    Check if event has required fields and valid timestamp.

    Args:
        event: Dictionary containing 'service' and 'timestamp' fields

    Returns:
        bool: True if event is valid, False otherwise
    """
    # Must have 'service' field
    if 'service' not in event or not event['service']:
        return False

    # Must have 'timestamp' field
    if 'timestamp' not in event:
        return False

    # Timestamp must be valid ISO format
    try:
        datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
        return True
    except (ValueError, AttributeError):
        return False


def filter_valid_events(events):
    """
    Filter out malformed events.

    Args:
        events: List of event dictionaries

    Returns:
        List of valid events
    """
    valid = []
    for event in events:
        if is_valid_event(event):
            valid.append(event)
    return valid


def group_by_service(events):
    # Group events by service name.
    service_map = {}
    for event in events:
        service = event['service']
        if service not in service_map:
            service_map[service] = []
        service_map[service].append(event)
    return service_map


def parse_timestamp(timestamp_str):
    # Parse ISO 8601 timestamp string to datetime object.
    return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))


def detect_gaps(service, sorted_heartbeats, interval_seconds, allowed_misses):
    """
    Detect alert-worthy gaps in heartbeat sequence.

    Logic:
    - Compare each consecutive pair of heartbeats
    - Calculate time gap in seconds
    - Calculate how many heartbeats were missed
    - If missed >= allowed_misses, create alert

    Args:
        service: Service name
        sorted_heartbeats: List of heartbeat events sorted chronologically
        interval_seconds: Expected interval between heartbeats
        allowed_misses: Number of consecutive misses before alerting

    Returns:
        List of alert dictionaries
    """
    alerts = []

    for i in range(len(sorted_heartbeats) - 1):
        current_time = parse_timestamp(sorted_heartbeats[i]['timestamp'])
        next_time = parse_timestamp(sorted_heartbeats[i + 1]['timestamp'])

        gap_seconds = (next_time - current_time).total_seconds()

        if ((gap_seconds // interval_seconds - 1) + int(gap_seconds % interval_seconds != 0)) >= allowed_misses:
            alert_time = current_time + timedelta(seconds=allowed_misses * interval_seconds)
            alerts.append({
                'service': service,
                'alert_at': alert_time.isoformat().replace('+00:00', 'Z')
            })

    return alerts


def detect_heartbeat_alerts (events ,expected_interval_seconds ,allowed_misses):
    """
    Main function to detect heartbeat monitoring alerts.

    Steps:
    1. Validate and filter events (skip malformed)
    2. Group events by service
    3. Sort events chronologically per service
    4. Detect gaps >= allowed_misses * interval
    5. Return alerts

    Args:
        events: List of heartbeat event dictionaries
        expected_interval_seconds: Expected interval between heartbeats (e.g., 60)
        allowed_misses: Number of consecutive misses before alerting (e.g., 3)

    Returns:
        List of alert dictionaries with 'service' and 'alert_at' fields
    """
    valid_events = filter_valid_events(events)
    service_events = group_by_service(valid_events)

    # Process each services
    alerts = []
    for service, heartbeats in service_events.items():
        # Sort chronologically
        heartbeats.sort(key=lambda x: x['timestamp'])

        service_alerts = detect_gaps(service, heartbeats, expected_interval_seconds, allowed_misses)
        alerts.extend(service_alerts)

    return alerts


def main():
    #Load events from JSON file
    with open('events.json', 'r') as f:
        events = json.load(f)

    # Configuration parameters
    expected_interval_seconds = 60
    allowed_misses = 3

    alerts = detect_heartbeat_alerts(events, expected_interval_seconds, allowed_misses)
    print(json.dumps(alerts, indent=2))


if __name__ == '__main__':
    main()
