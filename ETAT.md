# État — où en est le projet, et par quoi commencer

> **Document de passation.** Il est la mémoire du projet entre deux sessions.
> Une session qui ouvre ce dépôt lit `00_Prompt_MapDee.md`, puis **ce fichier**,
> avant toute autre chose.
>
> Il se réécrit à chaque changement d'état. L'historique est dans git.

---

## 1. LES BLOCAGES — un restant sur neuf : B7 (définitions — mur, contact, bande)

> **Révision du 05/08/2026.** Une version antérieure listait dix blocages, dont
> **deux étaient déjà résolus par le commit qui les écrivait** — « le plan n'est
> référencé nulle part » et « `00` n'a pas de première tâche ». Ils sont retirés.
> Trouvé par audit adversarial ; c'est exactement la faute que ce document
> dénonce en §2 — présenter comme un fait ce qu'on n'a pas revérifié.
>
> Et un blocage a été **ajouté** : il n'était dans aucune des listes, et c'est le
> plus grave.

**Aucune boucle d'exploration ne peut démarrer tant que ces neuf points ne sont
pas réglés.** Ce ne sont pas des améliorations : plusieurs sont posés par les
documents eux-mêmes comme des conditions d'arrêt.

| # | ce qui bloque | conséquence |
|---|---|---|
| ~~**B1**~~ | ~~**La métrique d'É4 n'existe nulle part**~~ — **LEVÉ le 05/08** : `ADR-001` **ACCEPTÉE**. La métrique est la **corrélation de rang partielle**, bloc de contrôle **gelé par tour** commun à É2/É4, **BH à 10 % sur les candidats seuls** tranche, p-value de Student en entrée, IC publié. `05` est mis à jour. | le sommet du harnais existe : É4 devient calculable et mécanisable dès que C3 est gelé |
| ~~**B2**~~ | ~~**Trois documents donnent trois réponses à « que puis-je lancer ? »**~~ — **LEVÉ le 05/08** : `ADR-002` **ACCEPTÉE** (délégation de Meddy). La réponse canonique : interdits, (1) toute mesure **référençant la cible** avant C3 gelé, (2) toute lecture **sans protocole pré-enregistré**. Le reste est lisible, consommation actée. C5 et C2 légitimes ; **É0/É2 légitimes sur périmètre de fiche** ; É3/É4 attendent C3 ; la réserve reste intouchable. `06` §10 réécrit dans ces termes. | le banc réel n'attend plus que : fin de construction, méthode admise par ÉS, et C3 pour É3/É4 |
| ~~**B3**~~ | ~~**`ADR-000` ne nomme pas le jour de banc d'instrument**~~ — **LEVÉ le 05/08**, addendum à l'ADR : la convention complète y est transcrite, C2 est débloqué. *Réserve : le banc d'instrument n'est porté par aucune garde de code, il tient par discipline.* | `05` en fait une condition d'arrêt explicite → C2 bloqué → C3 → C4 → le banc. Le jour n'est nommé que dans un **commentaire de script**. |
| ~~**B4**~~ | ~~**`journal/registre-des-grandeurs.md` n'existe pas**~~ — **LEVÉ le 05/08** : créé, avec ses états, son format de ligne et l'emplacement du nombre de candidats à déclarer avant le premier calcul | `05` §5 : « aucun calcul ne se fait avant » son existence |
| ~~**B5**~~ | ~~**Les fiches de `03` n'ont pas les lignes qu'`05` exige**~~ — **LEVÉ le 05/08** : les 16 fiches A1-D2 portent `coût` (**estimation a priori, marquée comme telle**, corrigée à la première exécution) et `périmètre minimal` — deux périmètres nommés en tête de registre, **J3** (9-11 déc.) par défaut, **J8** (9-16 déc.) pour les grandeurs d'événements rares, jamais la réserve. *Réserve : le bloc E n'a toujours pas de fiches au format d'`05` — c'est la régularisation C5, déjà en §4.* | — |
| ~~**B6**~~ | ~~**É2 est inerte par construction**~~ — **LEVÉ le 05/08** : le **témoin trivial entre dans le bloc d'É2 dès le départ** (audit I.7, intégré dans `05`), et É4 est débloqué par `ADR-001` — le bloc se remplit donc dès le premier tour | — |
| **B7** | **« mur », « contact », « bande d'étude » ne sont définis nulle part** | plusieurs fiches ne sont pas calculables ; la bande pilote pourtant deux décisions de production |
| ~~**B8**~~ | ~~**La correction de multiplicité n'a ni seuil ni procédure**~~ — **LEVÉ le 05/08** : **Benjamini-Hochberg à 10 %**, collection = **les candidats seuls** — résolutions et symboles sont des conjonctions internes, pas des tests (`ADR-001`, II.3) | échéance tenue : écrit **avant** le premier calcul d'É4 |
| ~~**B9**~~ | ~~**L'IC de Student n'a pas de niveau de confiance écrit**~~ — **LEVÉ le 05/08** : **bilatéral, 95 %, publié** — et il ne décide pas, BH décide (`ADR-001`, II.4) | — |

### Les douze décisions de conception de C9 — recensées le 05/08 dans la spec

**`chantiers/C9-harnais.md` §3 les recense toutes** (D1-D12), avec leur
statut : trois se **transcrivent** du code au lieu de s'inventer (le schéma de
`deep`, la grille `BIN_REL = 2,5e-5`, les états du registre) · six sont
**PROPOSÉ** à l'arbitrage (modèle génératif, mécanismes injectés, place d'ÉS,
ex æquo, promotion de la grille hors archive, alignement du format d'`05` §5) ·
deux sont **réservées à Meddy** (amplitude plausible D6, nombre de candidats
D10) · une exige une **ADR avant le premier É3** (l'échelle la plus fine,
D12). Et la « vérité à injecter » est dissoute : la vérité d'ÉS est le label
d'injection, pas le devenir — ÉS n'attend pas C3.

*(Une version antérieure renvoyait à un « détail complet dans le rapport
d'audit du 05/08 » qui n'y a jamais figuré — référence pendante, constatée en
écrivant la spec.)*

**Tout le reste des rapports d'audit — environ 65 points — est de l'hygiène.**
Renvois vers du code hors dépôt, coût de lecture sous-estimé, quatre façons
d'énumérer les mêmes types, « traversée » contre « transfert ». Ça se corrige au
fil de l'eau et **ça ne bloque rien**.

---

## 2. ⚠️ CE QUI N'EST PAS ÉTABLI, ET QUI A ÉTÉ PRÉSENTÉ COMME TEL

**À lire avant de citer un chiffre de cette session.**

Tout ce qui a été mesuré dans la nuit du 04→05/08/2026 l'a été **sur des
artefacts produits par un pipeline dont l'audit a ensuite montré les défauts**,
et **avec des manifestes de provenance non certifiée**.

| affirmation | son vrai statut |
|---|---|
| « les artefacts sur disque étaient à `DEEP_MS = 10000` » | **SUPPOSÉ par un script**, pas mesuré. Les 93 manifestes portaient tous `provenance_certifiee: false`. |
| « un seul jeu de paramètres dans `hl_book`, `hl_orders`, `hl_fills` » | **conclusion tirée de ces mêmes manifestes non certifiés** — la commande qui « fait foi » blanchissait ce qu'un autre script avait marqué comme incertain |
| les temps de rejeu des trois bras | **mesurés, mais chauffe désactivée** — ils ne décrivent pas le régime de production |
| le dimensionnement du mois | **extrapolé, puis mesuré faux de 41 %** au troisième bras |

**Ce qui, en revanche, est factuel** : tout ce qui porte sur le **texte** des
documents. « `00` ne référence pas `06` », « aucune fiche ne porte de ligne
`coût` », « le registre n'existe pas » — ça se vérifie en ouvrant le fichier, ça
ne dépend d'aucune donnée.

**La règle à retenir** : un constat sur un document est vérifiable en secondes.
Un constat sur la donnée produite cette nuit ne l'est pas, tant que le pipeline
n'a pas été refait et son résultat re-mesuré.

---

## 3. L'état matériel au 05/08/2026, ~02 h 40 — après redémarrage machine

**⚠️ La machine a redémarré à 02:23:09.** Une version antérieure de ce document
affirmait « les processus OS survivent aux coupures de session » — vrai pour une
coupure de session, **faux pour un redémarrage**, et le redémarrage est arrivé.
La construction est morte au jour 2/7 BTC (`20251202`), C5 au 13ᵉ jour-symbole
(`20251214 BTC`). **Les deux ont été relancés à 02:36** — les recettes savent
reprendre : `lot.py` saute les jours complets sur disque, C5 a été relancé sur
les seuls jours restants (14-16), après purge de l'extraction partielle.

| | état | où regarder |
|---|---|---|
| **construction, tranche 1** | relancée 05/08 02:36 — jour 1 sauté (fabriqué avant le reboot, manifeste écrit), reprise au `20251202 BTC`. **~40-55 h** restantes. **Auto-relance au boot depuis 04:26** : tâche `GON-MapDee-construction-reprise` (S4U, démarrage + 2 min), prouvée de bout en bout — verrou d'instance dans le script, refus testé pendant qu'une construction tournait | le log le plus récent de `journal/construction/` (le log du premier lancement, interrompu, est commité tel quel) |
| **C5 étape 1** (distributions) | **12/18 jours-symboles faits et rapatriés** (`journal/c5/`, commités). Les 6 restants (14-16 × BTC/ETH) relancés 02:36 depuis la recette **versionnée** `chantiers/c5_distributions.py` — les sorties s'écrivent dans `chantiers/`, à déplacer vers `journal/c5/` à la fin | `journal/c5/c5-etape1-reprise.log` |
| **C8.3** | **EN COURS depuis 05/08 ~05 h** — protocole pré-enregistré (`chantiers/c8_3_fenetre_simultanee.py`) : l'estimateur de C8.2 sur les 5 jours pleins de capture simultanée. Aucun verdict nouveau : publie la stabilité inter-jours | `journal/c8-3-mesure-20260805.log`, rapport à la fin |
| **C8.2** | **TERMINÉE ET RENDUE le 05/08** — verdict pré-enregistré : **reconstructible, 4/4 cibles** (incohérence 0,06-1,20 %, seuil 50 %). Binance 7-21× plus cohérent qu'Hyperliquid. Rapport : `journal/c8-rapport-20260805.md` · chiffres : `journal/c8-mesure-20260805.json` · recette versionnée : `chantiers/c8_mesure.py` | table de traversée **à jour** : A3 et B3 traversent, D2 garde sa condition propre — 8 traversent, 7 sous condition, 8 non |

## 3 bis. Le socle

**Le pipeline** — restauré depuis git, avec la cadence paramétrable et
l'empreinte par artefact. Il porte encore des défauts identifiés et non
corrigés, dont trois qui n'empêchent pas de construire mais empêchent
d'interpréter : le taux de jointure diffs→statuts se déclare « à remesurer à
chaque heure » et n'est appelé nulle part · des lignes illisibles sont jetées
sans compteur · un compteur de qualité mélange deux causes.

**Les données** — les artefacts d'ancienne génération de `deep` ont été
supprimés (aucun saut possible, aucun mélange) ; **la construction les
refabrique en ce moment** au réglage arrêté, manifeste par artefact. `hl_book`, `hl_orders` et
`hl_fills` restent en place, avec leurs manifestes **non certifiés**.

**Le réglage arrêté** — `DEEP_MS = 250` (mesuré : l'émission sort à chaque photo
du carnet) · `DEEP_BAND = 0.10`, **nappe large** (décision, pas mesure : c'est le
seul choix irréversible de la construction).

**Le coût réel** — mesuré au troisième bras, chauffe désactivée : un jour-symbole
coûte ~53 min contre ~26 à l'ancien réglage. **Le mois complet est autour de
55-60 h**, pas 30. Le disque tient largement.

**Neutralisé** — `_lot2.ps1` refuse de s'exécuter : il construisait la zone
d'extension de la réserve, ce qui fermait définitivement l'unique issue prévue
par `ADR-000`. Conservé intact.

---

## 4. Ce qui peut démarrer sans rien attendre

**Quatre chantiers, pas deux.** Une version antérieure de ce document n'en
listait que deux et concluait « tout le reste attend » — c'était faux, et ça
cachait le chantier que le plan déclare primordial.

**C0 — la littérature.** Ce que la microstructure et la surveillance de marché
définissent réellement comme leurre, liquidité cachée, absorption. Aucune donnée
touchée. C'est ce qui alimente les définitions manquantes de **B7**.

**C8 — ce qui traverse vers Binance.** Papier pour l'essentiel. Et la question
qui commande tout le produit : la décomposition **exécuté / retiré / ajouté**
est-elle reconstructible côté Binance ? Si non, le produit change de nature — et
il vaut mieux l'apprendre en semaine 1 qu'en P7.

**C5 — les protagonistes.** **Déjà lancé**, protocole pré-enregistré dans
`chantiers/C5-protagonistes.md`. Réserve à porter : ses six grandeurs sont
décrites dans le protocole mais **n'ont pas de fiche au format d'`05`**, ce que
`06` interdit. À régulariser avant d'en tirer un résultat.

**C9 — le harnais.** Spécifié le 05/08 (`chantiers/C9-harnais.md`), décisions
D3/D4/D8/D9/D10 **validées par Meddy le jour même**, et **le code existe** :
paquet `harnais/` — préflight (chaque contrôle lève, et la suite prouve qu'il
peut lever), générateur synthétique (schéma `deep` transcrit, vérité séparée,
déterminisme octet par octet), registre (ajout seul), épreuves É0/É1/É2
mécaniques + refus explicites d'É3 (D12 ouverte) et É4 (C3 non gelé), grille
promue hors archive (D2), garde-fous d'`05` §3, stats du banc (Spearman
partiel, Student, BH). **54/54 tests**, dont grille et schéma vérifiés bit à
bit contre un artefact `deep` réel. La déclaration D10 est au registre (16
candidats + témoin T0 hors compte, fiche dans `03`).
**ÉS EST RENDUE le 05/08** (`journal/es-rapport-20260805.md`) — quatre
itérations de méthode, chacune tranchée par son bras nul, verdict final sur
graines neuves : **absorption ADMIS (plancher 0,5×), recharge ADMIS (1,0×),
leurre ÉCARTÉ (8,0× > barre 2,0 d'ADR-004)** — aucun négatif leurre ne sera
interprétable avec cette méthode. Planchers au registre. Transverses :
l'estimateur partiel dérive en ~k/n (règle à porter dans `05` : n
observations/jour ≥ 100 × taille du bloc, avant le premier É4 réel) ; la
puissance dit **d ≳ 1,2 détectable sur 8 jours, 0,75 avec la tranche 2**.
**LE PREMIER TOUR DE BANC RÉEL EST RENDU — 06/08, 04 h 22**
(`journal/e0-rapport-20260806.md`) : sur 727 059 observations réelles
alignées (J3 complet), **É0 : zéro doublon parmi les huit mesurables** — la
fusion 300 → 16 tient ; **É2 : les huit passent sous 0,50 contre le témoin**
(A1 à 0,025, C1 le plus proche à 0,416) — personne ne redit la masse brute ;
É1 : huit admissibles, huit mesures de dégradation dues. **Les huit sont en
É3, refusées proprement** : la frontière du banc est désormais le rejeu
événementiel + l'ADR D12 + le gel de C3. Diagnostic clé publié avant
verdict : l'intrication |Δmid| est négligeable partout SAUF B5 (−0,69,
définitionnel — son É4 devra le traiter, c'est écrit d'avance).

**LE BANC EST COMPLET ET CHARGÉ depuis le 05/08 ~05 h 30** : la boucle
existe (`harnais/boucle.py` — ordre d'`05`, É0 avec départage par coût,
refus propres, 59 tests), la règle k/n est dans `05` §4 **et** dans le code,
et **les 16 candidats sont déposés au registre** (préflight passé, hash
inscrit), chacun en attente des données de son périmètre. Ce qui manque au
banc n'est plus du banc : les artefacts J3/J8 (construction, ~2 j), C3 pour
É3/É4 (gel après C2 sur le jour de banc), le rejeu événementiel + ADR D12
pour É3, ~~et les extracteurs de séries~~ — **FAITS le 05/08 ~06 h**
(`harnais/extracteurs.py`, 64 tests) : dix séries extractibles (A1, A4, B1,
B2, B5, C1, C2, C3, D1, T0), sept absences motivées (A2/B4 → B7, A3/B3/D2 →
flux exécuté à brancher sur les transactions agrégées — interface prête,
A5 → calibration, A6 → coût Hawkes). Lecture en flux, un jour réel ne se
charge jamais entier. Dès que la construction livre J3 : brancher le flux
exécuté, puis `boucle.tour(series)` — É0 tournera pour de vrai.

Tout le reste attend soit la construction, soit les définitions.

---

## 4 bis. La file de reprise — dans cet ordre

> **ORDRE PERMANENT (Meddy, 05/08 ~06 h 30 : « continue jusqu'au signal J3 et
> tire É0 »)** : un moniteur persistant surveille la livraison des jours
> `deep`. Au signal « J3 COMPLET » (les 6 jour-symboles 09-11 × BTC/ETH avec
> manifestes) : `python -m harnais.e0_reel` — préflight, extraction,
> `boucle.tour` — puis relire la sortie, commiter le registre, rapporter.
> En cas d'ÉCHEC de construction : diagnostiquer, réparer, relancer
> (`construire_decembre.ps1` est idempotent et verrouillé).

1. ~~**Rapport C8.2** + table de traversée~~ — **FAIT le 05/08** :
   `journal/c8-rapport-20260805.md`, A3 et B3 traversent, D2 garde sa
   condition propre ;
2. ~~**B5** : compléter les fiches de `03`~~ — **FAIT le 05/08** ;
3. ~~**premier jour-symbole terminé** → corriger `06` §8~~ — **FAIT le 05/08**
   sur le jour 1 (~72 min chauffe active, poste par poste). Reste ouvert dans
   `06` §8 : le poste écriture des tables et `hl_book` (premiers jours
   phase `all`, 08-16) et la chauffe isolée ;
4. **fin de C5 étape 1** → déplacer les 6 dernières sorties de `chantiers/`
   vers `journal/c5/`, puis calculer les garde-fous §6 **sur les 18
   jours-symboles ensemble** (la reprise ne les imprime que sur 14-16) — aucun
   classement sans eux ;
5. ~~**`ADR-002`**~~ — **ACCEPTÉE le 05/08** sur délégation (B2 levé) ; dans
   la même délégation : **`ADR-004`** (amplitude plausible = 2,0× le
   voisinage) et **`ADR-003`** (structure de la cible fixée, gel après C2 sur
   le jour de banc) ;
6. ~~**C0** et la **spécification de C9**~~ — **OUVERTS le 05/08, livrables
   rendus** : `chantiers/C9-harnais.md` (spec de bout en bout — les douze
   décisions recensées : D1/D2/D7 transcrites du code, D3/D4/D8/D9 en
   **PROPOSÉ**, D6/D10 **réservées à Meddy**, D12 exige une ADR avant É3) et
   `chantiers/C0-litterature.md` (synthèse d'orientation + formes proposées
   pour les trois définitions de B7, constantes à lire sur le jour de banc).
   **En attente d'arbitrage : D3, D4, D8, D9, D10 et les trois formes de B7.**
   La lecture des sources de C0 reste à faire — la synthèse est de mémoire,
   marquée comme telle.

## 4 ter. LES DETTES OUVERTES — la table unique (05/08/2026, ~15 h)

> Inventaire exigé par Meddy (« la dette réelle est-elle dans les
> documents ? »). Réponse honnête : l'essentiel l'était, dispersé ; deux
> dettes ne vivaient que dans la conversation. **Cette table est désormais
> l'endroit** : une dette s'y ajoute quand on la découvre, s'y raye quand on
> la ferme — jamais en silence.

| dette | trace | ce qui la ferme |
|---|---|---|
| **corrections du lanceur en attente de fin de run** — en-tête « 24 jours » (c'est 16), message « ECHEC 08-31 » (c'est 08-16), `$DEPOT` en dur (→ `$PSScriptRoot`), préflight non appelé (`sale=True` constate sans bloquer), **et le repointage hors `_recupere` — se ferme DANS LA MÊME FENÊTRE que l'étape 3 de C10 (renvoi croisé)** | audit externe du 05-06/08, vérifié ligne à ligne | éditer `construire_decembre.ps1` **au premier arrêt naturel du run** — jamais pendant (règle payée 10 h ce matin) |
| ~~**`_recupere/construit/` est une dépendance d'exécution dure**~~ — **TRANCHÉ le 06/08** (délégation) : `00` §7 corrigé (l'état transitoire est dit, `construit/` redevient auditable) ET la promotion est décidée — chantier **C10** (`chantiers/C10-promotion-instrument.md`), jamais sous un run, après la tranche 1, test de reproductibilité sha256 AVANT tout déplacement | `00` §7 + C10 | exécuter C10 après la tranche 1 |
| **C6 (incertitude) n'est pas spécifié** — et `06` §9 interdit la tranche 2 avant lui ; l'oublier figerait la réserve par défaut | nulle part avant cette table | spécifier C6 avant la fin de tranche 1 + arbitrage tranche 2 |
| **manifestes `hl_*` anciens non certifiés** — le préflight du harnais les refusera au premier calcul qui les touche | ETAT §3 bis (sans l'implication préflight) | recertifier ou trancher par ADR avant tout calcul sur `hl_*` |
| **le témoin T0 n'existe que sur J3** — les candidats J8 (D1) attendront à É2 (refus propre, garde de longueur) | commentaire `e0_reel.py` + test F1 | extraire T0 sur J8 quand J8 livré |
| **extracteurs absents** : A2/B4 (→ B7), A3/B3/D2 (→ flux exécuté, interface prête), A5 (calibration), A6 (coût) | `harnais/extracteurs.py::ABSENTS` + ETAT §4 | B7 (jour de banc) · branchement transactions agrégées · décisions dédiées |
| **intrication mécanique séries ↔ \|Δmid\|** — résiduel après marge intérieure, publié au tir | audit F9 + diagnostics `e0_reel` | lecture obligatoire au premier É4 (la cible EST le déplacement) |
| **puissance : 8 jours ne voient que d ≳ 1,2** | rapport ÉS §3 | arbitrage tranche 2 (chez Meddy) |
| **typage annulé/mangé/rechargé** — 2ᵉ passe sur le jour de banc, protocole séparé à écrire | `C2-observation.md` §4 | écrire ce protocole après C2, avant la passe |
| **les mesures de dégradation dues avant É4** — la question É1 « survit-elle à la dégradation ? » n'élimine pas mais **exige une mesure** : due pour chaque ⚠️ de la vague 1 ET pour les 7 familles à ligne écrite de la vague 2 (audit du 06/08) | `05` §4 + table C0 §5 quater | mesurer sur le régime d'affichage réel, avant le premier É4 de chaque candidat concerné |
| **le voisinage du mur est en paliers, pas en distance** — `bs` diffère par symbole (2 contre 0,1) : ±20 paliers ne couvrent pas la même distance relative, ce qui pollue la comparaison des constantes M entre symboles. Reclassée de « micro-dette générateur » à dette de **production** le 06/08 : elle vient d'affecter une constante mesurée de B7 (audit). Le facteur 3 BTC/ETH est probablement réel (nice() ne peut introduire que ~×2 sur la largeur), mais ça ne se dira proprement qu'après correction | rapports C2 + audit du 06/08 | **2ᵉ passe C2** : voisinage exprimé en distance relative au mid, pas en nombre de paliers — une ligne |
| **la règle de graines d'ÉS** — `GRAINES_CALIB = [:16]` en dur dans v5, alors que le 16 est précisément la taille diagnostiquée instable pour le centrage (absorption, v5) ; la constante attend intacte le prochain mécanisme centré | audit du 06/08 | avant la prochaine campagne ÉS : taille de calibration justifiée par la variance inter-lots mesurée, pas héritée |
| micro-dettes assumées : `n` du générateur non décrémenté sur annulation partielle · double extraction des jours J3 partagés dans `e0_reel` | cette table | au premier besoin réel, pas avant |

## 5. Les décisions qui n'appartiennent pas au co-chercheur

* le troisième symbole
* ~~le sort de l'enregistreur de production~~ — **tranché et RÉPARÉ le 05/08**
  (C8.4) : diagnostic rendu (`journal/c8-4-diagnostic-enregistreur-20260805.md`),
  priorités corrigées, **S4U appliqué et prouvé** — la capture survit désormais
  aux redémarrages sans session ouverte (retour ≤ 5 min)
* **la cible et le devenir, une fois rédigés** — ce sont les définitions du
  produit
* les seuils des critères d'arrêt
* toute dépense

---

## 6. L'avertissement de méthode, tiré de cette session

Deux fautes ont été commises cette nuit, et elles se reproduiront si rien ne les
contient :

**Vérifier par `grep` n'est pas vérifier.** Un `grep` de termes montre ce qui
reste, **jamais ce qui manque**. Un fichier non commité a été supprimé après une
vérification de ce type ; trois de ses apports ont été perdus, et il n'y avait
aucun filet git. **Commiter avant de modifier** rend la vérification mécanique
au lieu d'être une impression.

**Une règle écrite en prose n'arrête personne.** Ce qui a réellement bloqué une
action cette nuit était du code qui lève. Ce qui était écrit en gras dans un
document lu quelques minutes plus tôt n'a rien bloqué. **Toute règle qui compte
doit devenir quelque chose qui échoue bruyamment.**
