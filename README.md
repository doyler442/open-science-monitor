# Open Science Policy Monitor

Automated monthly monitoring of open science policies across 19 IS journals and conferences. Proposes updates to the interactive matrix at [cathaldoyle.com/how-open/](https://cathaldoyle.com/how-open/) via GitHub Pull Requests.

## How it works

1. **GitHub Actions** triggers monthly (1st of each month, 9am UTC / 9pm NZST)
2. **Python script** fetches author guideline pages for all 19 venues
3. **Claude API** (Sonnet) reads each page and codes policies against 8 open science practices
4. **Comparison** against current codings in `venues.json`
5. **Pull Request** created automatically if any changes are detected, with evidence quotes
6. **You review** the PR, click merge if correct
7. **Plesk** auto-deploys from GitHub to your live site

## Repository structure

```
open-science-monitor/
├── .github/workflows/monitor.yml   # Monthly cron job
├── index.html                      # The live matrix (loads venues-data.js)
├── venues-data.js                  # Venue codings as JS (auto-updated by monitor)
├── venues.json                     # Master data file + venue URLs
├── monitor.py                      # Main monitoring script
├── prompt.txt                      # System prompt for Claude API
└── README.md
```

## How the data flows

`index.html` loads `venues-data.js` via a `<script>` tag. The monitor updates both `venues.json` (master data) and `venues-data.js` (what the page reads) in the same PR. When you merge, Plesk pulls both files. The page loads the new data automatically. You never download or upload any files.

## Setup

### 1. Create the GitHub repository

```bash
gh repo create open-science-monitor --public --source=. --push
```

### 2. Add your Anthropic API key as a repository secret

Go to **Settings → Secrets and variables → Actions → New repository secret**

- Name: `ANTHROPIC_API_KEY`
- Value: your Anthropic API key

### 3. Add the website HTML

Copy your `open_science_matrix_website.html` into the repo as `index.html`.

### 4. Verify author guideline URLs

The `guide_urls` in `venues.json` are best-guess URLs. Before the first run, verify each URL loads the actual author guidelines page. Conference URLs change annually — update them to the current year's submission page.

### 5. Connect Plesk to GitHub

In your Plesk panel for `cathaldoyle.com`:

1. Go to **Git** (under Files section)
2. Set repository URL to your GitHub repo
3. Set deployment path to `/how-open/`
4. Set branch to `main`
5. Enable **Automatic deployment on push**
6. Deploy once manually to confirm

### 6. Test with a manual run

In GitHub, go to **Actions → Open Science Policy Monitor → Run workflow** to trigger a test run.

## Running locally

```bash
export ANTHROPIC_API_KEY=your-key-here
python monitor.py
```

Local runs update `venues.json` directly (no PR created). Useful for testing.

## Cost

~$0.30–0.50 per monthly run (19 API calls to Claude Sonnet). Under $6/year.

## Future possibilities

- Swap Claude API for local LLM via LM Studio (cost → $0, but Mac must be on)
- Researcher self-assessment interactive element on the page
