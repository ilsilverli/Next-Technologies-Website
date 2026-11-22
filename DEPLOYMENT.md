# Next Technologies performance update

Prepared from the live https://www.nextec.sa/ page retrieved on 2026-11-22.
This source is newer than the GitHub main branch. Its content, styles, images,
SEO titles, form behavior and page scripts are retained.

## cPanel deployment

1. Back up public_html/index.html and the existing public_html/.htaccess, if any.
2. Upload index.html, favicon.png and the assets directory to the domain's document root.
3. If .htaccess already exists, merge the supplied compression/cache blocks into it;
   preserve all existing redirects, handlers, access rules and other settings.
   If no .htaccess exists, use the supplied file.
4. Verify the homepage and assets return HTTP 200; check English/Arabic navigation,
   mobile menu and any theme controls that exist in the deployed baseline. Do not
   submit the contact form as a test without intending to send a real inquiry.
5. Request HTML with Accept-Encoding: gzip, br and verify Content-Encoding is gzip
   or br. If it is absent, ask the host to enable mod_deflate or compression in cPanel.
6. Rerun PageSpeed Insights on mobile and desktop. Performance gains are not verified
   until this package is deployed and the public responses are tested.

## What changed

- Embedded logo and hero images moved to byte-identical content-hashed files.
- Existing Google Fonts families/weights are self-hosted with font-display: swap.
- Font declarations are inline, removing the render-blocking Google Fonts CSS request.
- Apache mod_deflate configuration enables text compression when supported.
- Content-hashed images/fonts receive one-year immutable caching when mod_headers is enabled.

## Validation and limits

Automated checks verify unchanged scripts and design CSS, preserved page content,
image byte equality, valid structured-data JSON and JavaScript syntax, resolved local
assets/fonts and retained high priority on the hero image. No browser QA or fresh
Lighthouse score is claimed. Live hosting access is required to complete deployment.

## Rollback

Restore the backed-up index.html and .htaccess. New content-hashed assets may remain;
the restored HTML will not reference them.
