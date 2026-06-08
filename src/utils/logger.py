"""Small logging helper for scripts."""

from __future__ import annotations

import logging


def get_logger(name: str = "cardiotwin") -> logging.Logger:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    return logging.getLogger(name)

