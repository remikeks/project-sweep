# Supabase Content Portal Contract

## Scope

The Supabase portal owns author-facing uploads and review screens. SWEEP owns
the definitive catalogue, publication workflow, and learner visibility.

Upload files directly to the configured Supabase Storage bucket. Once an
upload succeeds, register its URL and metadata with SWEEP; do not expose a
Supabase service-role key in the browser.

## Roles

| Portal role | SWEEP permission | Allowed actions |
|---|---|---|
| Content Author | `add_courseasset`, `change_courseasset`, `view_courseasset` | Register a draft; submit it for review |
| Content Reviewer | `review_courseasset` | Approve reviewed content |
| Content Publisher | `publish_courseasset`, `bulk_import_courseasset` | Publish, retire, and bulk-import metadata |

Run `python manage.py bootstrap_content_roles` after deploying migrations,
then assign staff to the Django groups with the matching names.

## API

All endpoints are under `/courses/content-api/`. They are currently protected
by Django permissions and are designed for a same-origin admin or a later
Supabase JWT/service-token authentication adapter.

### Read catalogue

`GET /catalog/`

Returns courses, modules, and all asset metadata for the portal.

### Register one uploaded asset

`POST /assets/`

```json
{
  "course_slug": "foundations-of-child-protection",
  "module_order": 1,
  "title": "Learner guide",
  "asset_type": "learner_guide",
  "external_url": "https://<project>.supabase.co/storage/v1/object/.../guide.pdf",
  "version": "1.0",
  "language": "en",
  "order": 10,
  "is_downloadable": true
}
```

The asset is always registered as a `draft`, regardless of client input.

### Bulk import

`POST /assets/import/`

Send `{ "assets": [ ... ] }` with the same records as above. The request is
atomic: no asset is added if any submitted record is invalid.

### Workflow action

`POST /assets/<asset_id>/<action>/`

Valid transitions are:

```text
draft --submit--> in_review --approve--> approved --publish--> published --retire--> retired
```

Only `published` assets appear on learner module pages.

## Required Supabase configuration

Set the following server environment variables when the Supabase project is
available:

```text
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_STORAGE_BUCKET=sweep-course-assets
SUPABASE_JWT_ISSUER=https://<project>.supabase.co/auth/v1
SUPABASE_JWT_AUDIENCE=authenticated
```

The next integration step is a JWT-verification adapter that maps Supabase
portal claims to the SWEEP permissions above. It requires the actual issuer,
audience, signing-key/JWKS policy, and portal-origin URL; these are project
specific and must not be guessed.
