# État — où en est le projet, et par quoi commencer

> **Document de passation.** Il est la mémoire du projet entre deux sessions.
> Une session qui ouvre ce dépôt lit `00_Prompt_MapDee.md`, puis **ce fichier**,
> avant toute autre chose.
>
> Il se réécrit à chaque changement d'état. L'historique est dans git.

---

## 1. LES BLOCAGES — sept restants sur neuf

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
| **B1** | **La métrique d'É4 n'existe nulle part.** `05` dit ce qu'elle mesure — « le gain par-dessus les candidats déjà retenus » — **sans jamais nommer la quantité**. L'AUC est interdite, toute grandeur économique aussi. Il ne reste rien. | **É4 n'est pas calculable**, donc la boucle n'a pas d'épreuve terminale, donc É2 ne remplit jamais son bloc de référence, donc **rien ne peut être retenu**. Le sommet du harnais est indéfini. → `decisions/ADR-001`, **PROPOSÉ, en attente d'arbitrage** |
| **B2** | **Trois documents donnent trois réponses à « que puis-je lancer ? »** | `05` §2 dit rien · `05` §9 et `06` V1 disent jusqu'à É2 · `06` V2 dit jusqu'à É3. **La bonne réponse est « rien »** : É0 et É2 touchent du marché, et aucun jour d'exploration ne s'ouvre avant C3 gelé. ⚠️ **Cette réponse est elle-même contestée** (audit du 05/08, I.1) : lue littéralement, elle interdit C5 — lancé — **et C2, qui doit précéder C3**. Arbitrage ouvert : `decisions/ADR-002`. |
| ~~**B3**~~ | ~~**`ADR-000` ne nomme pas le jour de banc d'instrument**~~ — **LEVÉ le 05/08**, addendum à l'ADR : la convention complète y est transcrite, C2 est débloqué. *Réserve : le banc d'instrument n'est porté par aucune garde de code, il tient par discipline.* | `05` en fait une condition d'arrêt explicite → C2 bloqué → C3 → C4 → le banc. Le jour n'est nommé que dans un **commentaire de script**. |
| ~~**B4**~~ | ~~**`journal/registre-des-grandeurs.md` n'existe pas**~~ — **LEVÉ le 05/08** : créé, avec ses états, son format de ligne et l'emplacement du nombre de candidats à déclarer avant le premier calcul | `05` §5 : « aucun calcul ne se fait avant » son existence |
| **B5** | **Les fiches de `03` n'ont pas les lignes qu'`05` exige** | il en manque **deux**, pas une : `coût` (règle de départage d'É0) et le **périmètre minimal**, qu'`05` exige déclaré dans la fiche avant le calcul |
| **B6** | **É2 est inerte par construction** | son bloc de référence part vide et ne se remplit qu'après É4, lui-même bloqué par B1 |
| **B7** | **« mur », « contact », « bande d'étude » ne sont définis nulle part** | plusieurs fiches ne sont pas calculables ; la bande pilote pourtant deux décisions de production |
| **B8** | **La correction de multiplicité n'a ni seuil ni procédure** | l'interdit de « changer un seuil après résultat » **ne l'empêche pas** — le changement par ADR avec repassage est prévu (`01` §4, `05` §10). **L'échéance réelle est avant le premier calcul d'É4** : urgent, pas condamné (correction du 05/08). Le risque était de plus dimensionné sur « une soixantaine » de candidats ; `03` en porte **29**. |
| **B9** | **L'IC de Student n'a pas de niveau de confiance écrit** | É4 n'est pas applicable de façon reproductible → traité par `ADR-001` |

### Et douze décisions de conception que C9 exigerait d'inventer

Le harnais — **le chantier que `06` déclare primordial** — n'est pas
constructible en l'état. Quelqu'un qui n'a pas participé à sa conception devrait
inventer, au minimum : le schéma que le générateur doit émettre (il ne vit que
dans une archive déclarée sans autorité) · le modèle génératif du carnet · la
constante de grille, écrite dans aucun document · **la vérité à injecter — qui
est le devenir, lequel n'a pas de définition opératoire** · l'amplitude plausible
du phénomène, sans laquelle le critère d'arrêt le plus important est
inapplicable · le vocabulaire d'états du registre, dont deux schémas concurrents
coexistent · et la place d'ÉS, absent de la liste des épreuves de C9.

**Détail complet dans le rapport d'audit du 05/08.** Aucun de ces points n'est un
défaut de conception : ce sont des décisions qui n'ont simplement pas encore été
prises.

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

## 3. L'état matériel au 05/08/2026

**Le pipeline** — restauré depuis git, avec la cadence paramétrable et
l'empreinte par artefact. Il porte encore des défauts identifiés et non
corrigés, dont trois qui n'empêchent pas de construire mais empêchent
d'interpréter : le taux de jointure diffs→statuts se déclare « à remesurer à
chaque heure » et n'est appelé nulle part · des lignes illisibles sont jetées
sans compteur · un compteur de qualité mélange deux causes.

**Les données** — `deep/parts/` est **vide** : les artefacts d'ancienne
génération ont été supprimés, donc plus aucun jour ne peut être « sauté » et
plus aucun mélange de générations n'est possible. `hl_book`, `hl_orders` et
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

**C9 — le harnais.** `06` le déclare **le chantier primordial**, et il s'écrit
**pendant** la construction : les quatre pièces se développent et se testent sur
carnet fabriqué, où la vérité est connue. Elles ne dépendent d'aucune donnée
pour être écrites — seulement pour tourner.
⚠️ Mais voir §1 : douze décisions de conception restent à prendre, et **B1** doit
être arbitré avant que le sommet du harnais ait un sens.

Tout le reste attend soit la construction, soit les définitions.

---

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
