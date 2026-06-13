# 📋 OGA_WATCHAFRI — Hackathon Submission Description

> Copy and paste this into the Devpost / hackathon submission portal

---

## Project Name
**OGA_WATCHAFRI**

## Tagline
*"The Boss That Watches Over Africa"*

---

## Inspiration

Africa is losing billions to cyber fraud every year. In Nigeria alone, the EFCC
reports hundreds of millions of dollars lost annually to scams — and most victims
are ordinary people who received a suspicious WhatsApp message, a fake bank SMS,
or a convincing phone call from someone pretending to be from their telecom provider.

The tragedy isn't just the money lost — it's that most people don't know what to do
after being scammed, and many fall for the same trick twice.

I built OGA_WATCHAFRI because Africa deserves an AI guardian built specifically
for African fraud patterns, African institutions, and African communities.

---

## What It Does

OGA_WATCHAFRI is a multi-step reasoning AI agent that acts as a personal
cybersecurity bodyguard for African internet users. When a user describes a
suspicious situation, the agent:

1. **DETECTS** — Analyzes the situation for fraud patterns specific to Africa
   (419 scams, SIM swap, phishing, mobile money fraud, fake investments)

2. **ADVISES** — Provides immediate step-by-step response guidance with real
   African institution contacts (EFCC, CBN, NCC, MTN, GTBank, etc.)

3. **EDUCATES** — Explains what happened in simple language with shareable
   tips the user can send to their family WhatsApp group

---

## How I Built It

- **Microsoft Azure AI Foundry** — Core agent platform
- **Prompt Flow** — Orchestrates the 3-node multi-step reasoning pipeline
- **GPT-4o-mini** — Powers all three reasoning nodes
- **Python** — Integration layer and local runner
- **GitHub** — Version control and submission

The agent uses a chained Prompt Flow architecture where each node's output
feeds into the next, creating genuine multi-step reasoning rather than
a single prompt response.

---

## Challenges I Ran Into

- Designing prompts that reason accurately about African-specific fraud patterns
  without hallucinating institution names or phone numbers
- Balancing response detail with simplicity for non-technical users
- Ensuring the JSON output from Node 1 parses correctly into Node 2's context

---

## Accomplishments I'm Proud Of

- Built a genuinely Africa-first AI tool — not a generic chatbot repurposed for Africa
- The agent references real Nigerian, Ghanaian, and Kenyan institutions accurately
- The educator node produces responses that feel human, warm, and culturally resonant
- Responsible AI is baked in from the ground up — not an afterthought

---

## What I Learned

- How to design effective multi-step reasoning pipelines in Azure AI Foundry
- The power of Prompt Flow for chaining LLM outputs as structured inputs
- How important cultural context is when building AI for underserved communities
- That a well-scoped, focused agent beats a bloated, generalized one every time

---

## What's Next for OGA_WATCHAFRI

- 🌐 Web interface (Streamlit or Flask) for easy public access
- 🗣️ Support for Pidgin English, Hausa, Yoruba, Igbo, and Swahili
- 📱 WhatsApp integration — fight scams on the platform where they happen most
- 🏛️ Direct API integration with EFCC and CBN reporting portals
- 📊 Fraud trend dashboard showing most common scams by region

---

## Track
Reasoning Agents

## Tools Used
Microsoft Azure AI Foundry, Prompt Flow, GPT-4o-mini, Python, GitHub

## GitHub Repository
https://github.com/YOUR_USERNAME/OGA_WATCHAFRI

---

*Built with 💚 for Africa. OGA_WATCHAFRI — The Boss That Watches Over Africa.*
