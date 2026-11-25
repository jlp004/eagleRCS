import time
class RetransmissionManager:

    def __init__(self, timeout=3, max_retries=3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.pending_messages = {}
        self.failed_messages = {}

    def track_message(self, message_id, message):
        #store the og message until it is recieved
        self.pending_messages[message_id] = {
            "message": message,
            "sent_time": time.monotonic(),
            "retries": 0
        }

    def acknowledge_message(self, message_id):
        #remove the message since it was received successfully
        if message_id in self.pending_messages:
            del self.pending_messages[message_id]
            return True

        return False

    def retransmit_message(self, message_id):
        if message_id not in self.pending_messages:
            return None

        pending = self.pending_messages[message_id]

        #store failed messages when the retry limit is reached
        if pending["retries"] >= self.max_retries:
            self.failed_messages[message_id] = pending["message"]
            del self.pending_messages[message_id]
            return None

        #increase the retry count and reset the timer
        pending["retries"] += 1
        pending["sent_time"] = time.monotonic()

        return pending["message"]
    def check_timeouts(self):
        current_time = time.monotonic()
        timed_out = []

        #find messages that have not been acknowledged in time
        for message_id, pending in self.pending_messages.items():
            elapsed = current_time - pending["sent_time"]

            if elapsed >= self.timeout:
                timed_out.append(message_id)

        return timed_out
    
if __name__ == "__main__":
    manager = RetransmissionManager()
    manager.track_message("msg1", b"Hello")

    for i in range(4):
        print(f"Retry {i + 1}:", manager.retransmit_message("msg1"))
    print("Pending messages:", manager.pending_messages)
    print("Failed messages:", manager.failed_messages)