#!/bin/bash
export http_proxy="http://proxy.server:3128"
export https_proxy="http://proxy.server:3128"
exec /home/meowcolate/.virtualenvs/transport-api-venv/bin/uvicorn \
  --app-dir /home/meowcolate/uk-transport-reliability-api \
  --uds "${DOMAIN_SOCKET}" \
  app.main:app
