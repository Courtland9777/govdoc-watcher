# govdoc-watcher

Small Python/Docker project for watching public government document listing pages and keeping a local copy of the selected PDF. It is designed around dynamic discovery: the watcher starts from a stable listing page, ranks candidate PDF links, downloads the selected document, validates that it looks like a PDF, and records local metadata.

Current status: public review / portfolio-support cleanup. This repository is a focused local utility, not a hosted product, public API, notification service, clinical system, HIPAA-validated workflow, or patient-data workflow.

## What it demonstrates

- A containerized background watcher with a one-shot run mode.
- Configuration-driven document source definitions.
- HTML link discovery and source-specific ranking for CMS ICD-10-PCS update PDFs.
- Safe local replacement semantics with archived prior active PDFs.
- Metadata persistence for selected URL, checksums, timestamps, ranking reason, and errors.
- Unit tests around discovery, ranking, config loading, downloading, storage, and project layout.

## Current source

The included configuration tracks the public CMS ICD-10-PCS Coding Guidelines listing page:

- `discovery_url`: `https://www.cms.gov/medicare/coding-billing/icd-10-codes`
- selected document type: dated official ICD-10-PCS coding guideline update PDFs
- intentionally ignored for this workflow: annual guideline files and unavailable links

No CMS PDF is committed to this repository. Runtime downloads, archives, metadata, and logs are local generated artifacts.

## Discovery flow

1. Fetch discovery page.
2. Parse all anchors.
3. Normalize relative links.
4. Build candidates from anchor text and URL.
5. For the CMS ICD-10-PCS source, keep dated update PDFs only (`/files/document/<month>-<day>-<year>-official-icd-10-pcs-coding-guidelines.pdf`). Annual files are intentionally ignored because they are not considered the latest operational document for this workflow.
6. Reject excluded or unavailable links.
7. Rank and choose the best candidate.

## Ranking

Generic source ranking weights required pattern match, extension match, and detected year. Excluded links are disqualified. The CMS ICD-10-PCS source uses source-specific URL matching and selects the newest parsed dated update PDF.

## Repository layout

- `config/sources.yaml`: source definitions and discovery/ranking rules.
- `src/govdoc_watcher/`: application code.
- `tests/`: pytest coverage for core behavior.
- `data/active/`: generated active PDFs at runtime.
- `data/archive/`: generated archived prior active PDFs at runtime.
- `data/metadata/`: generated metadata JSON at runtime.
- `logs/`: generated runtime logs.

The generated `data/` and `logs/` directories are represented by `.gitkeep` files only.

## Configuration

`config/sources.yaml` supports:

- `id`, `name`, `agency`, `discovery_url`, `document_type`
- `required_text_patterns`, `exclude_text_patterns`
- `allowed_extensions`
- `prefer_newest_year`
- `check_interval_hours`, `enabled`

Environment variables are shown in `.env.example`:

- `RUN_ONCE`: run one cycle and exit when `true`.
- `DEFAULT_CHECK_INTERVAL_HOURS`: loop delay when not running once.
- `LOG_LEVEL`: Python logging level.
- `HTTP_TIMEOUT_SECONDS`: HTTP timeout for discovery and download requests.
- `USER_AGENT`: outbound request user agent.

## Local setup

Python validation:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e '.[test]'
python3 -m pytest
```

Docker Compose validation:

```bash
cp .env.example .env
docker compose config
```

Runtime commands are intentionally separate from validation because they can make live network requests and write generated files:

```bash
docker compose up -d --build
docker compose logs -f
```

One-shot mode:

```bash
RUN_ONCE=true docker compose up --build
```

## Runtime outputs

- Active PDFs: `./data/active/<source-id>.pdf`
- Archived PDFs: `./data/archive/<source-id>/...`
- Metadata: `./data/metadata/<source-id>.json`
- Logs: `./logs/govdoc-watcher.log`

Do not commit downloaded PDFs, generated metadata, logs, local `.env`, or other runtime artifacts.

## Validation

Repo-appropriate checks:

```bash
git diff --check
python3 -m compileall src tests
python3 -m pytest
docker compose config
```

`docker compose config` requires a local `.env` because `docker-compose.yaml` references `env_file: .env`. Use `.env.example` as the source for safe non-secret defaults, keep `.env` untracked, and delete or leave it local after validation.

## Error handling

Handles discovery/download HTTP failures, malformed or unmatched links, unavailable entries, non-PDF/zero-byte/invalid header downloads, metadata persistence errors, and safe replacement semantics.

## Healthcheck note

No healthcheck yet because no internal endpoint/CLI probe exists that reliably represents end-to-end watcher health in this version.

## Limitations

- Generic HTML matching may need source-specific tuning.
- No notifications yet.
- No API/UI in this phase.
- No scheduler beyond the in-process sleep loop.
- No retry/backoff policy beyond ordinary exception handling.
- No authentication support is active in the current source configuration.
- No production deployment, uptime, compliance, clinical validation, HIPAA, or patient-data claim is made.

## Privacy and secrets posture

- The configured source is a public CMS listing page.
- The repository does not require runtime credentials for the included source.
- `.env` is ignored and should remain local.
- Downloaded PDFs, metadata JSON, and logs are generated locally and ignored by default.
- The project should not be used with patient data, private documents, credentials, or sensitive records without a separate design and security review.

## License posture

No standard open-source license file is included yet. Until a license is added, treat this repository as public-viewable source code rather than reusable open-source software.

## Future extension points

- API
- MCP
- web UI
- notification integrations
- source-specific scrapers
- authenticated sources

These are future ideas only, not implemented capabilities. This phase intentionally exposes no web service; Nginx Proxy Manager and `proxy_net` are not required.
