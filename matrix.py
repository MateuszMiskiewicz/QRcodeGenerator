def make_board(version: int):
    size = 21 + 4 * (version - 1)

    board = [[None for _ in range(size)] for _ in range(size)]
    reserved = [[False for _ in range(size)] for _ in range(size)]

    return board, reserved


def place_pattern(board, reserved, r, c):
    pattern = [
        [1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1],
    ]
    for i in range(7):
        for j in range(7):
            board[r+i][c+j] = pattern[i][j]
            reserved[r+i][c+j] = True


def timing_pattern(board, reserved):
    for i in range(len(board)):
        if not reserved[6][i]:
            board[6][i] = 1 - (i % 2)
        reserved[6][i] = True
        if not reserved[i][6]:
            board[i][6] = 1 - (i % 2)
        reserved[i][6] = True


def place_alignment(board, reserved, center_r, center_c):
    # 5x5, top-left = center-2
    pattern = [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    top = center_r - 2
    left = center_c - 2
    for r in range(5):
        for c in range(5):
            board[top + r][left + c] = pattern[r][c]
            reserved[top + r][left + c] = True


def dark_module(board, reserved, version):
    board[4 * version + 9][8] = 1
    reserved[4 * version + 9][8] = True


def stream_to_board(board, reserved, stream):

    size = len(board)
    col = size - 1
    direction = 1
    i = 0
    while col > 0:

        if col == 6:
            col -= 1

        if direction == 1:
            rows = range(size - 1, -1, -1)
        else:
            rows = range(size)

        for r in rows:
            for c in (col, col - 1):
                if board[r][c] is None and not reserved[r][c]:
                    board[r][c] = int(stream[i]) if i < len(stream) else 0
                    i += 1

        direction = direction * (-1)
        col -= 2


def mask0(r, c):
    return (r + c) % 2 == 0


def apply_mask(board, reserved):
    for i in range(len(board)):
        for j in range(len(board)):
            if not reserved[i][j]:
                if mask0(i, j):
                    board[i][j] ^= 1


def place_finder_with_sep(board, reserved, r, c):
    n = len(board)

    for rr in range(r - 1, r + 8):
        for cc in range(c - 1, c + 8):
            if 0 <= rr < n and 0 <= cc < n:
                reserved[rr][cc] = True
                if board[rr][cc] is None:
                    board[rr][cc] = 0

    place_pattern(board, reserved, r, c)


def reserve_format_areas(board, reserved):
    n = len(board)

    for c in range(9):
        if c == 6:
            continue
        reserved[8][c] = True
        if board[8][c] is None:
            board[8][c] = 0

    for r in range(9):
        if r == 6:
            continue
        reserved[r][8] = True
        if board[r][8] is None:
            board[r][8] = 0

    reserved[8][8] = True
    if board[8][8] is None:
        board[8][8] = 0

    for c in range(n - 8, n):
        reserved[8][c] = True
        if board[8][c] is None:
            board[8][c] = 0

    for r in range(n - 7, n):
        reserved[r][8] = True
        if board[r][8] is None:
            board[r][8] = 0


def build_base(version):

    size = 21 + 4 * (version - 1)
    alignment_pos = 4 * version + 10
    board = [[None for _ in range(size)] for _ in range(size)]
    reserved = [[False for _ in range(size)] for _ in range(size)]

    place_finder_with_sep(board, reserved, 0, 0)
    place_finder_with_sep(board, reserved, 0, len(board) - 7)
    place_finder_with_sep(board, reserved, len(board) - 7, 0)

    timing_pattern(board, reserved)
    dark_module(board, reserved, version)
    if version >= 2:
        place_alignment(board, reserved, alignment_pos, alignment_pos)

    reserve_format_areas(board, reserved)

    return board, reserved
