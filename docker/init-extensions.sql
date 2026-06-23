-- Initialize PostgreSQL extensions for the property rental application

-- PostGIS extension for geographic data types and functions
CREATE EXTENSION IF NOT EXISTS postgis;

-- pgvector extension for semantic search using embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- UUID extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
