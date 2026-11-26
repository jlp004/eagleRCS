# eagleRCS

## Notes on current transport.py (API)
- `transport.py` in `backend/`, UDP only, raw bytes only, no message format
- Will add separate TCP file after

Usage example:
t = Transport("alice")
t.add_peer("bob", "127.0.0.1", 5001) # add each peer's ip and port
t.on_receive = handler # handler(peer_id, data: bytes)
t.start(5000) # bind, start listening
t.send("bob", b"...") # -> True/False (True = handed to OS, NOT delivered)
t.broadcast(["bob", "carol"], b"...")  # -> list of failed peer_ids
t.remove_peer("bob")
t.close()

Notes:
- Both sides must `add_peer` each other, or incoming messages are dropped (unknown senders are ignored)
- `on_receive` runs on the listener thread, not the UI thread; the UI should put messages in a queue
- Keep messages under about 1400 bytes (not enforced)