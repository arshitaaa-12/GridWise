CREATE TABLE IF NOT EXISTS buildings (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    tariff_rate DECIMAL(10,4) DEFAULT 0.15
);

CREATE TABLE IF NOT EXISTS consumption_readings (
    id BIGSERIAL PRIMARY KEY,
    building_id INT REFERENCES buildings(id),
    timestamp TIMESTAMPTZ NOT NULL,
    consumption_kwh DECIMAL(10,4) NOT NULL,
    temperature_c DECIMAL(5,2),
    humidity_pct DECIMAL(5,2),
    UNIQUE(building_id, timestamp)
);

CREATE TABLE IF NOT EXISTS anomalies (
    id BIGSERIAL PRIMARY KEY,
    building_id INT REFERENCES buildings(id),
    detected_at TIMESTAMPTZ NOT NULL,
    actual_kwh DECIMAL(10,4),
    expected_kwh DECIMAL(10,4),
    method VARCHAR(50),
    severity VARCHAR(20),
    shap_explanation JSONB,
    recommendation TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_readings_building_ts ON consumption_readings(building_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_anomalies_building ON anomalies(building_id, detected_at DESC);

INSERT INTO buildings (name, location, tariff_rate)
VALUES ('Demo Building', 'India', 0.15)
ON CONFLICT DO NOTHING;