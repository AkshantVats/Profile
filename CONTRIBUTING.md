# Contributing

Thanks for your interest in this site and blog.

## How to contribute

1. **Fork** the repository and create a branch from `main`.
2. For **new or updated blog posts**, follow [blog/NEW-POST-CHECKLIST.md](blog/NEW-POST-CHECKLIST.md) end to end (HTML meta, `blog/series-index.json`, local sanity checks).
3. Open a **pull request** with a short description of what changed and why.

## Pull request expectations

- Keep changes **scoped** to the post or fix you are making — no drive-by refactors, unrelated formatting sweeps, or renames outside your change.
- Ensure new posts have valid `href` entries in `series-index.json` (not `#` unless the post is intentionally a draft).
- If you touch series navigation or listings, verify locally with `python3 -m http.server` from the repo root and check the post, `blog/index.html`, and the homepage Writing section.

## Questions

Open an issue or reach out via the contact links on the site.
