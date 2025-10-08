"""app package for the water-potability API.

This file makes the `app` directory an importable Python package which prevents
ModuleNotFoundError when running `uvicorn app.main:app` with the reload/watchers.
"""

__all__ = ["main"]
