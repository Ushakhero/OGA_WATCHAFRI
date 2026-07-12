"""
OGA_WATCHAFRI - 3-Node AI Reasoning Agent
The Boss That Watches Over Africa
Supports English, Nigerian Pidgin, and Hausa
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url=os.environ.get("AZURE_AI_ENDPOINT"),
    api_key=os.environ.get("AZURE_AI_KEY"),
)
MODEL = os.environ.get("AZURE_DEPLOYMENT_NAME", "gpt-4o-mini")

# Hausa word list for language detection
HAUSA_WORDS = [
    'ina', 'kai', 'suna', 'wanda', 'don', 'da', 'ba', 'ne', 'ce',
    'kudi', 'banki', 'waya', 'sms', 'aiki', 'gida', 'yau', 'jiya',
    'mace', 'namiji', 'allah', 'riba', 'zamba', 'laifi', 'sun',
    'aka', 'ana', 'mai', 'yan', 'abu', 'kuma', 'amma', 'saboda',
    'lokaci', 'mutum', 'arewa', 'kudin', 'aikawa', 'karba', 'sako',
    'wani', 'neman', 'cewa', 'lashe', 'biya', 'danna', 'rufe',
    'asusuna', 'hanyar', 'zuba', 'cikin', 'crypto', 'yawa'
]


def detect_language(text):
    """
    Detect if the user is writing in Hausa.
    Returns 'hausa' or 'english'.
    """
    words = text.lower().split()
    if not words:
        return 'english'
    hausa_count = sum(1 for w in words if w in HAUSA_WORDS)
    if hausa_count >= 2 or (hausa_count / len(words)) > 0.15:
        return 'hausa'
    return 'english'


def node1_fraud_detector(situation, language='english'):
    """Node 1 - Detect the fraud type and severity."""

    if language == 'hausa':
        system_prompt = """Kai kwararre ne wajen gano zamba a Najeriya da Afirka.

Dole ka gano irin zamba, matakin hadari, da dalilan da suka sa kake tunanin haka.

Ka amsa a cikin wannan tsari na JSON kawai - ba ka rubuta komai a wajen JSON ba:
{
  "fraud_type": "Irin zamba da aka gano",
  "severity": "CRITICAL ko HIGH ko MEDIUM ko LOW",
  "confidence": "HIGH ko MEDIUM ko LOW",
  "red_flags": ["alamar hadari 1", "alamar hadari 2"],
  "reasoning": "Takaitaccen bayani a Hausa"
}"""
    else:
        system_prompt = """You are an expert fraud detection agent specializing in Nigerian and African fraud patterns.

Analyze the situation and identify: fraud type, severity level, confidence, red flags, and reasoning.

Respond ONLY in this exact JSON format - no text outside the JSON:
{
  "fraud_type": "Type of fraud detected",
  "severity": "CRITICAL or HIGH or MEDIUM or LOW",
  "confidence": "HIGH or MEDIUM or LOW",
  "red_flags": ["flag 1", "flag 2", "flag 3"],
  "reasoning": "Brief explanation of why this is fraud"
}

Common Nigerian fraud patterns: 419 advance fee scams, SIM swap attacks, BVN identity fraud,
phishing via SMS or WhatsApp, fake investment schemes, POS skimming, romance scams,
fake CBN or bank alerts, crypto investment fraud, OPay or PalmPay reversal fraud, ATM card swap."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Analyze this situation:\n\n" + situation}
        ],
        max_tokens=600,
        temperature=0.3,
    )

    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except Exception:
        return {
            "fraud_type": "Zamba" if language == 'hausa' else "Suspicious Activity",
            "severity": "HIGH",
            "confidence": "MEDIUM",
            "red_flags": ["Ba a iya tabbatarwa" if language == 'hausa' else "Could not parse details"],
            "reasoning": text
        }


def node2_incident_advisor(situation, fraud_analysis, language='english'):
    """Node 2 - Give immediate recovery steps with real contacts."""

    fraud_type = fraud_analysis.get('fraud_type', 'fraud')
    severity = fraud_analysis.get('severity', 'HIGH')

    if language == 'hausa':
        system_prompt = """Kai mai ba da shawara ne ga wadanda suka fada wa masu zamba a Najeriya.

An gano: """ + fraud_type + """ | Matakin hadari: """ + severity + """

Ka ba da matakan gaggawa da za su taimaka wajen dawo da kudi ko hana karin asara.
Ka ambaci lambobin waya na gaske:
- EFCC: 0800-326-5252
- CBN: 0700-225-5226
- Yan sanda ta Intanet: 08057750448
- MTN: 180 (don yanke SIM)
- Airtel: 121
- GTBank: 0700-482-6328
- Access Bank: 1-800-000-2348
- Zenith Bank: 0700-350-8000

Ka rubuta a Hausa a fili. Ka fara da mafi muhimmancin mataki."""
    else:
        system_prompt = """You are an incident response advisor helping fraud victims in Nigeria and Africa.

Detected fraud: """ + fraud_type + """ | Severity: """ + severity + """

Provide IMMEDIATE action steps to help the victim recover money or prevent further loss.
Include REAL Nigerian institution contacts:
- EFCC Fraud Hotline: 0800-326-5252
- CBN Consumer Protection: 0700-225-5226
- Nigeria Police Cybercrime: 08057750448
- MTN (to freeze SIM): 180
- Airtel: 121
- GTBank: 0700-482-6328
- Access Bank: 1-800-000-2348
- Zenith Bank: 0700-350-8000
- First Bank: 0700-343-2265

Write in clear, plain language. Start with the most urgent step. Number each step."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Situation: " + situation + "\n\nFraud Analysis: " + str(fraud_analysis)}
        ],
        max_tokens=800,
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()


def node3_awareness_educator(situation, fraud_analysis, incident_advice, language='english'):
    """Node 3 - Educate and create shareable WhatsApp content."""

    fraud_type = fraud_analysis.get('fraud_type', 'fraud')

    if language == 'hausa':
        system_prompt = """Kai malamin wayar da kan jama'a ne game da zamba a Najeriya.

Irin zamba: """ + fraud_type + """

Ka rubuta sako guda daya mai sauki wanda za a iya raba shi a WhatsApp da dangi da abokai.
Ka yi amfani da Hausa ta yau da kullun.
Ka fara da GARGADI
Ka bayyana yadda zamba ke aiki cikin jumla 2-3
Ka ba da hanyoyi 3 na kare kai
Ka kare da lambar EFCC: 0800-326-5252
Tsawon: jumla 8-10 kawai."""
    else:
        system_prompt = """You are a fraud awareness educator for Nigerian and African communities.

Fraud type detected: """ + fraud_type + """

Create ONE shareable WhatsApp message that families can forward to protect each other.
Use simple everyday language - mix English and Nigerian Pidgin naturally.
Start with WARNING
Explain how this scam works in 2-3 sentences
Give 3 ways to protect yourself
End with EFCC hotline: 0800-326-5252
Add relevant emojis. Length: 8-10 sentences maximum."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Situation: " + situation + "\nFraud type: " + fraud_type}
        ],
        max_tokens=500,
        temperature=0.6,
    )
    return response.choices[0].message.content.strip()


def run_analysis(situation, language=None):
    """Run all 3 nodes on a situation."""
    if language is None:
        language = detect_language(situation)

    fraud_analysis = node1_fraud_detector(situation, language)
    incident_advice = node2_incident_advisor(situation, fraud_analysis, language)
    education = node3_awareness_educator(situation, fraud_analysis, incident_advice, language)

    return {
        'language': language,
        'detection': fraud_analysis,
        'incident_advice': incident_advice,
        'education': education
    }


if __name__ == "__main__":
    print("OGA_WATCHAFRI - The Boss That Watches Over Africa")
    print("=" * 55)
    print("Languages: English, Hausa, Nigerian Pidgin")
    print("=" * 55)

    situation = input("\nDescribe the situation / Ka bayyana abin da ya faru:\n> ")
    if not situation.strip():
        situation = "Someone sent me a WhatsApp message saying I won N500,000 and should send N5,000 to claim it"

    detected = detect_language(situation)
    print("\n[Language detected: " + detected.upper() + "]")
    print("\nAnalyzing... Ana nazari...\n")

    result = run_analysis(situation, detected)
    det = result['detection']

    print("NODE 1 - " + ("GANO ZAMBA" if detected == 'hausa' else "FRAUD DETECTOR"))
    print("  Type: " + str(det.get('fraud_type')))
    print("  Severity: " + str(det.get('severity')))
    for flag in det.get('red_flags', []):
        print("  - " + flag)

    print("\nNODE 2 - " + ("SHAWARA" if detected == 'hausa' else "INCIDENT ADVISOR"))
    print(result['incident_advice'])

    print("\nNODE 3 - " + ("ILIMI" if detected == 'hausa' else "AWARENESS EDUCATOR"))
    print(result['education'])
