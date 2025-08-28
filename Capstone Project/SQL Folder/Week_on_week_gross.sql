WITH base AS (
  SELECT
    tool_name,
    platform,
    start_week,
    SUM(popularity_score) AS popularity_score
  FROM tool_trends
  GROUP BY tool_name, platform, start_week
),
lagged AS (
  SELECT
    tool_name,
    platform,
    start_week,
    popularity_score,
    LAG(popularity_score) OVER (PARTITION BY tool_name, platform ORDER BY start_week) AS prev_score
  FROM base
)
SELECT
  tool_name,
  platform,
  start_week,
  popularity_score,
  CASE
    WHEN prev_score IS NULL OR prev_score = 0 THEN 0
    ELSE (popularity_score - prev_score) / prev_score
  END AS wow_growth
FROM lagged
ORDER BY start_week, tool_name, platform;