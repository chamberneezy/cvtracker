# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repo holds Mario Breljak's CV and cover letter, each maintained as multiple self-contained HTML files tailored to different job applications. There is no build step, no package manager, and no server — every file is opened directly in a browser or converted straight to PDF.

CV variants (all share identical HTML/CSS structure, only text content differs):
- `cv_eng1.html` — Data Analyst & Tracking Specialist positioning
- `cv_eng2.html` — Digital Campaign & Performance Specialist positioning (ad trading, programmatic, tracking concepts)
- `cv_ecom.html` — Ecommerce Manager positioning (Shopify/CRO-focused)
- `cv_ger2.html` — German (B2) translation of `cv_eng2.html`

Cover letters (share their own separate, simpler layout):
- `cover_letter.html` — English, tailored per application
- `cover_letter_ger.html` — German (B2) translation

When asked to create a new variant (e.g. targeting a different role or language), copy the closest existing file rather than starting from scratch — the CSS is identical across all `cv_*.html` files, so only the sidebar/About Me/Experience text needs to change. These root-level `cv_*.html` / `cover_letter*.html` files are general-purpose positioning templates (source material to copy from) — they are no longer where per-application tailored content goes; see "Job Application Workflow" below.

`jobs/` holds one subfolder per actual job application (see "Job Application Workflow" below), and `index.html` is a static landing page listing them as clickable cards.

## Exporting to PDF

Export via headless Chrome (no other tooling is installed/needed):

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="/Users/mario/Documents/CV/cv_build/<name>.pdf" \
  "file:///Users/mario/Documents/CV/cv_build/<name>.html"
```

Output PDF filename always mirrors the source HTML filename (e.g. `cv_eng2.html` → `cv_eng2.pdf`). When the user asks to export a file to PDF, just run it — no need to confirm first.

## Shared CV Architecture (`cv_eng1.html`, `cv_eng2.html`, `cv_ecom.html`, `cv_ger2.html`)

Two-column CSS grid layout, no external CSS framework (previously used Tailwind CDN — no longer the case):
- `.cv-page` / `.cv-grid` — outer wrapper; `.cv-grid` uses a `linear-gradient` (not a background on the sidebar element itself) so the dark sidebar color continues across page breaks when printed/exported to multi-page PDF.
- `.sidebar` — dark navy column: profile photo, "Tools"/`Kompetenzen` skills list (`.sidebar-title` + `.sidebar-body` with `.cat`/`.item` pairs), and Education (`.edu-school`/`.edu-degree`).
- `.main` — white column: header (`.cv-name`, `.cv-subtitle`, `.cv-contact`), then `About Me`/`Über mich` and `Experience`/`Berufserfahrung` sections.
- `.job` blocks: `.job-header` (`.job-company` + `.job-date`), `.job-title`, optional `.job-desc` paragraph, and `.job-bullets` list. Note: several roles intentionally have no `.job-desc` — only add one if new source text explicitly includes a summary sentence, don't invent one.
- One `.job` (currently Adssential) carries an inline `style="break-before:page;page-break-before:always;"` to force a clean page 2 start in print — preserve this when reordering jobs.
- `.print-btn` — the on-screen "Save as PDF / Print" button, hidden in `@media print` via `display:none !important`.
- `@media print` also forces `size: A4 portrait; margin: 0`, repaints the sidebar gradient onto `body` (so it fills the full physical page even past the last line of content), and disables font ligatures for cleaner rendering.

## Cover Letter Architecture (`cover_letter.html`, `cover_letter_ger.html`)

Single-column layout, distinct from the CV files: `.container` → `.header` (`.candidate-name`, `.candidate-title`, `.contact-info`) → `.subject-line` → justified `<p>` body paragraphs (optionally a `<ul>` with `.bullet-bold` lead-ins) → `.signature`. `@page { size: A4; margin: 0; }` handles print sizing; there's no on-screen print button in these files.

## Job Application Workflow (Tailoring for a New Job Posting)

When the user pastes a job description (JD) and asks for a tailored application, follow `.claude/skills/CV_Skill.md` — it holds the candidate ground truth (career history, dates, positioning) and the step-by-step workflow: (1) a brief fit score + target title + strategic hooks/gaps, (2) CV content modules (header, summary, skills groups, experience bullets), (3) a cover letter draft. Language (English vs. German) is auto-routed per that file's rules based on the JD.

**Every job application gets its own folder under `jobs/`:**
- Folder name: kebab-case `<role-slug>-<company-slug>` (e.g. `online-marketing-social-media-manager-pistor`).
- Contains `cv.html` and `cover_letter.html` (the default case). A job may also have extra cover-letter variant files (e.g. `cover_letter_b1b2.html`) — see "Job Listing (`index.html`)" below for how to register a variant so it shows up as its own tab.
- Build `cv.html` by copying whichever root-level `cv_*.html` template is the closest positioning/language match (per the convention above), then apply the skill's CV content modules as text only — the skill's "single-column ATS formatting" principle governs how the copy-pasteable module text itself reads (no markdown tables, clean linear text), not the site's two-column sidebar/main HTML layout, which must stay untouched.
- The copied `.sidebar-photo img` keeps a root-relative `src="./profile_photo.png"` from the template — since `cv.html` now lives two levels deeper (`jobs/<folder>/cv.html`), fix this path to `../../profile_photo.png` (there's an `onerror` fallback to a placeholder avatar, so a wrong path fails silently instead of erroring — always check it manually).
- Build `cover_letter.html` the same way, copying from `cover_letter.html`/`cover_letter_ger.html` at root (whichever matches the JD's language) and applying the skill's cover letter draft.
- After generating content, ask the user before finalizing if the fit is ambiguous or a strategic framing choice (e.g. how to handle a gap) needs a call — otherwise just create the folder.
- **Also add a card for it to `index.html`** — see below. There's no server/build step, so the job list can't be read from the filesystem automatically; a new job folder is invisible on the landing page until its card is added too.
- **Also compute the four scoring fields** (fitScore/matchLevel, atsScore, adjustment, verdict) for the `index.html` card — see "Scoring a Job Application" below. Do this for every new job, not just on request.

## Scoring a Job Application

Every job card on `index.html` shows three computed metrics, derived from real comparisons (not guessed) each time a job folder is created:

1. **Match** (`fitScore` 0–10, `matchLevel` label) — the fit score already produced in the skill's Step 1. Map it to a label: **Poor** (<5) / **Good** (5–7.4) / **Excellent** (≥7.5).
2. **ATS Score** (`atsScore`, 0–100) — % of JD-derived keywords/phrases (tools, responsibilities, domain terms — 12–20 terms is typical) found verbatim (case-insensitive) in the combined text of the job's `cv.html` + `cover_letter.html`. Build the keyword list from the actual JD, check each with `grep -i -F` against both files (use `command grep`, not the shell's `grep` wrapper function — it mishandles multiple unquoted file args in this environment), and report `matched/total * 100`.
   - **A term a real gap names doesn't count as matched.** When the cover letter's honest-gap paragraph (see "Editing Conventions" below) names a tool/skill the candidate lacks — e.g. "mit ERP-Systemen habe ich keine direkte Praxis" — a verbatim grep will still hit on "ERP" even though the sentence is a disclosure, not a claim. Don't score that as a match, and don't drop the term from the denominator either (that was tried once and produces an inflated score the same way) — score it as **not matched**, same as if the term were absent entirely. The term still came from the real JD and the candidate still doesn't have it; the gap should show up in the number.
   - Beyond that check, don't otherwise inflate the score by keyword-stuffing terms the candidate doesn't genuinely have — a deliberately-omitted term (a real gap) should simply stay missing.
3. **CV Adjustment** (`adjustment` label) — how much the tailored `cv.html` differs from the root-level template it was copied from. Strip HTML tags from both files, run `difflib.SequenceMatcher` (Python stdlib) over the plain text, and take `(1 - similarity_ratio) * 100`. Map to: **Low** (<35%) / **Medium** (35–65%) / **High** (>65%).
4. **Verdict** (`verdict`, `"Apply"` / `"Long Shot"`) — Claude's own deliberate judgment call from Step 1 on whether this is genuinely worth applying to, not an auto-derived threshold off `fitScore`. In practice it will almost always track `matchLevel` (Poor → Long Shot), but it's set consciously each time so it can diverge if the holistic read differs from the raw number.

Add all of `fitScore`, `matchLevel`, `atsScore`, `adjustment`, `verdict` to that job's entry in the `index.html` `jobs` array (see below) — the row rendering already expects these fields.

Be direct about fit in Step 1 even when it stings — a low `fitScore`/`verdict: "Long Shot"` is a feature of this workflow, not a failure to sound positive. If asked to build the application anyway, do so (with honest gaps named in the cover letter, not papered over), but never round a weak fit up to look better on the dashboard.

## Job Listing (`index.html`)

Static landing page styled as a paper "manifest" (see "Design Language" below) rather than a card grid. Job rows are rendered by a small inline `jobs` array (not a filesystem scan — this is a no-build-step, no-server project) — each entry is `{ title, company, folder, fitScore, matchLevel, atsScore, adjustment, verdict }` (see "Scoring a Job Application" above for the last five), where `folder` is the job's directory name under `jobs/`. Clicking a row navigates the same tab (`window.location.href`, not `window.open`) to `job-view.html?folder=<folder>&title=<title>&company=<company>&fitScore=<fitScore>&matchLevel=<matchLevel>&atsScore=<atsScore>&adjustment=<adjustment>&verdict=<verdict>` — a shared root-level page that shows a **Fit Assessment** panel (verdict stamp + fit/ATS/adjustment metrics, then "Strong match" / "Real gaps" columns), then a tabbed document viewer, plus a back link to `index.html`. Two `window.open()` calls per click used to be the mechanism, but browsers only allow one popup per click gesture, so the cover letter silently failed to open — `job-view.html` exists specifically to avoid that. When a new job folder is created, add a matching entry to the `jobs` array in `index.html` **and** a matching entry to the `fitSummaries` object in `job-view.html` (keyed by `folder`, holding the free-text `strengths`/`gaps` arrays from Step 1 — the numeric scores arrive via URL params from `index.html` instead of being duplicated there) in the same change.

`job-view.html`'s document viewer is tabbed, not stacked: a `CV` tab plus one or more cover-letter tabs, but only **one iframe ever loads at a time** — clicking a tab replaces the single shared iframe's `src` rather than pre-loading every document, so opening a job never means scrolling past documents you didn't ask for. By default a job gets a single "Cover Letter" tab pointing at `cover_letter.html`. A job can instead have multiple cover-letter variants (e.g. a `cover_letter_b1b2.html` alongside the original `cover_letter.html`) by adding an entry to the `coverLetterVariants` object in `job-view.html`, keyed by `folder`, listing `{ label, file }` per variant — register it there, no other page needs to know. **Any fact stated in one variant (e.g. the candidate's real German level) must be stated identically in every other variant of that letter** — variants differ in register/style/structure only, never in what they claim to be true.

## Design Language (`index.html`, `tracker.html`, `job-view.html`)

These three dashboard/shell pages (not the `cv_*.html`/`cover_letter*.html` templates or `jobs/*` content, which are untouched) share a "manifest / tracking-slip" visual identity, applied via the `frontend-design` skill — see `.claude/skills/frontend-design/SKILL.md`. Manila-paper background (`--paper: #EFE8D6`), deep-ink navy text, Fraunces serif for page titles only, IBM Plex Mono for everything else. No cards, no border-radius, no drop shadows — status/verdict values render as literal bordered ink "stamps" (`.stamp`/`.verdict` classes: red/green/amber/blue, matching semantic meaning everywhere). Each of the three files repeats the same CSS custom-property token block in its own `<style>` (no shared stylesheet, consistent with this project's fully self-contained-HTML convention) — keep new tokens/classes added to one in sync across the other two if they need the same treatment.

## Job Hunt Tracker (`tracker.html`)

A dashboard mirroring the user's external "Job hunt" tracking spreadsheet, so applications can be checked without leaving this project. Linked from `index.html`'s header. This is fully self-service in the browser — Add/Edit/Delete buttons on the page — not something Claude maintains by editing the file:
- `seedApplications` in the `<script>` is a one-time seed, used only the first time the page loads in a given browser (no existing `localStorage['jobTracker.records.v1']`). After that, all reads/writes go through `localStorage` via the on-page UI, and `seedApplications` is never read again for that browser — don't expect edits to it to show up for a user who has already interacted with the page.
- Data is per-browser/per-device only (no server, no sync) and invisible to Claude — don't offer to update "a" tracker entry on the user's behalf; direct them to the page's Add/Edit/Delete UI instead.
- Record shape: `{ id, job, company, platform, status, stage, dateSent, link, notes, appFolder? }`. `status`: "Completed" (sent) / "Waiting" (drafted) / "Draft". `stage`: "Waiting answer" / "Rejected" / "Interview" / "Offer" — the stat row is derived from this automatically. `appFolder` (optional, not exposed in the form) links a row's job title to `job-view.html` when set to a matching `jobs/` folder name.
- If asked to change `tracker.html`'s code/design itself (fields, styling, seed data before first load), that's a normal file edit like any other page here.

## Editing Conventions

- When asked to update job content from pasted text, replace only the given text (title, bullets) and preserve existing HTML structure/classes exactly — don't add commentary, don't reformat surrounding markup, and don't backfill a `.job-desc` paragraph if the new text doesn't include one.
- When creating a German translation, keep tool names, company names, and established English/technical loanwords untranslated (e.g. Tracking, Dashboard, KPI, GTM, Server-Side, Looker Studio); translate everything else at B2 level. Translate `GDPR` → `DSGVO`; keep `Swiss FADP` as-is. Localize month abbreviations and "Present" → "heute" in date ranges.
- Always remove/omit any leftover template "PRINT" section at the bottom of a page.
