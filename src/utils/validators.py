"""
Validators utils
"""

import re


def check_password_strong(password: str) -> bool:
    """
    Check if password is strong
    """

    matches = [
        re.search(r"[a-z]", password), # Verify lowercase
        re.search(r"[A-Z]", password), # Verify uppercase
        re.search(r"\d", password), # Verify number
        re.search(r"\W", password) # Verify special character
    ]

    return all(matches)
