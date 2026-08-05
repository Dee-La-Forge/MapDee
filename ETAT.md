# État — où en est le projet, et par quoi commencer

> **Document de passation.** Il est la mémoire du projet entre deux sessions.
> Une session qui ouvre ce dépôt lit `00_Prompt_MapDee.md`, puis **ce fichier**,
> avant toute autre chose.
>
> Il se réécrit à chaque changement d'état. L'historique est dans git.

---

## 1. LES BLOCAGES — deux restants sur neuf : B2 (arbitrage de Meddy) et B7 (définitions)

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
| **B2** | **Trois documents donnent trois réponses à « que puis-je lancer ? »** | `05` §2 dit rien · `05` §9 et `06` V1 disent jusqu'à É2 · `06` V2 dit jusqu'à É3. **La bonne réponse est « rien »** : É0 et É2 touchent du marché, et aucun jour d'exploration ne s'ouvre avant C3 gelé. ⚠️ **Cette réponse est elle-même contestée** (audit du 05/08, I.1) : lue littéralement, elle interdit C5 — lancé — **et C2, qui doit précéder C3**. Arbitrage ouvert : `decisions/ADR-002`. |
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
| **construction, tranche 1** | relancée 05/08 02:36 — jour 1 sauté (fabriqué avant le reboot, manifeste écrit), reprise au `20251202 BTC`. **~40-55 h** restantes | le log le plus récent de `journal/construction/` (le log du premier lancement, interrompu, est commité tel quel) |
| **C5 étape 1** (distributions) | **12/18 jours-symboles faits et rapatriés** (`journal/c5/`, commités). Les 6 restants (14-16 × BTC/ETH) relancés 02:36 depuis la recette **versionnée** `chantiers/c5_distributions.py` — les sorties s'écrivent dans `chantiers/`, à déplacer vers `journal/c5/` à la fin | `journal/c5/c5-etape1-reprise.log` |
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

**C9 — le harnais.** `06` le déclare **le chantier primordial**. **Spécifié de
bout en bout le 05/08** : `chantiers/C9-harnais.md` — architecture (préflight
en tête), contrats des quatre pièces, seuils transcrits d'`05`/`ADR-001`, les
douze décisions recensées avec leur statut (§1). La construction du code peut
démarrer sur P0/P1/P2 dès l'arbitrage des PROPOSÉ.

Tout le reste attend soit la construction, soit les définitions.

---

## 4 bis. La file de reprise — dans cet ordre

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
5. **`ADR-002`** — attend **l'arbitrage de Meddy** (B2) ;
6. ~~**C0** et la **spécification de C9**~~ — **OUVERTS le 05/08, livrables
   rendus** : `chantiers/C9-harnais.md` (spec de bout en bout — les douze
   décisions recensées : D1/D2/D7 transcrites du code, D3/D4/D8/D9 en
   **PROPOSÉ**, D6/D10 **réservées à Meddy**, D12 exige une ADR avant É3) et
   `chantiers/C0-litterature.md` (synthèse d'orientation + formes proposées
   pour les trois définitions de B7, constantes à lire sur le jour de banc).
   **En attente d'arbitrage : D3, D4, D8, D9, D10 et les trois formes de B7.**
   La lecture des sources de C0 reste à faire — la synthèse est de mémoire,
   marquée comme telle.

## 5. Les décisions qui n'appartiennent pas au co-chercheur

* le troisième symbole
* le sort de l'enregistreur de production — il se dégrade, et chaque jour de
  panne est un jour de fenêtre de traversée perdu définitivement
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
