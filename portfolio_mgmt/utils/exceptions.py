class BadCredentials(Exception):
    """Raised when wrong login (username, password, 2FA token) triplets are passed."""

    pass
