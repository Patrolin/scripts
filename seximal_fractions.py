from fractions import Fraction
from typing import *


def rep(a: int, b: int, base: int):

    # SETUP
    high = Fraction(a, b)
    low = high % 1

    # TOP
    def top():
        nonlocal high
        digits = []
        while high > 0:
            high, c = divmod(high, base)
            digits.append(int(c))
        return list(reversed(digits))

    # BOTTOM
    def bottom():
        nonlocal low
        digits, remainders = [], []
        while low > 0:
            low *= base
            digit, remainder = int(low), low
            try:
                i = remainders.index(remainder)
            except ValueError:
                digits.append(digit)
                remainders.append(remainder)
            else:
                return digits[:i], digits[i:]
            low %= 1
        return digits, []

    # CALC
    return top(), bottom()


def mml(seq: Sequence[int]):
    return ''.join('rcdefgab'[c] if 0 <= c <= 7 else str(c) for c in seq)


def yt(seq: Sequence[int]):
    return ''.join(' 67890'[c] if 0 <= c <= 7 else str(c) for c in seq)


def rows(n: int):
    for i in range(2, n):
        top, bottom = rep(1, i, 6) # generates seximal fractions song (https://www.youtube.com/watch?v=yV00FdOHcCg)
        b, r = bottom
        b, r = yt(b), yt(r) # convert to youtube piano format (https://www.youtube.com/watch?v=k-k0hgIhddc)
        yield f'{b}{f"({r})" if r else ""}'


for r in rows(31):
    print(r, end='')
