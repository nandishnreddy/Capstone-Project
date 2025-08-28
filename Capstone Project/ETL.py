import pandas as pd
import logging
import psycopg2
from psycopg2 import sql

# -------------------------------
# Setup Logging
# -------------------------------
logging.basicConfig(
    filename="log_files.log.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -------------------------------
# Database Connection Parameters
# -------------------------------
DB_HOST = "aws-1-ap-southeast-1.pooler.supabase.com"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres.piofjbmotpiwbrfaxyws"
DB_PASSWORD = "12ad34cf@RKSM"  # URL-encode special chars if needed

# -------------------------------
# Load Raw Data
# -------------------------------
try:
    raw_df = pd.read_csv("combined_trends.csv")  # Replace with your CSV path
    logging.info("Raw data loaded successfully.")
except Exception as e:
    logging.error(f"Failed to load raw data: {e}")
    raise

# -------------------------------
# Clean Data
# -------------------------------
try:
    raw_df["tool_name"] = raw_df["tool_name"].str.strip().str.title()
    raw_df["platform"] = raw_df["platform"].str.strip().str.title()
    raw_df["start_week"] = pd.to_datetime(raw_df["start_week"])
    raw_df["end_week"] = pd.to_datetime(raw_df["end_week"])
    raw_df["popularity_score"] = pd.to_numeric(raw_df["popularity_score"], errors="coerce").fillna(0)
    logging.info("Data cleaning completed.")
except Exception as e:
    logging.error(f"Data cleaning failed: {e}")
    raise

# -------------------------------
# Connect to Database (Session Pooler)
# -------------------------------
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode='require'
    )
    cursor = conn.cursor()
    logging.info("Database connection via session pooler established.")
except Exception as e:
    logging.error(f"Database connection failed: {e}")
    raise

# -------------------------------
# Function to safely load data
# -------------------------------
def safe_load(df, table_name="genai_tools"):
    try:
        # Remove duplicates based on tool_name + start_week
        df_to_insert = df.drop_duplicates(subset=["tool_name", "start_week"])

        for idx, row in df_to_insert.iterrows():
            cursor.execute(
                """
                INSERT INTO tool_trends (tool_name, category, platform, start_week, end_week, popularity_score)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    row["tool_name"],
                    row["category"],
                    row["platform"],
                    row["start_week"],
                    row["end_week"],
                    row["popularity_score"]
                )
            )

        conn.commit()
        logging.info("ETL pipeline completed successfully with categories.")
    except Exception as e:
        conn.rollback()
        logging.error(f"ETL pipeline failed: {e}")
        raise

# -------------------------------
# Load the data
# -------------------------------
safe_load(raw_df)

# -------------------------------
# Verify Data Load
# -------------------------------
try:
    cursor.execute("SELECT * FROM tool_trends ORDER BY start_week DESC LIMIT 10;")
    result = cursor.fetchall()
    for r in result:
        print(r)
    logging.info("Data verification completed successfully.")
except Exception as e:
    logging.error(f"Data verification failed: {e}")
    raise
finally:
    cursor.close()
    conn.close()
    logging.info("Database connection closed.")
