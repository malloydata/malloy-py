#!/bin/bash

mkdir $HOME/.snowflake
(cat <<- SNOWFLAKE
[default]
account="$SNOWFLAKE_ACCOUNT"
user="$SNOWFLAKE_USER"
password="$SNOWFLAKE_PASSWORD"
warehouse="$SNOWFLAKE_WAREHOUSE"
database="$SNOWFLAKE_DATABASE"
schema="$SNOWFLAKE_SCHEMA"
SNOWFLAKE
) > $HOME/.snowflake/connections.toml
