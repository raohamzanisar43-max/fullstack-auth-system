-- Tracerfy Backend Database Initialization
-- This script is run when the PostgreSQL container starts for the first time

-- Create database if it doesn't exist
-- (This is handled by the POSTGRES_DB environment variable)

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for better performance
-- (These will be created by Alembic migrations, but some basic ones here)

-- Set default timezone
SET timezone = 'UTC';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE tracerfy_db TO tracerfy_user;
