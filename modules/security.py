def generate_token(length=16) -> str:
    """Generates token of selected length"""
    characters = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(characters) for _ in range(length))
    return token

