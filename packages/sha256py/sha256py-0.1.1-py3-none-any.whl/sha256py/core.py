from .utils import pad_message, split_chunks, to_bytes, right_rotate


class Sha256:
    # Initial hash values (first 32 bits of the fractional parts of the square roots of the first 8 primes)
    _H = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    ]

    # Round constants (first 32 bits of the fractional parts of the cube roots of the first 64 primes)
    _K = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b,
        0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01,
        0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7,
        0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
        0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152,
        0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
        0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc,
        0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819,
        0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116, 0x1e376c08,
        0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f,
        0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
        0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
    ]

    def __init__(self, data: str, log_func=None):
        self._message = to_bytes(data)
        self._hash = None
        self._chunks = None
        self._log = log_func or (lambda *args, **kwargs: None)

    def _preprocess(self):
        if self._chunks is None:
            padded = pad_message(self._message)
            self._log("[Preprocess] Padded message length:", len(padded))
            self._chunks = split_chunks(padded, 64)
            self._log("[Preprocess] Total chunks:", len(self._chunks))
        return self._chunks

    def _bytes_to_words(self, chunk):
        words = [int.from_bytes(chunk[i:i + 4], 'big') for i in range(0, 64, 4)]
        self._log("[Chunk to Words] w[0..15]:", [f"{w:08x}" for w in words])
        return words

    def _words_to_bytes(self, words):
        return b''.join(w.to_bytes(4, 'big') for w in words)

    def _compute(self):
        h = self._H.copy()
        self._log("[Init] Initial hash values:", [f"{v:08x}" for v in h])

        for chunk_index, chunk in enumerate(self._preprocess()):
            self._log(f"\nProcessing chunk {chunk_index}")
            w = self._bytes_to_words(chunk) + [0] * 48  # Message schedule

            for i in range(16, 64):
                s0 = right_rotate(w[i - 15], 7) ^ right_rotate(w[i - 15], 18) ^ (w[i - 15] >> 3)
                s1 = right_rotate(w[i - 2], 17) ^ right_rotate(w[i - 2], 19) ^ (w[i - 2] >> 10)
                w[i] = (w[i - 16] + s0 + w[i - 7] + s1) & 0xFFFFFFFF

            self._log("[Schedule] w[16..63]:", [f"{x:08x}" for x in w[16:]])

            a, b, c, d, e, f, g, h0 = h
            self._log("[Init] Round variables:", [f"{x:08x}" for x in (a, b, c, d, e, f, g, h0)])

            for i in range(64):
                S1 = right_rotate(e, 6) ^ right_rotate(e, 11) ^ right_rotate(e, 25)
                ch = (e & f) ^ (~e & g)
                temp1 = (h0 + S1 + ch + self._K[i] + w[i]) & 0xFFFFFFFF
                S0 = right_rotate(a, 2) ^ right_rotate(a, 13) ^ right_rotate(a, 22)
                maj = (a & b) ^ (a & c) ^ (b & c)
                temp2 = (S0 + maj) & 0xFFFFFFFF

                h0 = g
                g = f
                f = e
                e = (d + temp1) & 0xFFFFFFFF
                d = c
                c = b
                b = a
                a = (temp1 + temp2) & 0xFFFFFFFF

                if i < 4 or i > 59 or i % 16 == 0: # Reducing log size
                    self._log(f"[Round {i:02}] State:", [f"{x:08x}" for x in (a, b, c, d, e, f, g, h0)])

            h = [(x + y) & 0xFFFFFFFF for x, y in zip(h, [a, b, c, d, e, f, g, h0])]
            self._log("[Chunk Complete] Updated hash values:", [f"{v:08x}" for v in h])

        return self._words_to_bytes(h)

    def digest(self) -> bytes:
        if self._hash is None:
            self._hash = self._compute()
        return self._hash

    def hexdigest(self) -> str:
        return self.digest().hex()

    def bindigest(self) -> str:
        return ''.join(f"{byte:08b}" for byte in self.digest())
