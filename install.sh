#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  SWAEV GoldBEAM TUI — one-command installer
#
#  curl -fsSL https://raw.githubusercontent.com/swaev/tui/main/install.sh | bash
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
IFS=$'\n\t'

# ── Config (update GITHUB_RAW when the repo is live) ─────────────────────────
GITHUB_RAW="https://raw.githubusercontent.com/CK5515/SWAEV_TUI/main"
SWAEV_HOME="${HOME}/.swaev"
BIN_DIR="${HOME}/.local/bin"
VERSION="0.1.0"

# ── Colours ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

_ok()   { printf "  ${GREEN}✓${NC}  %s\n" "$*"; }
_step() { printf "  ${DIM}→${NC}  %s\n" "$*"; }
_warn() { printf "  ${YELLOW}⚠${NC}  %s\n" "$*"; }
_die()  { printf "\n  ${RED}✗  Error:${NC} %s\n\n" "$*"; exit 1; }

printf "\n"
printf "  ${BOLD}${CYAN}SWAEV GoldBEAM TUI${NC}  ${DIM}v%s${NC}\n" "${VERSION}"
printf "  ${DIM}Subquadratic chromatin contact map prediction${NC}\n"
printf "\n"

# ── 1. Python ─────────────────────────────────────────────────────────────────
command -v python3 &>/dev/null || _die "python3 not found — install Python 3.9+ and retry."

PY_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
PY_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
[[ ${PY_MAJOR} -ge 3 && ${PY_MINOR} -ge 9 ]] \
  || _die "Python 3.9+ required (found $(python3 --version))."

_ok "Python $(python3 -c 'import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}\")')"

# ── 2. Directories ────────────────────────────────────────────────────────────
mkdir -p "${SWAEV_HOME}" "${BIN_DIR}"
_ok "Install directory  ${SWAEV_HOME}"

# ── 3. Download client.py ─────────────────────────────────────────────────────
_step "Fetching GoldBEAM TUI..."
if curl -fsSL "${GITHUB_RAW}/client.py" -o "${SWAEV_HOME}/client.py"; then
  _ok "client.py downloaded"
else
  _die "Download failed — check your connection or the GITHUB_RAW URL in this script."
fi

# ── 4. Dependencies ───────────────────────────────────────────────────────────
_step "Installing Python dependencies..."
python3 -m pip install --quiet --upgrade rich requests \
  || _die "pip install failed. Try manually: pip3 install rich requests"
_ok "rich + requests installed"

# ── 5. Write the swaev wrapper ────────────────────────────────────────────────
cat > "${BIN_DIR}/swaev" << 'WRAPPER'
#!/usr/bin/env bash
# SWAEV GoldBEAM TUI launcher — managed by install.sh
exec python3 "${HOME}/.swaev/client.py" "$@"
WRAPPER
chmod +x "${BIN_DIR}/swaev"
_ok "'swaev' command → ${BIN_DIR}/swaev"

# ── 6. PATH plumbing ──────────────────────────────────────────────────────────
add_to_path() {
  local rc="$1" line='export PATH="$HOME/.local/bin:$PATH"'
  grep -qF '.local/bin' "${rc}" 2>/dev/null && return 0
  printf '\n# Added by SWAEV installer\n%s\n' "${line}" >> "${rc}"
  _ok "Added ~/.local/bin to PATH in ${rc}"
}

if [[ ":${PATH}:" == *":${BIN_DIR}:"* ]]; then
  _ok "~/.local/bin already in PATH"
else
  case "${SHELL:-}" in
    */zsh)
      add_to_path "${ZDOTDIR:-$HOME}/.zshrc"
      ;;
    */bash)
      add_to_path "${HOME}/.bashrc"
      # Also patch .bash_profile on macOS where .bashrc isn't sourced by login shells
      [[ "$(uname)" == "Darwin" ]] && add_to_path "${HOME}/.bash_profile"
      ;;
    */fish)
      FISH_RC="${HOME}/.config/fish/config.fish"
      mkdir -p "$(dirname "${FISH_RC}")"
      grep -qF '.local/bin' "${FISH_RC}" 2>/dev/null \
        || printf '\n# Added by SWAEV installer\nfish_add_path "$HOME/.local/bin"\n' >> "${FISH_RC}"
      _ok "Added ~/.local/bin to PATH in ${FISH_RC}"
      ;;
    *)
      _warn "Unknown shell '${SHELL:-}'. Add ${BIN_DIR} to your PATH manually."
      ;;
  esac
  # Activate in the current shell session so the user can type swaev immediately
  export PATH="${BIN_DIR}:${PATH}"
fi

# ── 7. Done ───────────────────────────────────────────────────────────────────
printf "\n"
printf "  ${BOLD}${GREEN}Installation complete.${NC}\n"
printf "\n"
printf "  Launch the TUI:\n"
printf "\n"
printf "    ${BOLD}${CYAN}swaev${NC}\n"
printf "\n"

# Remind the user to reload their shell rc if we just patched it
# (PATH is already live for the current session via the export above)
