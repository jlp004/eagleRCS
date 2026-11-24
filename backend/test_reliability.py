import unittest
from unittest.mock import patch
from crc import calculate_crc, verify_crc
from retransmission import RetransmissionManager


class TestCRC(unittest.TestCase):
    def test_crc_calculation(self):
        self.assertEqual(calculate_crc(b"Hello"), 4157704578)

    def test_valid_message(self):
        message = b"Hello"
        self.assertTrue(verify_crc(message, calculate_crc(message)))

    def test_corrupted_message(self):
        checksum = calculate_crc(b"Hello")
        self.assertFalse(verify_crc(b"Hella", checksum))

class TestRetransmission(unittest.TestCase):
    def setUp(self):
        self.manager = RetransmissionManager()
        self.manager.track_message("msg1", b"Hello")

    def test_message_tracking(self):
        self.assertIn("msg1", self.manager.pending_messages)

    def test_acknowledgment(self):
        self.assertTrue(self.manager.acknowledge_message("msg1"))
        self.assertNotIn("msg1", self.manager.pending_messages)

    def test_retransmission(self):
        result = self.manager.retransmit_message("msg1")
        self.assertEqual(result, b"Hello")

    def test_retry_limit(self):
        for _ in range(3):
            self.manager.retransmit_message("msg1")
        self.assertIsNone(self.manager.retransmit_message("msg1"))
        self.assertNotIn("msg1", self.manager.pending_messages)

    def test_failed_message(self):
        for _ in range(4):
            self.manager.retransmit_message("msg1")
        self.assertEqual(
            self.manager.failed_messages["msg1"], b"Hello"
        )

    def test_timeout(self):
        sent_time = self.manager.pending_messages["msg1"]["sent_time"]
        with patch("retransmission.time.monotonic",
                   return_value=sent_time + 4):
            self.assertIn("msg1", self.manager.check_timeouts())


if __name__ == "__main__":
    unittest.main()