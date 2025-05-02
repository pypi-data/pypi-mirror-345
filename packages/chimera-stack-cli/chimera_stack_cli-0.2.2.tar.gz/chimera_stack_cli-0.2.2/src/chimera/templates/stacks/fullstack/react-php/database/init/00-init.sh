#!/bin/bash

# This script selects the appropriate initialization SQL file based on database type
# It should be executed by the Docker entrypoint mechanism for database containers

# Determine database type
if [ -n "$POSTGRES_USER" ]; then
  echo "PostgreSQL detected, using PostgreSQL-specific schema"
  # For PostgreSQL, the entrypoint will automatically execute .sql files in alphabetical order
  cp /docker-entrypoint-initdb.d/01-schema-pgsql.sql /docker-entrypoint-initdb.d/02-execute.sql
  # Remove MySQL script to avoid errors
  rm -f /docker-entrypoint-initdb.d/01-schema.sql
elif [ -n "$MYSQL_USER" ] || [ -n "$MARIADB_USER" ]; then
  echo "MySQL/MariaDB detected, using MySQL/MariaDB-specific schema"
  # For MySQL/MariaDB, the script will be executed by the entrypoint
  # No action needed as 01-schema.sql is already in place
  # Remove PostgreSQL script to avoid errors
  rm -f /docker-entrypoint-initdb.d/01-schema-pgsql.sql
else
  echo "Unknown database type, using MySQL schema as default"
  # Remove PostgreSQL script to avoid errors
  rm -f /docker-entrypoint-initdb.d/01-schema-pgsql.sql
fi

# Make this script delete itself after execution to avoid it being run multiple times
rm -f "$0"
