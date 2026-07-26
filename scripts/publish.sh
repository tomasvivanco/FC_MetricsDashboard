#!/usr/bin/env bash
#
# Publish this repository to GitHub and turn on GitHub Pages.
#
#   bash scripts/publish.sh
#
# Uses the GitHub CLI if it is installed and authenticated (creates the repo,
# pushes, enables Pages — no browser needed). Otherwise it walks you through
# the manual path. Safe to re-run: it never force-pushes and never deletes.

set -u

BOLD=$'\033[1m'; DIM=$'\033[2m'; RED=$'\033[31m'; GRN=$'\033[32m'
YEL=$'\033[33m'; RST=$'\033[0m'

say()  { printf '%s\n' "$*"; }
ok()   { printf '%s✓%s %s\n' "$GRN" "$RST" "$*"; }
warn() { printf '%s!%s %s\n' "$YEL" "$RST" "$*"; }
die()  { printf '%s✗%s %s\n' "$RED" "$RST" "$*" >&2; exit 1; }

cd "$(dirname "$0")/.." || die "Could not enter the repository folder."
REPO_DIR="$(pwd)"

say ""
say "${BOLD}Publishing the Fab City Metrics Dashboard${RST}"
say "${DIM}${REPO_DIR}${RST}"
say ""

# ---------------------------------------------------------------- sanity ----
command -v git >/dev/null 2>&1 || die "git is not installed."
git rev-parse --git-dir >/dev/null 2>&1 || die "This folder is not a git repository."

BRANCH="$(git branch --show-current)"
[ -n "$BRANCH" ] || die "No branch checked out."
ok "Repository found, on branch '${BRANCH}'."

if [ -n "$(git status --porcelain)" ]; then
  warn "You have uncommitted changes:"
  git status --short | sed 's/^/    /'
  say ""
  printf "Commit them now? [y/N] "
  read -r reply
  case "$reply" in
    [yY]*)
      git add -A || die "git add failed."
      printf "Commit message: "
      read -r msg
      [ -n "$msg" ] || msg="Update dashboard"
      git commit -q -m "$msg" || die "Commit failed."
      ok "Committed."
      ;;
    *) warn "Continuing — uncommitted changes will not be published." ;;
  esac
fi

COMMITS="$(git rev-list --count HEAD 2>/dev/null || echo 0)"
[ "$COMMITS" -gt 0 ] || die "Nothing committed yet."
ok "${COMMITS} commit(s) ready to publish."
say ""

# ------------------------------------------------- clean a placeholder remote ----
if git remote get-url origin >/dev/null 2>&1; then
  CURRENT="$(git remote get-url origin)"
  case "$CURRENT" in
    *TU-USUARIO*|*TU-REPO*|*NOMBRE-DEL-REPO*|*'<'*)
      warn "The 'origin' remote still points at a placeholder:"
      say "    ${CURRENT}"
      git remote remove origin || die "Could not remove the placeholder remote."
      ok "Placeholder removed."
      ;;
    *)
      ok "Remote already set: ${CURRENT}"
      ;;
  esac
fi

# ------------------------------------------------------------- gh CLI path ----
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  GH_USER="$(gh api user --jq .login 2>/dev/null || echo '')"
  ok "GitHub CLI authenticated${GH_USER:+ as ${BOLD}${GH_USER}${RST}}."
  say ""

  if git remote get-url origin >/dev/null 2>&1; then
    say "Pushing to the existing remote…"
    git push -u origin "$BRANCH" || die "Push failed."
  else
    DEFAULT_NAME="fab-city-metrics-dashboard"
    printf "Repository name [%s]: " "$DEFAULT_NAME"
    read -r REPO_NAME
    [ -n "$REPO_NAME" ] || REPO_NAME="$DEFAULT_NAME"

    printf "Public or private? [public/private, default public]: "
    read -r VIS
    case "$VIS" in private|p) VIS_FLAG="--private" ;; *) VIS_FLAG="--public" ;; esac

    say ""
    say "Creating ${BOLD}${REPO_NAME}${RST} and pushing…"
    gh repo create "$REPO_NAME" $VIS_FLAG --source=. --remote=origin --push \
      || die "gh repo create failed. The name may already be taken — try another."
  fi

  ok "Pushed."
  say ""

  SLUG="$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null || echo '')"
  if [ -n "$SLUG" ]; then
    say "Enabling GitHub Pages…"
    if gh api -X POST "repos/${SLUG}/pages" \
         -f "source[branch]=${BRANCH}" -f "source[path]=/" >/dev/null 2>&1; then
      ok "Pages enabled."
    else
      if gh api "repos/${SLUG}/pages" >/dev/null 2>&1; then
        ok "Pages was already enabled."
      else
        warn "Could not enable Pages automatically (private repos need a paid plan)."
        say "    Turn it on at: https://github.com/${SLUG}/settings/pages"
        say "    Source: Deploy from a branch → ${BRANCH} → / (root)"
      fi
    fi
    OWNER="${SLUG%%/*}"; NAME="${SLUG##*/}"
    say ""
    ok "Repository: ${BOLD}https://github.com/${SLUG}${RST}"
    ok "Dashboard:  ${BOLD}https://${OWNER}.github.io/${NAME}/${RST}"
    say "${DIM}Pages takes a minute or two to build the first time.${RST}"
  fi
  say ""
  exit 0
fi

# ------------------------------------------------------------- manual path ----
if command -v gh >/dev/null 2>&1; then
  warn "GitHub CLI is installed but not authenticated."
  say "    Run ${BOLD}gh auth login${RST} then re-run this script — it does everything for you."
else
  warn "GitHub CLI not installed. Install it with ${BOLD}brew install gh${RST} to automate this."
fi
say ""
say "${BOLD}Manual route${RST}"
say ""

if ! git remote get-url origin >/dev/null 2>&1; then
  say "1. Create an ${BOLD}empty${RST} repository at https://github.com/new"
  say "   Do not add a README, .gitignore or licence — this repo already has them."
  say ""
  printf "2. Your GitHub username: "
  read -r GH_USER
  [ -n "$GH_USER" ] || die "A username is required."
  printf "3. The repository name you just created: "
  read -r REPO_NAME
  [ -n "$REPO_NAME" ] || die "A repository name is required."

  case "$GH_USER$REPO_NAME" in
    *TU-USUARIO*|*TU-REPO*|*'<'*|*'>'*)
      die "Those are still placeholders — type your real username and repository name." ;;
  esac

  git remote add origin "https://github.com/${GH_USER}/${REPO_NAME}.git" \
    || die "Could not add the remote."
  ok "Remote set: https://github.com/${GH_USER}/${REPO_NAME}.git"
  say ""
fi

say "Pushing… ${DIM}(GitHub will ask for your username and a Personal Access Token — not your password)${RST}"
say ""
if git push -u origin "$BRANCH"; then
  URL="$(git remote get-url origin)"
  SLUG="${URL#*github.com[:/]}"; SLUG="${SLUG%.git}"
  OWNER="${SLUG%%/*}"; NAME="${SLUG##*/}"
  say ""
  ok "Pushed."
  say ""
  say "${BOLD}Last step — turn on Pages:${RST}"
  say "  https://github.com/${SLUG}/settings/pages"
  say "  Source: Deploy from a branch → ${BRANCH} → / (root) → Save"
  say ""
  say "The dashboard will be at ${BOLD}https://${OWNER}.github.io/${NAME}/${RST}"
else
  say ""
  die "Push failed. Common causes:
    · The repository does not exist yet — create it at https://github.com/new
    · Authentication — GitHub needs a Personal Access Token, not your account password.
      Create one at https://github.com/settings/tokens with 'repo' scope.
    · Wrong URL — check it with: git remote -v"
fi
say ""
