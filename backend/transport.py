# This file is the UDP transport layer for the P2P chat. It allows messages to be sent and
# received by moving raw bytes between named peers. Other modules can call
# send() or broadcast() and plug a function into on_receive as needed.
# This layer sends raw bytes with no message format of its own; higher layers define any format.

import socket # To open connections
import threading # For background process

# Every peer is a network endpoint consisting of a UDP socket, an address book, and a
# listener thread
class Transport:
    def __init__(self, my_id):
        self.my_id = my_id # local peer identifier, for ref by caller

        # Single IPv4 UDP socket for both sending and receiving so peers see bound port as 
        # sender address, matching what add_peer stored
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Two dicts because every incoming packet needs address -> name lookup (receive path),
        # every send needs name -> address
        # Keep both -> each lookup instant, add_peer/remove_peer are only places interacting
        # with these
        self.peer_to_addr = {} # map name to address
        self.addr_to_peer = {} # map address to name

        self.on_receive = None # callback; store function when UDP packet arrives
        self.running = False # True while the listener loop should keep running

    def start(self, port):
        # bind to all local interfaces so other computers can reach this peer, not just this machine
        self.sock.bind(("0.0.0.0", port))
        self.sock.settimeout(0.5) # wake up every 0.5s to recheck self.running
        self.running = True # mark listener as active
        
        # daemon=True lets program exit even if close() forgotten
        listener_thread = threading.Thread(target=self._listen, daemon=True) # background receive thread
        listener_thread.start() # begin listening loop

    def close(self):
        self.running = False # stop listener loop
        self.sock.close() # close socket and free port

    # add_peer and remove_peer both update dictionaries to keep lookups synced whenever peer 
    # joins or leaves chat
    def add_peer(self, peer_id, ip, port):
        self.peer_to_addr[peer_id] = (ip, port) # save peer_id -> address
        self.addr_to_peer[(ip, port)] = peer_id # save address -> peer_id

    def remove_peer(self, peer_id):
        # remove name from peer_to_addr, keep address to remove from addr_to_peer
        addr = self.peer_to_addr.pop(peer_id, None)

        if addr is not None: # only if peer actually existed
            self.addr_to_peer.pop(addr, None) # remove reverse entry using prev address

    # Returns True if OS accepted bytes, False if peer is unknown or send failed
    # UDP doesn't guarantee delivery, so True doesn't mean peer received anything (at 
    # least at this stage)
    def send(self, peer_id, data) -> bool:
        if peer_id not in self.peer_to_addr: # unknown peer id
            return False
        try:
            self.sock.sendto(data, self.peer_to_addr[peer_id]) # send raw bytes to peer address
        except OSError: # OS rejected send
            return False
        return True # handed off to OS socket

    # Loops over send() -> group chat can reuse
    # Returns failed peer_ids -> retransmission knows what to retry
    def broadcast(self, peer_ids, data):
        failed = [] # track peer_ids that failed to send
        for peer_id in peer_ids:
            if not self.send(peer_id, data): # send failed
                failed.append(peer_id)
        return failed # return list of failed peer_ids

    # Starts with _ (means it's internal), nothing outside this class should call it
    def _listen(self):
        while self.running: # keep receiving while active

            # Windows specific issue with sending to a port where there is no listener
            # Avoid ConnectionResetError

            try: # attempt to receive
                # 2048-byte buffer should fit most chat messages
                # Msgs small for now to avoid oversized datagrams
                data, addr = self.sock.recvfrom(2048) # wait for one letter
            
            except ConnectionResetError: # Windows reports last send hit closed port
                continue # ignore it and keep listening
            except socket.timeout: # no packet within 0.5s, check before OSError since timeout is OSError
                continue # recheck self.running
            except OSError: # socket closed or oversized packet, checked after ConnectionResetError/socket.timeout
                if self.running: # keep listening if still running
                    continue
                break # exit listener loop on shutdown

            peer_id = self.addr_to_peer.get(addr) # look up sender name

            if peer_id is None: # drop unknown senders, basic allowlist
                # Not real authentication since UDP source addresses can be forged, to be fixed
                continue

            if self.on_receive is not None: # only call if handler registered
                # a bug in it must not kill listening
                # UI code may need to hand off to own/separate thread
                try:
                    self.on_receive(peer_id, data) # provide message
                except Exception as e: # if code crashes
                    print("on_receive error:", e) # log, keep listening