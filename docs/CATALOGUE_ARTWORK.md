# Catalogue artwork

Ten original illustrations were generated with the built-in image generation tool
for the ten current schools. Courses inherit their school's artwork; these are
school-aligned thumbnails, not unique illustrations for every course.

The exact prompts and original local source paths are recorded in
`scripts/catalogue_thumbnail_sources.json`. The original PNGs are local generation
artifacts, not deployment dependencies. The checked-in WebP files in
`static/img/catalogue/` are the deployment assets.

Each illustration has 480-pixel and 960-pixel variants in a 3:2 ratio. Cards use
responsive sources and lazy loading; detail-page artwork loads eagerly. Images
are decorative because adjacent headings identify the school or course. Existing
valid uploaded school posters take precedence over generated artwork.

`core/catalogue_artwork.py` maps stable school slugs to image identities. Unknown
schools use the community illustration. No database migration, duplicated course
resource, or storage upload is needed for this presentation-only update.

To regenerate WebP variants from the original PNGs, provide `RUNTIME_NODE_MODULES`
pointing to a Node modules directory containing Sharp, update local source paths
if necessary, and run `node scripts/prepare_catalogue_thumbnails.mjs` from the
repository root. Image generation prompts should be retained when replacing art.

This artwork update does not publish the four staged curriculum courses or their
32 review assets. Curriculum and assessment review remain separate release gates.
