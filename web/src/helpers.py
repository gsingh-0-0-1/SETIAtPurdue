import random
from src.constants import ALL_AFFILS, TOKEN_CHARS

def match_email_affil(email, affil):
    return email.endswith(ALL_AFFILS[affil])

def random_string_token(l = 100):
    return ''.join([random.choice(TOKEN_CHARS) for i in range(l)])
