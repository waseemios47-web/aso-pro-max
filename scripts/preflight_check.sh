#!/usr/bin/env bash
# 开源前安全自检脚本
# 用法: bash scripts/preflight_check.sh
# 检查仓库是否含敏感信息，安全可推 GitHub

set -u
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXIT_CODE=0

red() { printf "\033[31m%s\033[0m\n" "$1"; }
green() { printf "\033[32m%s\033[0m\n" "$1"; }
yellow() { printf "\033[33m%s\033[0m\n" "$1"; }

fail() { red "❌ $1"; EXIT_CODE=1; }
warn() { yellow "⚠️  $1"; }
ok()   { green "✅ $1"; }

echo "=== Preflight: $SKILL_DIR ==="
echo

# 1. 凭据文件不能在 skill 目录
echo "[1/8] Credentials not in skill dir..."
if [ -f "$SKILL_DIR/.env" ]; then
  fail ".env exists in skill dir! Move to ~/.config/aso-pro-max/.env"
elif [ -d "$SKILL_DIR/.secrets" ]; then
  fail ".secrets/ exists in skill dir! Move to ~/.config/aso-pro-max/.secrets/"
else
  ok "No .env or .secrets/ inside skill"
fi

# 2. .gitignore 必须存在且覆盖关键模式
echo "[2/8] .gitignore covers sensitive patterns..."
GITIGNORE="$SKILL_DIR/.gitignore"
if [ ! -f "$GITIGNORE" ]; then
  fail ".gitignore missing"
else
  for pat in ".env" ".secrets/" "*.pem" "__pycache__" "*.pyc"; do
    if ! grep -qF "$pat" "$GITIGNORE"; then
      fail ".gitignore missing pattern: $pat"
    fi
  done
  [ $EXIT_CODE -eq 0 ] && ok ".gitignore looks good"
fi

# 3. 无 pyc / __pycache__ 残留（嵌入本机绝对路径）
echo "[3/8] No bytecode artifacts..."
PYC_COUNT=$(find "$SKILL_DIR" -name "__pycache__" -o -name "*.pyc" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PYC_COUNT" -gt 0 ]; then
  fail "Found $PYC_COUNT bytecode artifacts. Run: find . -name '__pycache__' -exec rm -rf {} +"
else
  ok "No bytecode files"
fi

# 4. 无 OS / IDE 元数据
echo "[4/8] No OS/IDE metadata..."
META=$(find "$SKILL_DIR" -name ".DS_Store" -o -name ".idea" -o -name "*.swp" 2>/dev/null | wc -l | tr -d ' ')
if [ "$META" -gt 0 ]; then
  warn "Found $META metadata files (.DS_Store/.idea/.swp). Clean before push."
else
  ok "No OS/IDE metadata"
fi

# 5. 扫所有文本文件中的真实 ASA 凭据格式（排除本脚本自身）
echo "[5/8] No real ASA credentials embedded..."
LEAKS=$(grep -rE "SEARCHADS\.[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}" "$SKILL_DIR" 2>/dev/null \
  | grep -v "preflight_check\|SEARCHADS\.xxxxxxxx\|example\|template" | head -3)
if [ -n "$LEAKS" ]; then
  fail "Found possible real ASA credentials:"
  echo "$LEAKS"
else
  ok "No real-format ASA credentials"
fi

# 6. 私钥内容（排除本脚本自身）
echo "[6/8] No private key contents..."
KEY=$(grep -rE "BEGIN EC PRIVATE|BEGIN RSA PRIVATE|BEGIN PRIVATE KEY" "$SKILL_DIR" 2>/dev/null \
  | grep -v "preflight_check" | head -2)
if [ -n "$KEY" ]; then
  fail "Found private key contents:"
  echo "$KEY"
else
  ok "No private keys"
fi

# 7. 无本机绝对路径残余（排除本脚本自身和已知占位符）
echo "[7/8] No hard-coded user paths..."
USER_PATHS=$(grep -rE "/Users/[a-z]+/" "$SKILL_DIR" 2>/dev/null \
  | grep -v ".gitignore\|.git/\|preflight_check" | head -3)
if [ -n "$USER_PATHS" ]; then
  warn "Found user paths (review if these are example placeholders or real):"
  echo "$USER_PATHS"
else
  ok "No hard-coded /Users/ paths"
fi

# 8. 必备开源文件
echo "[8/8] Required open-source files..."
for f in LICENSE README.md CHANGELOG.md requirements.txt .gitignore; do
  if [ ! -f "$SKILL_DIR/$f" ]; then
    fail "Missing: $f"
  fi
done
[ $EXIT_CODE -eq 0 ] && ok "All required files present"

echo
if [ $EXIT_CODE -eq 0 ]; then
  green "🎉 ALL CLEAR — safe to push to public repo"
else
  red "🛑 ISSUES FOUND — fix before pushing"
fi
exit $EXIT_CODE
