import copy


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
            board[r + i][c + j] = pattern[i][j]
            reserved[r + i][c + j] = True


def timing_pattern(board, reserved):

    for i in range(len(board)):
        if not reserved[6][i]:
            board[6][i] = 1 - (i % 2)
        reserved[6][i] = True
        if not reserved[i][6]:
            board[i][6] = 1 - (i % 2)
        reserved[i][6] = True


def place_alignment(board, reserved, center_r, center_c):

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
        rows = range(size - 1, -1, -1) if direction == 1 else range(size)
        for r in rows:
            for c in (col, col - 1):
                if board[r][c] is None and not reserved[r][c]:
                    board[r][c] = int(stream[i]) if i < len(stream) else 0
                    i += 1
        direction *= -1
        col -= 2


def get_mask_value(mask_num, r, c):

    masks = {
        0: (r + c) % 2 == 0,
        1: r % 2 == 0,
        2: c % 3 == 0,
        3: (r + c) % 3 == 0,
        4: (r // 2 + c // 3) % 2 == 0,
        5: (r * c) % 2 + (r * c) % 3 == 0,
        6: ((r * c) % 2 + (r * c) % 3) % 2 == 0,
        7: ((r + c) % 2 + (r * c) % 3) % 2 == 0
    }
    return masks[mask_num]


def apply_mask(board, reserved, mask_num):

    for r in range(len(board)):
        for c in range(len(board)):
            if not reserved[r][c]:
                if get_mask_value(mask_num, r, c):
                    board[r][c] ^= 1


def calculate_penalty(board):

    size = len(board)
    penalty = 0

    for r in range(size):
        row_count = 1
        col_count = 1
        for i in range(1, size):
            if board[r][i] == board[r][i - 1]:
                row_count += 1
            else:
                if row_count >= 5: penalty += (3 + (row_count - 5))
                row_count = 1
            if board[i][r] == board[i - 1][r]:
                col_count += 1
            else:
                if col_count >= 5: penalty += (3 + (col_count - 5))
                col_count = 1


    for r in range(size - 1):
        for c in range(size - 1):
            if board[r][c] == board[r + 1][c] == board[r][c + 1] == board[r + 1][c + 1] is not None:
                penalty += 3

    return penalty


def apply_best_mask(board, reserved, version, ecc_level="M"):

    import format_info as fi
    best_board = None
    min_penalty = float('inf')
    best_mask_idx = 0

    for m_idx in range(8):
        temp_board = copy.deepcopy(board)
        apply_mask(temp_board, reserved, m_idx)


        fmt = fi.make_format_bits(ecc_level, m_idx)
        fi.place_format_info(temp_board, reserved, fmt)

        score = calculate_penalty(temp_board)
        if score < min_penalty:
            min_penalty = score
            best_board = temp_board
            best_mask_idx = m_idx

    return best_board, best_mask_idx


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
        if c != 6: reserved[8][c] = True
    for r in range(9):
        if r != 6: reserved[r][8] = True
    reserved[8][8] = True
    for c in range(n - 8, n): reserved[8][c] = True
    for r in range(n - 7, n): reserved[r][8] = True


def build_base(version):

    size = 21 + 4 * (version - 1)
    alignment_pos = 4 * version + 10
    board, reserved = make_board(version)

    place_finder_with_sep(board, reserved, 0, 0)
    place_finder_with_sep(board, reserved, 0, size - 7)
    place_finder_with_sep(board, reserved, size - 7, 0)

    timing_pattern(board, reserved)
    dark_module(board, reserved, version)
    if version >= 2:
        place_alignment(board, reserved, alignment_pos, alignment_pos)

    reserve_format_areas(board, reserved)
    return board, reserved