from typedefs import Message

def main():
    msg = Message("TEST")
    msg.add_metadata()
    print(msg.crc)
    decrypted_crc = msg.decrypt_crc(msg=msg)
    Message.convert_crc_to_string(decrypted_crc)

if __name__ == "__main__":
    main()