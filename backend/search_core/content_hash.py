import hashlib


def calculate_content_hash(title, content):
    text = f"{title}\n{content}"

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()
