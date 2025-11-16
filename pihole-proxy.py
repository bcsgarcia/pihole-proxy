#!/usr/bin/env python3
from flask import Flask, jsonify
import requests
import logging
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Configurações do Pi-hole via variáveis de ambiente
PIHOLE_URL = os.getenv('PIHOLE_URL', 'http://localhost')
PIHOLE_PASSWORD = os.getenv('PIHOLE_PASSWORD')

if not PIHOLE_PASSWORD:
    logging.error("PIHOLE_PASSWORD environment variable is not set!")
    exit(1)

def get_sid():
    """Faz login no Pi-hole e retorna o SID"""
    try:
        response = requests.post(
            f"{PIHOLE_URL}/api/auth",
            json={"password": PIHOLE_PASSWORD},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if 'session' in data and 'sid' in data['session']:
                return data['session']['sid']
        logging.error(f"Auth failed: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Auth error: {e}")
    return None

@app.route('/stats')
def get_stats():
    """Pega estatísticas completas do Pi-hole"""
    sid = get_sid()
    if not sid:
        return jsonify({"error": "Authentication failed"}), 401
    
    try:
        # Buscar summary (tem active clients correto)
        summary_response = requests.get(
            f"{PIHOLE_URL}/api/stats/summary",
            headers={"X-FTL-SID": sid},
            timeout=5
        )
        
        if summary_response.status_code == 200:
            data = summary_response.json()
            return jsonify(data)
        
        logging.error(f"Stats failed: {summary_response.status_code} - {summary_response.text}")
        return jsonify({"error": "Failed to get stats"}), summary_response.status_code
    except Exception as e:
        logging.error(f"Stats error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    """Health check"""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=False)
