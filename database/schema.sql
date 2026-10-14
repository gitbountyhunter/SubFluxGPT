-- SubFluxGPT Database Schema
-- PostgreSQL schema for storing bug bounty data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Programs table: Bug bounty programs
CREATE TABLE IF NOT EXISTS programs (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,  -- hackerone, bugcrowd, yeswehack, etc.
    program_id VARCHAR(100) NOT NULL,  -- Platform-specific program ID
    name VARCHAR(255) NOT NULL,
    url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform, program_id)
);

-- Reports table: Disclosed vulnerability reports
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    program_id INTEGER REFERENCES programs(id) ON DELETE CASCADE,
    platform_report_id VARCHAR(100) NOT NULL,  -- Platform-specific report ID
    title VARCHAR(500) NOT NULL,
    weakness VARCHAR(255),
    severity VARCHAR(50),
    reporter VARCHAR(255),
    bounty_amount DECIMAL(10, 2),
    disclosed_at TIMESTAMP WITH TIME ZONE,
    url TEXT,
    raw_content TEXT,  -- Full report text
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform, platform_report_id)
);

-- Domains table: Extracted apex domains
CREATE TABLE IF NOT EXISTS domains (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) NOT NULL UNIQUE,
    apex_domain VARCHAR(255) NOT NULL,
    tld VARCHAR(50) NOT NULL,
    first_seen_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    report_count INTEGER DEFAULT 0,
    is_validated BOOLEAN DEFAULT FALSE,
    validation_status VARCHAR(50),  -- pending, valid, invalid
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Subdomains table: Discovered subdomains
CREATE TABLE IF NOT EXISTS subdomains (
    id SERIAL PRIMARY KEY,
    domain_id INTEGER REFERENCES domains(id) ON DELETE CASCADE,
    subdomain VARCHAR(255) NOT NULL,
    first_seen_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    report_count INTEGER DEFAULT 0,
    is_validated BOOLEAN DEFAULT FALSE,
    validation_status VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(domain_id, subdomain)
);

-- Report-Domain junction table: Which domains are mentioned in which reports
CREATE TABLE IF NOT EXISTS report_domains (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES reports(id) ON DELETE CASCADE,
    domain_id INTEGER REFERENCES domains(id) ON DELETE CASCADE,
    context TEXT,  -- How the domain was mentioned in the report
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(report_id, domain_id)
);

-- Scope rules table: Program scope definitions
CREATE TABLE IF NOT EXISTS scope_rules (
    id SERIAL PRIMARY KEY,
    program_id INTEGER REFERENCES programs(id) ON DELETE CASCADE,
    rule_type VARCHAR(50) NOT NULL,  -- in_scope, out_of_scope
    target_type VARCHAR(50) NOT NULL,  -- domain, url, ip, wildcard
    pattern VARCHAR(500) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Collection runs table: Track data collection runs
CREATE TABLE IF NOT EXISTS collection_runs (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,  -- running, completed, failed
    reports_collected INTEGER DEFAULT 0,
    domains_extracted INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    metadata JSONB
);

-- Training runs table: Track model training runs
CREATE TABLE IF NOT EXISTS training_runs (
    id SERIAL PRIMARY KEY,
    model_type VARCHAR(50) NOT NULL,  -- llama2c, nanogpt
    model_size VARCHAR(20) NOT NULL,  -- 15M, 42M, 110M
    status VARCHAR(50) NOT NULL,  -- running, completed, failed
    train_loss DECIMAL(10, 6),
    val_loss DECIMAL(10, 6),
    reports_used INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    checkpoint_path TEXT,
    is_deployed BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    metadata JSONB
);

-- Model checkpoints table: Track model versions
CREATE TABLE IF NOT EXISTS model_checkpoints (
    id SERIAL PRIMARY KEY,
    training_run_id INTEGER REFERENCES training_runs(id) ON DELETE CASCADE,
    model_type VARCHAR(50) NOT NULL,
    model_size VARCHAR(20) NOT NULL,
    version INTEGER NOT NULL,
    checkpoint_path TEXT NOT NULL,
    is_best BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Inference logs table: Track model usage
CREATE TABLE IF NOT EXISTS inference_logs (
    id SERIAL PRIMARY KEY,
    checkpoint_id INTEGER REFERENCES model_checkpoints(id) ON DELETE SET NULL,
    query TEXT NOT NULL,
    response TEXT,
    latency_ms INTEGER,
    tokens_generated INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_reports_program_id ON reports(program_id);
CREATE INDEX IF NOT EXISTS idx_reports_disclosed_at ON reports(disclosed_at);
CREATE INDEX IF NOT EXISTS idx_domains_apex_domain ON domains(apex_domain);
CREATE INDEX IF NOT EXISTS idx_subdomains_domain_id ON subdomains(domain_id);
CREATE INDEX IF NOT EXISTS idx_report_domains_report_id ON report_domains(report_id);
CREATE INDEX IF NOT EXISTS idx_report_domains_domain_id ON report_domains(domain_id);
CREATE INDEX IF NOT EXISTS idx_scope_rules_program_id ON scope_rules(program_id);
CREATE INDEX IF NOT EXISTS idx_collection_runs_platform ON collection_runs(platform);
CREATE INDEX IF NOT EXISTS idx_collection_runs_status ON collection_runs(status);
CREATE INDEX IF NOT EXISTS idx_training_runs_status ON training_runs(status);
CREATE INDEX IF NOT EXISTS idx_training_runs_model_type ON training_runs(model_type);
CREATE INDEX IF NOT EXISTS idx_model_checkpoints_is_active ON model_checkpoints(is_active);
CREATE INDEX IF NOT EXISTS idx_inference_logs_timestamp ON inference_logs(timestamp);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_programs_updated_at BEFORE UPDATE ON programs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reports_updated_at BEFORE UPDATE ON reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_domains_updated_at BEFORE UPDATE ON domains
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subdomains_updated_at BEFORE UPDATE ON subdomains
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scope_rules_updated_at BEFORE UPDATE ON scope_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
