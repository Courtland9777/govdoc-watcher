# govdoc-watcher

Containerized watcher/downloader for public government guideline PDFs. It solves manual checking/downloading/replacing by dynamically discovering current document links from stable listing pages.

## Why dynamic discovery
Government PDF URLs change by year/update cycle, so this service discovers links from listing pages (for CMS, ICD-10 listing page) instead of pinning a fixed URL.

## Service layout
Repository root is the app root. Key paths: `./config/`, `./data/active`, `./data/archive`, `./data/metadata`, `./logs/`, `./src/govdoc_watcher/`, `./tests/`.

## Source configuration
`config/sources.yaml`:
- id, name, agency, discovery_url, document_type
- required_text_patterns, exclude_text_patterns
- allowed_extensions
- prefer_newest_year
- check_interval_hours, enabled

## Discovery flow
1. Fetch discovery page.
2. Parse all anchors.
3. Normalize relative links.
4. Build candidates from anchor text + URL.
5. For the CMS ICD-10-PCS source, keep dated update PDFs only (`/files/document/<month>-<day>-<year>-official-icd-10-pcs-coding-guidelines.pdf`). Annual files are intentionally ignored because they are not considered the latest operational document for this workflow.
6. Reject excluded/unavailable links.
7. Rank and choose best candidate.

## Ranking
Generic source ranking weights required pattern match, extension match, and detected year. Excluded links are disqualified. The CMS ICD-10-PCS source uses source-specific URL matching and selects the newest parsed dated update PDF.

## Add another source
Add another item in `config/sources.yaml` with its discovery URL and pattern rules.

## Run
```bash
docker compose config
docker compose up -d --build
docker compose logs -f
```

One-shot mode:
```bash
RUN_ONCE=true docker compose up --build
```

## Host file locations (repository root bind mounts)
- Active PDFs: `./data/active/<source-id>.pdf`
- Archived PDFs: `./data/archive/<source-id>/...`
- Metadata: `./data/metadata/<source-id>.json`
- Logs: `./logs/govdoc-watcher.log`

## Error handling
Handles discovery/download HTTP failures, malformed or unmatched links, unavailable entries, non-PDF/zero-byte/invalid header downloads, metadata persistence errors, and safe replacement semantics.

## Healthcheck note
No healthcheck yet because no internal endpoint/CLI probe exists that reliably represents end-to-end watcher health in this version.

## Limitations
- Generic HTML matching may need source-specific tuning.
- No notifications yet.
- No API/UI in this phase.

## Future extension points
- API
- MCP
- web UI
- notification integrations
- source-specific scrapers
- authenticated sources

This phase intentionally exposes no web service; Nginx Proxy Manager and `proxy_net` are not required.
