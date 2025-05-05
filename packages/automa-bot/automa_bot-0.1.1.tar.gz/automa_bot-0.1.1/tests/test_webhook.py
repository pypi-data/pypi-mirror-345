from src.automa.bot.webhook import generate_webhook_signature, verify_webhook


def test_returns_false_if_secret_is_not_a_string():
    result = verify_webhook(1, "signature", "{}")

    assert result is False


def test_returns_false_if_secret_is_empty():
    result = verify_webhook("", "signature", "{}")

    assert result is False


def test_returns_false_if_signature_is_not_a_string():
    result = verify_webhook("secret", 1, "{}")

    assert result is False


def test_returns_false_if_signature_is_empty():
    result = verify_webhook("secret", "", "{}")

    assert result is False


def test_returns_false_if_signature_is_wrong():
    result = verify_webhook("secret", "signature", "{}")

    assert result is False


def test_returns_true_if_signature_is_correct():
    result = verify_webhook(
        "secret",
        "77325902caca812dc259733aacd046b73817372c777b8d95b402647474516e13",
        "{}",
    )

    assert result is True


def test_verifies_the_generated_signature():
    # Generate signature
    signature = generate_webhook_signature("secret", "{}")

    # Verify with the same parameters
    result = verify_webhook("secret", signature, "{}")

    assert result is True
