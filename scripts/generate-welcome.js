#!/usr/bin/env node
'use strict';

/**
 * Génère un fichier de bienvenue autonome à partir du modèle HTML
 * (le même fichier que celui qui contient le formulaire, ex. index.html).
 *
 * Usage : node scripts/generate-welcome.js "<prenom>" "<nom>" "<date JJ/MM/AAAA>"
 *
 * Important : ce script réutilise TEL QUEL le modèle HTML (formulaire + livre),
 * exactement comme le fait la fonction generateWelcomeFile() côté navigateur.
 * Il n'y a donc qu'une seule source de vérité pour la logique de défilement
 * (boucle infinie, durées, etc.) : le modèle. Si le modèle est mis à jour,
 * les fichiers générés par ce script le seront automatiquement aussi.
 */

const fs = require('fs');
const path = require('path');

const [, , prenomArg, nomArg, dateArg] = process.argv;

if (!prenomArg || !nomArg || !dateArg) {
  console.error('Usage: node generate-welcome.js "<prenom>" "<nom>" "<date JJ/MM/AAAA>"');
  process.exit(1);
}

const prenom = prenomArg.trim();
const nom = nomArg.trim();

// ---- Localisation du modèle ----
// On cherche le fichier qui contient le formulaire (celui déployé sur GitHub Pages).
// Adapte CANDIDATE_TEMPLATES si ton fichier a un autre nom/emplacement.
const CANDIDATE_TEMPLATES = ['index.html', 'solid-bienvenue.html', 'templates/solid-bienvenue.html'];
const templatePath = CANDIDATE_TEMPLATES.map(p => path.resolve(process.cwd(), p)).find(p => fs.existsSync(p));

if (!templatePath) {
  console.error('Modèle introuvable. Cherché : ' + CANDIDATE_TEMPLATES.join(', '));
  process.exit(1);
}

const templateHtml = fs.readFileSync(templatePath, 'utf8');

// ---- Formatage de la date (jour mois année, ex. "11 août 2026") ----
// Format unique accepté en entrée : JJ/MM/AAAA (ex: 09/08/2026)
function formatDateFr(rawValue) {
  const raw = String(rawValue).trim();
  const match = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.exec(raw);

  if (!match) {
    console.error('Date invalide, format attendu JJ/MM/AAAA (ex: 09/08/2026). Reçu : ' + rawValue);
    process.exit(1);
  }

  const day = Number(match[1]);
  const month = Number(match[2]);
  const year = Number(match[3]);

  if (month < 1 || month > 12 || day < 1 || day > 31) {
    console.error('Date invalide, format attendu JJ/MM/AAAA (ex: 09/08/2026). Reçu : ' + rawValue);
    process.exit(1);
  }

  const d = new Date(year, month - 1, day);
  return new Intl.DateTimeFormat('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' }).format(d);
}

const dateStr = formatDateFr(dateArg);

// ---- Échappement pour insertion dans une chaîne JS ----
const esc = s => s.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/</g, '\\u003C');

const presetScript = `<script>window.SOLID_PRESET_NAME = { prenom: "${esc(prenom)}", nom: "${esc(nom)}", date: "${esc(dateStr)}" };<\/script>`;

// ---- Transformations : identiques à generateWelcomeFile() côté navigateur ----
let html = templateHtml;
// Retire l'écran de formulaire : le fichier généré ne doit contenir que le livre
html = html.replace(/<section id="formScreen"[\s\S]*?<\/section>\s*/, '');
// Le bouton "restart" doit rejouer le livre (il n'y a plus de formulaire à réafficher)
html = html.replace('Envoyer un nouveau message', 'Revoir le message');
// Injecte le préréglage juste avant le script principal
html = html.replace('<script>', presetScript + '\n<script>');

if (!html.includes('SOLID_PRESET_NAME')) {
  console.error("Échec de l'injection du préréglage dans le modèle.");
  process.exit(1);
}

// ---- Nom de fichier ----
const slug = s => s
  .toLowerCase()
  .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/^-+|-+$/g, '');

const fileName = `bienvenue-${slug(prenom)}-${slug(nom)}.html`;

fs.writeFileSync(path.resolve(process.cwd(), fileName), html, 'utf8');

// ---- Sortie pour $GITHUB_OUTPUT ----
console.log(`FICHIER_GENERE=${fileName}`);
