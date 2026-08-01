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
import re
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


# ---------------------------------------------------------------------------
# Community threat intelligence: track scam phone numbers and links reported
# by users so future reports can be checked against a shared history.
#
# IMPORTANT (privacy): we never store the user's message text here - only the
# specific phone number / link strings extracted from it. This keeps the
# "we don't store your messages" promise intact while still letting the
# community benefit from repeat-offender detection.
# ---------------------------------------------------------------------------

NIGERIA_PHONE_RE = re.compile(
    r'(?:\+?234[\s-]?[7-9][01]\d[\s-]?\d{3}[\s-]?\d{4}|0[7-9][01]\d[\s-]?\d{3}[\s-]?\d{4})'
)
URL_RE = re.compile(r'\b(?:https?://)?(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?\b')

# Domains that are too common/generic to be useful signals on their own
URL_IGNORE_LIST = {
    'gmail.com', 'yahoo.com', 'whatsapp.com', 'facebook.com', 'gtbank.com',
    'accessbankplc.com', 'zenithbank.com', 'firstbanknigeria.com', 'cbn.gov.ng',
    'efcc.gov.ng', 'mtnonline.com', 'airtel.com.ng', 'opayweb.com', 'palmpay.com'
}


def normalize_phone(raw):
    digits = re.sub(r'\D', '', raw)
    if digits.startswith('234'):
        digits = '0' + digits[3:]
    return digits


def extract_entities(text):
    """Pull candidate scam phone numbers and links out of free text.
    Returns a list of {type, value} dicts. Deliberately conservative:
    bank account numbers are NOT extracted here because a bare 10-digit
    number is too ambiguous (amounts, OTPs, etc.) to log with confidence.
    """
    entities = []
    seen = set()

    for match in NIGERIA_PHONE_RE.findall(text):
        value = normalize_phone(match)
        if len(value) == 11 and value not in seen:
            seen.add(value)
            entities.append({'type': 'phone', 'value': value})

    for match in URL_RE.findall(text):
        value = match.lower().rstrip('.,)')
        domain = value.replace('https://', '').replace('http://', '').split('/')[0]
        if domain in URL_IGNORE_LIST or domain in seen:
            continue
        seen.add(domain)
        entities.append({'type': 'url', 'value': value})

    return entities


def _ensure_entities_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reported_entities (
            id SERIAL PRIMARY KEY,
            entity_type TEXT NOT NULL,
            entity_value TEXT NOT NULL,
            fraud_type TEXT,
            severity TEXT,
            report_count INTEGER DEFAULT 1,
            first_reported_at TIMESTAMP DEFAULT NOW(),
            last_reported_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(entity_type, entity_value)
        );
    """)


def check_entity_history(entities):
    """Look up prior reports for extracted entities. Returns a list of
    {type, value, report_count, first_reported_at} for anything seen before.
    Fails silently (returns []) if the DB isn't configured - this must never
    block the main analysis flow.
    """
    if not entities:
        return []
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        return []
    alerts = []
    try:
        conn = psycopg2.connect(db_url)
        with conn:
            with conn.cursor() as cur:
                _ensure_entities_table(cur)
                for e in entities:
                    cur.execute("""
                        SELECT report_count, first_reported_at FROM reported_entities
                        WHERE entity_type = %s AND entity_value = %s;
                    """, (e['type'], e['value']))
                    row = cur.fetchone()
                    if row and row[0] >= 2:
                        first_reported = row[1]
                        alerts.append({
                            'type': e['type'],
                            'value': e['value'],
                            'report_count': row[0],
                            'first_reported_at': first_reported.isoformat() if hasattr(first_reported, 'isoformat') else str(first_reported) if first_reported else None
                        })
        conn.close()
    except Exception as ex:
        print(f"[check_entity_history] failed: {ex}")
    return alerts


def log_entity_reports(entities, fraud_type, severity):
    """Upsert extracted entities: increment report_count if seen before,
    insert a new row (report_count=1) otherwise. Runs in a background
    thread so it never slows down the response to the user.
    """
    if not entities:
        return
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        return
    try:
        conn = psycopg2.connect(db_url)
        with conn:
            with conn.cursor() as cur:
                _ensure_entities_table(cur)
                for e in entities:
                    cur.execute("""
                        INSERT INTO reported_entities (entity_type, entity_value, fraud_type, severity)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (entity_type, entity_value)
                        DO UPDATE SET
                            report_count = reported_entities.report_count + 1,
                            last_reported_at = NOW(),
                            severity = EXCLUDED.severity;
                    """, (e['type'], e['value'], fraud_type, severity))
        conn.close()
    except Exception as ex:
        print(f"[log_entity_reports] failed: {ex}")

LOGO_URL = "https://raw.githubusercontent.com/Ushakhero/OGA_WATCHAFRI/main/ogawatchafri-logo.png.png"

# Bump this string any time static/main.js or static/style.css changes.
# It forces browsers (and any CDN/proxy cache) to fetch the new file
# instead of an old cached copy after a deploy.
STATIC_VERSION = "3"

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
  <button class="lang-btn" id="btn-yo" onclick="setLang('yoruba')">Yoruba</button>
  <button class="lang-btn" id="btn-ig" onclick="setLang('igbo')">Igbo</button>
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
  <div class="example-chip yo-chip" style="display:none" onclick="useExample(this)">Ẹnìkan fi ránṣẹ́ sí mi lórí WhatsApp pé mo ti jáwé N500,000 kí n sì fi N5,000 ránṣẹ́ kí n tó lè gbà á</div>
  <div class="example-chip yo-chip" style="display:none" onclick="useExample(this)">MTN pè mí, wọ́n béèrè fún nọ́mbà SIM mi àti NIN mi</div>
  <div class="example-chip yo-chip" style="display:none" onclick="useExample(this)">Mo gba SMS láti ọ̀dọ̀ GTBank pé wọ́n máa dí àkọọ́lẹ̀ mi, kí n tẹ ìjápọ̀ yìí gtb-verify.net</div>
  <div class="example-chip yo-chip" style="display:none" onclick="useExample(this)">Ẹnìkan fún mi ní ìdóko-owó crypto tí yóò mú èrè 300% padà wá láàrin ọjọ́ méje</div>
  <div class="example-chip ig-chip" style="display:none" onclick="useExample(this)">Otu onye zitere m ozi WhatsApp na m meriri N500,000 na m kwesịrị izipu N5,000 iji nweta ya</div>
  <div class="example-chip ig-chip" style="display:none" onclick="useExample(this)">MTN kpọrọ m, jụọ maka nọmba SIM m na NIN m</div>
  <div class="example-chip ig-chip" style="display:none" onclick="useExample(this)">Enwetara m ozi si na GTBank na akaụntụ m ga-emechi, pịa njikọ a gtb-verify.net</div>
  <div class="example-chip ig-chip" style="display:none" onclick="useExample(this)">Otu onye nyere m onyinye itinye ego crypto nke ga-enye uru 300% n'ime ụbọchị asaa</div>
</div>

<div class="chat-container" id="chatContainer"></div>

<div class="input-area">
  <div class="input-wrap">
    <textarea id="userInput" placeholder="Describe the suspicious message, call, or situation..." rows="1" onkeydown="handleKey(event)" oninput="autoResize(this)"></textarea>
    <button class="mic-btn" id="micBtn" onclick="toggleVoice()" title="Speak your situation">&#127908;</button>
    <button class="send-btn" id="sendBtn" onclick="sendMessage()">&#10148;</button>
  </div>
  <div class="disclaimer">OGA_WATCHAFRI never stores your message. Reported scam numbers/links are logged anonymously to warn others. Always contact authorities for serious cases.</div>
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
        'features': ['voice-input', 'voice-output', 'hausa', 'yoruba', 'igbo', 'translation']
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
        entities = extract_entities(situation)
        community_alerts = check_entity_history(entities)

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

        threading.Thread(
            target=log_entity_reports,
            kwargs={
                'entities': entities,
                'fraud_type': fraud_analysis.get('fraud_type', 'unknown'),
                'severity': fraud_analysis.get('severity', 'unknown')
            },
            daemon=True
        ).start()

        return jsonify({
            'status': 'complete',
            'source': source,
            'language': language,
            'detection': fraud_analysis,
            'incident_advice': incident_advice,
            'education': education,
            'community_alerts': community_alerts
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=False)
