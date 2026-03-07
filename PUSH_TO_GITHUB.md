# Push this project to GitHub

Repo: **https://github.com/jonah-davis/COGS-189-Group-Project-WI26**

## One-time: fix Git (if you see Xcode license error)

```bash
sudo xcodebuild -license
```

## Option A — Use this folder as the repo (overwrites GitHub)

Run from this directory (`cogs 189`):

```bash
cd "/Users/surajbendi/cogs 189"
git init
git remote add origin https://github.com/jonah-davis/COGS-189-Group-Project-WI26.git
git add .
git commit -m "COGS 189 final project: analysis, paper, visuals, dataset layout"
git branch -M main
git push -u origin main --force
```

(`--force` replaces the current repo contents with this project.)

## Option B — Clone repo, copy project in, then push

```bash
cd /Users/surajbendi
git clone https://github.com/jonah-davis/COGS-189-Group-Project-WI26.git COGS-189-Group-Project-WI26
cd COGS-189-Group-Project-WI26
# Copy all files from "cogs 189" into this folder (overwriting README etc.), then:
git add .
git commit -m "COGS 189 final project: analysis, paper, visuals, dataset layout"
git push -u origin main
```

## What was checked

- The GitHub repo currently has only: LICENSE, README, and a `main/` folder with `.gitignore`, `.venv`, and a long `requirements.txt` (Jupyter freeze). No analysis code or data.
- This project is the full one (dataset, analysis, paper, visuals). A root `requirements.txt` and `.gitignore` were added so the repo works after you push.
