def tables():
    exp = [0] * 512
    log = [0] * 256

    poly = 0x11D
    x = 1

    for i in range(255):
        exp[i] = x
        log[x] = i
        x <<= 1
        if x & 0x100:
            x ^= poly

    for i in range(255, 512):
        exp[i] = exp[i - 255]

    return log, exp


def gf_mul(a, b, log, exp):
    if a == 0 or b == 0:
        return 0
    return exp[log[a] + log[b]]
