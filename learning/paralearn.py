"""Fail-closed transport for ParaLearn CBT's documented external API."""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlsplit
from urllib.request import Request, urlopen

from django.conf import settings


class ParaLearnError(Exception):
    """Base integration error safe to present as a generic learner message."""


class ParaLearnConfigurationError(ParaLearnError):
    """The deployment has not supplied the required workspace credentials."""


class ParaLearnRequestError(ParaLearnError):
    """The configured provider could not complete a request."""


class ParaLearnResultNotFoundError(ParaLearnRequestError):
    """ParaLearn has not created a result slip for this attempt yet."""


class ParaLearnProtocolError(ParaLearnError):
    """A provider response does not satisfy the documented CBT contract."""


@dataclass(frozen=True)
class LaunchResponse:
    provider_candidate_id: str
    launch_url: str


def launch_is_configured() -> bool:
    """Require a real workspace key before an outbound provision request."""
    return bool(
        settings.PARALEARN_API_BASE_URL
        and settings.PARALEARN_API_KEY
        and settings.PARALEARN_API_KEY_HEADER
    )


def result_reconciliation_is_configured() -> bool:
    """Polling needs the same authenticated workspace configuration as launch."""
    return launch_is_configured() and bool(settings.PARALEARN_RESULT_PATH_TEMPLATE)


def webhook_is_configured() -> bool:
    """Webhooks need only the workspace's HMAC secret and known HMAC scheme."""
    return bool(
        settings.PARALEARN_WEBHOOK_SIGNING_SECRET
        and settings.PARALEARN_WEBHOOK_SIGNATURE_HEADER
        and settings.PARALEARN_WEBHOOK_SIGNATURE_ALGORITHM == "hmac-sha256"
    )


def payload_sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verify_webhook_signature(payload: bytes, supplied_signature: str | None) -> bool:
    """Verify ParaLearn's documented ``sha256=<HMAC>`` against raw bytes."""
    if not webhook_is_configured() or not supplied_signature:
        return False
    prefix = settings.PARALEARN_WEBHOOK_SIGNATURE_PREFIX
    if prefix and not supplied_signature.startswith(prefix):
        return False
    candidate = supplied_signature[len(prefix):] if prefix else supplied_signature
    expected = hmac.new(
        settings.PARALEARN_WEBHOOK_SIGNING_SECRET.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(candidate.strip().lower(), expected)


class ParaLearnClient:
    """Client for candidate provisioning and result-slip retrieval.

    SWEEP supplies its local attempt UUID as ParaLearn's ``externalAttemptId``
    and a separately generated opaque learner UUID as ``studentId``. The
    provider returns a hosted Candidate Gate deep link; SWEEP never constructs
    that URL or handles the candidate PIN itself.
    """

    def _require_launch_configuration(self):
        if not launch_is_configured():
            raise ParaLearnConfigurationError(
                "ParaLearn launch is disabled until SWEEP has a workspace API key in its secret manager."
            )
        parsed = urlsplit(settings.PARALEARN_API_BASE_URL)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ParaLearnConfigurationError("ParaLearn API base URL must be an absolute HTTPS URL.")

    @staticmethod
    def _absolute_url(base_url: str, path: str) -> str:
        if not path.startswith("/"):
            raise ParaLearnConfigurationError("ParaLearn endpoint paths must start with '/'.")
        return urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))

    @staticmethod
    def _required_text(payload: dict[str, Any], name: str) -> str:
        value = payload.get(name)
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > 2000:
            raise ParaLearnProtocolError(f"ParaLearn response is missing a valid {name}.")
        return value.strip()

    def _request_json(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        self._require_launch_configuration()
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = Request(self._absolute_url(settings.PARALEARN_API_BASE_URL, path), data=data, method=method)
        request.add_header("Accept", "application/json")
        request.add_header(
            settings.PARALEARN_API_KEY_HEADER,
            f"{settings.PARALEARN_API_KEY_PREFIX}{settings.PARALEARN_API_KEY}",
        )
        if data is not None:
            request.add_header("Content-Type", "application/json")
        try:
            with urlopen(request, timeout=settings.PARALEARN_HTTP_TIMEOUT_SECONDS) as response:  # nosec B310 - configured HTTPS URL
                response_body = response.read()
        except HTTPError as exc:
            if method == "GET" and exc.code == 404:
                raise ParaLearnResultNotFoundError("ParaLearn has not published a result slip yet.") from exc
            raise ParaLearnRequestError(f"ParaLearn returned HTTP {exc.code}.") from exc
        except (URLError, TimeoutError) as exc:
            raise ParaLearnRequestError("ParaLearn could not be reached.") from exc
        try:
            decoded = json.loads(response_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ParaLearnProtocolError("ParaLearn returned invalid JSON.") from exc
        if not isinstance(decoded, dict):
            raise ParaLearnProtocolError("ParaLearn returned an unexpected JSON body.")
        return decoded

    def _validate_launch_url(self, launch_url: str) -> str:
        parsed = urlsplit(launch_url)
        allowed_hosts = {host.lower() for host in settings.PARALEARN_ALLOWED_LAUNCH_HOSTS}
        if not allowed_hosts:
            allowed_hosts.add(urlsplit(settings.PARALEARN_API_BASE_URL).hostname or "")
        if parsed.scheme != "https" or not parsed.hostname or parsed.hostname.lower() not in allowed_hosts:
            raise ParaLearnProtocolError("ParaLearn returned a launch URL outside the configured HTTPS hosts.")
        return launch_url

    def create_launch(self, *, attempt, learner_identity) -> LaunchResponse:
        """Provision one candidate and receive ParaLearn's hosted SSO deep link."""
        response = self._request_json(
            "POST",
            settings.PARALEARN_CANDIDATE_PROVISION_PATH,
            {
                "examId": attempt.course.paralearn_assessment_id,
                "candidateName": attempt.user.get_full_name() or attempt.user.get_username(),
                "studentId": str(learner_identity.external_id),
                "externalAttemptId": str(attempt.id),
                "email": attempt.user.email,
                "metadata": {
                    "sweepLearnerId": str(learner_identity.external_id),
                    "sweepAttemptId": str(attempt.id),
                },
            },
        )
        return LaunchResponse(
            provider_candidate_id=self._required_text(response, "id"),
            launch_url=self._validate_launch_url(self._required_text(response, "launchUrl")),
        )

    def fetch_result(self, *, attempt_reference: str) -> dict[str, Any]:
        """Fetch a documented result slip by ParaLearn or SWEEP attempt ID."""
        if not result_reconciliation_is_configured():
            raise ParaLearnConfigurationError(
                "ParaLearn result reconciliation is disabled until workspace credentials are configured."
            )
        path = settings.PARALEARN_RESULT_PATH_TEMPLATE
        if "{attempt_reference}" in path:
            path = path.replace("{attempt_reference}", quote(attempt_reference, safe=""))
        elif "{provider_attempt_id}" in path:
            # Support this former setting name for existing deployments. Both
            # ParaLearn's internal ID and SWEEP's external UUID are accepted
            # by the documented result-slip endpoint.
            path = path.replace("{provider_attempt_id}", quote(attempt_reference, safe=""))
        else:
            raise ParaLearnConfigurationError(
                "ParaLearn result path must contain the {attempt_reference} placeholder."
            )
        return self._request_json("GET", path)
