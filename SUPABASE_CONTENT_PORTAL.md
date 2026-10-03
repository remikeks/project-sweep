# Supabase Content Portal Contract

## Scope and ownership

`/courses/content/` is SWEEP's authenticated content-admin workspace. It
gives authors, reviewers, and publishers a clear catalogue, direct browser
uploads, preview links, replacement drafts, and atomic metadata imports.

Supabase Storage owns file bytes. SWEEP owns the definitive course catalogue,
asset metadata, workflow audit trail, publication decision, and learner
visibility. A browser never receives a Supabase service-role/secret key.

The browser uploads with a short-lived, one-use signed URL issued by SWEEP.
After the upload succeeds, it registers metadata against the matching upload
authorization. This prevents an author from registering an arbitrary object
or another author's signed object.

## Roles and workflow

| Portal role | SWEEP permission | Allowed actions |
|---|---|---|
| Content Author | `add_courseasset`, `change_courseasset`, `view_courseasset` | Upload a draft, submit their own draft, prepare a replacement for their published or retired asset |
| Content Reviewer | `view_courseasset`, `review_courseasset` | Preview and approve content in review |
| Content Publisher | `view_courseasset`, `publish_courseasset`, `bulk_import_courseasset` | Publish, retire, and bulk-import metadata |

Transitions are one-way:

```text
draft --submit--> in_review --approve--> approved --publish--> published --retire--> retired
```

Only `published` assets appear to learners. A replacement is a new `draft`;
the prior published version stays available until the replacement is approved
and published, at which point SWEEP retires it. This retains a safe rollback
path and audit history.

Run this after migrations, then assign staff to the matching groups:

```text
python manage.py bootstrap_content_roles
```

## APIs

All administration endpoints are under `/courses/content-api/`. They accept a
normal authenticated Django session (with CSRF protection) or an explicitly
configured, verified Supabase user JWT in `Authorization: Bearer <token>`.
An invalid Bearer token never falls back to a browser session.

| Method and path | Permission | Purpose |
|---|---|---|
| `GET /catalog/` | view | Courses, modules, and asset metadata |
| `POST /uploads/sign/` | add | Issue a one-use signed upload URL |
| `POST /assets/` | add | Register an upload as a draft |
| `POST /assets/import/` | bulk import | Atomically import external-URL metadata |
| `GET /assets/<id>/preview/` | view | Create a short-lived preview URL for an asset |
| `POST /assets/<id>/replacement-upload/` | add | Issue a signed upload for a replacement |
| `POST /assets/<id>/replace/` | add | Register a replacement as a draft |
| `POST /assets/<id>/<action>/` | action-specific | Submit, approve, publish, or retire |

The learner-only download route is `GET /courses/assets/<id>/download/`. It
checks the learner's enrollment and redirects to a short-lived Storage URL;
the canonical Storage URL is not rendered into learner pages.

### Direct Storage upload

First request a signed URL:

```json
POST /courses/content-api/uploads/sign/
{
  "course_slug": "foundations-of-child-protection",
  "module_order": 1,
  "asset_type": "learner_guide",
  "filename": "learner-guide.pdf",
  "content_type": "application/pdf",
  "size_bytes": 245760
}
```

The response includes `upload_intent_id`, `upload_url`, `storage_path`, and
an expiry. Upload the bytes with `PUT upload_url`, then register them:

```json
POST /courses/content-api/assets/
{
  "course_slug": "foundations-of-child-protection",
  "module_order": 1,
  "title": "Learner guide",
  "asset_type": "learner_guide",
  "upload_intent_id": "a4f1b6f5-...",
  "version": "1.0",
  "language": "en",
  "order": 10,
  "is_downloadable": true
}
```

The client must not send a service-role key, a signed URL token to SWEEP, or
a client-selected storage path. SWEEP chooses a unique path under the course
prefix and permits a bounded set of document, spreadsheet, video, audio, and
plain-text MIME types. It also validates semantic version, language, URL,
file extension, upload size, course/module ownership, payload size, and bulk
row count.

### Bulk import

`POST /courses/content-api/assets/import/` accepts:

```json
{
  "assets": [
    {
      "course_slug": "foundations-of-child-protection",
      "module_order": 1,
      "title": "Learner guide",
      "asset_type": "learner_guide",
      "external_url": "https://cdn.example.org/guide.pdf",
      "version": "1.0",
      "language": "en",
      "order": 10,
      "is_downloadable": true
    }
  ]
}
```

It is atomic: no asset is added if a single submitted row is malformed or
references an unknown course/module. Imports create `draft` assets regardless
of client-supplied workflow fields.

## Required deployment configuration

The SWEEP Supabase project has the schema migrations, the three portal role
groups, and the private `sweep-course-assets` bucket configured. The bucket
enforces the same 100 MB and 13 MIME-type limits as the Django portal. It has
no direct browser RLS policy; Django must issue the short-lived signed URLs.

Configure these server environment variables in each Django runtime:

```text
SUPABASE_URL=https://zuieopythyjvupcxyjng.supabase.co
SUPABASE_STORAGE_BUCKET=sweep-course-assets
SUPABASE_SERVICE_ROLE_KEY=<server-only-secret>
SUPABASE_STORAGE_SIGNED_URL_TTL=600

SUPABASE_JWT_ISSUER=https://zuieopythyjvupcxyjng.supabase.co/auth/v1
SUPABASE_JWT_AUDIENCE=authenticated
SUPABASE_JWKS_URL=https://zuieopythyjvupcxyjng.supabase.co/auth/v1/.well-known/jwks.json
SUPABASE_JWT_ALGORITHMS=ES256
SUPABASE_JWT_ROLE_CLAIM=app_metadata.sweep_role
SUPABASE_JWT_ROLE_MAP={"content_author":["courses.add_courseasset","courses.change_courseasset","courses.view_courseasset"],"content_reviewer":["courses.view_courseasset","courses.review_courseasset"],"content_publisher":["courses.view_courseasset","courses.publish_courseasset","courses.bulk_import_courseasset"]}
```

JWT verification is fail-closed: issuer, audience, JWKS URL, and allowed
asymmetric algorithms must all be configured. HS algorithms and `none` are
rejected. The verifier validates signature, issuer, audience, lifetime,
subject, and Supabase's `authenticated` role, and caches JWKS for at most ten
minutes. It does not guess where portal claims live or which roles they mean.

For example, if the project's custom access-token hook intentionally emits
roles at `app_metadata.sweep_role`, configure that exact path and a JSON map
whose values are only these SWEEP permission strings:

```json
{
  "content_author": ["courses.add_courseasset", "courses.change_courseasset", "courses.view_courseasset"],
  "content_reviewer": ["courses.view_courseasset", "courses.review_courseasset"],
  "content_publisher": ["courses.view_courseasset", "courses.publish_courseasset", "courses.bulk_import_courseasset"]
}
```

The current Supabase Storage gateway accepts credential-free CORS preflight
requests from browser origins for `PUT` signed-upload URLs. This was verified
against the project; storage security is enforced by the private bucket and
the single-use signed URL, not a browser-origin allowlist. Keep the bucket
private unless a deliberately public distribution policy is approved. The
Storage service key belongs only in the Django runtime's secret store—never in
`.env` committed to Git, JavaScript, templates, logs, or API responses.

Run `python manage.py purge_content_upload_intents` on a scheduled job to
remove abandoned one-use upload authorizations; consumed records are retained
for seven days by default for operational traceability.
