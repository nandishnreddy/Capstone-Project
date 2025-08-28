create database genai_trend_tracker;

CREATE TABLE tool_trends (
    tool_id SERIAL PRIMARY KEY,          -- auto increment, starts from 1
    tool_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),               -- e.g., LLM, Framework, DB
    platform VARCHAR(100),               -- e.g., GitHub, Reddit
    start_week DATE NOT NULL,
    end_week DATE NOT NULL,
    popularity_score NUMERIC(10,2),      -- for trend score with decimals
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

select * from tool_trends;

