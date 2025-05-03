def right_rotate(n, d):
    return ((n >> d) | (n << (32 - d))) & 0xFFFFFFFF

def to_bytes(message):
    return message.encode() if isinstance(message, str) else message

def pad_message(message):
    original_len_bits = len(message) * 8
    message += b'\x80'  # Append a single '1' bit (as 0x80)
    while (len(message) * 8 + 64) % 512 != 0:
        message += b'\x00'  # Pad with '0' bits
    message += original_len_bits.to_bytes(8, 'big')  # Add original length as 64-bit big-endian
    return message

def split_chunks(message, size):
    return [message[i:i + size] for i in range(0, len(message), size)]
