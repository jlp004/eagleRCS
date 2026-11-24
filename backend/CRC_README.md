CRC and Retransmission

Uses CRC32 to detect corrupted messages and retransmission to handle corrupted or lost messages.

--> Files

- `crc.py` — calculates and verifies CRC checksums
- `retransmission.py` — handles ACKs, retries, timeouts, and failed messages
- `test_crc_retransmission.py` — simulates corruption and retransmission
- `test_reliability.py` — contains automated unit tests

--> Settings

- timeout: 3 seconds
- maximum retries: 3
Both are configurable. No additional libraries are needed.

--> Testing

run from the backend folder:

python3 -m unittest test_reliability -v
python3 test_crc_retransmission.py


-- all 9 unit tests passed, along with the corrupted message and retransmission simulation

--> Integration

- calculate and attach the CRC before sending a message
- track each outgoing message using its message ID
- verify the CRC on the receiving end
- acknowledge valid messages and retry corrupted or timed-out messages
- check `failed_messages` for failed deliveries

Both modules work independently for now. actual network transmission, ACK/NACK communication, message formatting and duplicate handling still need to be integrated
