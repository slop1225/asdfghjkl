# Shadowban Monitor

Background monitoring of X/Twitter shadowban status for:

- @keepsayinitkris
- @insanejarona
- @keptsayinitkris

## How it works

A GitHub Action runs every 15 minutes, checks the accounts via the [yuzurisa API](https://shadowban.yuzurisa.com/), and saves the results to `data/history.json`. The website reads that file.

## Setup

1. Create a new **public** GitHub repository
2. Upload all the files from this folder (keep the folder structure)
3. Go to **Settings → Pages**
   - Source: `Deploy from a branch`
   - Branch: `main` / `/ (root)`
4. Wait ~1 minute — your site will be live at `https://YOUR_USERNAME.github.io/REPO_NAME`

The first check will happen within 15 minutes (or you can trigger it manually under the **Actions** tab).

## Files

- `index.html` — the dashboard
- `check.py` — the script that polls the API
- `.github/workflows/check.yml` — the scheduled job
- `data/history.json` — stored results
