-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a table for vector search (this is just for reference, Django will create the actual tables)
CREATE TABLE IF NOT EXISTS text_chunks_example (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    embedding vector(1536) NOT NULL
);

-- Create an index for efficient similarity search (for reference)
CREATE INDEX ON text_chunks_example USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);