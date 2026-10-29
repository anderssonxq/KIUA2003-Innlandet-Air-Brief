"""Bounded MET requests with persistent HTTP caching and no automatic retries."""
import gzip
import io
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from .core import DESCRIPTOR_URL, FORECAST_URL, Rejected, load_json, require, sha256, write_json

MAX_BYTES = 2 * 1024 * 1024
FORBIDDEN_KEYS = {"contact", "email", "phone", "telephone", "person", "persons", "user", "users", "account", "accounts", "author"}


def check_no_contact_metadata(value):
    if isinstance(value, dict):
        require(not FORBIDDEN_KEYS.intersection(k.lower() for k in value), "Unexpected personal/contact metadata; source rejected")
        for child in value.values():
            check_no_contact_metadata(child)
    elif isinstance(value, list):
        for child in value:
            check_no_contact_metadata(child)
    elif isinstance(value, str):
        require(not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", value), "Unexpected email address in source; rejected")


def http_date(value):
    try:
        stamp = parsedate_to_datetime(value)
        return stamp if stamp.tzinfo else stamp.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    """MET asks clients to follow redirects; restrict them to its HTTPS product."""
    def __init__(self):
        super().__init__()
        self.redirect_count = 0

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parts = urllib.parse.urlparse(newurl)
        require(parts.scheme == "https" and parts.hostname == "api.met.no" and parts.port in (None, 443), "Redirect outside MET HTTPS origin rejected")
        require(not parts.username and not parts.password and parts.path.startswith("/weatherapi/airqualityforecast/"), "Redirect outside source product rejected")
        self.redirect_count += 1
        require(self.redirect_count <= 2, "Source redirect limit exceeded")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def decode_source(data):
    try:
        payload = json.loads(data)
    except (ValueError, UnicodeError) as exc:
        raise Rejected("Source response contains invalid JSON") from exc
    require(isinstance(payload, dict), "Source response must be a JSON object")
    check_no_contact_metadata(payload)
    return payload


def fetch_json(url, cache_dir, now=None):
    require(url in (FORECAST_URL, DESCRIPTOR_URL), "Source URL is not allowlisted")
    now = now or datetime.now(timezone.utc)
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    stem = sha256(url.encode("utf-8"))
    body_path, meta_path = cache_dir / (stem + ".json"), cache_dir / (stem + ".http.json")
    cached = load_json(meta_path) if meta_path.exists() else {}
    require(isinstance(cached, dict), "Malformed cache metadata")
    expiry = http_date(cached.get("expires"))
    if body_path.exists() and expiry and now < expiry:
        data = body_path.read_bytes()
        require(sha256(data) == cached.get("sha256"), "Cached source hash mismatch")
        payload = decode_source(data)
        return payload, {**cached, "transport": "cache_before_expires"}
    user_agent = os.environ.get("MET_USER_AGENT", "KIUA2003-InnlandetAirBrief/0.1")
    require(0 < len(user_agent) <= 256 and "\n" not in user_agent and "\r" not in user_agent, "Invalid MET User-Agent")
    headers = {"User-Agent": user_agent, "Accept": "application/json", "Accept-Encoding": "gzip"}
    if body_path.exists() and cached.get("last_modified"):
        headers["If-Modified-Since"] = cached["last_modified"]
    request = urllib.request.Request(url, headers=headers)
    # Honor system HTTPS proxy settings (needed on managed/campus networks).
    # The initial URLs and redirect destinations remain explicitly restricted.
    opener = urllib.request.build_opener(SafeRedirect())
    try:
        response = opener.open(request, timeout=20)
    except urllib.error.HTTPError as exc:
        if exc.code == 304 and body_path.exists():
            data = body_path.read_bytes()
            require(sha256(data) == cached.get("sha256"), "Cached source hash mismatch")
            cached.update({"expires": exc.headers.get("Expires", cached.get("expires")), "status": 304})
            write_json(meta_path, cached)
            payload = decode_source(data)
            return payload, {**cached, "transport": "conditional_304"}
        raise Rejected(f"MET returned HTTP {exc.code}; halted without retry") from exc
    except (OSError, urllib.error.URLError) as exc:
        raise Rejected("MET request failed or timed out; halted without retry") from exc
    with response:
        require(response.status == 200, f"Unexpected MET status {response.status}; halted")
        require("application/json" in response.headers.get("Content-Type", ""), "MET response is not JSON")
        data = response.read(MAX_BYTES + 1)
        require(len(data) <= MAX_BYTES, "Compressed source response exceeds 2 MiB")
        if response.headers.get("Content-Encoding", "").lower() == "gzip":
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
                data = stream.read(MAX_BYTES + 1)
        require(len(data) <= MAX_BYTES, "Source response exceeds 2 MiB")
        payload = decode_source(data)
        metadata = {"url": url, "status": 200, "retrieved_at": now.isoformat(), "expires": response.headers.get("Expires"), "last_modified": response.headers.get("Last-Modified"), "sha256": sha256(data), "bytes": len(data)}
        body_path.write_bytes(data)
        write_json(meta_path, metadata)
        return payload, {**metadata, "transport": "network_200"}


def acquire(source, fixture_dir, cache_dir):
    if source == "live":
        forecast, forecast_meta = fetch_json(FORECAST_URL, cache_dir)
        descriptor, descriptor_meta = fetch_json(DESCRIPTOR_URL, cache_dir)
        return forecast, descriptor, {"mode": "live", "forecast": forecast_meta, "descriptor": descriptor_meta, "endpoint_requests_max": 2, "redirects_per_endpoint_max": 2, "http_transactions_max": 6, "retry_limit": 0}
    directory = Path(fixture_dir)
    forecast_path, descriptor_path = directory / "hamar_aqi_20261027.json", directory / "aqi_descriptor.json"
    forecast, descriptor = load_json(forecast_path), load_json(descriptor_path)
    check_no_contact_metadata(forecast)
    check_no_contact_metadata(descriptor)
    manifest = load_json(directory / "source_manifest.json")
    require(sha256(forecast_path.read_bytes()) == manifest["forecast"]["sha256"], "Fixture forecast hash mismatch")
    require(sha256(descriptor_path.read_bytes()) == manifest["descriptor"]["sha256"], "Fixture descriptor hash mismatch")
    return forecast, descriptor, {**manifest, "mode": "fixture", "historical": True}
