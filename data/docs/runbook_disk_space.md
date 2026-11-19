# Runbook: Disk space running low

Keywords: disque, espace disque, disque plein, volume, logs volumineux, sauvegardes, suppression de fichiers

## Symptoms

Monitoring reports disk usage above 90 percent. Services fail to write logs
or temporary files.

## Initial checks

Identify which volume is full and which directories grow fastest. Check log
rotation status and look for very large log files.

## Common causes

Log rotation is disabled or failing. A debug mode was left enabled. Old
backups were not cleaned up.

## Escalation and restrictions

Never delete files on production volumes without approval. Ask the operations
team to validate which files can be archived or removed.
