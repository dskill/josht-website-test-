# Pages CMS prototype validation

Checked 2026-10-21 against official Pages CMS 2.1.8 source and documentation.

## Configuration

`.pages.yml` passed the official Zod `ConfigSchema` with zero schema issues and zero YAML warnings/errors. Official schema blob: `cc434fd87bcebc80aa8fe777b99c7d0f943ef11f`. The temporary validator used Zod 3.25.76 and YAML 2.4.2; only the Next.js field-registry import was replaced by its exact verified set of field types. No production dependency or authentication was added.

- Schema: https://github.com/hunvreus/pagescms/blob/main/lib/config-schema.ts
- Field schemas and save behavior: https://github.com/hunvreus/pagescms/blob/main/lib/schema.ts
- Serialization: https://github.com/hunvreus/pagescms/blob/main/lib/serialization.ts
- Image mapping: https://github.com/hunvreus/pagescms/blob/main/fields/core/image/index.tsx
- Docs: https://pagescms.org/docs/configuration/
- Setup: https://pagescms.org/docs/quick-start/

All four initial JSON content files passed the upstream generated field schemas. The seven current image values resolved to local files and survived input/output mapping unchanged. A synthetic upload maps `dist/assets/uploads/test-new-photo.jpg` to `/assets/uploads/test-new-photo.jpg`; the deployment compiler adds the GitHub Pages base path.

The upstream save pipeline was simulated for text clearing and event deletion. Required fixed object groups prevent merge mode from restoring cleared text. Removed optional fields and empty lists are supported by the renderer; wholly blank homepage/presentation files are treated as empty objects, matching upstream empty serialization.

## Rendering

Before adding maintenance guide content, every existing HTML page was byte-identical to its prior prepared output. After adding the guide links, all 15 visitor pages remain byte-identical; only separate maintenance pages differ. All 28 initial content blocks are exactly equal after JSON parsing. No new sample event or edited wording is published.

The isolated standard-library tests cover no-op output, escaped text edits, event creation/reordering/removal/archiving, omitted optional fields, fully cleared text files, image replacement and alt text, missing media, unsafe URLs and missing template slots. Tests use immutable original fixtures so later legitimate CMS edits do not invalidate fidelity assertions. The regular build separately validates current content.

## Not yet verified

No hosted App installation, OAuth grant, signed-in CMS save, actual hosted upload or invitation was performed. Repository commit and GitHub Pages deployment verification do not substitute for the first authenticated CMS edit test. The owner must review the actual hosted GitHub App permission screen and choose only this test repository; current App documentation lists broader permissions including Administration and Actions write.
