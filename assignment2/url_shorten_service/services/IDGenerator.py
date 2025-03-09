import random
import string

from services.mode import Mode

BASE62 = string.digits + string.ascii_lowercase + string.ascii_uppercase
BASE64 = BASE62 + '-_'


def lcg(num: int, a=10069, c=1, m=2 ** 32) -> int:
    """
    A linear congruential generator. Here, m defines the range of output is [0,m-1], and m=2^n make mod easier.
    To generate a full cycle sequence, should satisfy a≡1 (mod 4), c is a constant.
    """
    return (a * num + c) & (m - 1)


class IDGenerator:
    def __init__(self, shuffle=False, mode=Mode.BASIC):
        self.charset = BASE64
        self.seed = random.randint(1, 2025)
        self.mode = mode
        print("using seed", self.seed)

        if shuffle:
            char_list = list(self.charset)
            random.shuffle(char_list)
            self.charset = ''.join(char_list)
            print("shuffled charset:", self.charset)

    def base64_encode(self, num: int) -> str:
        base = len(self.charset)
        if num == 0:
            return self.charset[0]
        char_list = []
        while num:
            num, rem = divmod(num, base)
            char_list.append(self.charset[rem])
        return ''.join(reversed(char_list))

    def lcg_encode(self, num: int, b=3):
        obfuscated = lcg(num, c=self.seed, m=64 ** b)
        return self.base64_encode(obfuscated)

    def encode(self, num: int) -> str:
        if self.mode == Mode.LCG:
            return self.lcg_encode(num)
        return self.base64_encode(num)
