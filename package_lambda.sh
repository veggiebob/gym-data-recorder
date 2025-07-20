#!/usr/bin/env bash
set -euo pipefail

# ─── CONFIG ────────────────────────────────────────────────────────────────
VENV_DIR=".venv"                # path to your virtualenv
REQ_FILE="requirements.txt"     # where to freeze deps
PACKAGE_DIR="lambda-package"           # temp install dir
DEPLOY_ZIP="gym-data-lambda.zip"     # output zip
SRC_GLOB="env.json *.py"        # which files to include from CWD
# ──────────────────────────────────────────────────────────────────────────

echo "📦 Freezing dependencies from ${VENV_DIR} → ${REQ_FILE}"
# 1. freeze deps
source "${VENV_DIR}/bin/activate"
pip freeze > "${REQ_FILE}"
deactivate

echo "🗂️ Preparing clean package dir: ${PACKAGE_DIR}/"
rm -rf "${PACKAGE_DIR}"
mkdir -p "${PACKAGE_DIR}"

echo "📥 Installing dependencies into ${PACKAGE_DIR}/"
pip install --upgrade -r "${REQ_FILE}" -t "${PACKAGE_DIR}/"

echo "📄 Copying source files into ${PACKAGE_DIR}/"
cp ${SRC_GLOB} "${PACKAGE_DIR}/"

echo "🦅 Creating ${DEPLOY_ZIP}"
pushd "${PACKAGE_DIR}" > /dev/null
zip -r "../${DEPLOY_ZIP}" . > /dev/null
popd > /dev/null

echo "✅ Done! Upload ${DEPLOY_ZIP} to Lambda."