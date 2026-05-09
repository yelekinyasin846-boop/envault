"""Custom exceptions for envault."""


class EnvaultError(Exception):
    """Base exception for all envault errors."""


class DecryptionError(EnvaultError):
    """Raised when decryption fails, typically due to a wrong passphrase."""

    def __init__(self, message: str = "Decryption failed. The passphrase may be incorrect."):
        super().__init__(message)


class EncryptionError(EnvaultError):
    """Raised when encryption fails."""

    def __init__(self, message: str = "Encryption failed."):
        super().__init__(message)


class InvalidBlobError(EnvaultError):
    """Raised when the encrypted blob is malformed or corrupted."""

    def __init__(self, message: str = "The encrypted data blob is invalid or corrupted."):
        super().__init__(message)
