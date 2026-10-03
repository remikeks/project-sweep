"""Authentication and permission mapping for the content-admin API.

Session-authenticated Django staff continue to work unchanged. A caller that
supplies a Bearer token must pass Supabase JWT verification; a bad token never
falls back to a logged-in browser session.
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from functools import wraps

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse

logger = logging.getLogger(__name__)

CONTENT_PERMISSIONS = frozenset(
    {
        "courses.add_courseasset",
        "courses.change_courseasset",
        "courses.view_courseasset",
        "courses.review_courseasset",
        "courses.publish_courseasset",
        "courses.bulk_import_courseasset",
    }
)


class PortalAuthenticationError(RuntimeError):
    pass


class PortalConfigurationError(RuntimeError):
    pass


def _claim_value(claims, dotted_path):
    value = claims
    for segment in dotted_path.split("."):
        if not segment:
            raise PortalConfigurationError("A configured JWT claim path is invalid.")
        if not isinstance(value, dict):
            return None
        value = value.get(segment)
    return value


def _claim_values(value):
    if isinstance(value, str):
        return {value}
    if isinstance(value, (list, tuple)) and all(isinstance(item, str) for item in value):
        return set(value)
    if value is None:
        return set()
    raise PortalAuthenticationError("The configured permissions claim has an invalid format.")


def _role_map():
    value = settings.SUPABASE_JWT_ROLE_MAP
    if not isinstance(value, dict):
        raise PortalConfigurationError("SUPABASE_JWT_ROLE_MAP must be a JSON object.")
    result = {}
    for role, permissions in value.items():
        if not isinstance(role, str):
            raise PortalConfigurationError("SUPABASE_JWT_ROLE_MAP contains an invalid role.")
        mapped_permissions = _claim_values(permissions)
        if not mapped_permissions <= CONTENT_PERMISSIONS:
            raise PortalConfigurationError("SUPABASE_JWT_ROLE_MAP contains an unsupported permission.")
        result[role] = mapped_permissions
    return result


class SupabaseJWTVerifier:
    """Verify only explicitly configured asymmetric Supabase access tokens."""

    _clients = {}

    def __init__(self):
        if not (
            settings.SUPABASE_JWT_ISSUER
            and settings.SUPABASE_JWT_AUDIENCE
            and settings.SUPABASE_JWKS_URL
            and settings.SUPABASE_JWT_ALGORITHMS
        ):
            raise PortalConfigurationError(
                "Supabase JWT verification is not configured for this environment."
            )
        parsed_algorithms = tuple(settings.SUPABASE_JWT_ALGORITHMS)
        if any(algorithm.startswith("HS") or algorithm == "none" for algorithm in parsed_algorithms):
            raise PortalConfigurationError("Only explicitly configured asymmetric JWT algorithms are accepted.")
        self.algorithms = parsed_algorithms
        self.issuer = settings.SUPABASE_JWT_ISSUER.rstrip("/")
        self.audience = settings.SUPABASE_JWT_AUDIENCE
        self.jwks_url = settings.SUPABASE_JWKS_URL

    def _jwks_client(self):
        cache_key = (self.jwks_url, settings.SUPABASE_JWKS_CACHE_SECONDS)
        client = self._clients.get(cache_key)
        if client is None:
            client = jwt.PyJWKClient(
                self.jwks_url,
                cache_keys=True,
                lifespan=settings.SUPABASE_JWKS_CACHE_SECONDS,
            )
            self._clients[cache_key] = client
        return client

    def verify(self, token):
        if token.count(".") != 2 or token.startswith("sb_"):
            raise PortalAuthenticationError("A Supabase user access token is required.")
        try:
            header = jwt.get_unverified_header(token)
            if header.get("alg") not in self.algorithms:
                raise PortalAuthenticationError("JWT uses an unapproved signing algorithm.")
            key = self._jwks_client().get_signing_key_from_jwt(token).key
            claims = jwt.decode(
                token,
                key,
                algorithms=self.algorithms,
                audience=self.audience,
                issuer=self.issuer,
                options={"require": ["exp", "iat", "iss", "aud", "sub"]},
            )
        except PortalAuthenticationError:
            raise
        except jwt.PyJWTError as exc:
            logger.info("Rejected Supabase JWT: %s", exc.__class__.__name__)
            raise PortalAuthenticationError("The Supabase access token is invalid or expired.") from exc
        except (OSError, ValueError) as exc:
            logger.warning("Unable to verify Supabase JWT: %s", exc.__class__.__name__)
            raise PortalAuthenticationError("The Supabase access token could not be verified.") from exc
        if claims.get("role") != "authenticated" or not isinstance(claims.get("sub"), str):
            raise PortalAuthenticationError("The access token is not an authenticated user session.")
        return claims


def permissions_from_claims(claims):
    """Map only a deployment-configured claim schema to SWEEP permissions."""
    permissions = set()
    claim_path = settings.SUPABASE_JWT_PERMISSION_CLAIM
    role_claim_path = settings.SUPABASE_JWT_ROLE_CLAIM
    if not claim_path and not role_claim_path:
        raise PortalConfigurationError("No Supabase claim-to-permission mapping has been configured.")
    if claim_path:
        values = _claim_values(_claim_value(claims, claim_path))
        if not values <= CONTENT_PERMISSIONS:
            raise PortalAuthenticationError("The access token requests an unsupported content permission.")
        permissions.update(values)
    if role_claim_path:
        role_map = _role_map()
        for role in _claim_values(_claim_value(claims, role_claim_path)):
            if role not in role_map:
                raise PortalAuthenticationError("The access token has no mapped content role.")
            permissions.update(role_map[role])
    return frozenset(permissions)


def _local_username(subject):
    # A hash keeps the local audit identity inside Django's default 150-char
    # username field even if an IdP uses a long opaque subject.
    digest = hashlib.sha256(subject.encode("utf-8")).hexdigest()
    return f"supabase-{digest}"


def local_user_for_claims(claims):
    """Create an unusable-password local audit identity for a verified subject."""
    user_model = get_user_model()
    username_field = user_model.USERNAME_FIELD
    lookup = {username_field: _local_username(claims["sub"])}
    defaults = {}
    email = claims.get("email")
    if email and any(field.name == "email" for field in user_model._meta.fields):
        defaults["email"] = email[:254]
    user, created = user_model.objects.get_or_create(defaults=defaults, **lookup)
    if created:
        user.set_unusable_password()
        user.save(update_fields=["password"])
    if not user.is_active:
        raise PortalAuthenticationError("This portal account is inactive.")
    return user


@dataclass(frozen=True)
class ContentActor:
    user: object
    permissions: frozenset
    source: str
    subject: str | None = None

    def has_perm(self, permission):
        return permission in self.permissions

    @property
    def is_superuser(self):
        return bool(getattr(self.user, "is_superuser", False))


def content_actor_from_request(request):
    """Resolve one content actor, preferring an explicit Bearer token."""
    authorization = request.headers.get("Authorization", "")
    if authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            raise PortalAuthenticationError("Use an Authorization: Bearer <token> header.")
        claims = SupabaseJWTVerifier().verify(token.strip())
        user = local_user_for_claims(claims)
        return ContentActor(
            user=user,
            permissions=permissions_from_claims(claims),
            source="supabase_jwt",
            subject=claims["sub"],
        )
    if request.user.is_authenticated:
        return ContentActor(
            user=request.user,
            permissions=frozenset(
                permission for permission in CONTENT_PERMISSIONS if request.user.has_perm(permission)
            ),
            source="django_session",
        )
    raise PortalAuthenticationError("Sign in to the content portal.")


def require_content_permission(permission):
    if permission not in CONTENT_PERMISSIONS:
        raise ValueError("Unsupported content permission.")

    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            try:
                actor = content_actor_from_request(request)
            except PortalConfigurationError as exc:
                return JsonResponse({"ok": False, "error": str(exc)}, status=503)
            except PortalAuthenticationError as exc:
                return JsonResponse({"ok": False, "error": str(exc)}, status=401)
            if not actor.is_superuser and not actor.has_perm(permission):
                return JsonResponse({"ok": False, "error": "You do not have permission for this action."}, status=403)
            request.content_actor = actor
            return view(request, *args, **kwargs)

        return wrapped

    return decorator
