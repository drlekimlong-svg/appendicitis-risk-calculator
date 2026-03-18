CREATE TABLE IF NOT EXISTS saved_predictions (
    id TEXT PRIMARY KEY,
    created_at_utc TEXT NOT NULL,
    user_email TEXT,
    user_name TEXT,
    research_id TEXT,
    model_key TEXT NOT NULL,
    model_display_name TEXT NOT NULL,
    ui_language TEXT NOT NULL,
    app_version TEXT NOT NULL,
    probability REAL NOT NULL,
    ci_low REAL,
    ci_high REAL,
    linear_predictor REAL NOT NULL,
    input_json TEXT NOT NULL,
    result_json TEXT NOT NULL
);

ALTER TABLE saved_predictions
ADD COLUMN IF NOT EXISTS research_id TEXT;
