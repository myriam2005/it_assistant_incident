# Runbook: Database connection pool saturation

Keywords: base de données, bd, pool, connexions, saturation, application lente, requêtes lentes, timeout

## Symptoms

The application is slow and requests time out. Database warnings report high
connection pool usage, for example above 80 percent.

## Initial checks

Review the connection pool usage over time. Identify slow queries and check
how the application opens and closes connections. Look for connections that
stay open too long.

## Common causes

Long-running queries hold connections. The application does not release
connections after use. A traffic increase exceeds the configured pool size.

## Escalation and restrictions

Escalate before changing production capacity settings. Any pool size change
must be approved and scheduled. Do not kill database sessions without
authorization.
