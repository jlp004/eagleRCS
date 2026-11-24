import zlib


def calculate_crc(message: bytes) -> int:
    # calc the CRC32 checksum 
    return zlib.crc32(message)
def verify_crc(message: bytes, received_crc: int) -> bool:
    #recal the checksum and compare it with the og
    return calculate_crc(message) == received_crc

if __name__ == "__main__":
    message = b"Hello"
    checksum = calculate_crc(message)

    print("Message:", message)
    print("CRC:", checksum)

    # test an unchanged message
    print("Valid message:", verify_crc(message, checksum))

    # simulate a corrupted message
    corrupted_message = b"Hella"
    print("Corrupted message:", verify_crc(corrupted_message, checksum))

