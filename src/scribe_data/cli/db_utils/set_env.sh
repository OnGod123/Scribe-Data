#!/bin/bash

# Define the MeiliSearch API key
api_key="_PufaaRUK4yOJm1XkyQHU9A51TfPDjGUfIJTR_sq9LA"
export MEILISEARCH_API_KEY="$api_key"

# Define PostgreSQL connection details
database="translation"
user="postgres"
password="new_password"
host="localhost"
port="5432"

# Export PostgreSQL connection environment variables
export POSTGRES_DB="$database"
export POSTGRES_USER="$user"
export POSTGRES_PASSWORD="$password"
export POSTGRES_HOST="$host"
export POSTGRES_PORT="$port"

echo "Environment variables set:"
echo "MEILISEARCH_API_KEY=[hidden for security]"
echo "POSTGRES_DB=$POSTGRES_DB"
echo "POSTGRES_USER=$POSTGRES_USER"
echo "POSTGRES_PASSWORD=[hidden for security]"
echo "POSTGRES_HOST=$POSTGRES_HOST"
echo "POSTGRES_PORT=$POSTGRES_PORT"