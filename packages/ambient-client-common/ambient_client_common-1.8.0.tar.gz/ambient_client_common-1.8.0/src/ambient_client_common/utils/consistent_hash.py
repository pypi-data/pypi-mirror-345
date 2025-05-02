import hashlib


def consistent_hash(value: str) -> str:
    """
    Generate a consistent hash for the given value.
    """

    return hashlib.sha256(value.encode()).hexdigest()
