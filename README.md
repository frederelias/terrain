# Terrain — repérage de lots

Outil de terrain pour repérer des lots cadastrés autour de soi au Québec
(Laurentides, Lanaudière…), identifier la municipalité et la MRC, vérifier
s'il s'agit d'une terre publique, puis ouvrir Infolot, le Registre foncier et
le rôle d'évaluation avec le numéro de lot déjà copié.

Tout tourne dans le navigateur. Aucun serveur, aucune clé d'API, aucune donnée
personnelle ne sort du téléphone.

## Mettre en ligne sur GitHub Pages (gratuit, ~5 minutes)

1. Crée un compte sur github.com si tu n'en as pas.
2. Clique **New repository** → nom : `terrain` → **Public** → **Create repository**.
3. Sur la page du dépôt, clique **uploading an existing file** et dépose les
   4 fichiers : `index.html`, `manifest.webmanifest`, `sw.js`, `icon.svg`.
   Clique **Commit changes**.
4. **Settings** → **Pages** → Source : **Deploy from a branch** →
   Branch : `main`, dossier `/ (root)` → **Save**.
5. Après ~1 minute, l'adresse apparaît en haut de la page Pages :
   `https://TON-NOM.github.io/terrain/`
6. Ouvre cette adresse sur le téléphone, puis **Partager → Sur l'écran d'accueil**
   (iPhone) ou **⋮ → Installer l'application** (Android).

Le HTTPS est fourni par GitHub : c'est obligatoire pour que le navigateur
accepte de donner la position GPS.

## Réglages

En haut de `index.html`, bloc `CONFIG` :

- `scanRadius` : rayon du scan en mètres (250 par défaut).
- `roles` : colle l'URL de la carte interactive du rôle d'évaluation de chaque
  MRC (Argenteuil, Pays-d'en-Haut, Matawinie, D'Autray). Tant que c'est vide,
  le bouton « Rôle d'évaluation » lance une recherche web avec le nom de la
  municipalité.

## Sources de données (gratuites, sans inscription)

- Lots du cadastre rénové — MELCCFP/MRNF, `geo.environnement.gouv.qc.ca`
- Découpage municipal (nom, MRC, site web, téléphone) — MRNF, `servicescarto.mrnf.gouv.qc.ca`
- Droits fonciers (baux) sur terres publiques — MRNF
- Fonds de carte : OpenStreetMap, imagerie Esri

## Limites connues

- Le propriétaire n'est jamais dans ces services : il faut le Registre foncier
  (compte client, 1 $ par document) ou le rôle d'évaluation de la MRC.
- La « tenure » affichée est indicative (présence de baux publics). La source
  officielle reste le Registre du domaine de l'État.
- Il faut du réseau cellulaire pour les cartes et les requêtes. La coquille de
  l'app, elle, fonctionne hors ligne.
