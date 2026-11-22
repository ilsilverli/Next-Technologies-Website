# Next Technologies website

Company website for Next Technologies, live at https://nextec.sa (English) and
https://nextec.sa/ar/ (Arabic). Static pages, hosted on cPanel.

## Files

- `index.html`: the English page, and the single source of layout, styles and English text.
- `i18n/ar.json`: the Arabic text for every element marked `data-i="…"` in `index.html`,
  plus the Arabic page title, description and accessibility labels.
- `ar/index.html`: the Arabic page. **Generated, do not edit by hand** (see below).
- `thank-you.html`: bilingual page shown after the enquiry form is sent.
- `assets/`: images and self-hosted fonts.
- `.htaccess`: redirect to https://nextec.sa, security headers, compression and caching.
  On the server these rules sit below cPanel's own PHP blocks; merge, never replace.
- `sitemap.xml`, `robots.txt`: for search engines.
- `tools/build_arabic.py`: builds `ar/index.html`.

## Editing

1. Change `index.html` (layout or English text) and/or `i18n/ar.json` (Arabic text).
   New text that should be translated needs a `data-i="key"` attribute in `index.html`
   and a matching entry under `"text"` in `i18n/ar.json`.
2. Rebuild the Arabic page from the repository root:

       python3 tools/build_arabic.py

   It stops with an error, without writing a partial page, if any Arabic text is missing.
3. Preview with `python3 -m http.server 8000` and check http://localhost:8000/ and
   http://localhost:8000/ar/ at desktop and mobile widths.
4. Open a pull request and merge into `main` after review.

## Deploying

Upload to the domain's `public_html` on cPanel: `index.html`, `ar/index.html`,
`thank-you.html`, `sitemap.xml`, `robots.txt`, `favicon.png` and any changed files in
`assets/`. Back up the files being replaced first. `i18n/`, `tools/` and the Markdown
files are not needed on the server.

## Contact form

The enquiry form posts to FormSubmit using the account's random alias (the email address
is not in the page), then returns visitors to `thank-you.html`. A hidden `Language` field
tells you which language page the enquiry came from.

## Ownership

Company website source for Next Technologies. No open-source licence has been granted.
