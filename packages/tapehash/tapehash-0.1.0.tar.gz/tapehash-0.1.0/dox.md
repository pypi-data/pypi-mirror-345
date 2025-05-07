# tapehash

## Classes

### `HasNonceProtocol(Protocol)`

The HasNonceProtocol requires that an implementation has a settable nonce
property.

#### Properties

- nonce

## Functions

### `tapehash1(preimage: bytes, code_size: int = 20) -> bytes:`

Runs the tapehash 1 algorithm on the preimage and returns a 32-byte hash.
Computational complexity is tuneable via the `code_size` parameter.

### `tapehash2(preimage: bytes, tape_size_multiplier: int = 2) -> bytes:`

Runs the tapehash2 algorithm on the preimage and returns a 32-byte hash. Memory
complexity can be tuned via the `tape_size_multiplier` parameter.

### `tapehash3(preimage: bytes, code_size: int = 64, tape_size_multiplier: int = 2) -> bytes:`

Runs the tapehash3 algorithm on the preimage and returns a 32-byte hash.
Computational complexity is tuneable via the `code_size` parameter. Memory
complexity is tuneable via the `tape_size_multiplier` parameter.

### `license():`

Copyright (c) 2025 Jonathan Voss (k98kurz) Permission to use, copy, modify,
and/or distribute this software for any purpose with or without fee is hereby
granted, provided that the above copyright notice and this permission notice
appear in all copies. THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS
ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE
USE OR PERFORMANCE OF THIS SOFTWARE.

### `work(state: HasNonceProtocol, serialize: Callable, difficulty: int, hash_algo: Callable) -> HasNonceProtocol:`

Continually increments `state.nonce` until the difficulty score of
`hash_algo(serialize(state))` >= target, then returns the updated state.

### `calculate_difficulty(val: bytes) -> int:`

Calculates the difficulty of a hash by dividing 2**256 (max int) by the supplied
val interpreted as a big-endian unsigned int. This provides a linear metric that
represents the expected amount of work (hashes) that have to be computed on
average to reach the given hash val or better (lower).

### `calculate_target(difficulty: int) -> int:`

Calculates the target value that a hash must be below to meet the difficulty
threshold.

### `check_difficulty(val: bytes, difficulty: int) -> bool:`

Returns True if the val has a difficulty score greater than or equal to the
supplied difficulty, otherwise False.

### `version() -> str:`

Returns the current library version.


