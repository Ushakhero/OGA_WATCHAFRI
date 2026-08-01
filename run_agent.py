"""
OGA_WATCHAFRI - 3-Node AI Reasoning Agent
The Boss That Watches Over Africa
Supports English, Nigerian Pidgin, Hausa, Yoruba, and Igbo
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

# Yoruba word list for language detection (accepts common typing without tone marks)
YORUBA_WORDS = [
    'mo', 'wa', 'ni', 'ti', 'ki', 'ati', 'fun', 'pe', 'se', 'yi',
    'yin', 'won', 'oun', 'bawo', 'sugbon', 'owo', 'banki', 'foonu',
    'ile', 'ana', 'oni', 'okunrin', 'obinrin', 'olorun', 'ere',
    'jibiti', 'esan', 'omo', 'nitori', 'akoko', 'eniyan', 'ariwa',
    'gba', 'eni', 'wipe', 'sanwo', 'asiko', 'ile', 'sinu', 'opolopo',
    'oga', 'egbon', 'ranse', 'foonu', 'ipe', 'iwifun', 'ojo', 'meje'
]

# Igbo word list for language detection
IGBO_WORDS = [
    'ana', 'gi', 'ha', 'ya', 'na', 'ka', 'maka', 'ihe', 'onye',
    'ego', 'ulo', 'oku', 'ozi', 'taa', 'unyaahu', 'nwoke', 'nwanyi',
    'chukwu', 'uru', 'aghughọ', 'aghughq', 'ikpe', 'otu', 'mana',
    'oge', 'mmadu', 'ugwu', 'zipu', 'nata', 'najuu', 'kwuo', 'pia',
    'mechie', 'akauntu', 'uzo', 'otutu', 'ubochi', 'asaa', 'mba'
]


def detect_language(text):
    """
    Detect the language of the user's message.
    Returns one of 'hausa', 'yoruba', 'igbo', or 'english'.
    """
    words = text.lower().split()
    if not words:
        return 'english'

    scores = {
        'hausa': sum(1 for w in words if w in HAUSA_WORDS),
        'yoruba': sum(1 for w in words if w in YORUBA_WORDS),
        'igbo': sum(1 for w in words if w in IGBO_WORDS),
    }

    best_lang = max(scores, key=scores.get)
    best_count = scores[best_lang]

    if best_count >= 2 or (best_count / len(words)) > 0.15:
        return best_lang
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
    elif language == 'yoruba':
        system_prompt = """Ìwọ ni onímọ̀-ẹ̀rọ tí ó ṣe amọ̀ràn nípa ìwádìí jìbìtì ní Nàìjíríà àti Áfríkà.

O gbọ́dọ̀ ṣàwárí irú jìbìtì náà, ìwọ̀n ewu rẹ̀, àti àwọn ìdí tí ó fi mú ọ rò báyìí.

Fèsì nínú ìlànà JSON yìí nìkan - má ṣe kọ ohunkóhun ní ìta JSON náà:
{
  "fraud_type": "Irú jìbìtì tí a ṣàwárí",
  "severity": "CRITICAL tàbí HIGH tàbí MEDIUM tàbí LOW",
  "confidence": "HIGH tàbí MEDIUM tàbí LOW",
  "red_flags": ["àmì ewu 1", "àmì ewu 2"],
  "reasoning": "Àlàyé kúkúrú ní èdè Yorùbá"
}"""
    elif language == 'igbo':
        system_prompt = """Ị bụ ọkachamara na nchọpụta aghụghọ na Naịjirịa na Afrịka.

Ị ga-achọpụta ụdị aghụghọ, ọkwa ihe egwu ya, na ihe mere i ji chee otú a.

Zaghachi naanị n'ụdị JSON a - edekwala ihe ọ bụla n'èzí JSON:
{
  "fraud_type": "Ụdị aghụghọ achọpụtara",
  "severity": "CRITICAL ma ọ bụ HIGH ma ọ bụ MEDIUM ma ọ bụ LOW",
  "confidence": "HIGH ma ọ bụ MEDIUM ma ọ bụ LOW",
  "red_flags": ["ihe akara ize ndụ 1", "ihe akara ize ndụ 2"],
  "reasoning": "Nkọwa dị mkpirikpi n'asụsụ Igbo"
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

    FALLBACK_TEXT = {
        'hausa': ("Zamba", "Ba a iya tabbatarwa"),
        'yoruba': ("Jìbìtì", "A kò lè jẹ́rìí sí i"),
        'igbo': ("Aghụghọ", "Enweghị ike ịkọwa nkọwa"),
    }

    try:
        return json.loads(text)
    except Exception:
        fraud_type, red_flag = FALLBACK_TEXT.get(language, ("Suspicious Activity", "Could not parse details"))
        return {
            "fraud_type": fraud_type,
            "severity": "HIGH",
            "confidence": "MEDIUM",
            "red_flags": [red_flag],
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
    elif language == 'yoruba':
        system_prompt = """Ìwọ ni olùdámọ̀ràn fún àwọn tí a ti tan jẹ ní Nàìjíríà.

A ti ṣàwárí: """ + fraud_type + """ | Ìwọ̀n ewu: """ + severity + """

Fún ni ní àwọn ìgbésẹ̀ kánjú tí yóò ràn án lọ́wọ́ láti gba owó padà tàbí dí ìpàdánù míì síi.
Mẹnu kan àwọn nọ́mbà fóònù gidi:
- EFCC: 0800-326-5252
- CBN: 0700-225-5226
- Ọlọ́pàá Ayélujára: 08057750448
- MTN: 180 (láti dí SIM)
- Airtel: 121
- GTBank: 0700-482-6328
- Access Bank: 1-800-000-2348
- Zenith Bank: 0700-350-8000

Kọ ní èdè Yorùbá tí ó ṣe kedere. Bẹ̀rẹ̀ pẹ̀lú ìgbésẹ̀ tí ó ṣe pàtàkì jùlọ. Ka nọ́ńbà kọ̀ọ̀kan."""
    elif language == 'igbo':
        system_prompt = """Ị bụ onye ndụmọdụ maka ndị e ghọgburu n'aghụghọ na Naịjirịa.

Achọpụtara: """ + fraud_type + """ | Ọkwa ihe egwu: """ + severity + """

Nye nzọụkwụ ngwa ngwa ga-enyere ha aka nweghachi ego ma ọ bụ gbochie mfu ọzọ.
Kpọtụrụ ọnụọgụ ekwentị eziokwu:
- EFCC: 0800-326-5252
- CBN: 0700-225-5226
- Ndị Uwe Ojii Ịntanetị: 08057750448
- MTN: 180 (iji kpuchie SIM)
- Airtel: 121
- GTBank: 0700-482-6328
- Access Bank: 1-800-000-2348
- Zenith Bank: 0700-350-8000

Dee ya n'asụsụ Igbo doro anya. Bido site na nzọụkwụ kacha mkpa. Gụọ nọmba nzọụkwụ ọ bụla."""
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
    elif language == 'yoruba':
        system_prompt = """Ìwọ ni olùkọ́ nípa jíjí kánkán fún àwọn àdúgbò ní Nàìjíríà.

Irú jìbìtì tí a ṣàwárí: """ + fraud_type + """

Kọ ọ̀rọ̀ kan tí a lè fi ránṣẹ́ sórí WhatsApp fún ẹbí àti ọ̀rẹ́ láti dáàbò bo ara wọn.
Bẹ̀rẹ̀ pẹ̀lú IKILỌ̀
Ṣàlàyé bí jìbìtì náà ṣe ń ṣiṣẹ́ ní gbolohun 2-3
Fún ni ní ọ̀nà 3 láti dáàbò bo ara ẹni
Parí pẹ̀lú nọ́mbà EFCC: 0800-326-5252
Fi àwòrán emoji tí ó bá a mu. Gùn: gbolohun 8-10 péré."""
    elif language == 'igbo':
        system_prompt = """Ị bụ onye nkuzi maka mmụta gbasara aghụghọ maka obodo Naịjirịa.

Ụdị aghụghọ achọpụtara: """ + fraud_type + """

Dee otu ozi a ga-esi na WhatsApp kesaa iji chebe ezinụlọ na ndị enyi.
Bido na ỊDỌ AKA NA NTỊ
Kọwaa otu aghụghọ a si arụ ọrụ na ahịrịokwu 2-3
Nye ụzọ 3 isi chebe onwe gị
Jiri nọmba EFCC mechie: 0800-326-5252
Tinye emoji kwesịrị ekwesị. Ogologo: ahịrịokwu 8-10 kacha."""
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
    print("Languages: English, Hausa, Yoruba, Igbo, Nigerian Pidgin")
    print("=" * 55)

    situation = input("\nDescribe the situation / Ka bayyana abin da ya faru:\n> ")
    if not situation.strip():
        situation = "Someone sent me a WhatsApp message saying I won N500,000 and should send N5,000 to claim it"

    detected = detect_language(situation)
    print("\n[Language detected: " + detected.upper() + "]")
    print("\nAnalyzing... Ana nazari...\n")

    result = run_analysis(situation, detected)
    det = result['detection']

    node1_labels = {'hausa': 'GANO ZAMBA', 'yoruba': 'AWARI JIBITI', 'igbo': 'ACHỌPỤTA AGHỤGHỌ'}
    node2_labels = {'hausa': 'SHAWARA', 'yoruba': 'IMORAN', 'igbo': 'NDUMODU'}
    node3_labels = {'hausa': 'ILIMI', 'yoruba': 'EKO', 'igbo': 'MMUTA'}

    print("NODE 1 - " + node1_labels.get(detected, "FRAUD DETECTOR"))
    print("  Type: " + str(det.get('fraud_type')))
    print("  Severity: " + str(det.get('severity')))
    for flag in det.get('red_flags', []):
        print("  - " + flag)

    print("\nNODE 2 - " + node2_labels.get(detected, "INCIDENT ADVISOR"))
    print(result['incident_advice'])

    print("\nNODE 3 - " + node3_labels.get(detected, "AWARENESS EDUCATOR"))
    print(result['education'])
