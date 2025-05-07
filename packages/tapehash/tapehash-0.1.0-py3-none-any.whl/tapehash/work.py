from typing import Protocol, Callable
import math


class HasNonceProtocol(Protocol):
    """The HasNonceProtocol requires that an implementation has a settable
        nonce property.
    """
    @property
    def nonce(self) -> int:
        ...
    @nonce.setter
    def nonce(self, val: int):
        ...

def calculate_difficulty(val: bytes) -> int:
    """Calculates the difficulty of a hash by dividing 2**256 (max int)
        by the supplied val interpreted as a big-endian unsigned int.
        This provides a linear metric that represents the expected
        amount of work (hashes) that have to be computed on average to
        reach the given hash val or better (lower).
    """
    val = int.from_bytes(val, 'big')
    if not val:
        return 2**256
    return 2**256 // val

def calculate_target(difficulty: int) -> int:
    """Calculates the target value that a hash must be below to meet
        the difficulty threshold.
    """
    return 2**256 if not difficulty else 2**256 // difficulty

def check_difficulty(val: bytes, difficulty: int) -> bool:
    """Returns True if the val has a difficulty score greater than or
        equal to the supplied difficulty, otherwise False.
    """
    return calculate_difficulty(val) >= difficulty

def work(
    state: HasNonceProtocol, serialize: Callable[[HasNonceProtocol], bytes],
    difficulty: int, hash_algo: Callable[[bytes], bytes]
) -> HasNonceProtocol:
    """Continually increments `state.nonce` until the difficulty score of
        `hash_algo(serialize(state))` >= target, then returns the updated
        state.
    """
    target = calculate_target(difficulty)
    while int.from_bytes(hash_algo(serialize(state)), 'big') > target:
        state.nonce += 1
    return state

