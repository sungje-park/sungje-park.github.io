# Sungje Park's website

This site uses Hugo and the PaperMod Git submodule. The exact Hugo release is in `.hugo-version`; Git records the exact PaperMod commit. Use the project launcher for local work so your builds match GitHub Actions.

## Local development

```sh
git submodule update --init --recursive
./scripts/hugo version
./scripts/hugo server
```

The launcher downloads Hugo Extended from its official GitHub release, checks the published SHA-256 checksum, and stores the executable and default build cache under the ignored `.tools/` directory. CI sets `HUGO_CACHEDIR` to its runner temporary directory instead. The launcher supports macOS and Linux and leaves any system Hugo installation alone. On macOS it expands the release package without installing it system-wide or running installer scripts.

Run the same production checks as CI before committing:

```sh
./scripts/hugo --environment production --minify --panicOnWarning --printPathWarnings
python3 scripts/check_site.py public
git diff --check
```

To test a GitHub Pages project subpath locally, add `--baseURL https://example.org/site/` to the build and `--base-url https://example.org/site/` to the link check. The checker uses only Python's standard library and verifies local links, assets, anchors, image alt attributes, XML, and JSON-LD without fetching external websites. Generated `public/`, `resources/_gen/`, `.tools/`, and the Hugo lock file are ignored by Git.

## Builds and deployment

The `Hugo / Build` check runs on pull requests to `main`, pushes to `main`, and manual dispatches. It uses the shared version pin and fails on warnings or invalid local links. Pull-request and dependency-branch builds use a placeholder URL with a project subpath, and do not upload a Pages artifact or deploy. Only a successful build of `main` can deploy to GitHub Pages.

Once these workflows are on GitHub, make **Build** a required check for `main` in the repository's branch protection or ruleset. Also enable **Settings → Actions → General → Workflow permissions → Allow GitHub Actions to create and approve pull requests** for the Hugo update workflow. The workflow creates update PRs; it does not approve or merge them.

## Dependency updates

- Dependabot checks Actions every Monday at 09:00 and PaperMod at 09:15, in `America/Los_Angeles` time. Actions are pinned to full commit hashes with release-version comments so Dependabot can propose reviewed updates.
- `Update Hugo` checks the latest stable Hugo release every Monday at 16:35 UTC, or on manual dispatch. It changes only `.hugo-version`, proposes a PR on `dependency/hugo`, and explicitly dispatches the build workflow on that branch. This dispatch lets the bot's PR receive build checks using the repository's `GITHUB_TOKEN`, without a separate token secret.
- Review release notes, the production build, and the rendered homepage and updates page before merging. Updates are never merged automatically. A successful local build does not establish that a GitHub workflow or deployment has run.

For a manual Hugo update, change `.hugo-version` to a stable release and run the production checks. For a manual PaperMod update:

```sh
git -C themes/PaperMod fetch origin master
git -C themes/PaperMod checkout --detach origin/master
./scripts/hugo --environment production --minify --panicOnWarning --printPathWarnings
```

Commit the changed submodule pointer with any required override fixes. Avoid editing files inside the submodule; use a project override when an upstream fix is still pending.

## Custom template overrides

Hugo prefers project templates under `layouts/` over the matching theme templates. Updating PaperMod does not replace these files, so compare them with upstream changes when reviewing theme PRs:

- `baseof.html`: keyboard skip-link target, language attributes, and page structure.
- `_partials/header.html`: desktop navigation, mobile dropdown, social links, and accessibility.
- `_partials/menu-links.html`: shared navigation destinations and CV link for both layouts.
- `_partials/extend_footer.html`: loads the mobile menu's close-on-selection, outside-click, and Escape behavior.
- `_partials/head.html`: homepage title and favicon tags.
- `_partials/social_icons.html`: accessible labels for social links.
- `_partials/site-url.html`: local resource links that include the configured site subpath.
- `_default/list.html` and the shortcodes: site-specific content and publication/update layouts.

Keep the local changes when merging relevant upstream fixes. For example, deprecated language properties must use `Locale`, `Label`, and `Direction`, and page keywords use `.Keywords` instead of `.Params.keywords`.
