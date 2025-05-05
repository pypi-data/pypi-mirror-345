import hashlib


class StablePrng:
    """A PRNG for test purposes which remains the same accross python versions and platforms"""

    blocksize = len(hashlib.sha256(b'').digest())
    state = bytearray([0] * blocksize)

    @staticmethod
    def block() -> bytes:
        out = hashlib.sha256(StablePrng.state + bytearray([0])).digest()
        StablePrng.state = hashlib.sha256(StablePrng.state + bytearray([1])).digest()
        return out

    @staticmethod
    def randbytes(n: int) -> bytearray:
        cnt = 0
        out = bytearray()
        while cnt < n:
            out += StablePrng.block()
            cnt += StablePrng.blocksize
        return out[:n]

    @staticmethod
    def seed(s: int):
        size = (s.bit_length() + 7) // 8
        StablePrng.state = s.to_bytes(size, byteorder='little')

    @staticmethod
    def randint(min_val: int, max_val: int) -> int:
        delta = max_val - min_val
        delta_mask = (1 << delta.bit_length()) - 1
        delta_size = (delta.bit_length() + 7) // 8

        delta_val = delta + 1
        while delta_val > delta:
            r = int.from_bytes(StablePrng.randbytes(delta_size), byteorder='little')
            delta_val = r & delta_mask
        out = delta_val + min_val
        assert out >= min_val
        assert out <= max_val
        return out
