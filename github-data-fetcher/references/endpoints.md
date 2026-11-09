# GitHub Endpoints, Limits, and Response Fields

Compose URLs and interpret responses with the exact formats below. All REST paths are relative to `https://api.github.com`. Match the owner, repository, and path casing exactly as shown on GitHub; do not rely on case normalization or redirects.

## Raw file URL

- Format: `https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}`.
- `ref` may be a branch name, a tag name, or a commit SHA; only a full commit SHA makes the content immutable.
- Serves files up to 100 MB; files above 100 MB are not served and require release assets or Git LFS.
- For private repositories, prefer `gh api` or the REST contents endpoint; raw URLs require the token in the `Authorization: Bearer` header.

## Contents endpoint

- `GET /repos/{owner}/{repo}/contents/{path}?ref={ref}`.
- For a file path, the JSON response contains `content` (base64) and `size`; directories return an array of entries.
- A directory listing returns at most 1,000 entries; for larger directories use the tree endpoint.
- Size tiers for file content: up to 1 MB in the JSON response; up to 100 MB with the raw media type; above 100 MB not supported at all.
- Raw media type: send header `Accept: application/vnd.github.raw+json` to receive the raw bytes instead of base64 JSON.
- Status 409 with "Git Repository is empty" means the repository has no commits.

## Tree endpoint

- `GET /repos/{owner}/{repo}/git/trees/{tree_ref}?recursive=1`.
- `tree_ref` accepts a tree SHA or a ref (branch or tag) name.
- Prefer resolving the default branch first via `GET /repos/{owner}/{repo}` (field `default_branch`) rather than assuming `main` or `master`.
- When the response contains `"truncated": true`, the listing is incomplete; fall back to per-directory contents requests.

## Archive endpoints

- `GET /repos/{owner}/{repo}/zipball/{ref}` and `GET /repos/{owner}/{repo}/tarball/{ref}`.
- Both respond with a 302 redirect to a codeload host; the HTTP client must follow redirects.
- The archive root folder is named `{repo}-{resolved-short-SHA}`, so an extracted archive does not have the bare repository name as its root.
- Direct codeload forms: `https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}` and `https://codeload.github.com/{owner}/{repo}/zip/refs/tags/{tag}` (also `/tar.gz/` instead of `/zip/`).

## Release endpoints

- `GET /repos/{owner}/{repo}/releases` lists releases; use `?per_page=1` for the most recent one, including prereleases and drafts visible to the token.
- `GET /repos/{owner}/{repo}/releases/latest` returns the most recent release that is neither a draft nor a prerelease.
- `GET /repos/{owner}/{repo}/releases/tags/{tag}` returns the release for a tag, or 404 when it does not exist.
- Relevant fields: `tag_name`, `name`, `draft`, `prerelease`, `published_at`, `assets[].name`, `assets[].size`, `assets[].browser_download_url`, `zipball_url`, `tarball_url`.
- Asset download URLs redirect to an object-storage host; the HTTP client must follow redirects.

## Version and comparison endpoints

- `GET /repos/{owner}/{repo}/commits?path={path}&sha={branch}&per_page=1` returns the most recent commit touching the path; the first element's `sha` is the current version of that file.
- `GET /repos/{owner}/{repo}/commits/{ref}` returns the head commit of a branch, tag, or SHA; `ref` accepts branch and tag names.
- `GET /repos/{owner}/{repo}/tags` lists tags (paginated); do not assume a guaranteed ordering.
- `GET /repos/{owner}/{repo}/compare/{base}...{head}` returns `status` (`ahead`, `behind`, `identical`, or `diverged`), `ahead_by`, `behind_by`, and `files[]` with per-file `sha` and `patch`.
- The compare response omits the per-file list when the commit range is large (observed with a range 436 commits ahead); answer per-file change questions through the commits-by-path endpoint instead.
- `GET /rate_limit` returns current limit usage in `resources.core` and does not count against the primary limit.

## Conditional requests

- Store the `ETag` response header from the previous fetch.
- Re-request with header `If-None-Match: "{etag}"`; a `304 Not Modified` response means the resource is unchanged and does not count against the primary rate limit.
- `Last-Modified` with `If-Modified-Since` works the same way when no ETag is present.

## Rate limits

- Unauthenticated REST requests: 60 per hour, counted per originating IP address.
- The limits above apply to requests against api.github.com; fetches from raw.githubusercontent.com are not REST API calls and do not consume that budget.
- Authenticated requests with a personal access token: 5,000 per hour.
- Response headers: `x-ratelimit-limit`, `x-ratelimit-remaining`, and `x-ratelimit-reset` (epoch seconds).
- Secondary rate limits surface as 403 or 429 with a `Retry-After` header; wait for the stated period and retry once.

## Error meanings

- 404: nonexistent owner, repository, path, ref, or release; also returned for private resources when authentication is missing, so check auth before concluding the resource does not exist.
- 403 with rate-limit headers or body: primary or secondary rate limit exceeded.
- 409: empty repository on a contents request.
