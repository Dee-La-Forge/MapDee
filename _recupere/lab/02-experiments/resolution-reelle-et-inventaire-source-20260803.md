# La résolution RÉELLE de Hyperliquid, et ce que la source contient vraiment

_03/08/2026, 10 h 45. Deux mesures et un inventaire. Consigné parce que les
deux corrigent une affirmation que j'avais faite et que le dossier portait._

---

## 1. La granularité de Hyperliquid est le BLOC, pas la nanoseconde

Le jeu OPEN BOOK horodate à la nanoseconde, et c'est **réel** : 100 % des lignes
ont une partie sous la milliseconde non nulle. On pourrait croire qu'on dispose
d'une résolution nanoseconde.

**On ne l'a pas, et personne ne l'aura**, parce que la bourse ne produit pas
d'événements à cette échelle. Mesuré sur 7 fichiers horaires, 4 jours, 2
symboles, des heures calmes et des heures chargées :

| fichier | événements | instants DISTINCTS | év./inst. | p10 | méd. | p90 |
|---|---|---|---|---|---|---|
| 01/12 btc 03 h | 4 082 070 | 37 422 | 109 | 54 | **87** | 151 |
| 01/12 btc 15 h | 8 765 379 | 37 834 | 232 | 53 | **84** | 154 |
| 03/12 eth 09 h | 1 396 714 | 36 213 | 39 | 54 | **89** | 158 |
| 05/12 btc 20 h | 3 956 934 | 36 405 | 109 | 55 | **90** | 154 |
| 07/12 eth 12 h | 895 136 | 35 890 | 25 | 55 | **91** | 155 |
| 08/12 btc 01 h | 5 206 251 | 36 984 | 141 | 54 | **88** | 153 |
| 08/12 btc 18 h | 4 797 118 | 37 783 | 127 | 54 | **88** | 147 |

**La colonne qui prouve tout est la troisième.** Le nombre d'instants distincts
ne bouge pas : 35 890 à 37 834 par heure, que la place traite 895 136
événements ou 8 765 379. **Dix fois plus d'activité, le même nombre
d'instants.** C'est la signature d'une cadence FIXE, indépendante du volume.

Hyperliquid produit **~10,2 blocs par seconde**. Tous les événements d'un bloc
partagent exactement l'horodatage du bloc — 112 événements par instant en
moyenne. La médiane entre deux blocs est de **87 ms**, l'intervalle
interdécile de 54 à 155 ms.

### Ce que ça implique

* **Rien à acquérir.** Aucun fournisseur ne peut descendre sous 87 ms : c'est la
  bourse qui est ainsi faite, pas la collecte.
* **La troncature à la milliseconde du pipeline ne perd rien**
  (`build_openbook_day.py:250`, `ts // 1_000_000`). On ne sépare pas deux
  événements distants de 87 ms en gardant les nanosecondes.
* **Mais notre carnet est 10× trop grossier pour la source.** Il est
  reconstruit à ~930 ms de cadence médiane (`SNAP_MS = 1000`,
  `SNAP_MIN_MS = 250`) là où la donnée permet 87 ms. **C'est un choix, pas une
  limite**, et il coûte une question précise : *le mur est-il apparu AVANT que
  le prix bouge, ou APRÈS ?* À 930 ms, un décalage de 200 ms est invisible —
  et sans lui on ne distingue pas une manipulation d'une réaction défensive.
  C'est le cœur de l'hypothèse directionnelle de l'ADR-021.

---

## 2. Inventaire de la source — ce qu'on a, ce qu'on n'a pas

Le README du jeu (Zenodo 18184441, DOI 10.5281/zenodo.18184441) liste :

| archive | taille | sur disque |
|---|---|---|
| `btc_orders_202512.tar.xz` | 19 Go | **oui** |
| `eth_orders_202512.tar.xz` | 12 Go | **oui** |
| `book_diffs_202512.tar` | 50 Go | **oui** (BTC+ETH+SOL entrelacés) |
| `trades_2025_12.tar` | 6,7 Go | **oui** |
| `mapdir.tar.xz` | 10 Mo | **oui** |
| `sol_orders_202512.tar.xz` | 6,3 Go | en cours |
| `btc_rejected_202512.tar.xz` | **46 Go** | non |
| `eth_rejected_202512.tar.xz` | **24 Go** | non |
| `sol_rejected_202512.tar.xz` | 8,5 Go | non |
| `trades_2025_10.tar` | 10 Go | non |
| `trades_2025_11.tar` | 8,9 Go | non |
| `trades_2026_01.tar` | 3,9 Go | non |

**107 Go du même dépôt qu'on n'avait pas pris.** Les transactions couvrent
octobre 2025 à janvier 2026, pas seulement décembre, et **tous les coins** —
250+ contrats perpétuels, pas trois.

### Correction : SOL n'est PAS inexploitable

J'ai écrit le 03/08 à 10 h que SOL n'avait « pas ses statuts d'ordres » et
était donc inutilisable. **Faux.** `sol_orders_202512.tar.xz` existe (6,3 Go).
J'ai conclu de son absence sur NOTRE disque à son absence dans le jeu.

Conséquence : **un troisième symbole certifiant est disponible**, ce qui n'est
pas rien pour un protocole dont les barres se comptent par symbole.

### Priorité retenue, et pourquoi

1. **`sol_orders` (6,3 Go)** — un symbole de plus, immédiatement exploitable,
   le meilleur rapport valeur/place du lot.
2. **`btc_rejected` + `eth_rejected` (70 Go)** — les ordres rejetés
   n'atteignent **jamais le carnet visible** (README §Raw Book Diffs). Ils ne
   servent donc pas à l'ADR-021, qui travaille sur la configuration visible.
   Leur valeur est sur l'INTENTION : un ordre qu'un acteur a voulu placer et
   que le moteur a refusé dit quelque chose que le résultat ne dit pas.
   À prendre quand la place le permet.
3. Le reste (SOL rejetés, mois de transactions supplémentaires) — plus tard.

### Contrainte de place

E: avait **68 Go libres** pour 107 Go manquants. Libérés le 03/08 à 10 h 40 :
les extractions horaires des jours **01-07, gelés donc jamais reconstruits**
(21 Go), plus des doublons et des sondes. **89 Go disponibles.**
`work/20251208` est CONSERVÉ : il sert de chauffe au jour 09.

---

## 3. Ce que ce jeu vaut, mesuré contre l'alternative essayée

| | 0xArchive (02/08) | OPEN BOOK |
|---|---|---|
| trous | **12 %**, 9 coupures, la plus longue 56 min | aucun déclaré, aucun rencontré |
| reprise | 669 lignes sur 6,4 M attendues | — |
| jointure carnet → temps | — | **100,00 %** (3 manquants sur 1 805 630) |
| carnets croisés | — | **0** sur 7 jours × 2 symboles |
| parquets produits | — | 193, **0 tronqué** |

La curation est réelle : trois flux alignés, format binaire documenté au champ
près, tables de correspondance, lecteur de référence, et un article associé —
*« The "Neutrinos" of the Order Book: Pervasive, Weakly Interacting Order Flow
and its Consequences »*.

**Ce que je ne peux PAS affirmer** : si Hyperliquid publie l'équivalent par
ailleurs. Je ne l'ai pas vérifié, et je ne l'écris pas de mémoire.
