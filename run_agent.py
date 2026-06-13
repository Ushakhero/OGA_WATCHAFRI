"""
OGA_WATCHAFRI — Main Agent Runner
The Boss That Watches Over Africa

Multi-step reasoning agent for African cyber fraud detection,
victim advising, and community education.

Built for Microsoft Agents League Hackathon 2026
Track: Reasoning Agents | Tool: Azure AI Foundry
"""

import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# ── Azure AI Foundry Configuration ──────────────────────────────────────────
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_AI_ENDPOINT"),
    api_key=os.getenv("AZURE_AI_KEY"),
    api_version="2024-02-01"
)

DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4o-mini")

# ── Load Prompt Templates ────────────────────────────────────────────────────
def load_prompt(filename: str) -> str:
    path = os.path.join("prompt-flow", filename)
    with open(path, "r") as f:
        content = f.read()
    # Extract system and user sections
    return content

def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.3, max_tokens: int = 700) -> str:
    """Call Azure OpenAI with system + user prompt."""
    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

# ── Node 1: Fraud Detector ───────────────────────────────────────────────────
def node1_fraud_detector(user_input: str) -> dict:
    print("\n🔍 OGA_WATCHAFRI is analyzing your situation...\n")

    system_prompt = """You are OGA_WATCHAFRI's Fraud Detection Engine — a cybersecurity expert 
specializing in African digital fraud patterns including Nigerian 419 scams, 
mobile money fraud, SIM swap attacks on African telecoms, phishing targeting 
African banks, fake investment schemes, romance scams, fake job offers, 
WhatsApp/SMS impersonation, and social engineering via phone calls.

Analyze the user's input step-by-step and respond ONLY in this exact JSON format:
{
  "fraud_type": "Name of fraud type or No fraud detected",
  "fraud_category": "phishing|advance_fee|sim_swap|fake_investment|romance_scam|fake_job|mobile_money_fraud|impersonation|unknown|none",
  "red_flags": ["red flag 1", "red flag 2", "red flag 3"],
  "confidence": "HIGH|MEDIUM|LOW",
  "is_fraud": true or false,
  "severity": "CRITICAL|HIGH|MEDIUM|LOW",
  "reasoning": "Brief step-by-step analysis"
}"""

    user_prompt = f"Analyze this situation for cyber fraud:\n\n{user_input}"

    raw = call_llm(system_prompt, user_prompt, temperature=0.2, max_tokens=600)

    try:
        # Strip markdown code fences if present
        clean = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)
    except json.JSONDecodeError:
        result = {"raw_output": raw, "is_fraud": True, "confidence": "MEDIUM"}

    return result

# ── Node 2: Incident Advisor ─────────────────────────────────────────────────
def node2_incident_advisor(user_input: str, fraud_analysis: dict) -> str:
    print("🚨 Generating incident response guidance...\n")

    system_prompt = """You are OGA_WATCHAFRI's Incident Response Advisor — helping African fraud 
victims respond immediately and correctly.

Key African reporting contacts you know:
- EFCC Nigeria: efccnigeria.org | 0800-326-5374
- CBN Consumer Protection: 0800-225-5226  
- NCC Nigeria: 622 (any network)
- Nigeria Cybercrime reporting: report.cybercrime.gov.ng
- GTBank Fraud: 0700-4826-2657 | Access Bank: 01-2712005
- MTN Nigeria: 180 | Airtel: 121 | Glo: 121
- Ghana Police Cybercrime: 18555
- Safaricom M-Pesa Fraud: 0722-000-100

Give immediate, practical, step-by-step advice. Be empathetic. Use simple language.
Format with clear headers and numbered steps."""

    user_prompt = f"""Original situation:
{user_input}

Fraud analysis:
{json.dumps(fraud_analysis, indent=2)}

Provide immediate incident response guidance:"""

    return call_llm(system_prompt, user_prompt, temperature=0.3, max_tokens=700)

# ── Node 3: Awareness Educator ───────────────────────────────────────────────
def node3_awareness_educator(user_input: str, fraud_analysis: dict, incident_advice: str) -> str:
    print("🎓 Preparing your awareness education...\n")

    system_prompt = """You are OGA_WATCHAFRI's Awareness Educator — teaching everyday Africans 
about cyber fraud in warm, simple, relatable language. You use mild Pidgin phrases 
where natural (e.g., "E don do!", "No fall for am"), reference everyday African life, 
and make tips easy to share with family WhatsApp groups.

Structure response with these sections:
## 🎓 What Just Happened To You
## 🌍 How This Works in Africa  
## 🛡️ 3 Simple Rules To Never Fall For This Again
## 📢 Share This Warning (short shareable message)
## 💪 Final Words

Keep total under 400 words. Be warm, African, and real."""

    user_prompt = f"""Situation faced: {user_input}
Detection result: {fraud_analysis.get('fraud_type', 'Suspicious activity')}
Advice given: {incident_advice[:200]}...

Now educate and empower the user:"""

    return call_llm(system_prompt, user_prompt, temperature=0.4, max_tokens=500)

# ── Main Agent Orchestrator ──────────────────────────────────────────────────
def run_oga_watchafri(user_input: str) -> None:
    print("=" * 60)
    print("🛡️  OGA_WATCHAFRI — The Boss That Watches Over Africa")
    print("=" * 60)
    print(f"\n📝 Your report: {user_input}\n")
    print("-" * 60)

    # Node 1: Detect
    fraud_analysis = node1_fraud_detector(user_input)

    if isinstance(fraud_analysis, dict) and not fraud_analysis.get("raw_output"):
        severity = fraud_analysis.get("severity", "UNKNOWN")
        fraud_type = fraud_analysis.get("fraud_type", "Unknown")
        confidence = fraud_analysis.get("confidence", "UNKNOWN")
        is_fraud = fraud_analysis.get("is_fraud", False)

        emoji = "🔴" if severity == "CRITICAL" else "🟠" if severity == "HIGH" else "🟡"
        print(f"{emoji} DETECTION RESULT")
        print(f"   Fraud Type : {fraud_type}")
        print(f"   Confidence : {confidence}")
        print(f"   Severity   : {severity}")
        print(f"   Red Flags  : {', '.join(fraud_analysis.get('red_flags', []))}")
        print(f"   Reasoning  : {fraud_analysis.get('reasoning', '')}")
        print("-" * 60)
    else:
        is_fraud = True
        print("⚠️  Detection completed (raw output mode)")
        print("-" * 60)

    # Node 2: Advise
    incident_advice = node2_incident_advisor(user_input, fraud_analysis)
    print("🚨 INCIDENT RESPONSE GUIDANCE")
    print("-" * 60)
    print(incident_advice)
    print("-" * 60)

    # Node 3: Educate
    education = node3_awareness_educator(user_input, fraud_analysis, incident_advice)
    print("\n🎓 AWARENESS EDUCATION")
    print("-" * 60)
    print(education)
    print("=" * 60)
    print("\n✅ OGA_WATCHAFRI analysis complete. Stay safe, stay sharp! 💪🌍")
    print("=" * 60)


# ── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\nWelcome to OGA_WATCHAFRI 🛡️")
    print("Tell me about a suspicious message, call, or situation.\n")

    # Demo mode: run with sample inputs if no argument provided
    import sys
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        # Interactive mode
        user_input = input("📝 Describe the suspicious situation: ").strip()
        if not user_input:
            # Fallback demo
            user_input = "Someone sent me a WhatsApp message saying I won N500,000 and should send N5,000 to claim it"
            print(f"\n[Demo mode] Using sample input: {user_input}\n")

    run_oga_watchafri(user_input)
