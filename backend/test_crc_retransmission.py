from crc import calculate_crc, verify_crc
from retransmission import RetransmissionManager

def test_corrupted_message():
    manager = RetransmissionManager()
    message = b"Hello"
    checksum = calculate_crc(message)
    manager.track_message("msg1", message)

    # simulate corruption during transmission
    corrupted_message = b"Hella"

    if not verify_crc(corrupted_message, checksum):
        print("Corrupted message detected.")
        print("NACK received.")

        #retrieve the og message for resending
        resent_message = manager.retransmit_message("msg1")

        if verify_crc(resent_message, checksum):
            print("Retransmitted message:", resent_message)
            print("CRC verification successful.")
            manager.acknowledge_message("msg1")
            print("ACK received.")
    print("Pending messages:", manager.pending_messages)


if __name__ == "__main__":
    test_corrupted_message()