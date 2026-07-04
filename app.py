"""
OGA_WATCHAFRI — Flask Web App with Chat Interface
The Boss That Watches Over Africa
"""

from flask import Flask, jsonify, request
from run_agent import node1_fraud_detector, node2_incident_advisor, node3_awareness_educator
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import json

try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("[warning] psycopg2 not available — usage logging disabled")

load_dotenv()

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["20 per hour", "5 per minute"]
)

def log_usage(fraud_type, severity, source='public'):
    """Log each public query to the shared database for monitoring."""
    if not PSYCOPG2_AVAILABLE:
        return
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
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """)
                cur.execute("""
                    INSERT INTO usage_log (source, fraud_type, severity)
                    VALUES (%s, %s, %s);
                """, (source, fraud_type, severity))
        conn.close()
    except Exception as e:
        print(f"[usage_log] failed: {e}")

LOGO_URL = "https://raw.githubusercontent.com/Ushakhero/OGA_WATCHAFRI/main/ogawatchafri-logo.png.png"

CHAT_UI = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OGA_WATCHAFRI — AI Fraud Defense for Africa</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=DM+Mono:wght@400&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
:root{--bg:#0a1628;--s:#0f1e3a;--s2:#162444;--b:#1e3a5f;--gold:#c9961a;--g2:#f0c96e;--r:#ef4444;--gr:#10b981;--t:#e8f0fe;--m:#7a9bc4;}
body{background:var(--bg);color:var(--t);font-family:'Space Grotesk',sans-serif;min-height:100vh;display:flex;flex-direction:column;}
header{padding:12px 24px;background:rgba(10,22,40,0.95);border-bottom:1px solid var(--b);display:flex;align-items:center;gap:12px;position:sticky;top:0;z-index:100;}
.logo-img{width:44px;height:44px;border-radius:10px;object-fit:cover;flex-shrink:0;}
.logo-text h1{font-size:18px;font-weight:700;color:var(--gold);}
.logo-text p{font-size:11px;color:var(--m);font-family:'DM Mono',monospace;}
.pulse-dot{width:7px;height:7px;border-radius:50%;background:var(--gr);animation:pulse 2s infinite;margin-left:auto;}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.hero{text-align:center;padding:40px 24px 24px;max-width:700px;margin:0 auto;}
.hero h2{font-size:28px;font-weight:700;color:var(--t);margin-bottom:10px;line-height:1.3;}
.hero p{font-size:15px;color:var(--m);line-height:1.6;}
.examples{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:20px 24px 0;}
.example-chip{background:var(--s2);border:1px solid var(--b);border-radius:20px;padding:7px 14px;font-size:12px;color:var(--m);cursor:pointer;transition:all .2s;}
.example-chip:hover{border-color:var(--gold);color:var(--gold);}
.chat-container{flex:1;max-width:800px;width:100%;margin:20px auto 0;padding:0 16px;display:flex;flex-direction:column;gap:16px;}
.message{display:flex;gap:12px;animation:fadeIn .3s ease;}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.message.user{flex-direction:row-reverse;}
.avatar{width:36px;height:36px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:16px;}
.avatar.bot{background:linear-gradient(135deg,#c9961a,#8a6a1a);}
.avatar.user{background:var(--s2);border:1px solid var(--b);}
.bubble{max-width:80%;background:var(--s);border:1px solid var(--b);border-radius:16px;padding:14px 16px;font-size:14px;line-height:1.6;}
.message.user .bubble{background:var(--s2);border-color:var(--gold);}
.node-section{margin-top:12px;padding:12px;border-radius:10px;border-left:3px solid;}
.node-detect{border-color:var(--r);background:rgba(239,68,68,.06);}
.node-advise{border-color:var(--gold);background:rgba(201,150,26,.06);}
.node-educate{border-color:var(--gr);background:rgba(16,185,129,.06);}
.node-title{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;font-family:'DM Mono',monospace;}
.node-detect .node-title{color:var(--r);}
.node-advise .node-title{color:var(--gold);}
.node-educate .node-title{color:var(--gr);}
.badge{display:inline-block;font-size:10px;padding:2px 8px;border-radius:12px;font-family:'DM Mono',monospace;margin-left:6px;}
.badge.critical{background:rgba(239,68,68,.2);color:#ef4444;}
.badge.high{background:rgba(245,158,11,.2);color:#f59e0b;}
.badge.medium{background:rgba(201,150,26,.2);color:var(--gold);}
.badge.low{background:rgba(16,185,129,.2);color:var(--gr);}
.typing{display:flex;gap:5px;align-items:center;padding:8px 0;}
.typing span{width:8px;height:8px;border-radius:50%;background:var(--m);animation:bounce .8s infinite;}
.typing span:nth-child(2){animation-delay:.15s;}
.typing span:nth-child(3){animation-delay:.3s;}
@keyframes bounce{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-8px)}}
.input-area{position:sticky;bottom:0;background:var(--bg);border-top:1px solid var(--b);padding:16px;margin-top:auto;}
.input-wrap{max-width:800px;margin:0 auto;display:flex;gap:10px;align-items:flex-end;}
textarea{flex:1;background:var(--s);border:1px solid var(--b);border-radius:12px;padding:12px 16px;color:var(--t);font-family:'Space Grotesk',sans-serif;font-size:14px;resize:none;outline:none;min-height:48px;max-height:120px;transition:border-color .2s;line-height:1.5;}
textarea:focus{border-color:var(--gold);}
textarea::placeholder{color:var(--m);}
.send-btn{width:48px;height:48px;background:linear-gradient(135deg,var(--gold),#a07828);border:none;border-radius:12px;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:all .2s;color:#0a1628;font-size:20px;}
.send-btn:hover{transform:translateY(-1px);box-shadow:0 4px 16px rgba(201,150,26,.4);}
.send-btn:disabled{opacity:.5;cursor:not-allowed;transform:none;}
.disclaimer{text-align:center;font-size:11px;color:var(--m);padding:8px 24px;font-family:'DM Mono',monospace;}
pre{white-space:pre-wrap;word-wrap:break-word;font-family:'Space Grotesk',sans-serif;font-size:13px;}
@media(max-width:600px){.hero h2{font-size:22px;}.bubble{max-width:92%;}}
</style>
</head>
<body>
<header>
  <img src="LOGO_URL_PLACEHOLDER" alt="OGA_WATCHAFRI" class="logo-img" onerror="this.style.display='none'">
  <div class="logo-text">
    <h1>OGA_WATCHAFRI</h1>
    <p>The Boss That Watches Over Africa · AI Fraud Defense</p>
  </div>
  <div class="pulse-dot"></div>
</header>

<div class="hero">
  <h2>Got a suspicious message, call, or situation?</h2>
  <p>Describe what happened and OGA_WATCHAFRI will detect the fraud, advise you on what to do, and teach you how to stay safe — in plain language.</p>
</div>

<div class="examples">
  <div class="example-chip" onclick="useExample(this)">Someone sent me a WhatsApp message saying I won ₦500,000 and should send ₦5,000 to claim it</div>
  <div class="example-chip" onclick="useExample(this)">MTN called me asking for my SIM serial number and NIN</div>
  <div class="example-chip" onclick="useExample(this)">I got an SMS from GTBank saying my account will be blocked — click this link: gtb-verify.net</div>
  <div class="example-chip" onclick="useExample(this)">Someone offered me a crypto investment with 300% returns in 7 days</div>
</div>

<div class="chat-container" id="chatContainer"></div>

<div class="input-area">
  <div class="input-wrap">
    <textarea id="userInput" placeholder="Describe the suspicious message, call, or situation..." rows="1" onkeydown="handleKey(event)" oninput="autoResize(this)"></textarea>
    <button class="send-btn" id="sendBtn" onclick="sendMessage()">&#10148;</button>
  </div>
  <div class="disclaimer">OGA_WATCHAFRI does not store your messages. Always contact authorities for serious cases.</div>
</div>

<script>
function autoResize(el){el.style.height='auto';el.style.height=Math.min(el.scrollHeight,120)+'px';}
function handleKey(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMessage();}}
function useExample(el){document.getElementById('userInput').value=el.textContent;sendMessage();}
function addMessage(role,content){
  const c=document.getElementById('chatContainer');
  const d=document.createElement('div');
  d.className=`message ${role}`;
  const av=role==='user'?'👤':'🛡️';
  const ac=role==='user'?'user':'bot';
  d.innerHTML=`<div class="avatar ${ac}">${av}</div><div class="bubble">${content}</div>`;
  c.appendChild(d);
  d.scrollIntoView({behavior:'smooth',block:'end'});
}
function showTyping(){
  const c=document.getElementById('chatContainer');
  const d=document.createElement('div');
  d.className='message bot';d.id='typing-indicator';
  d.innerHTML=`<div class="avatar bot">🛡️</div><div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div>`;
  c.appendChild(d);d.scrollIntoView({behavior:'smooth',block:'end'});
}
function removeTyping(){const el=document.getElementById('typing-indicator');if(el)el.remove();}
function formatResponse(data){
  const det=data.detection||{};
  const sev=(det.severity||'medium').toLowerCase();
  const fraudType=det.fraud_type||'Unknown';
  const redFlags=(det.red_flags||[]).map(f=>`<div style="margin:3px 0;font-size:13px;">⚠️ ${f}</div>`).join('');
  const reasoning=det.reasoning||'';
  const advice=data.incident_advice||'';
  const education=data.education||'';
  return `
    <div style="font-weight:600;font-size:15px;margin-bottom:12px;">OGA_WATCHAFRI has analyzed your situation:</div>
    <div class="node-section node-detect">
      <div class="node-title">🔍 Node 1 — Fraud Detector</div>
      <div style="font-weight:600;font-size:14px;">${fraudType} <span class="badge ${sev}">${(det.severity||'').toUpperCase()}</span> <span class="badge" style="background:rgba(255,255,255,.1);color:var(--m)">${det.confidence||''} confidence</span></div>
      ${redFlags?`<div style="margin-top:8px;">${redFlags}</div>`:''}
      ${reasoning?`<div style="margin-top:8px;font-size:12px;color:var(--m);font-style:italic;">${reasoning}</div>`:''}
    </div>
    <div class="node-section node-advise" style="margin-top:10px;">
      <div class="node-title">🚨 Node 2 — Incident Advisor</div>
      <pre>${advice}</pre>
    </div>
    <div class="node-section node-educate" style="margin-top:10px;">
      <div class="node-title">🎓 Node 3 — Awareness Educator</div>
      <pre>${education}</pre>
    </div>
    <div style="margin-top:12px;font-size:12px;color:var(--m);text-align:center;font-family:'DM Mono',monospace;">
      ✅ OGA_WATCHAFRI analysis complete. Stay safe, stay sharp! 💪🌍
    </div>`;
}
async function sendMessage(){
  const input=document.getElementById('userInput');
  const btn=document.getElementById('sendBtn');
  const situation=input.value.trim();
  if(!situation)return;
  addMessage('user',situation);
  input.value='';input.style.height='auto';
  btn.disabled=true;showTyping();
  try{
    const r=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({situation})});
    const data=await r.json();
    removeTyping();
    if(data.error){addMessage('bot',`<span style="color:var(--r)">Error: ${data.error}</span>`);}
    else{addMessage('bot',formatResponse(data));}
  }catch(e){removeTyping();addMessage('bot',`<span style="color:var(--r)">Something went wrong. Please try again.</span>`);}
  btn.disabled=false;
}
</script>
</body>
</html>"""

CHAT_UI = CHAT_UI.replace("LOGO_URL_PLACEHOLDER", LOGO_URL)

@app.route('/', methods=['GET'])
def index():
    return CHAT_UI

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'OGA_WATCHAFRI is live', 'version': '1.0'})

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

    if source == 'goldenshield' and pattern:
        situation = f"{situation}\n\n[GoldenShield detected: {pattern} pattern, risk level {risk_level}, fraud score {fraud_score}%]"

    try:
        fraud_analysis = node1_fraud_detector(situation)
        incident_advice = node2_incident_advisor(situation, fraud_analysis)
        education = node3_awareness_educator(situation, fraud_analysis, incident_advice)

        # Log usage for monitoring
        import threading
        threading.Thread(
            target=log_usage,
            kwargs={
                'fraud_type': fraud_analysis.get('fraud_type', 'unknown'),
                'severity': fraud_analysis.get('severity', 'unknown'),
                'source': source
            },
            daemon=True
        ).start()

        return jsonify({
            'status': 'complete',
            'source': source,
            'detection': fraud_analysis,
            'incident_advice': incident_advice,
            'education': education
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=False)
