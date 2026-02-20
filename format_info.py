FORMAT_GEN_POLY = 0b10100110111
FORMAT_XOR_MASK = 0b101010000010010


ECC_BITS = {
    "L": 0b01,
    "M": 0b00,
    "Q": 0b11,
    "H": 0b10,
}


def format_bits(data):
    v = data << 10

    for bit in range(14, 9, -1):
        if (v >> bit) & 1:
            v ^= FORMAT_GEN_POLY << (bit - 10)

    return v & 0x3FF


def make_format_bits(ecc, mask):
    fb = (ECC_BITS[ecc] << 3) | mask
    rem = format_bits(fb)
    final = (fb << 10) | rem
    final ^= FORMAT_XOR_MASK
    return f"{final:015b}"


def place_format_info(board, reserved, fmt_bits: str) -> None:
    n = len(board)
    bits = [int(b) for b in fmt_bits]

    coords_a = [
        (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5),
        (8, 7), (8, 8),
        (7, 8), (5, 8), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8),
    ]

    coords_b = [

        (8, n - 1), (8, n - 2), (8, n - 3), (8, n - 4),
        (8, n - 5), (8, n - 6), (8, n - 7), (8, n - 8),


        (n - 7, 8), (n - 6, 8), (n - 5, 8), (n - 4, 8),
        (n - 3, 8), (n - 2, 8), (n - 1, 8),
    ]


    for k, (r, c) in enumerate(coords_a):
        board[r][c] = bits[k]
        reserved[r][c] = True


    for k, (r, c) in enumerate(coords_b):
        board[r][c] = bits[k]
        reserved[r][c] = True
