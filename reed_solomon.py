from gf_256 import gf_mul


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
