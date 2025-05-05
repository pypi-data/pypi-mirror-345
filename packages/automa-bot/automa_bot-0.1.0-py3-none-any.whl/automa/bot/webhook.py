import hashlib
import hmac


def verify_webhook(secret: str, signature: str, payload: str) -> bool:
    if (
        not secret
        or not isinstance(secret, str)
        or not signature
        or not isinstance(signature, str)
    ):
        return False

    generated_signature = generate_webhook_signature(secret, payload)

    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(generated_signature, signature)


def generate_webhook_signature(secret: str, payload: str) -> str:
    return hmac.new(
        secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()
