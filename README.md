# 🛡️ OGA_WATCHAFRI
### *"The Boss That Watches Over Africa"*

> **AI-powered multi-step reasoning agent that detects cyber fraud, advises victims, and educates African communities — built on Microsoft Azure AI Foundry**

---

![OGA_WATCHAFRI Banner](demo/banner-placeholder.md)

## 🌍 The Problem

Africa is facing a **cyber fraud epidemic**:

- 🇳🇬 Nigeria loses an estimated **$500M+** annually to cybercrime (EFCC reports)
- 📱 Mobile money fraud, SIM swap attacks, and phishing are rising across Ghana, Kenya, and South Africa
- 💬 WhatsApp scams, fake bank alerts, and "Yahoo Yahoo" social engineering target millions daily
- 😔 Most victims don't know what to do **after** being scammed — and fall for the same trick twice

The average African internet user has **no AI-powered tool** built specifically for their threat landscape.

**OGA_WATCHAFRI changes that.**

---

## 💡 The Solution

OGA_WATCHAFRI is a **multi-step reasoning AI agent** built on **Microsoft Azure AI Foundry** that:

| Step | Agent Action |
|------|-------------|
| 🔍 **DETECT** | Analyzes suspicious messages, links, calls, or situations for fraud signals |
| 🚨 **ADVISE** | Guides victims through immediate recovery steps using African institutions |
| 🎓 **EDUCATE** | Teaches users the fraud technique used and how to avoid it in future |

---

## 🏗️ Agent Architecture

```
┌─────────────────────────────────────────────────┐
│                  USER INPUT                      │
│  (suspicious message / scam situation / link)    │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│          NODE 1: 🔍 FRAUD DETECTOR              │
│  - Identifies fraud type (phishing, SIM swap,   │
│    419 scam, fake investment, mobile money)      │
│  - Lists red flags found                        │
│  - Assigns confidence level (High/Med/Low)      │
│  Output: fraud_type, red_flags[], confidence    │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│         NODE 2: 🚨 INCIDENT ADVISOR             │
│  - Determines urgency level                     │
│  - Recommends African institutions to contact   │
│    (EFCC, CBN, MTN/Airtel, local police)        │
│  - Step-by-step victim recovery plan            │
│  - Lists what NOT to do                         │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│         NODE 3: 🎓 AWARENESS EDUCATOR           │
│  - Names and explains the fraud technique       │
│  - Gives Africa-specific context                │
│  - 3 simple prevention tips                     │
│  - Memorable warning phrase                     │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│            FINAL USER RESPONSE                  │
│  Clear, simple, actionable guidance             │
└─────────────────────────────────────────────────┘
```

---

## 🛠️ Built With

| Tool | Purpose |
|------|---------|
| **Microsoft Azure AI Foundry** | Core agent platform |
| **Prompt Flow** | Multi-step reasoning orchestration |
| **GPT-4o-mini** | Language model powering all nodes |
| **Python 3.11** | Flow logic and integration |
| **GitHub** | Version control and submission |

---

## 🚀 Getting Started

### Prerequisites
- Microsoft Azure account (free tier works)
- Access to [Azure AI Foundry](https://ai.azure.com)
- Python 3.11+
- Git

### Setup Instructions

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/OGA_WATCHAFRI.git
cd OGA_WATCHAFRI

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your Azure credentials
cp .env.example .env
# Edit .env with your Azure AI Foundry endpoint and API key

# 4. Run the agent locally
python run_agent.py
```

### Environment Variables

```env
AZURE_AI_ENDPOINT=https://your-foundry-endpoint.openai.azure.com/
AZURE_AI_KEY=your_api_key_here
AZURE_DEPLOYMENT_NAME=gpt-4o-mini
```

---

## 💬 Example Interactions

### Example 1 — WhatsApp Money Scam
**User Input:**
> *"Someone sent me a WhatsApp message saying I won ₦500,000 and I should send ₦5,000 to claim it"*

**OGA_WATCHAFRI Response:**
- 🔍 **Detected:** Advance Fee Fraud (419 Scam) — HIGH confidence
- 🚨 **Advice:** Do NOT send any money. Block the number immediately. Report to EFCC via efccnigeria.org
- 🎓 **Education:** This is the classic "you must pay to receive" trick — no legitimate prize ever requires upfront payment

---

### Example 2 — Fake Bank Alert
**User Input:**
> *"I got an SMS from GTBank saying my account will be blocked. I should click this link: gtb-verify.net"*

**OGA_WATCHAFRI Response:**
- 🔍 **Detected:** Phishing Attack — HIGH confidence (fake domain, urgency tactic)
- 🚨 **Advice:** Do NOT click the link. Call GTBank directly on 0700-4826-2657. Report to CBN on 0800-225-5226
- 🎓 **Education:** Banks never send verification links via SMS — always visit the official website directly

---

### Example 3 — SIM Swap Attack
**User Input:**
> *"Someone called me claiming to be from MTN and asked for my SIM serial number and NIN"*

**OGA_WATCHAFRI Response:**
- 🔍 **Detected:** SIM Swap Social Engineering — HIGH confidence
- 🚨 **Advice:** Hang up immediately. Call MTN on 180 to secure your account. Contact your bank to freeze transactions
- 🎓 **Education:** Telecom staff never call to ask for your SIM serial — this is used to steal your number and access your mobile money

---

## 🌍 Real-World Impact

- 🎯 **Target Users:** 200M+ internet users across Nigeria, Ghana, Kenya, South Africa, and beyond
- 📱 **Key Threat Coverage:** 419 scams, phishing, SIM swap, fake investment schemes, mobile money fraud
- 🏛️ **African Institution Integration:** EFCC, CBN, NCC, local telecom providers, national police
- 🗣️ **Simple Language:** Responses designed for users who may not be tech-savvy
- 🌐 **Accessible:** Works via web interface — no app download needed

---

## 🤝 Responsible AI

OGA_WATCHAFRI is built with responsible AI principles at its core:

- 🔒 **No data storage** — user inputs are never logged or stored
- ⚠️ **Clear limitations** — always recommends professional/legal help for serious cases
- 🏛️ **Defers to authorities** — directs users to EFCC, police, and banks for legal action
- 🧠 **Transparency** — explains its reasoning at every step
- 🚫 **Not a substitute** — explicitly states it does not replace law enforcement
- ♿ **Inclusive design** — simple English, avoids technical jargon

See [responsible-ai.md](docs/responsible-ai.md) for full details.

---

## 📁 Project Structure

```
OGA_WATCHAFRI/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── run_agent.py                 # Main entry point
├── .env.example                 # Environment variable template
├── prompt-flow/
│   ├── flow.dag.yaml            # Prompt Flow DAG definition
│   ├── node1_detector.jinja2    # Fraud Detection prompt
│   ├── node2_advisor.jinja2     # Incident Advisor prompt
│   └── node3_educator.jinja2    # Awareness Educator prompt
├── docs/
│   └── responsible-ai.md        # Responsible AI statement
└── demo/
    └── screenshots/             # Demo screenshots
```

---

## 👤 Author

Built with 💚 for Africa — submitted to **Microsoft Agents League Hackathon 2026**
Track: **Reasoning Agents** | Tool: **Microsoft Azure AI Foundry**

---

## 📜 License

MIT License — free to use, adapt, and build upon for the good of Africa 🌍
