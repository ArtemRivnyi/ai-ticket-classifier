import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

smtp_server = os.getenv("MAIL_SERVER")
smtp_port = int(os.getenv("MAIL_PORT"))
smtp_user = os.getenv("MAIL_USERNAME")
smtp_password = os.getenv("MAIL_PASSWORD")

print(f"Testing connection to {smtp_server}:{smtp_port}...")
print(f"User: {smtp_user}")

try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)
    print("✅ Connection and login successful!")
    server.quit()
except Exception as e:
    print(f"❌ Connection failed: {e}")
