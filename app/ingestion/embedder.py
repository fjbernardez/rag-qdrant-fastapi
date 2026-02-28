import hashlib
import random


VECTOR_SIZE = 1536


def embed_text(text: str, *, vector_size: int = VECTOR_SIZE) -> list[float]:
    if vector_size <= 0:
        raise ValueError("vector_size must be > 0")

    digest = hashlib.sha256(text.encode("utf-8")).digest()
    seed = int.from_bytes(digest[:8], byteorder="big", signed=False)
    rng = random.Random(seed)
    return [rng.uniform(-1.0, 1.0) for _ in range(vector_size)]
