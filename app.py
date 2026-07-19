"""
OGA_WATCHAFRI - Flask Web App with Chat Interface
The Boss That Watches Over Africa
Voice Mode, Multi-Language, Hausa Support, Translation
"""

from flask import Flask, jsonify, request
from run_agent import node1_fraud_detector, node2_incident_advisor, node3_awareness_educator, detect_language
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import psycopg2

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='/static')

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["20 per hour", "5 per minute"]
)

def log_usage(fraud_type, severity, source='public', language='english'):
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        return
    try:
        conn = psycopg2.connect(db_url)
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS usage_log (
                        id SERIAL PRIMARY KEY,
                        source TEXT,
                        fraud_type TEXT,
                        severity TEXT,
                        language TEXT DEFAULT 'english',
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """)
                cur.execute("""
                    INSERT INTO usage_log (source, fraud_type, severity, language)
                    VALUES (%s, %s, %s, %s);
                """, (source, fraud_type, severity, language))
        conn.close()
    except Exception as e:
        print(f"[usage_log] failed: {e}")

LOGO_URL = "https://raw.githubusercontent.com/Ushakhero/OGA_WATCHAFRI/main/ogawatchafri-logo.png.png"

# Bump this string any time static/main.js or static/style.css changes.
# It forces browsers (and any CDN/proxy cache) to fetch the new file
# instead of an old cached copy after a deploy.
STATIC_VERSION = "1"

CHAT_UI = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OGA_WATCHAFRI -- AI Fraud Defense for Africa</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=DM+Mono:wght@400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/style.css?v=STATIC_VERSION_PLACEHOLDER">
</head>
<body>
<header>
  <img src="LOGO_PLACEHOLDER" alt="OGA_WATCHAFRI" class="logo-img" onerror="this.style.display='none'">
  <div class="logo-text">
    <h1>OGA_WATCHAFRI</h1>
    <p>The Boss That Watches Over Africa - AI Fraud Defense</p>
  </div>
  <div class="pulse-dot"></div>
</header>

<div class="hero">
  <h2 id="heroTitle">Got a suspicious message, call, or situation?</h2>
  <p id="heroSub">Describe what happened and OGA_WATCHAFRI will detect the fraud, advise you on what to do, and teach you how to stay safe in plain language.</p>
</div>

<div class="lang-toggle">
  <button class="lang-btn active" id="btn-en" onclick="setLang('english')">English</button>
  <button class="lang-btn" id="btn-ha" onclick="setLang('hausa')">Hausa</button>
</div>

<div class="examples" id="examplesDiv">
  <div class="example-chip en-chip" onclick="useExample(this)">Someone sent me a WhatsApp message saying I won N500,000 and should send N5,000 to claim it</div>
  <div class="example-chip en-chip" onclick="useExample(this)">MTN called me asking for my SIM serial number and NIN</div>
  <div class="example-chip en-chip" onclick="useExample(this)">I got an SMS from GTBank saying my account will be blocked click this link gtb-verify.net</div>
  <div class="example-chip en-chip" onclick="useExample(this)">Someone offered me a crypto investment with 300% returns in 7 days</div>
  <div class="example-chip ha-chip" style="display:none" onclick="useExample(this)">An aiko mun da sako a WhatsApp cewa mun lashe N500,000 amma dole mu biya N5,000 don karba</div>
  <div class="example-chip ha-chip" style="display:none" onclick="useExample(this)">MTN sun kira ni suna neman lambar SIM card da NIN na</div>
  <div class="example-chip ha-chip" style="display:none" onclick="useExample(this)">Na sami SMS daga GTBank cewa za a rufe asusuna danna wannan hanyar</div>
  <div class="example-chip ha-chip" style="display:none" onclick="useExample(this)">Wani ya ce zan samu riba mai yawa idan na zuba kudi a cikin crypto</div>
</div>

<div class="chat-container" id="chatContainer"></div>

<div class="input-area">
  <div class="input-wrap">
    <textarea id="userInput" placeholder="Describe the suspicious message, call, or situation..." rows="1" onkeydown="handleKey(event)" oninput="autoResize(this)"></textarea>
    <button class="mic-btn" id="micBtn" onclick="toggleVoice()" title="Speak your situation">&#127908;</button>
    <button class="send-btn" id="sendBtn" onclick="sendMessage()">&#10148;</button>
  </div>
  <div class="disclaimer">OGA_WATCHAFRI does not store your messages. Always contact authorities for serious cases.</div>
</div>

<script src="/static/main.js?v=STATIC_VERSION_PLACEHOLDER"></script>
</body>
</html>"""

CHAT_UI = CHAT_UI.replace("LOGO_PLACEHOLDER", LOGO_URL)
CHAT_UI = CHAT_UI.replace("STATIC_VERSION_PLACEHOLDER", STATIC_VERSION)

@app.route('/', methods=['GET'])
def index():
    return CHAT_UI

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'OGA_WATCHAFRI is live',
        'version': '2.0',
        'features': ['voice-input', 'voice-output', 'hausa', 'translation']
    })

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("5 per minute")
def analyze():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON body provided'}), 400

    situation = data.get('situation', '').strip()
    if not situation:
        return jsonify({'error': 'situation field is required'}), 400

    source = data.get('source', 'direct')
    pattern = data.get('pattern', '')
    risk_level = data.get('risk_level', '')
    fraud_score = data.get('fraud_score', '')
    language = data.get('language', None)

    if source == 'goldenshield' and pattern:
        situation = f"{situation}\n\n[GoldenShield detected: {pattern} pattern, risk level {risk_level}, fraud score {fraud_score}%]"

    if language is None:
        language = detect_language(situation)

    try:
        fraud_analysis = node1_fraud_detector(situation, language)
        incident_advice = node2_incident_advisor(situation, fraud_analysis, language)
        education = node3_awareness_educator(situation, fraud_analysis, incident_advice, language)

        import threading
        threading.Thread(
            target=log_usage,
            kwargs={
                'fraud_type': fraud_analysis.get('fraud_type', 'unknown'),
                'severity': fraud_analysis.get('severity', 'unknown'),
                'source': source,
                'language': language
            },
            daemon=True
        ).start()

        return jsonify({
            'status': 'complete',
            'source': source,
            'language': language,
            'detection': fraud_analysis,
            'incident_advice': incident_advice,
            'education': education
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=False)
