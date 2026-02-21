def to_bin(number):
    return bin(number)[2:].zfill(8)


def to_dec(bits):
    return int(bits, 2)


def word_to_ascii(word):
    return "".join(to_bin(ord(c)) for c in word)


max_bytes = {
    1: {"M": 16},
    2: {"M": 28},
    3: {"M": 44},
    4: {"M": 64},
    5: {"M": 86}
}

ec_bytes = {
    1: {"M": 10},
    2: {"M": 16},
    3: {"M": 26},
    4: {"M": 36},
    5: {"M": 48},
}


def qr_version(word, err="M"):
    bits = len(word)
    bytes_len = bits // 8

    for v in range(1, 6):
        if bytes_len <= max_bytes[v][err]:
            return v, ec_bytes[v][err]

    return None, None


def word_to_stream(word):
    mode = "0100"
    length = to_bin(len(word))
    terminator = "0000"

    bits = mode + length + word_to_ascii(word) + terminator

    # pad to byte
    if len(bits) % 8 != 0:
        bits += "0" * (8 - len(bits) % 8)

    version, _ = qr_version(bits, "M")

    total_bytes = max_bytes[version]["M"]
    curr_bytes = len(bits) // 8

    pad_seq = ["11101100", "00010001"]
    i = 0
    while curr_bytes < total_bytes:
        bits += pad_seq[i % 2]
        curr_bytes += 1
        i += 1

    return bits


def word_to_chunks(bits):
    return [to_dec(bits[i:i+8]) for i in range(0, len(bits), 8)]


def bytes_to_bitstream(byte_list):
    return "".join(f"{b:08b}" for b in byte_list)
