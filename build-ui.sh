#!/usr/bin/env bash

set -e
cd "$(dirname "$0")"

pushd search-ui
rm -rf dist
bun run build
popd

rm -rf src/historical_sources_search/static/*
cp -R search-ui/dist/* src/historical_sources_search/static/
