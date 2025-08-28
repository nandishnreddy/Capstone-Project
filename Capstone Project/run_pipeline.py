import subprocess
from datetime import datetime

log_file = "/home/nineleaps/PyCharmMiscProject/Capstone Project/log_files.log"

with open(log_file, "a") as f:
    f.write(f"\nPipeline started: {datetime.now()}\n")

    try:
        # Step 1: Scraper
        subprocess.run(["python3", "script.py"], check=True)
        f.write("Scraper completed successfully\n")

        # Step 2: ETL
        subprocess.run(["python3", "ETL.py"], check=True)
        f.write("ETL completed successfully\n")

        # Step 3: Reports
        subprocess.run(["python3", "EDA.py"], check=True)
        f.write("Report generation completed successfully\n")

        # Step 4: Email Alert
        subprocess.run(["python3", "email_alert.py"], check=True)
        f.write("Email alert sent successfully\n")

    except subprocess.CalledProcessError as e:
        f.write(f"Error occurred: {e}\n")
