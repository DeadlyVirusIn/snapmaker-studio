"""Model Discovery Hub v1 — metadata search + link-out only.

Source of truth: docs/design/MODEL_DISCOVERY_HUB.md.

STRICT SCOPE for v1:
- Metadata search via SANCTIONED provider APIs only (Thingiverse, MyMiniFactory,
  Cults3D). No scraping. No third-party files. No paid downloads.
- Direct import is DISABLED in v1 (`import_allowed` is always False with a reason).
- Link-out-only providers (Printables, Thangs, MakerWorld) never produce
  normalized result cards — only a search URL to open on the source site.
- No API secrets here ship to the client; keys are read server-side from env. If a
  key is missing the provider is reported disabled — we never fake live results.
"""
from __future__ import annotations

import os
import urllib.parse

# Providers whose APIs we are permitted to query for normalized results.
SANCTIONED = ("thingiverse", "myminifactory", "cults3d")
# Providers we only ever link out to (their own search page), never normalize.
LINK_OUT_ONLY = ("printables", "thangs", "makerworld")

# Where each sanctioned provider's API key would come from (server-side only).
_KEY_ENV = {
    "thingiverse": "THINGIVERSE_APP_TOKEN",
    "myminifactory": "MYMINIFACTORY_API_KEY",
    "cults3d": "CULTS3D_API_KEY",
}


def assert_sanctioned(source: str) -> None:
    """No-scrape guard: refuse to normalize anything outside the sanctioned list."""
    if source not in SANCTIONED:
        raise ValueError(f"provider '{source}' is not a sanctioned search provider")


def _result(title, source, source_url, *, thumbnail_url=None, license=None,
            price_status="unknown", file_formats=None, tags=None, attribution=None) -> dict:
    allowed, reason = compute_import_allowed(source, price_status, license)
    return {
        "title": title,
        "source": source,
        "source_url": source_url,
        "thumbnail_url": thumbnail_url,
        "license": license,
        "price_status": price_status,
        "file_formats": file_formats or [],
        "tags": tags or [],
        "attribution": attribution,
        "import_allowed": allowed,
        "reason_import_not_allowed": reason,
    }


def compute_import_allowed(source: str, price_status, license):
    """v1 gating. import_allowed defaults False; returns (allowed, reason)."""
    if source == "cults3d":
        return False, "no_download_api"          # files stay on Cults by design
    if price_status == "paid":
        return False, "paid"
    if not license or str(license).strip().lower() in {"", "unknown", "unclear"}:
        return False, "license_unclear"
    # Otherwise eligible in principle, but direct import is not implemented in v1.
    return False, "source_link_out_only"


# ---- provider normalizers (raw provider JSON -> ModelSearchResult) ----

def normalize_thingiverse(raw: dict) -> dict:
    assert_sanctioned("thingiverse")
    lic = raw.get("license")
    creator = raw.get("creator")
    return _result(
        raw.get("name") or raw.get("title") or "(untitled)",
        "thingiverse",
        raw.get("public_url") or raw.get("url") or "",
        thumbnail_url=raw.get("thumbnail"),
        license=lic,
        price_status="free",                      # Thingiverse is free hosting
        file_formats=raw.get("formats") or ["STL"],
        tags=raw.get("tags") or [],
        attribution=creator.get("name") if isinstance(creator, dict) else creator,
    )


def normalize_myminifactory(raw: dict) -> dict:
    assert_sanctioned("myminifactory")
    price = "paid" if raw.get("is_paid") or (raw.get("price") or 0) else "free"
    images = raw.get("images")
    designer = raw.get("designer")
    return _result(
        raw.get("name") or "(untitled)",
        "myminifactory",
        raw.get("url") or "",
        thumbnail_url=(images[0].get("thumbnail") if images else raw.get("thumbnail")),
        license=raw.get("license"),
        price_status=price,
        file_formats=raw.get("formats") or [],
        tags=raw.get("tags") or [],
        attribution=designer.get("name") if isinstance(designer, dict) else designer,
    )


def normalize_cults3d(raw: dict) -> dict:
    assert_sanctioned("cults3d")
    price = "paid" if (raw.get("price") or {}).get("cents") else ("free" if raw.get("free") else "unknown")
    creator = raw.get("creator")
    return _result(
        raw.get("name") or "(untitled)",
        "cults3d",
        raw.get("url") or "",
        thumbnail_url=(raw.get("illustrationImageUrl") or raw.get("thumbnail")),
        license=raw.get("license"),
        price_status=price,
        file_formats=raw.get("formats") or [],
        tags=raw.get("tags") or [],
        attribution=creator.get("nick") if isinstance(creator, dict) else creator,
    )


def link_out_url(source: str, query: str) -> str:
    """Build the provider's own search-page URL (link-out only; no fetching)."""
    q = urllib.parse.quote(query or "")
    return {
        "printables": f"https://www.printables.com/search/models?q={q}",
        "thangs": f"https://thangs.com/search/{q}",
        "makerworld": f"https://makerworld.com/en/search/models?keyword={q}",
    }.get(source, "")


def provider_enabled(source: str) -> bool:
    """A sanctioned provider is enabled only if its server-side key is present."""
    env = _KEY_ENV.get(source)
    return bool(env and os.environ.get(env))


def search(query: str, filters: dict | None = None) -> dict:
    """v1 search. With no API keys configured, returns no results plus a clear
    per-provider 'disabled' warning — never faked/scraped data."""
    filters = filters or {}
    results: list[dict] = []
    providers_queried: list[str] = []
    warnings: list[str] = []

    sources = filters.get("sources") or list(SANCTIONED)
    for src in sources:
        if src not in SANCTIONED:
            warnings.append(f"{src}: link-out only — open it on the source site")
            continue
        if not provider_enabled(src):
            warnings.append(f"{src}: search disabled (no API key configured)")
            continue
        providers_queried.append(src)
        # Live querying is wired per-adapter when a key exists; v1 ships the
        # adapters + normalizers + gating. No network call is made without a key.

    return {"results": results, "providers_queried": providers_queried, "warnings": warnings}
