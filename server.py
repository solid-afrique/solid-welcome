from flask import Flask, request, jsonify
import os
import requests
import subprocess
import sys

app = Flask(__name__)

# Configuration depuis les variables d'environnement
GITHUB_OWNER = os.getenv('GITHUB_OWNER', 'solid-afrique')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'solid-welcome')
WORKFLOW_FILE = os.getenv('WORKFLOW_FILE', 'generate-welcome.yml')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

if not GITHUB_TOKEN:
    print("⚠️  GITHUB_TOKEN non défini dans les variables d'environnement")
    sys.exit(1)

@app.route('/api/deploy', methods=['POST'])
def deploy():
    data = request.json
    prenom = data.get('prenom')
    nom = data.get('nom')
    date = data.get('date')

    if not all([prenom, nom, date]):
        return jsonify({'error': 'prenom, nom et date sont requis'}), 400

    # Déclenche le workflow GitHub
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/workflows/{WORKFLOW_FILE}/dispatches"
    headers = {
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github+json',
        'Content-Type': 'application/json'
    }
    payload = {
        'ref': 'main',
        'inputs': {'prenom': prenom, 'nom': nom, 'date': date}
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 204:
        return jsonify({
            'error': f'Échec du déclenchement du workflow (HTTP {response.status_code})',
            'details': response.text
        }), response.status_code

    # Génère le nom de fichier attendu
    import re
    def slugify(value):
        return re.sub(r'[^a-zA-Z0-9]+', '-', value).strip('-').lower() or 'x'
    
    filename = f"bienvenue-{slugify(prenom)}-{slugify(nom)}.html"
    public_url = f"https://{GITHUB_OWNER}.github.io/{GITHUB_REPO}/{filename}"

    return jsonify({
        'success': True,
        'message': 'Workflow déclenché avec succès',
        'url': public_url,
        'filename': filename
    })

if __name__ == '__main__':
    print("🚀 Serveur démarré sur http://localhost:5000")
    app.run(debug=True, port=5000)
