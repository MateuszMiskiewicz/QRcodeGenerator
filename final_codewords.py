import rs_blocks


def make_final_codewords(data, version, ecc):

    ec_len, groups = rs_blocks.RS_BLOCKS_V1_6[(version, ecc)]

    blocks = []
    x = 0

    for num_blocks, data_len in groups:
        for _ in range(num_blocks):
            blocks.append(data[x: x + data_len])
            x += data_len

    interleaved = []
    for i in range(len(data)):
        for b in blocks:
            if i < len(b):
                interleaved.append(b[i])

    return interleaved