"""
.. include:: ../README.md
.. include:: ../CHANGELOG.md
"""

from crypticorn.common.logging import configure_logging
configure_logging("crypticorn")

from crypticorn.client import ApiClient

__all__ = ["ApiClient"]

