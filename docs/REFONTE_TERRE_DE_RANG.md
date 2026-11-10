# Refonte « Terre de rang » — Phase A : audit et matrice

Branche : `terre-de-rang` · Base auditée : `main`, `index.html` v43 (10 novembre 2026) · Kit : `LOTS_Claude_Kit_v2`

Méthode : lecture complète du code (HTML, CSS, ~1 600 lignes de JavaScript), vérification ciblée des points sensibles, suite de 69 tests automatiques sans navigateur (jsdom). **Non vérifié sur téléphone réel** : capteurs, caméra en PWA installée, comportement en arrière-plan.

## 1. Constats critiques (P0 — à corriger avant tout embellissement)

| # | Constat vérifié dans le code | Risque | Correctif |
|---|---|---|---|
| P0-1 | La marche vit en mémoire ; `store.set('terrain.walks')` n'est appelé que dans `stopWalk()` (et à la suppression / restauration). | Fermeture de l'app, mise en veille agressive d'Android ou plantage = **tracé perdu en silence**. Les photos restent, mais rattachées à une marche qui n'existe plus. | Sauvegarde progressive de la marche active (toutes les 10 s et à `pagehide` / `visibilitychange`), reprise proposée au redémarrage. |
| P0-2 | Photo importée de la galerie depuis l'écran de visée : `pendingSrc='marche'` puis `pos=me`, `heading=aimHeading`. | Une vieille photo reçoit la **position et le cap du moment**, comme si elle avait été prise ici et maintenant (test d'acceptation 19). | Import = « photo importée », sans position ni cap, sauf confirmation explicite « prise ici maintenant ». |
| P0-3 | Aucun mode nuit (0 règle `prefers-color-scheme`). | Éblouissement le soir, contraste non maîtrisé ; exigence du kit (écrans 18–19). | Thème nuit complet, mêmes emplacements de boutons. |
| P0-4 | La photo s'enregistre au déclencheur, sans étape de vérification ; le lot est calculé au point GPS, sans précision affichée ni choix manuel. | Photos fantômes, mauvais lot associé près des limites. | Écran « Vérifier et enregistrer » (kit 14). |

Points vérifiés **conformes** : le cap est verrouillé au moment de « Fixer le point de vue » (`aimHeading=heading`) et n'est jamais recalculé ensuite ; un cap absent est enregistré comme `null`, sans direction inventée ; aucun texte blanc sur fond orange.

## 2. Matrice écran actuel → écran proposé

Légende : **EXISTANT** (garder tel quel) · **AMÉLIORER** (dans cette refonte) · **FUTUR** (backlog, hors refonte).

| Kit | État actuel dans le code | Fonctions existantes (identifiants) | Proposition | Données touchées | Tests | Statut |
|---|---|---|---|---|---|---|
| 01 Bienvenue | `#intro`, 5 diapositives + « Avant de partir » (`#permList`) | Installation PWA, permissions position/caméra/micro/boussole, `introOff`, liens conditions | Un seul écran d'accueil avec le nouveau logo, permissions progressives au premier usage ; le guide reste derrière « ? » | `terrain.introOff`, `terrain.seenGuide` | 1, 24 | AMÉLIORER |
| 02 Carte | `#map`, pin centrale, anneau, `.mapctl`, `.mectl`, `#strip`, `#peek` | Cadastre, municipalités, baux, scan, aperçu du lot sous la pin, boussole, position | Barre de puces (Lots, Rangs, Vacants ?, Filtres·n) ; scan en bouton de carte ; aperçu = « Lot sélectionné » | aucune | 2, 4 | AMÉLIORER |
| 03 Filtres | `#sheetFilters` | Vacant présumé, superficie min, ancienneté, 3 propriétaires +, type | Superficie min/max en ha **et** acres, libellé « Sans adresse civique — indice, pas une preuve », zone de recherche | `terrain.filters` (rétrocompatible) | 5 | AMÉLIORER |
| 04 Lot sur carte | `#peek` + `highlightOne` | Lot sous la pin, superficie, municipalité, usage, ancienneté | Carte « Lot sélectionné » avec avertissement contour, « Voir la fiche » + « Garder dans mon journal » | carnet | 7, 9 | AMÉLIORER |
| 05 Fiche résumé | `#sheetLot` : résumé `.sum` + sections repliables | Unités (pi², m², acres, ha), statuts, ♥ Garder, enregistrement auto | Grille identité (superficie, municipalité, MRC, propriétaire), « À vérifier avant d'aller plus loin » (accès, zonage, cadastre), provenance et date | carnet | 7, 9 | AMÉLIORER |
| 06 Sources | section `#secExplore` | Registre, rôle (Argenteuil en direct, Laval, Matawinie zoomée), Infolot, municipalité, pièces jointes images/documents, rôle 2026 ouvert | Liste « À la source » avec provenance et date, badges officiel / dérivé / estimé | photos (IndexedDB) | 8, 10 | AMÉLIORER |
| 07 Propriétaire | `#secOwner` | Nom, Canada411, Google, Facebook, LinkedIn, Registre des entreprises, avis de décès, Index des noms | Même contenu, mise en page du kit, rappel « aucun démarchage automatisé » | carnet | 9 | AMÉLIORER |
| 08 Suivi du lot | `#secFollow`, `#secContact`, `#secPhotos`, `#secSale` | Visité, contacté, note, lettre à imprimer, courriel, texto, Centris, annonces de 10 sources | Statut + **prochaine action** (date de relance), photos, notes | carnet : champ `next` ajouté (optionnel, rétrocompatible) | 9 | AMÉLIORER |
| 09 Journal | `#sheetCarnet` | Liste des lots, sélection multiple, favoris sur la carte, CSV, partage, sauvegarde/restauration, marches, rapport d'usage, micro | Renommer « Journal » ; recherche, tri, filtres par statut ; onglets Lots / Marches ; maintenance déplacée vers Outils | aucune (lecture) | 11 | AMÉLIORER |
| 10 Préparation de marche | inexistant (démarrage direct) | — | Écran court : précision GPS, réseau, lot courant, « Démarrer » | aucune | 12 | AMÉLIORER |
| 11 Marche active | `#walkStrip`, `btnWalk` | Distance, lot courant, alerte de limite (vibration), pause/reprise, terminer protégé | Ajouter durée, précision GPS, gros bouton Photo à une main | **marche active sauvegardée en continu (P0-1)** | 12, 13 | AMÉLIORER |
| 12 Fixer le point de vue | `#aim` | Téléphone à plat, boussole, cap, « Fixer » ; import galerie | Qualité du cap, « Prendre sans direction » explicite ; import galerie corrigé (P0-2) | photos | 14, 15, 19 | AMÉLIORER |
| 13 Snap | `#snap` | Aperçu caméra, zoom 1×/2×/4× + pincement, lampe, changement de caméra, repli appareil photo | « Cap fixé : 287° 🔒 », lot associé affiché | photos | 16, 17 | AMÉLIORER |
| 14 Vérifier la photo | **inexistant** | — | Nouveau : photo, précision GPS, cap, lot (ou « incertain » + choix), heure, note, Reprendre / Enregistrer | photos : champs `acc`, `note`, `lotSure` ajoutés | 18 | AMÉLIORER |
| 15 Bilan de marche | inexistant (message éphémère) | — | Distance, durée, lots traversés, photos, carte du tracé, accès au journal | marches : champ `lots` ajouté | 12 | AMÉLIORER |
| 16 Partage | `#shareModal` | ZIP par lot (photos, CSV, GeoJSON, KML, lisez-moi), lien Premium « bientôt » | Mise en page du kit ; ajouter Journal CSV et KML/GeoJSON de tout le journal ; « Noms et coordonnées : exclus » visible | aucune | 21 | AMÉLIORER |
| 17 Réglages | dispersé (Couches, bas du carnet, guide) | Couches, favoris seulement, sauvegarde, confidentialité, version, rapport d'usage | Nouvel onglet « Outils » : apparence (jour/nuit/auto), unités, sauvegarde, exports, sources, confidentialité, aide | `terrain.theme`, `terrain.units` | 23, 25 | AMÉLIORER |
| 18–19 Nuit | inexistant | — | Thème nuit (P0-3) | `terrain.theme` | 23 | AMÉLIORER |
| — | Fonctions présentes **absentes du kit** | Mesure distance/surface, couches (aérien, baux), recherche par lien Centris, réception de partage Centris, rapport d'usage et commentaires vocaux, sources d'annonces, alertes hors ligne | Toutes conservées : mesure et couches dans la carte, annonces dans la fiche, rapport d'usage dans Outils | — | 6, 28 | EXISTANT |
| — | Backlog du kit | Paquets hors ligne, liste de vérification complète, comparateur, alertes, IA, synchronisation | Hors refonte | — | — | FUTUR |

## 3. Navigation

Actuelle : Marcher · Photo · [Scanner] · Filtres · Carnet. Proposée (kit) : **Carte · Marcher · Journal · Outils**, avec Photo contextuelle (gros bouton pendant une marche, entrée dans la fiche), Scanner et Filtres déplacés sur la carte. Aucune fonction retirée : chacune garde un accès en un ou deux gestes.

## 4. Plan d'exécution

- **P0** (données) : sauvegarde progressive des marches, import galerie honnête, écran Vérifier, thème nuit.
- **P1** (marque et parcours) : nouveau logo et déclinaisons (après ton accord), tokens Terre de rang, navigation à 4 onglets, Journal, Outils, Marche (préparation, active, bilan), microcopies du kit.
- **P2** : provenance et dates sur chaque donnée, prochaine action par lot, exports du journal, mention territoriale révisée.

Chaque changement de format de stockage est **additif** (champs optionnels) : une sauvegarde faite avec v43 se restaure telle quelle.

## 5. Limites

Non testable ici : capteurs réels, caméra en PWA installée, mise en arrière-plan, plein soleil. Une session de test sur ton téléphone sera nécessaire avant publication (tests 13, 14, 16, 20, 26).
