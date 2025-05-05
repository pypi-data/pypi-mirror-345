"""
GeneratePasswords - Password Generator by Rania_Elkholy
"""

import random

lower_letters = list("abcdefghijklmnopqrstuvwxyz")
upper_letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
numbers = list("0123456789")
symbols = list("!#$%&()*@^_~,.?:;/[{}]")
similar_chars = {'1', 'l', 'I', '0', 'O'}

def generate_password(length=12, use_lower=True, use_upper=True, use_numbers=True, use_symbols=True, exclude_similar=True):
    if length < 4:
        raise ValueError("Password length must be at least 4")

    char_pool = []
    local_upper = upper_letters.copy()

    if use_lower:
        char_pool.extend(lower_letters)
    if use_upper:
        char_pool.extend(upper_letters)
    if use_numbers:
        char_pool.extend(numbers)
    if use_symbols:
        char_pool.extend(symbols)

    if exclude_similar:
        char_pool = [c for c in char_pool if c not in similar_chars]
        local_upper = [c for c in local_upper if c not in similar_chars]

    if not char_pool or not local_upper:
        raise ValueError("Character pool is empty after exclusions")

    password = [random.choice(local_upper)]
    temp_pool = []

    if use_lower:
        temp_pool.append(random.choice([c for c in lower_letters if c in char_pool]))
    if use_numbers:
        temp_pool.append(random.choice([c for c in numbers if c in char_pool]))
    if use_symbols:
        temp_pool.append(random.choice([c for c in symbols if c in char_pool]))

    remaining = length - len(password) - len(temp_pool)
    temp_pool += random.choices(char_pool, k=remaining)
    random.shuffle(temp_pool)
    password += temp_pool
    return ''.join(password)
