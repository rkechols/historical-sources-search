#!/usr/bin/env bash

set -e
cd "$(dirname "$0")"

uvicorn historical_sources_search.api:api \
    --log-config historical_sources_search/logging/config-dict.json \
    --host "0.0.0.0" \
    "$@"
