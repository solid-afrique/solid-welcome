import argparse
import json
import re
import unicodedata
import os
import subprocess


def slugify(value: str) -> str:
    value = unicodedata.normalize('NFD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^a-zA-Z0-9]+', '-', value).strip('-').lower()
    return value or 'x'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prenom', required=True)
    parser.add_argument('--nom', required=True)
    parser.add_argument('--date', required=True)
    parser.add_argument('--token', help='GitHub Personal Access Token (ou utilise GITHUB_TOKEN env var)')
    args = parser.parse_args()

    # Récupère le token depuis l'argument ou la variable d'environnement
    github_token = args.token or os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("⚠️  Token GitHub requis via --token ou GITHUB_TOKEN")
        return

    with open('template.html', encoding='utf-8') as f:
        html = f.read()

    preset = json.dumps(
        {"prenom": args.prenom, "nom": args.nom, "date": args.date},
        ensure_ascii=False,
    )
    preset_script = f'<script>window.SOLID_PRESET_NAME = {preset};</script>\n'
    html = html.replace('<script>', preset_script + '<script>', 1)

    filename = f"bienvenue-{slugify(args.prenom)}-{slugify(args.nom)}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Fichier généré : {filename}")

    # Configure git avec le token
    repo_url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url'], text=True).strip()
    
    # Remplace l'URL avec le token pour l'authentification
    if 'https://' in repo_url:
        auth_url = repo_url.replace('https://', f'https://{github_token}@')
        subprocess.run(['git', 'remote', 'set-url', 'origin', auth_url])

    # Commit et push
    try:
        subprocess.run(['git', 'add', filename], check=True)
        subprocess.run(['git', 'commit', '-m', f'Ajout page bienvenue {args.prenom} {args.nom}'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print(f"✅ Déployé sur GitHub : {filename}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur git : {e}")
    finally:
        # Restaure l'URL originale (sans token)
        subprocess.run(['git', 'remote', 'set-url', 'origin', repo_url])


if __name__ == '__main__':
    main()
