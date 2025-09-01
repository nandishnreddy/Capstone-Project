import pandas as pd
import logging
import psycopg2

# -------------------------------
# Setup Logging
# -------------------------------
logging.basicConfig(
    filename="log_files.log",
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
DB_PASSWORD = "12ad34cf@RKSM"  # make sure special chars are handled

# -------------------------------
# Load Raw Data
# -------------------------------
try:
    raw_df = pd.read_csv("combined_trends.csv")  # replace with your CSV path
    print(f"Raw data rows: {len(raw_df)}")
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
    raw_df["popularity_score"] = pd.to_numeric(
        raw_df["popularity_score"], errors="coerce"
    ).fillna(0)
    logging.info("Data cleaning completed.")
except Exception as e:
    logging.error(f"Data cleaning failed: {e}")
    raise

# -------------------------------
# Function to refresh data
# -------------------------------
def refresh_load(df, table_name="tool_trends"):
    conn = None
    cursor = None
    try:
        # Connect to DB
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            sslmode="require"
        )
        cursor = conn.cursor()
        logging.info("Database connection established.")

        # 1. Clear existing data
        cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY;")
        logging.info(f"Table {table_name} truncated.")

        # 2. Insert fresh data
        for idx, row in df.iterrows():
            cursor.execute(
                """
                INSERT INTO tool_trends 
                (tool_name, category, platform, start_week, end_week, popularity_score)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    row["tool_name"],
                    row["category"],
                    row["platform"],
                    row["start_week"],
                    row["end_week"],
                    row["popularity_score"],
                ),
            )

        conn.commit()
        logging.info("Data refreshed successfully.")
        print("✅ Data refresh completed.")
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Data refresh failed: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logging.info("Database connection closed.")


# -------------------------------
# Run refresh load
# -------------------------------
refresh_load(raw_df)
