---
name: github-data-fetcher
description: "Use this skill when the task requires fetching data from GitHub:
  reading raw file contents, downloading single files or zipped and tarred
  batches of repository files, downloading release assets or release source
  archives, and checking versions of files, commits, tags, or refs. Also use
  when listing repository contents, comparing refs, or troubleshooting GitHub
  rate limits and 404 responses during such fetches. Do not use for issue or
  pull request review workflows."
---
# GitHub Data Fetcher

## Scope

Fetch data from GitHub repositories: raw file contents, single-file downloads, zipped or tarred batch downloads, release assets and release archives, file and ref version checks, repository content listings, and ref comparisons. Issue and pull request review workflows are out of scope.

## Delivery and destination rule

Distinguish data fetched to complete a related task from data the user directly requested.

- Task-internal data: proceed autonomously, use the result in chat or memory, and spend minimal tokens doing so; do not ask the user anything about saving it.
- User-requested data: follow the user's request exactly. When the request does not state whether the data must be saved as a file or only displayed, ask which the user wants before writing anything.
- When data must be saved and the location is unspecified, ask for the destination; do not assume a download directory. When the target file already exists, confirm overwrite behavior with the user before replacing it.

## Authentication (token optional)

Public repositories require no token. Private repositories and higher rate limits require a token.

- CLI: run `gh auth status` to check; if unauthenticated, ask the user to run `gh auth login` themselves.
- curl: send `Authorization: Bearer $GITHUB_TOKEN`, reading the value from the `GITHUB_TOKEN` or `GH_TOKEN` environment variable.
- Never paste or inline a raw token value in commands, logs, or chat; reference the environment variable only.

## Transport selection

Classify the runtime before probing tools: determine whether a shell exists, and when it does, the OS and the shell family (probe commands in references/cli-recipes.md). PowerShell is not a separate transport: a Windows PowerShell 5.1, PowerShell 7, or cmd session is a shell covered by item 1 or item 2, with its command variants in references/cli-recipes.md. Then select the transport in this order:

1. Shell with GitHub CLI (`gh --version` succeeds): use gh for every capability; it handles authentication, redirects, and release assets. Read references/cli-recipes.md for exact commands.
2. Shell with git or curl but no gh: use git for clones, sparse checkout, and remote version checks, and curl for raw and REST endpoints. Read references/cli-recipes.md.
3. Agent runtime with a URL-opening tool and no shell network access: read raw text by opening the `https://raw.githubusercontent.com/...` URL with the URL-opening tool, then persist the returned text with the runtime's file-writing tool. For binary archives and release assets, use a shell environment or ask the user to download manually.
4. GitHub connector enabled in the runtime: use its functions for repository metadata and private repositories, but discover the exact function names in the runtime first; do not assume them.

## Capability workflows

### Verify before fetching

- Before composing or running any download command, confirm that the repository, ref, and path exist (contents or tree listing, a release lookup, or a single raw probe).
- When any of them does not exist, report that finding instead of producing commands for a nonexistent resource.

### Read raw data

- Compose the raw URL as `https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}`, where ref is a branch, a tag, or a commit SHA (details in references/endpoints.md).
- In a shell, fetch with `curl -fsSL <raw-url>`; always follow redirects when fetching from github.com URLs.
- Prefer raw URLs for content reads in unauthenticated environments: a raw fetch is not a REST API call and does not consume the REST per-hour budget (references/endpoints.md).
- Raw URLs serve files up to 100 MB; larger files require release assets or Git LFS (references/endpoints.md).

### Download a single file

- Download to the user-confirmed destination with `curl -fsSL -o <dest> <raw-url>`; this is binary-safe.
- Alternatively use `gh api` with the raw media type (references/cli-recipes.md).

### Download a zipped or tarred batch

- Full snapshot: fetch `https://api.github.com/repos/{owner}/{repo}/zipball/{ref}` or `/tarball/{ref}` with redirects followed; the archive root folder embeds the resolved commit SHA.
- Partial snapshot (a subset of paths): sparse clone with `git clone --depth 1 --filter=blob:none --sparse`, then `git sparse-checkout set <paths>`; this requires git 2.25 or newer.
- After extraction, report the archive root folder name to the user.

### Download releases

- Look up the release through `/releases/latest`, `/releases?per_page=1`, or `/releases/tags/{tag}` (references/endpoints.md). The endpoint `/releases/latest` excludes drafts and prereleases.
- With gh, run `gh release download <tag> --repo <owner>/<repo> --dir <dest>`; filter assets with `--pattern`, or fetch the release source archive with `--archive=zip` or `--archive=tar.gz`.
- Without gh, download each asset `browser_download_url` with `curl -fsSL -o`; do not use `gh api` for archive or asset URLs because it does not follow redirects (references/cli-recipes.md).

### Check versions

- Latest version of one file: query `/commits?path={path}&sha={branch}&per_page=1`; the first commit SHA is the file's current version (references/endpoints.md).
- Latest version of a ref: query `/commits/{ref}`; list tags with `/tags`; compare two refs with `/compare/{base}...{head}`.
- Pin refs to commit SHAs when the fetched data must be reproducible; branch heads move.
- To skip re-downloading unchanged content, send a conditional request with the stored ETag in `If-None-Match`; a 304 response means unchanged (references/endpoints.md).

### List repository contents

- Single directory: `/contents/{path}?ref={ref}` (at most 1,000 entries; use the tree endpoint for larger directories).
- Full tree: `/git/trees/{ref}?recursive=1`; when the response reports `"truncated": true`, fall back to per-directory listings.

## Errors and rate limits

- 404: wrong path or ref, missing authentication for a private repository, or a nonexistent release; verify spelling, ref, and auth before retrying.
- 409 on a contents request: the repository is empty.
- Primary rate limits: 60 requests per hour unauthenticated, 5,000 with a token; check `x-ratelimit-remaining`, batch listings through the recursive tree endpoint, and prefer conditional requests.
- 403 or 429 with a `Retry-After` header: secondary rate limit; wait for the stated period and retry once.
- Always use `--fail` with curl so an HTTP error fails the command instead of saving an error page as the file.

## References

- Read references/endpoints.md when composing raw URLs, REST calls, or version checks, or when unsure about size limits, response fields, or rate-limit endpoints.
- Read references/cli-recipes.md when executing fetches in a shell.
