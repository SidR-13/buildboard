import hashlib
import hmac


def verify_github_signature(payload_body: bytes, signature_header: str | None, secret: str) -> bool:
    if signature_header is None:
        return False

    expected_signature = "sha256=" + hmac.new(
        key=secret.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    # compare_digest, not ==: constant-time, so a timing side channel can't leak the secret
    return hmac.compare_digest(expected_signature, signature_header)
