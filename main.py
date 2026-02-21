from gf_256 import tables
from reed_solomon import rs_encode
from data_encode import word_to_stream, word_to_chunks, qr_version, bytes_to_bitstream
import matrix as mat
import format_info as fi
import display


log, exp = tables()

text = "youtube.com"
bits = word_to_stream(text)
data = word_to_chunks(bits)

version, ecc_len = qr_version(bits)

ecc = rs_encode(data, ecc_len, log, exp)

stream = bits + bytes_to_bitstream(ecc)

board, reserved = mat.build_base(version)

mat.stream_to_board(board, reserved, stream)
mat.apply_mask(board, reserved)

fmt = fi.make_format_bits("M", 0)
fi.place_format_info(board, reserved, fmt)
display.display(board)
