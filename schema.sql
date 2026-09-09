-- PostgreSQL + PostGIS Schema Definition
-- (Note: Run 'CREATE EXTENSION IF NOT EXISTS postgis;' in psql/pgAdmin first if PostGIS isn't enabled)

-- 1. Platforms Meta-Table (Argo Floats, Moored Buoys, Ships)
CREATE TABLE IF NOT EXISTS platforms (
    platform_id VARCHAR(50) PRIMARY KEY,
    platform_type VARCHAR(30) NOT NULL,
    institution VARCHAR(50) DEFAULT 'INCOIS',
    deployment_date DATE,
    last_contact TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. In-Situ Observations Table (PointZ Geometries: Lon, Lat, Depth)
CREATE TABLE IF NOT EXISTS observations (
    obs_id SERIAL PRIMARY KEY,
    platform_id VARCHAR(50) REFERENCES platforms(platform_id) ON DELETE CASCADE,
    time TIMESTAMP NOT NULL,
    geom GEOMETRY(PointZ, 4326) NOT NULL,
    depth_m FLOAT NOT NULL,
    temperature_c FLOAT,
    salinity_psu FLOAT,
    qc_flag INT DEFAULT 1
);

-- 3. Model vs Observation Comparison Results
CREATE TABLE IF NOT EXISTS model_comparisons (
    comparison_id SERIAL PRIMARY KEY,
    obs_id INT REFERENCES observations(obs_id) ON DELETE CASCADE,
    model_name VARCHAR(50) DEFAULT 'INCOIS-ROMS',
    model_temp_c FLOAT,
    temp_bias FLOAT,
    rmse FLOAT,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Spatial GiST Index for fast geographic and depth queries
CREATE INDEX IF NOT EXISTS idx_obs_geom ON observations USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_obs_time ON observations (time);