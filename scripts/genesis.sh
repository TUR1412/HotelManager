#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/TUR1412/HotelManager.git}"
WORK_ROOT="${WORK_ROOT:-$(pwd)}"
REPO_DIR="${REPO_DIR:-HotelManager}"
PUSH_MODE="${PUSH_MODE:-none}" # none|push|force-with-lease|force
SELF_DESTRUCT="${SELF_DESTRUCT:-0}" # 0|1
COMMIT_MESSAGE="${COMMIT_MESSAGE:-feat(GOD-MODE):  Ultimate Evolution - Quark-level UI & Arch Upgrade}"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PATCH_PATH="${PATCH_PATH:-${SCRIPT_DIR}/genesis.patch}"

if [[ ! -f "${PATCH_PATH}" ]]; then
  echo "Missing patch file: ${PATCH_PATH}" >&2
  exit 1
fi

REPO_PATH="${WORK_ROOT}/${REPO_DIR}"
did_clone=0

if [[ -d "${REPO_PATH}" ]]; then
  if [[ ! -d "${REPO_PATH}/.git" ]]; then
    echo "Destination exists but is not a git repository: ${REPO_PATH}" >&2
    exit 1
  fi
else
  mkdir -p -- "${WORK_ROOT}"
  echo "== clone =="
  git clone "${REPO_URL}" "${REPO_PATH}"
  did_clone=1
fi

pushd "${REPO_PATH}" >/dev/null
echo "== apply patch =="
if git apply --check "${PATCH_PATH}" >/dev/null 2>&1; then
  git apply --whitespace=nowarn "${PATCH_PATH}"
elif git apply -R --check "${PATCH_PATH}" >/dev/null 2>&1; then
  echo "Patch already applied; skipping."
else
  echo "Patch does not apply cleanly: ${PATCH_PATH}" >&2
  exit 1
fi

echo "== tests =="
PYTHONPATH="src" python -m compileall -q src tests
PYTHONPATH="src" python -m unittest discover -s tests -v

echo "== commit =="
git add -A
if git diff --cached --quiet; then
  echo "No changes staged; skipping commit."
else
  git commit -m "${COMMIT_MESSAGE}"
fi

if [[ "${PUSH_MODE}" != "none" ]]; then
  echo "== push (${PUSH_MODE}) =="
  case "${PUSH_MODE}" in
    push) git push ;;
    force-with-lease) git push --force-with-lease ;;
    force) git push --force ;;
    *) echo "Unknown PUSH_MODE: ${PUSH_MODE}" >&2; exit 1 ;;
  esac
fi
popd >/dev/null

if [[ "${SELF_DESTRUCT}" == "1" ]]; then
  if [[ "${did_clone}" != "1" ]]; then
    echo "Refusing to self-destruct: repo was not cloned by this run (${REPO_PATH})." >&2
    exit 1
  fi
  if [[ "${PUSH_MODE}" == "none" ]]; then
    echo "SELF_DESTRUCT requires PUSH_MODE != none." >&2
    exit 1
  fi
  echo "== self-destruct =="
  rm -rf -- "${REPO_PATH}"
fi
