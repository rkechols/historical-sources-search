#!/usr/bin/env bash

set -e
cd "$(dirname "$0")"

# check prerequisites
if ! command -v uv > /dev/null ; then
    echo "Please install uv (https://docs.astral.sh/uv/getting-started/installation/)"
    exit 1
fi

# set up the python virtual environment
uv sync --locked

# make sure the Chromium browser is installed
uv run playwright install --with-deps chromium

if [ ! -f .env ] ; then
    echo "Copying .env.sample --> .env"
    cp .env.sample .env
fi

uvx pre-commit install
