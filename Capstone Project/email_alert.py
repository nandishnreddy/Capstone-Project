import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ----------------------------
# Email Setup
# ----------------------------
sender = ("nandish.reddy@nineleaps.com")
password = "rwtw mnct uyxn rnkb"   # ⚠️ Use Gmail App Password, not your real password
receivers = ["keerthana.s@nineleaps.com", "abdul.kalam@nineleaps.com", "sanajana.ballal@nineleaps.com","dheeraj.kunuthur@nineleaps.com"]

# Create Email
msg = MIMEMultipart()
msg['From'] = sender
msg['To'] = ", ".join(receivers)
msg['Subject'] = "Weekly GenAI Trends Report"

body = "Hi Team,\n\nPlease find attached the GenAI Trends outputs.\n"
msg.attach(MIMEText(body, 'plain'))

# ----------------------------
# Attach CSV files from Week 3 folder
# ----------------------------
output_folder = "/home/nineleaps/PyCharmMiscProject/Capstone Project/week3_outputs"   # change this path as per your project
files_to_send = ["weekly_top5.csv", "top5_AIML_Tools_Overall.png", "top5_Cloud_Ai_Platforms.png", "top5_Code_Generation.png", "top5_Frameworks___Libraries.png", "top5_Image_Video_Audio_Generation.png", "top5_Llms___Chatbots.png", "top5_Open_Source_Models.png", "top5_Mlops___Orchestration.png", "top5_Productivity___Agents.png", "top5_Speech_Audio.png", "top5_Vector_Databases.png", "top10_weekly_trends.png", "top5_Other.png" ]  # specify only the ones you want

for file in files_to_send:
    filepath = os.path.join(output_folder, file)
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{file}"')
        msg.attach(part)
    else:
        print(f"⚠️ File not found: {filepath}")

# ----------------------------
# Send Email
# ----------------------------
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    server.send_message(msg)
    server.quit()
    print("✅ Email sent successfully with attachments.")
except Exception as e:
    print("❌ Error:", e)
