
import unittest
from main import detect_heartbeat_alerts, filter_valid_events, group_by_service


class TestHeartbeatMonitor(unittest.TestCase):
    def test_working_alert_case(self):
        """
        Test Case 1: Working Alert
        A service misses 3+ consecutive heartbeats and an alert is generated.
        """
        events = [
            {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:01:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:02:00Z"},
            # Missing: 10:03, 10:04, 10:05 (3 consecutive misses)
            {"service": "email", "timestamp": "2025-08-04T10:06:00Z"}
        ]

        expected_interval_seconds = 60
        allowed_misses = 3

        alerts = detect_heartbeat_alerts(events, expected_interval_seconds, allowed_misses)

        # should generate 1 alert
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['service'], 'email')
        # alert should be at the time of the 3rd miss: 10:02 + 3*60s = 10:05
        self.assertEqual(alerts[0]['alert_at'], '2025-08-04T10:05:00Z')

    def test_near_miss_case(self):
        """
        Test Case 2: Near-Miss (No Alert)
        A service misses only 2 consecutive heartbeats, so no alert is generated.
        """
        events = [
            {"service": "sms", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "sms", "timestamp": "2025-08-04T10:01:00Z"},
            # Missing: 10:02, 10:03
            {"service": "sms", "timestamp": "2025-08-04T10:04:00Z"}
        ]

        expected_interval_seconds = 60
        allowed_misses = 3

        alerts = detect_heartbeat_alerts(events, expected_interval_seconds, allowed_misses)
        # should not generate any alerts
        self.assertEqual(len(alerts), 0)

    def test_unordered_input(self):
        """
        Test Case 3: Unordered Input
        Events arrive out of chronological order.
        The system should sort them and process correctly.
        """
        events = [
            {"service": "push", "timestamp": "2025-08-04T10:06:00Z"},  # Out of order
            {"service": "push", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "push", "timestamp": "2025-08-04T10:02:00Z"},  # Out of order
            {"service": "push", "timestamp": "2025-08-04T10:01:00Z"}
            # Missing: 10:03, 10:04, 10:05 (3 consecutive misses after sorting)
        ]

        expected_interval_seconds = 60
        allowed_misses = 3

        alerts=detect_heartbeat_alerts(events ,expected_interval_seconds ,allowed_misses)

        # after sorting, should detect the gap and generate 1alert
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['service'], 'push')
        self.assertEqual(alerts[0]['alert_at'], '2025-08-04T10:05:00Z')

    def test_malformed_events(self):
        """
        Test Case 4: Malformed Events
        System should gracefully skip malformed events without crashing.

        Malformed cases:
        - Missing 'service' field
        - Missing 'timestamp' field
        - Invalid timestamp format
        """
        events = [
            {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},  # Valid
            {"timestamp": "2025-08-04T10:01:00Z"},  # Missing 'service'
            {"service": "email"},  # Missing 'timestamp'
            {"service": "email", "timestamp": "not-a-real-timestamp"},  # Invalid timestamp
            {"service": "email", "timestamp": "2025-08-04T10:01:00Z"},  # Valid
            {"service": "email", "timestamp": "2025-08-04T10:02:00Z"}   # Valid
        ]

        expected_interval_seconds = 60
        allowed_misses = 3

        # Should not crash
        alerts = detect_heartbeat_alerts(events, expected_interval_seconds, allowed_misses)

        self.assertEqual(len(alerts), 0)

    def test_filter_valid_events(self):
        """
        Additional test: Verify event filtering works correctly.
        """
        events = [
            {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},  # Valid
            {"timestamp": "2025-08-04T10:01:00Z"},  # Missing 'service'
            {"service": "email"},  # Missing 'timestamp'
            {"service": "email", "timestamp": "invalid-time"},  # Invalid timestamp
            {"service": "", "timestamp": "2025-08-04T10:02:00Z"},  # Empty service
        ]

        valid_events = filter_valid_events(events)

        # Only 1 valid event
        self.assertEqual(len(valid_events), 1)
        self.assertEqual(valid_events[0]['service'], 'email')

    def test_group_by_service(self):
        """
        Additional test: Verify service grouping works correctly.
        """
        events = [
            {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "sms", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:01:00Z"},
            {"service": "push", "timestamp": "2025-08-04T10:00:00Z"},
        ]

        grouped = group_by_service(events)

        self.assertEqual(len(grouped), 3)
        self.assertEqual(len(grouped['email']), 2)
        self.assertEqual(len(grouped['sms']), 1)
        self.assertEqual(len(grouped['push']), 1)

    def test_multiple_services_with_alerts(self):
        """
        Test Case 5: Multiple Services with Alerts
        Multiple services each miss 3+ consecutive heartbeats.
        Verify that alerts are triggered independently for each service.
        """
        events = [
            # Email service - should trigger alert
            {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:01:00Z"},
            # Missing: 10:02, 10:03, 10:04 (3 misses)
            {"service": "email", "timestamp": "2025-08-04T10:05:00Z"},

            # SMS service - should trigger alert
            {"service": "sms", "timestamp": "2025-08-04T10:00:00Z"},
            # Missing: 10:01, 10:02, 10:03 (3 misses)
            {"service": "sms", "timestamp": "2025-08-04T10:04:00Z"},

            # Push service - should trigger alert
            {"service": "push", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "push", "timestamp": "2025-08-04T10:01:00Z"},
            {"service": "push", "timestamp": "2025-08-04T10:02:00Z"},
            # Missing: 10:03, 10:04, 10:05 (3 misses)
            {"service": "push", "timestamp": "2025-08-04T10:06:00Z"}
        ]

        expected_interval_seconds = 60
        allowed_misses = 3

        alerts = detect_heartbeat_alerts(events, expected_interval_seconds, allowed_misses)
        self.assertEqual(len(alerts), 3)

        alert_by_service = {alert['service']: alert['alert_at'] for alert in alerts}

        # alert for email service
        self.assertIn('email', alert_by_service)
        self.assertEqual(alert_by_service['email'], '2025-08-04T10:04:00Z')

        # alert for sms service
        self.assertIn('sms', alert_by_service)
        self.assertEqual(alert_by_service['sms'], '2025-08-04T10:03:00Z')

        # push service alert
        self.assertIn('push', alert_by_service)
        self.assertEqual(alert_by_service['push'], '2025-08-04T10:05:00Z')


if __name__ == '__main__':
    unittest.main()
