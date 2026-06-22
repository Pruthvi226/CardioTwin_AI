"""Medical safety disclaimer utilities."""

DISCLAIMER = (
    "This system is for educational and research purposes only and should not be used "
    "as a substitute for professional medical advice, diagnosis, or treatment."
)


def with_disclaimer(payload: dict) -> dict:
    """Attach the project disclaimer to API payloads."""
    payload["disclaimer"] = DISCLAIMER
    return payload