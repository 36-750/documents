def fib(n: int) -> int:
    r = [0] * (n + 1)

    r[0] = 0
    r[1] = 0
    r[2] = 1

    for i in range(3, n + 1):
        r[i] = r[i - 1] + r[i - 2]

    return r[n]
