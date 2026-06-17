"""Local API adapter for the Snapmaker Studio desktop app.

Thin layer over the pure `snapstudio_core` engine — no business logic here.
Loopback-only, optional per-launch token. Run with `python -m snapstudio_api`.
"""
from .service import health, doctor, API_VERSION

__all__ = ["health", "doctor", "API_VERSION"]
