name: Check Shadowbans

on:
  schedule:
    - cron: '*/15 * * * *'   # every 15 minutes
  workflow_dispatch:         # allow manual runs from the Actions tab

jobs:
  check:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4

      - name: Check accounts and update history
        run: python3 check.py

      - name: Commit updated history
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git pull --rebase origin main
          git add data/history.json
          git diff --staged --quiet || git commit -m "Update shadowban history"
          git push
