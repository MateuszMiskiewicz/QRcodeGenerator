# =========================
# 1) GF(256) + Reed-Solomon
# =========================

def tables():
    exp = [0] * 512
    log = [0] * 256

    poly = 0x11D
    x = 1
    for i in range(256):
        exp[i] = x
        log[x] = i
        x <<= 1
        if x & 0x100:
            x ^= poly

    # duplikacja dla szybkiego exp[log[a]+log[b]]
    for i in range(256, 512):
        exp[i] = exp[i - 256]

    return log, exp


def gf_mul(a, b, log, exp):
    if a == 0 or b == 0:
        return 0
    return exp[log[a] + log[b]]


def poly_mul(p, q, log, exp):
    res = [0] * (len(p) + len(q) - 1)
    for i in range(len(p)):
        for j in range(len(q)):
            res[i + j] ^= gf_mul(p[i], q[j], log, exp)
    return res


def gen_poly(r, log, exp):
    g = [1]
    for i in range(r):
        g = poly_mul(g, [1, exp[i]], log, exp)
    return g


def rs_encode(data, r, log, exp):
    g = gen_poly(r, log, exp)
    res = [0] * r

    for byte in data:
        k = byte ^ res[0]
        res = res[1:] + [0]
        if k != 0:
            for i in range(r):
                res[i] ^= gf_mul(g[i+1], k, log, exp)

    return res


# =========================
# 2) QR data bitstream
# =========================

def to_bin8(x: int) -> str:
    return bin(x)[2:].zfill(8)


def word_to_ascii_bits(word: str) -> str:
    return "".join(to_bin8(ord(c)) for c in word)


# (Dla uproszczenia: tylko wersje 1..5 i poziom M)
max_bytes = {  # data codewords
    1: {"M": 16},
    2: {"M": 28},
    3: {"M": 44},
    4: {"M": 64},
    5: {"M": 86},
}

ec_bytes = {  # ecc codewords (r)
    1: {"M": 10},
    2: {"M": 16},
    3: {"M": 26},
    4: {"M": 36},
    5: {"M": 48},
}


def choose_version_for_bits(bitstream: str, level="M"):
    data_len_bytes = len(bitstream) // 8
    for v in range(1, 6):
        if data_len_bytes <= max_bytes[v][level]:
            return v
    return None


def build_data_codewords(word: str, level="M"):
    # mode (byte) + length(8-bit dla v<=9) + payload + terminator + pad do bajtu + pad bytes do max_bytes
    mode = "0100"
    length = to_bin8(len(word))
    terminator = "0000"

    bits = mode + length + word_to_ascii_bits(word) + terminator

    # dopełnij do bajtu
    if len(bits) % 8 != 0:
        bits += "0" * (8 - len(bits) % 8)

    v = choose_version_for_bits(bits, level)
    if v is None:
        raise ValueError("Za długie dane dla wersji 1..5 (M)")

    total_data_bytes = max_bytes[v][level]
    curr_bytes = len(bits) // 8

    pad_seq = ["11101100", "00010001"]
    i = 0
    while curr_bytes < total_data_bytes:
        bits += pad_seq[i % 2]
        curr_bytes += 1
        i += 1

    # zamień na listę bajtów (data codewords)
    data_codewords = [int(bits[i:i+8], 2) for i in range(0, len(bits), 8)]
    return v, data_codewords


# =========================
# 3) QR matrix + patterns
# =========================

def make_board(version: int):
    size = 21 + 4 * (version - 1)
    board = [[None for _ in range(size)] for _ in range(size)]
    reserved = [[False for _ in range(size)] for _ in range(size)]
    return board, reserved


def set_cell(board, reserved, r, c, val):
    board[r][c] = val
    reserved[r][c] = True


def place_finder(board, reserved, r, c):
    pattern = [
        [1,1,1,1,1,1,1],
        [1,0,0,0,0,0,1],
        [1,0,1,1,1,0,1],
        [1,0,1,1,1,0,1],
        [1,0,1,1,1,0,1],
        [1,0,0,0,0,0,1],
        [1,1,1,1,1,1,1],
    ]
    for i in range(7):
        for j in range(7):
            set_cell(board, reserved, r+i, c+j, pattern[i][j])

    # separator (biała ramka 1 moduł)
    for i in range(-1, 8):
        for j in [-1, 7]:
            rr = r + i
            cc = c + j
            if 0 <= rr < len(board) and 0 <= cc < len(board) and not reserved[rr][cc]:
                set_cell(board, reserved, rr, cc, 0)
    for j in range(-1, 8):
        for i in [-1, 7]:
            rr = r + i
            cc = c + j
            if 0 <= rr < len(board) and 0 <= cc < len(board) and not reserved[rr][cc]:
                set_cell(board, reserved, rr, cc, 0)


def timing_patterns(board, reserved):
    n = len(board)
    # wiersz 6
    for c in range(n):
        if not reserved[6][c]:
            set_cell(board, reserved, 6, c, c % 2)
    # kolumna 6
    for r in range(n):
        if not reserved[r][6]:
            set_cell(board, reserved, r, 6, r % 2)


def place_alignment(board, reserved, r, c):
    # 5x5
    pattern = [
        [1,1,1,1,1],
        [1,0,0,0,1],
        [1,0,1,0,1],
        [1,0,0,0,1],
        [1,1,1,1,1],
    ]
    for i in range(5):
        for j in range(5):
            set_cell(board, reserved, r+i, c+j, pattern[i][j])


def dark_module(board, reserved, version):
    # stały "dark module"
    r = 4 * version + 9
    c = 8
    set_cell(board, reserved, r, c, 1)


def reserve_format_areas(board, reserved):
    # Rezerwujemy pola na format info (żeby data/maska ich nie ruszały)
    n = len(board)
    # wokół lewego górnego findera: (r=8, c=0..8) i (c=8, r=0..8) z wyjątkiem (8,8)
    for c in range(9):
        if not reserved[8][c]:
            reserved[8][c] = True
            if board[8][c] is None:
                board[8][c] = 0
    for r in range(9):
        if not reserved[r][8]:
            reserved[r][8] = True
            if board[r][8] is None:
                board[r][8] = 0
    reserved[8][8] = True  # też zarezerwuj

    # po prawej od górnego prawego findera: (r=0..8, c=n-8)
    for r in range(8):
        if not reserved[r][n-8]:
            reserved[r][n-8] = True
            if board[r][n-8] is None:
                board[r][n-8] = 0

    # nad dolnym lewym finderem: (r=n-8, c=0..7)
    for c in range(8):
        if not reserved[n-8][c]:
            reserved[n-8][c] = True
            if board[n-8][c] is None:
                board[n-8][c] = 0


# =========================
# 4) Data placement + mask
# =========================

def place_data_bits(board, reserved, bits: str):
    n = len(board)
    idx = 0
    up = True
    col = n - 1

    while col > 0:
        if col == 6:  # omijamy timing column
            col -= 1

        rows = range(n-1, -1, -1) if up else range(n)
        for r in rows:
            for c in [col, col-1]:
                if not reserved[r][c]:
                    board[r][c] = int(bits[idx]) if idx < len(bits) else 0
                    idx += 1

        up = not up
        col -= 2

    return idx


def apply_mask0(board, reserved):
    n = len(board)
    for r in range(n):
        for c in range(n):
            if not reserved[r][c]:
                if (r + c) % 2 == 0:
                    board[r][c] ^= 1


# =========================
# 5) RUN: YouTube link v2-M
# =========================

log, exp = tables()

link = "https://www.youtube.com/"
v, data_codewords = build_data_codewords(link, level="M")
r = ec_bytes[v]["M"]

ecc = rs_encode(data_codewords, r, log, exp)

final_codewords = data_codewords + ecc
data_bits = "".join(to_bin8(b) for b in final_codewords)

#print("Version:", v)
#print("Data codewords:", len(data_codewords), "ECC codewords:", len(ecc), "Total:", len(final_codewords))
#print("Data bits:", len(data_bits))

board, reserved = make_board(v)

# findery
place_finder(board, reserved, 0, 0)
place_finder(board, reserved, 0, len(board) - 8)
place_finder(board, reserved, len(board) - 8, 0)

# timing + dark module
timing_patterns(board, reserved)
dark_module(board, reserved, v)

# alignment dla v=2: środek 5x5 ma być w (18,18) więc start (16,16)

#print(data_bits)
print(ecc)

print(data_bits)
for i in range(len(board)):
    print(reserved[i],"\n")