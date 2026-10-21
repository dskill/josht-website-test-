# Josh Tuininga static website and Pages CMS prototype

Public demo: https://dskill.github.io/josht-website-test-/
Repository: https://github.com/dskill/josht-website-test-
CMS setup guide: https://dskill.github.io/josht-website-test-/cms.html

Separate project started from dskill/website, revised to preserve joshtuininga.com structure, layout, artwork, typography and wording. The original repository, domain and Squarespace account are unchanged. Original art and text remain their owners’ work.

## Pages CMS

The root `.pages.yml` configures the official hosted editor at https://app.pagescms.org/. The owner must separately review GitHub authorization and install the Pages CMS GitHub App for **only dskill/josht-website-test-**, then open this repository's **main** branch. No App installation, OAuth grant, persistent credential or invitation is part of this code change. A signed-in CMS save and upload must still be tested after authorization; do not call that flow verified merely because the build passes.

- `cms/homepage.json`: original homepage text and link fields.
- `cms/presentations.json`: original presentation descriptions and reviews.
- `cms/events.json`: upcoming events and additional past entries; date/time labels stay plain text so ambiguous source dates are not silently changed.
- `cms/images.json`: seven existing homepage/presentation image slots.
- `dist/assets/uploads/`: default upload folder. The media picker can also select existing local artwork under `dist/assets/`. Do not delete original files referenced elsewhere.
- `cms/templates.json`: maintainer-owned original markup and field mapping, not exposed in the CMS.

Plain text fields are inserted with HTML escaping into their original inline formatting. They are split where formatting changes; layout is not editable. The initial CMS data produces the same visitor HTML and all 28 text blocks as before. The original past-event archive remains unchanged; new archived entries are prepended beneath its existing heading. Optional event images and links are supported. Images must be local JPG/PNG/GIF/WebP files smaller than 20 MiB. Fixed artwork slots preserve original geometry; use a similar aspect ratio.

After authorization, Pages CMS saves a GitHub commit. Commits to main run `.github/workflows/pages.yml`: tests → JavaScript checks → static compilation → link validation → GitHub Pages deployment. A failed validation leaves the previous deployment live. No frontend write token or CMS runtime is served to visitors. GitHub Actions uses ephemeral minimum-permission tokens; Pages CMS authorization is separate.

## Build and test

Only Python's standard library and Node for syntax checks are needed:

    python -m unittest discover -s tests -v
    node --check dist/app.js
    node --check dist/editor.js
    python prepare_pages.py --base-path /josht-website-test-
    python validate_site.py --directory _site --base-path /josht-website-test-

Serve `_site/` under the configured base path. For root hosting, omit `--base-path`. `prepare_pages.py` reads committed `dist/` templates and `cms/*.json`, then generates `_site/` without modifying source. Asset paths in CMS data use `/assets/...`; the build adds the GitHub Pages project prefix. The browser override renderer also handles local image paths, including nested events routes and local drafts.

Tests use isolated seed fixtures, not live CMS edits. They cover no-op fidelity, text escaping, event add/reorder/remove/archive, optional empty serialization, uploaded image substitution, unsafe URLs and invalid media. Test/sample edits are never published. `.pages.yml` was additionally validated against Pages CMS's official Zod configuration schema; see `reference/pages-cms-validation.md`.

`build.py` is an archival migration tool requiring lxml. It is **not** part of normal publishing; do not use it for CMS updates. `source-original/` and `reference/` preserve source captures and maps. Source wording, date ambiguities and original navigation remain intact.

## Older local editor

`editor.html` still supports browser-local text preview and JSON export, without authentication or publication. It loads the compiled published content. Its exported `content.json` is **not** the source for CMS-controlled fields; a maintainer must transfer edits into the matching `cms/*.json` files. `dist/content.json` retains the legacy baseline and original archive. Avoid concurrent editing through both systems. Drafts use sessionStorage and need a downloaded backup.

Maintenance tools remain separate from the original visitor navigation at `cms.html`, `guide.html` and `editor.html`.

## Remaining limitations

- Newsletter/contact widgets are removed and labeled unsupported; nothing is collected or forwarded. The original cart and legacy iCalendar downloads are disabled.
- Original historical event-detail links still lead to joshtuininga.com; this is not a complete archive migration or a calendar service.
- Instagram is a frozen image snapshot. Original media embeds and book-purchase links still depend on external providers.
- All site artwork, styles, fonts and scripts are repo-local. No Squarespace CMS, analytics, commerce backend or account system is copied.
- Preview indexing remains disabled. Domain/DNS, email, redirects, complete archives and replacement services need review before replacing or cancelling Squarespace.
- No Cloudflare migration or collaborator invitation has been performed.
