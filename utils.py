import tiktoken

cl100k_base_encoder = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Count tokens using tiktoken cl100k_base encoder"""
    return len(cl100k_base_encoder.encode(text))


def count_words(text: str) -> int:
    """Count words in text"""
    return len(text.split())
