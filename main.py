from gf_256 import tables
from reed_solomon import rs_encode
from data_encode import word_to_stream, word_to_chunks, qr_version, bytes_to_bitstream
import matrix as mat
import display
import gui


log, exp = tables()


def core_logic(text):

    bits = word_to_stream(text)
    version, ecc_len = qr_version(bits)

    if version is None:
        print("Tekst zbyt długi!")
        return

    data_chunks = word_to_chunks(bits)
    ecc = rs_encode(data_chunks, ecc_len, log, exp)
    full_stream = bits + bytes_to_bitstream(ecc)

    board, reserved = mat.build_base(version)
    mat.stream_to_board(board, reserved, full_stream)

    final_board, mask_idx = mat.apply_best_mask(board, reserved, version, "M")

    display.display(final_board)


if __name__ == "__main__":
    gui.start_app(core_logic)