"""
OGA_WATCHAFRI — Flask Web API
Wraps the 3-node reasoning agent so it can be called
by GoldenShield (and any other system) over HTTP.
"""

from flask import Flask, request, jsonify
import os
from run_agent import node1_fraud_detector, node2_incident_advisor, node3_awareness_educator
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'OGA_WATCHAFRI is live', 'version': '1.0'})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Accepts a fraud incident and runs it through all 3 nodes.
    
    Expected JSON body:
    {
        "situation": "description of the suspicious situation",
        "source": "goldenshield",          (optional)
        "risk_level": "HIGH",              (optional, from GoldenShield)
        "pattern": "sim_swap",             (optional, from GoldenShield)
        "fraud_score": 87.5               (optional, from GoldenShield)
    }
    
    Returns the full 3-node analysis.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON body provided'}), 400

    situation = data.get('situation', '').strip()
    if not situation:
        return jsonify({'error': 'situation field is required'}), 400

    # If called from GoldenShield, enrich the situation description
    source = data.get('source', 'direct')
    pattern = data.get('pattern', '')
    risk_level = data.get('risk_level', '')
    fraud_score = data.get('fraud_score', '')

    if source == 'goldenshield' and pattern:
        situation = f"{situation}\n\n[GoldenShield detected: {pattern} pattern, risk level {risk_level}, fraud score {fraud_score}%]"

    try:
        # Node 1 — Detect
        fraud_analysis = node1_fraud_detector(situation)

        # Node 2 — Advise
        incident_advice = node2_incident_advisor(situation, fraud_analysis)

        # Node 3 — Educate
        education = node3_awareness_educator(situation, fraud_analysis, incident_advice)

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
