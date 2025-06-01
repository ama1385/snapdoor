import requests
import time
from datetime import datetime

URL = "https://snapdoor.onrender.com"  # 🔗 عدّل الرابط لو تغير الدومين
INTERVAL = 5 * 60  # 🕔 5 دقائق بالثواني

def ping_site():
    try:
        response = requests.get(URL, timeout=10)
        status = response.status_code
        print(f"[{datetime.now()}] ✅ Ping ناجح - Status: {status}")
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now()}] ❌ فشل الاتصال: {e}")

if __name__ == "__main__":
    while True:
        ping_site()
        time.sleep(INTERVAL)
