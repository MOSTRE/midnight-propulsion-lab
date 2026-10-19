# Publish this project to GitHub

These steps publish the files you currently have; they do not make the research more validated than the documentation says.

## 1. Create an empty repository

On GitHub, choose **New repository** and name it `midnight-propulsion-lab`. Set it to Public if you want everyone to see it. Do not select GitHub's options to add a README, license, or `.gitignore`, because this project already contains those files.

## 2. Open PowerShell in this project folder

Make sure the folder contains `README.md`, `pyproject.toml`, `src`, `tests`, `research`, `results`, and `figures`.

Run:

```powershell
git init
git add .
git status
git commit -m "Initial release: reproducible propulsion screening study"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/midnight-propulsion-lab.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. If Git asks you to authenticate, use the sign-in method recommended by GitHub. Never put access tokens or passwords into the repository.

If `git remote add origin` says that `origin` already exists, check it with `git remote -v` and update it with `git remote set-url origin https://github.com/YOUR-USERNAME/midnight-propulsion-lab.git`.

## 3. Check the page

Open your GitHub repository page. Confirm the README charts display, links work, and the results and literature folders are included. The included GitHub Actions workflow will run tests when you push.

## 4. Do not overstate the result

Describe the project as a low-fidelity, reproducible computational screening study. Do not label it a new nuclear rocket, a proven invention, a flight-ready mission, or a Nobel-level discovery. The trajectory optimizer has not yet demonstrated robustness, and the Earth-to-Mars example omits important real mission dynamics.
