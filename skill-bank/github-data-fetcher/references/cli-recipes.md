# Shell Recipes (gh, git, curl)

Exact commands per capability. Replace OWNER, REPO, REF, PATH, TAG, DEST with the actual values. Quote any URL containing `?` or `&`, because shells treat both as operators when unquoted.

## Detect the environment

Stage 1 — classify the runtime before probing any tool:

- Determine whether a shell is available at all; when it is not, stop using this file and follow the transport selection in SKILL.md.
- Determine the OS: run `uname -a` on Unix-like systems; on Windows, `$env:OS` returns `Windows_NT`.
- Determine the shell family: inspect `$SHELL` on Unix-like systems; on Windows, identify whether the shell is Windows PowerShell 5.1, PowerShell 7 or newer, or cmd.

Stage 2 — probe the tools that exist in the classified runtime:

- GitHub CLI: `gh --version` then `gh auth status` (auth state before any private fetch).
- git: `git --version` (sparse checkout needs 2.25 or newer).
- curl on Unix-like shells: `curl --version`.
- Windows PowerShell 5.1: read `$PSVersionTable.PSVersion`; use `curl.exe`, never bare `curl`, because `curl` is there an alias for `Invoke-WebRequest` that rejects curl flags; `curl.exe` ships with Windows 10 version 1803 and later.
- PowerShell 7 or newer: bare `curl` no longer has the alias and runs the real `curl.exe` when it is on PATH.
- Windows without any curl: use `Invoke-WebRequest` with `-UseBasicParsing` (see the PowerShell 5.1 variant below).

## Read raw data

- gh: `gh api repos/OWNER/REPO/contents/PATH -H "Accept: application/vnd.github.raw+json"` prints raw content to stdout.
- curl: `curl -fsSL https://raw.githubusercontent.com/OWNER/REPO/REF/PATH`.

## Download a single file

- gh: `gh api repos/OWNER/REPO/contents/PATH -H "Accept: application/vnd.github.raw+json" > DEST`.
- curl: `curl -fsSL -o DEST https://raw.githubusercontent.com/OWNER/REPO/REF/PATH`.

## Download a zipped or tarred batch

- Full snapshot: `curl -fsSL -o REPO.zip "https://api.github.com/repos/OWNER/REPO/zipball/REF"`.
- Direct codeload form (no redirect hop): `curl -fsSL -o REPO.zip "https://codeload.github.com/OWNER/REPO/zip/refs/heads/BRANCH"`.
- Partial snapshot (git 2.25 or newer):

```
git clone --depth 1 --filter=blob:none --sparse https://github.com/OWNER/REPO.git REPO
cd REPO
git sparse-checkout set DIR1 DIR2
```

- Full shallow clone: `git clone --depth 1 https://github.com/OWNER/REPO.git`.
- Do not use `gh api` for zipball, tarball, or asset URLs: `gh api` does not follow the redirect, so the saved file is not the archive.

## Download releases

- List: `gh release list --repo OWNER/REPO`.
- Inspect one: `gh release view TAG --repo OWNER/REPO --json tagName,assets --jq '{tag: .tagName, assets: [.assets[].name]}'`.
- Download all assets: `gh release download TAG --repo OWNER/REPO --dir DEST`.
- Download filtered assets: `gh release download TAG --repo OWNER/REPO --dir DEST -p '*.deb' -p '*.rpm'`.
- Download the release source archive: `gh release download TAG --repo OWNER/REPO --archive=zip` (or `--archive=tar.gz`).
- Without gh, resolve the asset URL from the release JSON (`assets[].browser_download_url`), then: `curl -fsSL -H "Authorization: Bearer $GITHUB_TOKEN" -o ASSET "ASSET_URL"`.

## Check versions

- Latest commit of one file: `gh api "repos/OWNER/REPO/commits?path=PATH&sha=BRANCH&per_page=1" --jq '.[0].sha'`.
- Remote head of the default branch without cloning: `git ls-remote https://github.com/OWNER/REPO.git HEAD`.
- Remote tags: `git ls-remote --tags https://github.com/OWNER/REPO.git`.
- Compare refs: `gh api repos/OWNER/REPO/compare/BASE...HEAD --jq '{status, ahead_by, behind_by}'`.
- Conditional re-fetch with curl: capture the status separately, because `--fail` does not treat a 304 as an error and returns an empty body with exit code 0:

```
curl -s -o DEST -w '%{http_code}' -H 'If-None-Match: "ETAG"' "https://api.github.com/repos/OWNER/REPO/contents/PATH?ref=REF"
```

## List repository contents

- Resolve the default branch first: `gh api repos/OWNER/REPO --jq .default_branch`.
- Full tree: `gh api "repos/OWNER/REPO/git/trees/BRANCH?recursive=1" --jq '.tree[].path'`; check `.truncated` before trusting the list.
- One directory: `gh api "repos/OWNER/REPO/contents/DIR?ref=REF" --jq '.[].name'`.

## curl safety rules

- Always pass `-f` or `--fail`, so an HTTP error fails the command instead of writing an HTML or JSON error page into the output file.
- Always pass `-L` for api.github.com archive endpoints and asset URLs, which redirect to other hosts.
- Send `-H "Authorization: Bearer $GITHUB_TOKEN"` for private repositories and for the authenticated 5,000-requests-per-hour limit; read the token from the environment, never inline it.

## Windows PowerShell 5.1 variant

- Downloads need `-UseBasicParsing` to avoid the Internet Explorer parsing engine:

```
Invoke-WebRequest -UseBasicParsing -Uri "URL" -Headers @{ Authorization = "Bearer $env:GITHUB_TOKEN" } -OutFile "DEST"
```

- Follow the powershell-51-core skill for any script beyond a one-line download.
