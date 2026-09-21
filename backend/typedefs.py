from dataclasses import dataclass
from datetime import datetime
from tokenize import String
from Pyfhel import Pyfhel
import numpy as np

from datetime import datetime

LARGE_PRIME = 4294955009

class Message:
    def __init__(self, data=None):
        self.data       = data
        self.crc        = None
        self.timestamp  = None
        self.he         = None

    def generate_crc(self):
        self.he = Pyfhel()
        self.he.contextGen(scheme='BFV', n=2048, t=LARGE_PRIME)        
        self.he.keyGen()

        val_as_int = int.from_bytes(self.data.encode('utf-8'), byteorder='big') % LARGE_PRIME
        val_array= np.array([val_as_int], dtype=np.int64)

        self.crc =  self.he.encryptInt(val_array)

    # crc decryption / handling should be moved to a parent class / state machine later to hold HE
    # future me here yeah it definitely does bc this is horrible
    def decrypt_crc(self, msg: Message) -> list:
        return self.he.decryptInt(msg.crc)

    def convert_crc_to_string(crc_array: np.ndarray) -> str:
        val_as_int = int(crc_array[0])
    
        # 2. Calculate byte length needed for the integer
        byte_len = (val_as_int.bit_length() + 7) // 8 or 1
        
        # 3. Convert integer back to bytes, then decode to string
        crc_bytes = val_as_int.to_bytes(byte_len, byteorder='big')
        return crc_bytes.decode('utf-8')
        

    def add_metadata(self):
        self.generate_crc()
        self.timestamp = datetime.now()

    def __str__(self):
        return f"Message(data={self.data}, timestamp={self.timestamp}, crc={self.crc})"