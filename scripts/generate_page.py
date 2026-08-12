import argparse
import json
import re
import unicodedata


def slugify(value: str) -> str:
    value = unicodedata.normalize('NFD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^a-zA-Z0-9]+', '-', value).strip('-').lower()
    return value or 'x'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prenom', required=True)
    parser.add_argument('--nom', required=True)
    parser.add_argument('--date', required=True)
    args = parser.parse_args()

    with open('index.html', encoding='utf-8') as f:
        html = f.read()

    # Retire l'écran de formulaire : la page publiée démarre directement le livre.
    html = re.sub(r'<section id="formScreen".*?</section>\s*', '', html, flags=re.DOTALL)

    preset = json.dumps(
        {"prenom": args.prenom, "nom": args.nom, "date": args.date},
        ensure_ascii=False,
    )
    preset_script = f'<script>window.SOLID_PRESET_NAME = {preset};</script>\n'
    html = html.replace('<script>', preset_script + '<script>', 1)

    filename = f"bienvenue-{slugify(args.prenom)}-{slugify(args.nom)}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

    print(filename)


if __name__ == '__main__':
    main()
