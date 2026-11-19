# Runbook: HTTP 502 Bad Gateway

Keywords: 502, serveur web, passerelle, gateway, backend, redémarrage, restart, redémarrer le service

## Symptoms

Users receive HTTP 502 errors. The gateway logs show "upstream connection
refused" or "upstream timed out". The backend health check may fail.

## Initial checks

Check the gateway logs and identify the upstream service and port. Confirm
whether the backend health endpoint answers. Compare the current gateway
configuration with the approved deployment configuration.

## Common causes

The backend service is not running or not listening on the configured port.
The upstream address or port in the gateway configuration is wrong. A recent
deployment changed the backend port without updating the gateway.

## Escalation and restrictions

Do not restart production services without authorization. If the backend is
down, escalate to the operations team and wait for approval before any
restart. Record every action taken in the incident ticket.
