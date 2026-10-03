"""Small, server-only adapter for Supabase Storage's signed URL endpoints."""

import json
import logging
import re
from dataclasses import dataclass
from datetime import timedelta
from pathlib import PurePath
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen
from uuid import uuid4

from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify

logger = logging.getLogger(__name__)


class StorageConfigurationError(RuntimeError):
    """Raised when direct-to-storage uploads have not been configured."""


class StorageRequestError(RuntimeError):
    """Raised for an unsuccessful Storage API request without leaking secrets."""


ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "text/plain",
    "text/csv",
    "video/mp4",
    "video/webm",
    "audio/mpeg",
    "audio/mp4",
}

ASSET_TYPE_CONTENT_TYPES = {
    "learner_guide": {
        "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword", "text/plain",
    },
    "slides": {
        "application/pdf", "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.ms-powerpoint",
    },
    "video": {"video/mp4", "video/webm", "audio/mpeg", "audio/mp4"},
    "transcript": {
        "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword", "text/plain",
    },
    "worksheet": {
        "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel", "text/csv", "text/plain",
    },
    "reference": ALLOWED_CONTENT_TYPES,
}

EXTENSIONS_BY_CONTENT_TYPE = {
    "application/pdf": {".pdf"},
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": {".pptx"},
    "application/vnd.ms-powerpoint": {".ppt"},
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {".docx"},
    "application/msword": {".doc"},
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {".xlsx"},
    "application/vnd.ms-excel": {".xls"},
    "text/plain": {".txt", ".md"},
    "text/csv": {".csv"},
    "video/mp4": {".mp4"},
    "video/webm": {".webm"},
    "audio/mpeg": {".mp3"},
    "audio/mp4": {".m4a", ".mp4"},
}

_BUCKET_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,62}$")
_SAFE_PATH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,499}$")


@dataclass(frozen=True)
class SignedUpload:
    url: str
    storage_path: str
    expires_at: object


def _configured_base_url():
    value = settings.SUPABASE_URL.rstrip("/")
    parsed = urlparse(value)
    if not value or not parsed.netloc or parsed.scheme not in {"https", "http"}:
        raise StorageConfigurationError("Supabase Storage has not been configured with a valid project URL.")
    if parsed.scheme != "https" and not settings.DEBUG:
        raise StorageConfigurationError("Supabase Storage must use HTTPS outside local development.")
    return value


def storage_is_configured():
    return bool(settings.SUPABASE_URL and settings.SUPABASE_STORAGE_BUCKET and settings.SUPABASE_SERVICE_ROLE_KEY)


def _bucket_name():
    bucket = settings.SUPABASE_STORAGE_BUCKET
    if not _BUCKET_RE.fullmatch(bucket):
        raise StorageConfigurationError("The configured Supabase Storage bucket name is invalid.")
    return bucket


def _ttl():
    return min(max(int(settings.SUPABASE_STORAGE_SIGNED_URL_TTL), 60), 7200)


def validate_upload_metadata(*, asset_type, filename, content_type, size_bytes):
    if asset_type not in ASSET_TYPE_CONTENT_TYPES:
        raise ValueError("Choose a supported asset type.")
    if not isinstance(filename, str) or not filename.strip() or len(filename) > 255:
        raise ValueError("Provide a file name up to 255 characters long.")
    if not isinstance(content_type, str) or content_type.lower() not in ALLOWED_CONTENT_TYPES:
        raise ValueError("This file type is not allowed in the content portal.")
    content_type = content_type.lower()
    if content_type not in ASSET_TYPE_CONTENT_TYPES[asset_type]:
        raise ValueError("This file type does not match the selected asset type.")
    if isinstance(size_bytes, bool) or not isinstance(size_bytes, int) or not 0 < size_bytes <= settings.CONTENT_PORTAL_MAX_UPLOAD_BYTES:
        raise ValueError(f"File size must be between 1 byte and {settings.CONTENT_PORTAL_MAX_UPLOAD_BYTES} bytes.")
    suffix = PurePath(filename).suffix.lower()
    if suffix not in EXTENSIONS_BY_CONTENT_TYPE.get(content_type, set()):
        raise ValueError("The file extension does not match its declared content type.")


def build_storage_path(*, course_slug, module_order, filename):
    """Build a non-overwritable, traversal-safe object name under a fixed prefix."""
    path = PurePath(filename.replace("\\", "/"))
    suffix = path.suffix.lower()
    stem = slugify(path.stem)[:80] or "asset"
    location = f"module-{module_order}" if module_order is not None else "course"
    result = f"courses/{course_slug}/{location}/{uuid4().hex}-{stem}{suffix}"
    if not _SAFE_PATH_RE.fullmatch(result) or ".." in PurePath(result).parts:
        raise ValueError("Could not safely create an object path for this file.")
    return result


def canonical_storage_url(storage_path):
    """Canonical, non-signed URL kept for metadata; learners receive a signed URL."""
    base = _configured_base_url()
    bucket = _bucket_name()
    if not _SAFE_PATH_RE.fullmatch(storage_path) or ".." in PurePath(storage_path).parts:
        raise ValueError("Storage path is invalid.")
    return f"{base}/storage/v1/object/authenticated/{quote(bucket, safe='')}/{quote(storage_path, safe='/')}"


class SupabaseStorageClient:
    """Uses only standard-library HTTP so no Supabase server SDK is required."""

    def __init__(self):
        if not storage_is_configured():
            raise StorageConfigurationError(
                "Direct Supabase uploads are unavailable until the server-only Storage key is configured."
            )
        self.base_url = _configured_base_url()
        self.bucket = _bucket_name()
        self.key = settings.SUPABASE_SERVICE_ROLE_KEY

    @property
    def storage_api_url(self):
        return f"{self.base_url}/storage/v1"

    def _request(self, *, endpoint, payload):
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            f"{self.storage_api_url}{endpoint}",
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.key}",
                "apikey": self.key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=10) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            logger.warning("Supabase Storage request failed with status %s.", exc.code)
            raise StorageRequestError("Supabase Storage rejected the request.") from exc
        except URLError as exc:
            logger.warning("Supabase Storage could not be reached: %s", exc.reason)
            raise StorageRequestError("Supabase Storage could not be reached.") from exc
        except OSError as exc:
            logger.warning("Supabase Storage request failed: %s", exc)
            raise StorageRequestError("Supabase Storage request failed.") from exc
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.warning("Supabase Storage returned a non-JSON response.")
            raise StorageRequestError("Supabase Storage returned an invalid response.") from exc

    def create_signed_upload_url(self, storage_path):
        encoded = f"{quote(self.bucket, safe='')}/{quote(storage_path, safe='/')}"
        data = self._request(endpoint=f"/object/upload/sign/{encoded}", payload={})
        relative_url = data.get("url") if isinstance(data, dict) else None
        if not isinstance(relative_url, str) or not relative_url.startswith("/object/upload/sign/"):
            raise StorageRequestError("Supabase Storage returned an invalid upload URL.")
        return SignedUpload(
            url=f"{self.storage_api_url}{relative_url}",
            storage_path=storage_path,
            expires_at=timezone.now() + timedelta(seconds=_ttl()),
        )

    def create_signed_download_url(self, storage_path, *, download=False):
        encoded = f"{quote(self.bucket, safe='')}/{quote(storage_path, safe='/')}"
        data = self._request(endpoint=f"/object/sign/{encoded}", payload={"expiresIn": _ttl()})
        relative_url = data.get("signedURL") if isinstance(data, dict) else None
        if not isinstance(relative_url, str) or not relative_url.startswith("/object/sign/"):
            raise StorageRequestError("Supabase Storage returned an invalid preview URL.")
        suffix = "&download=" if download else ""
        return f"{self.storage_api_url}{relative_url}{suffix}"
