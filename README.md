# Josh Tuininga static website

Public repository: https://github.com/dskill/josht-website-test-

Separate project started from dskill/website (f128e6fb3548264fb65dfb8e7bcceccf6a18f2f0), revised to preserve joshtuininga.com page structure, layout, images and wording. The original dskill/website repository, joshtuininga.com domain and Squarespace account are unchanged. Original art and text remain their owners’ work.

## Publish and update

GitHub Pages is published by `.github/workflows/pages.yml` on commits to `main`. Select GitHub Actions in repository Settings → Pages. The workflow validates JavaScript, prepares project-relative URLs, checks local links and uploads the static artifact. It does not run `build.py` or overwrite content edits. GitHub provides short-lived job tokens with minimum permissions: read-only source access for build and Pages deployment permission for the deployment job. No frontend token, personal access token or GitHub OAuth application is required.

For homepage or events updates:
1. Open `editor.html` on the published site.
2. Edit original rich-text blocks and preview locally.
3. Download `content.json`.
4. Replace `dist/content.json` in this repository and commit to `main`.
5. Check the Actions run and published result.

The editor does not commit, push or publish. It has no GitHub authorization. Drafts use browser sessionStorage key `josh-fidelity-draft`; download a backup. Schema 2 stores `pages.index` and `pages.events` arrays of blocks with `id`, `label` and `html`. Keep the original IDs. The old redesign’s schema 1 is incompatible.

Serve `dist/` with any static HTTP server. To test project paths: `python prepare_pages.py --base-path /josht-website-test-` then `python validate_site.py --directory _site --base-path /josht-website-test-`. All artwork, CSS and fonts are stored in `dist/assets/original/` and require no Squarespace asset service.

## Source fidelity

Visitor pages retain the original HTML, CSS, images and wording, including date ambiguities. The only new visitor text labels unsupported Squarespace features. `source-original/` retains the captured reference pages; `reference/` records original URL and asset maps and the starting repository templates. `build.py` requires lxml and preserves schema 2 content edits by block ID. Only `--refresh-original-content` explicitly resets content to the source. Ordinary content updates need no rebuild.

Maintenance tools are separate at `guide.html` and `editor.html`, not added to the original visitor navigation.

## Static-site limitations

- Newsletter and contact widgets are removed and clearly labeled unsupported; nothing is collected or forwarded.
- Squarespace iCalendar downloads are disabled and labeled unsupported. Legacy event-detail links still lead to the original public pages; this is not a full archive migration.
- Instagram images are a frozen snapshot, not a live feed.
- Original provider embeds and outbound book-purchase links remain external dependencies.
- No Squarespace CMS, analytics, commerce backend or account functionality is copied.
- Preview indexing is disabled. Review SEO, redirects, all needed archives, domain/email records and replacement services before changing the domain or cancelling Squarespace.

See `dist/guide.html` for editing and migration notes.
