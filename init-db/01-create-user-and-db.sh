#!/bin/bash
set -e

# This script runs automatically when PostgreSQL container starts
# Create the application user and database

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    -- Create role/user for the application
    CREATE ROLE compass_user WITH LOGIN PASSWORD 'change_me';
    
    -- Create database owned by compass_user
    CREATE DATABASE gmucampus_db OWNER compass_user;
    
    -- Grant privileges
    GRANT CONNECT ON DATABASE gmucampus_db TO compass_user;
EOSQL

# Create tables in gmucampus_db
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "gmucampus_db" <<-EOSQL
    -- Create users table
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Grant permissions to compass_user
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO compass_user;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO compass_user;
EOSQL

echo "Database initialization completed successfully!"
