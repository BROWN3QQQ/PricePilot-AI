# Git Workflow

This repository uses a fixed two-branch workflow:

- `main`: stable branch for usage
- `dev`: active branch for development

The current rule is simple:

- all new work starts on `dev`
- only reviewed and usable code moves into `main`
- `main` should always stay in a state that can be pulled and used directly

## Branch Roles

### `main`

Use `main` for:

- stable releases
- reviewed documentation
- code that is ready for normal use

Do not use `main` for:

- unfinished features
- risky experiments
- partial refactors

### `dev`

Use `dev` for:

- normal feature development
- strategy iteration
- config and workflow changes
- documentation updates that are part of active work

`dev` may move faster than `main`, but it should still stay reasonably runnable.

## Fixed Process

### 1. Start from `dev`

Before doing development:

```powershell
git checkout dev
git pull origin dev
```

### 2. Make changes on `dev`

After edits:

```powershell
git status
git add <files>
git commit -m "Describe the change"
git push origin dev
```

### 3. Promote `dev` to `main`

Only when the code is ready for normal use:

```powershell
git checkout main
git pull origin main
git merge dev
git push origin main
```

### 4. Keep `dev` aligned after release

If `main` receives a direct fix or release commit, sync it back:

```powershell
git checkout dev
git pull origin dev
git merge main
git push origin dev
```

## Daily Rules

- Do not develop directly on `main`
- Do not push half-finished work to `main`
- Keep `dev` and `main` synchronized after every release
- Use clear commit messages
- Keep secrets, DB files, local reports, and runtime state uncommitted

## Recommended Commit Style

Examples:

- `Add dry-run daily report generator`
- `Tune low-frequency spot strategy filters`
- `Document deployment checklist`
- `Fix backtest report parsing`

Avoid vague messages like:

- `update`
- `fix`
- `change files`

## Release Checklist

Before merging `dev` into `main`:

- confirm `git status` is clean
- review changed files
- confirm docs still match actual commands
- confirm configs do not contain secrets
- confirm the branch is in a usable state

Then release:

```powershell
git checkout main
git pull origin main
git merge dev
git push origin main
```

After release:

```powershell
git checkout dev
git merge main
git push origin dev
```

## Emergency Fixes

If a production-facing fix must go to `main` first:

1. apply the fix on `main`
2. push `main`
3. immediately merge `main` back into `dev`

Do not leave `dev` behind after a hotfix.

## Current Repository Policy

For this repository:

- `main` is the branch to use
- `dev` is the branch to continue building on
- future implementation work should default to `dev`
- after a usable milestone, merge `dev` into `main`

