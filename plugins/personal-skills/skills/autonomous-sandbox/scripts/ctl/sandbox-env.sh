#!/bin/bash
# Container entry point. It lives in /run-ctl, which is read-only to the agent. It sets the egress environment,
# caps processes, starts the loopback relay to the host proxy, then runs "$@".
set -u
source /run-ctl/sandbox.conf
ulimit -u "${NPROC_LIMIT:-4096}" 2>/dev/null || true     # soft and hard together, so the agent cannot raise it
P=http://127.0.0.1:3128; NP=localhost,127.0.0.1,::1
export HTTPS_PROXY=$P HTTP_PROXY=$P https_proxy=$P http_proxy=$P NO_PROXY=$NP no_proxy=$NP
export npm_config_https_proxy=$P npm_config_proxy=$P npm_config_audit=false npm_config_fund=false
# Every TLS connection terminates at the host proxy, whose sandbox-only CA signs every certificate.
CA=/run-ctl/ca.crt
export NODE_EXTRA_CA_CERTS=$CA SSL_CERT_FILE=$CA REQUESTS_CA_BUNDLE=$CA CURL_CA_BUNDLE=$CA GIT_SSL_CAINFO=$CA \
       PIP_CERT=$CA npm_config_cafile=$CA
# A placeholder, not a secret: the host proxy replaces it with the real token on the way to api.anthropic.com.
# The project's own code may set the same value (Claude Code strips this variable from its Bash tool).
export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-sandbox-placeholder
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 DISABLE_TELEMETRY=1 DISABLE_ERROR_REPORTING=1 \
       ENABLE_CLAUDEAI_MCP_SERVERS=false CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL=1
export PATH=/opt/claude/bin:$PATH     # read-only CLI first; the driver also calls it by absolute path
# The relay runs only when the host proxy is up (inside a job); offline uses such as inspect.sh start no listener.
if [ -z "${SANDBOX_OFFLINE:-}" ] && [ -S /sock/proxy.sock ]; then
  python3 /run-ctl/relay.py &
  for _ in $(seq 50); do grep -q ':0C38 00000000:0000 0A' /proc/net/tcp 2>/dev/null && break; sleep 0.1; done
fi
exec "$@"
