# Ce qu'il faut savoir sur la donnée, et ce qu'il faut re-mesurer

> **AUCUN CHIFFRE DE CE DOCUMENT N'EST UN ACQUIS.** MapDee est une refonte :
> on reconstruit l'instrument, donc tout ce qui a été mesuré à travers
> l'ancien est à refaire. Ce fichier n'est pas une table de vérités, c'est
> **une liste de ce qu'il faut mesurer, avec ce qu'on avait trouvé avant**.
>
> Trois statuts, et la ligne n'est pas arbitraire :
>
> | marque | statut |
> |---|---|
> | **SOURCE** | propriété de l'archive ou de la place elle-même — volumétrie, couverture, schéma binaire, cadence de bloc. Ne dépend pas de notre pipeline. **Tient**, et se re-vérifie en minutes. |
> | **À RE-MESURER** | mesuré à travers un instrument qu'on reconstruit — cadences de reconstruction, paliers par photo, couvertures, effets de paramètres. **Le chiffre ne vaut rien**, il indique seulement où regarder. |
> | **PIÈGE** | un mécanisme qui a coûté du temps. **Sa valeur est le mécanisme, pas le chiffre.** « L'agrégat par côté doit être séparé » tient ; le décompte associé ne tient pas. |
>
> Deux démonstrations tombées le 04/08 : « 3 845 paliers par photo » n'est pas
> une constante (3 571 un autre jour, 3 204 à chauffe réduite), et la chauffe
> de 8 h ne fait pas ce que tout le dossier lui prêtait — voir §8.
>
> **Il ne contient aucune conclusion sur le marché** — pas d'AUC, pas de rho,
> pas de gain, pas de fréquence d'événement. Ces grandeurs-là n'ont aucune
> valeur probante et ne survivent pas à la refonte.

---

## 1. La source

Jeu **OPEN BOOK**, Hyperliquid, Zenodo `10.5281/zenodo.18184441`, **CC BY 4.0 —
attribution obligatoire** dans toute publication ou figure diffusée.

```bibtex
@dataset{hyperliquid_order_flow_2026,
  title  = {An Open Book: Level 4 Order Book Data from the Hyperliquid Exchange},
  author = {Albers, Jakob and Cucuringu, Mihai and Howison, Sam and
            Shestopaloff, Alexander Y.},
  year   = {2026}, publisher = {Zenodo}, doi = {10.5281/zenodo.18184441}
}
```

Article joint : *« The "Neutrinos" of the Order Book: Pervasive, Weakly
Interacting Order Flow and its Consequences »* — il porte sur les ordres
**rejetés**.

### Ce qui est sur disque (`data/l4/openbook-202512/`, 203 Go mesurés)

| archive | taille | couverture |
|---|---|---|
| `book_diffs_202512.tar` | 46 Gio | **Déc. 1-31**, 744 fichiers horaires, BTC+ETH+SOL entrelacés, **aucun trou** |
| `{btc,eth,sol}_orders_202512.tar.xz` | 35 Gio | Déc. 1-31, binaire packé 54 octets |
| `{btc,eth,sol}_rejected_202512.tar.xz` | 73 Gio | **89 % des soumissions — jamais ouverts** |
| `trades_2025_10 … 2026_01` | 27 Gio | **Oct. 2025 → Jan. 2026**, 250+ coins, les **deux** contreparties nommées |
| `mapdir.tar.xz` | 10 Mo | 328 456 adresses, 18 statuts |

**Le carnet et les statuts ne couvrent que décembre 2025.** Seules les
transactions vont d'octobre à janvier. Vérifié dans le `README.md` du jeu, le
04/08/2026. Il n'existe donc **pas d'autre mois de carnet** : toute planification
qui suppose « on prendra un autre mois » est fausse.

**Le champ qui change tout** : `timestampDiff` donne la durée de vie exacte de
chaque ordre en millisecondes, sans reconstruction. Schéma complet dans
`data/l4/openbook-202512/SCHEMA.md`.

---

## 2. La granularité réelle d'Hyperliquid — le BLOC

Mesuré sur 7 fichiers horaires, 4 jours, 2 symboles, heures calmes et chargées :

| | |
|---|---|
| blocs par seconde | **~10,2** |
| `dt` médian entre deux instants | **87 ms** (interdécile 54-155 ms) |
| événements par instant | 25 à 232 selon l'heure |
| **instants distincts par heure** | **35 890 à 37 834** |

**La colonne qui prouve tout est la dernière** : le nombre d'instants ne bouge
pas quand la place traite 895 136 événements ou 8 765 379. **Dix fois plus
d'activité, le même nombre d'instants.** C'est une cadence fixe, indépendante du
volume.

Deux conséquences :

* **Rien à acquérir sous 87 ms.** Aucun fournisseur ne peut descendre plus bas :
  c'est la bourse qui est ainsi faite, pas la collecte.
* **La troncature à la milliseconde ne perd rien** (`ts // 1_000_000`).

---

## 3. Ce que produit notre reconstruction

Chiffres du 20251208 BTC, mesurés le 04/08/2026 (chauffe 0 h, `--phase deep`).

| table | cadence | volume |
|---|---|---|
| `hl_book` (20 paliers/côté) | **122 192 photos/jour** — médiane ~1 002 ms, moyenne 718 ms | 2,44 M lignes |
| `deep` (nappe large) | **paramétrable** — voir §4 | voir §4 |
| `hl_orders` | événementiel | ~94 M ordres/jour |

Constantes de la reconstruction : `SNAP_MS = 1000` (battement), `SNAP_MIN_MS =
250` (**plancher dur**), `LEVELS = 20`, `BIN_REL = 2,5e-5`.

**La grille de palier** : `k = ⌊prix / nice(mid × BIN_REL)⌋`, `nice` arrondissant
en 1/2/5/10. Relevé sur l'enregistreur en fonctionnement le 04/08 : **`bs` = 2 $
pour BTC à 64 232 $**, 0,05 $ pour ETH à 1 875 $.

---

## 4. La cadence de `deep` — mesurée, et son plafond expliqué

**L'émission de `deep` est imbriquée sous la porte de `hl_book`** (`jour.py`,
la condition `dt < SNAP_MIN_MS …` précède l'émission profonde). Elle ne peut
donc sortir qu'aux instants où `hl_book` prend déjà une photo.

Conséquence, longtemps observée sans être expliquée : à `DEEP_MS = 10 000`, le
`dt` médian de `deep` vaut **10 366 ms**, et exactement 10 000 dans 0,15 % des
cas. **L'excédent de 366 ms est l'attente de la photo suivante** (demi-période
mesurée 359 ms). Concordance à 2 %.

### Mesure du 04/08/2026 — deux bras, même jour, même machine

| | `DEEP_MS=10000` / `BAND=0,10` | `DEEP_MS=250` / `BAND=0,02` |
|---|---|---|
| temps de rejeu | 1 041 s | 1 444 s — **+39 %** |
| photos `deep` | 8 294 | **122 192** |
| lignes | 23,9 M | 163,7 M |
| poids | 56,1 Mo | 309,5 Mo |

**`deep_snaps` = `book_snaps` = 122 192, exactement.** À `DEEP_MS ≤ 250`, `deep`
émet à **chaque photo de `hl_book`**. Descendre plus bas ne donne rien de plus :
il faut toucher `SNAP_MIN_MS`, qui porte sa propre justification.

Réserve : mesuré **chauffe à 0 h**. En production la chauffe rejoue 8 h de diffs
sans émettre, donc le surcoût d'émission est le même en absolu et la pénalité
relative est plus faible. Non mesuré.

---

## 5. La nappe `deep` — où est la masse

Mesuré le 04/08 sur `deep_20251216_BTC.parquet`, 3,5 M lignes échantillonnées,
911 photos, `bs` = 2 $ :

| bande gardée | paliers/photo | % des lignes | % de la masse |
|---|---|---|---|
| ±0,80 % | 638 | 16,6 % | 47,2 % |
| ±1,5 % | 1 134 | 29,5 % | 59,0 % |
| ±2,0 % | 1 467 | 38,2 % | 63,4 % |
| **±10 % (`DEEP_BAND` par défaut)** | **3 845** | **100 %** | **100 %** |

**83,4 % des lignes archivées sont au-delà de 0,80 % du mid.** Réduire la bande
est le **seul choix irréversible** d'une construction : on rétrécit toujours à
la lecture, on n'élargit jamais sans tout refaire.

---

## 6. Effet mesuré d'un carnet fin — sur un AUTRE instrument

> ⚠️ Mesuré sur le dataset Kaggle `hyperliquid-btc-high-frequency-microstructure`
> (BTC, mai 2026, 537 ms) contre une reconstruction à 62,6 s. **Ce n'est pas
> notre instrument** — notre `hl_book` de décembre est déjà à ~1 002 ms, soit
> 62× plus fin que le bras grossier de cette mesure. Conservé parce que l'effet
> est structurel et qu'il chiffre ce qu'une cadence grossière détruit.

Réplication **7 jours sur 7**, aucun changement de signe :

| | grossier 62,6 s | fin 537 ms |
|---|---|---|
| candidats écartés « invisibles » | **58,35 %** | **4,11 %** (facteur 12,0 à 16,1) |
| attente de la 1ʳᵉ photo, médiane | 35,5 s | **0,28 s** |
| surcoût en temps | — | **+5,9 %** sur 7 jours |
| surcoût disque | — | 25 Mo/jour |

Et **le coût statistique, qui va dans l'autre sens** : le nombre de lignes
palier-instant est multiplié par 1,78, mais le nombre de **clusters
d'indépendance est divisé par 2,3** (2 433 → 1 052), 7 jours sur 7. **Plus
d'événements, moins de puissance.**

Réserve du rapport d'origine, à porter : le contrefactuel manque pour **42,7 %**
des ordres retrouvés — dans les déciles de vie courte, le bras grossier n'a
aucune observation.

---

## 7. Corruptions et défauts connus

| | |
|---|---|
| `deep_20251202_BTC.parquet` | **corrompu** — `Parquet magic bytes not found in footer`. Détecté par le contrôle d'empreinte le 04/08. |
| `hl_fills` | **compte double** — 1 ligne par contrepartie. `part maker = 0,500000` par arithmétique. Toute somme de volume est fausse ×2. |
| jointure fills → ordres | **4,55 % des `oid` exécutés n'existent pas** dans `hl_orders` (~25 000 ordres/jour) |
| 12 décembre | jour **court** — 6 176 instants contre ~8 290 — et mid figé sur 65 instants consécutifs à partir de 19 h 01. Le pondérer à égalité dans une moyenne journalière est une faute. |
| jours 15, 16, 24-31 | diffs présents et de taille normale, **jamais reconstruits** avant le 04/08 |

**L'archive ne s'arrête PAS le 12 décembre.** Affirmation héritée, mesurée
fausse le 04/08 : les 31 jours de diffs sont présents, et le 14 se reconstruit
normalement (8 307 instants, amplitude de prix normale). Vérification : 4
minutes.

---

## 8. Pièges de reconstruction — chacun a été payé

1. **La chauffe de 8 h ne fait PAS ce qu'on lui prête.** ⚠️ Longtemps justifiée
   par un déficit de masse asymétrique en début de journée, censé fabriquer un
   faux déséquilibre directionnel. **Mesuré, même jour, mêmes instants, en
   passant `WARMUP_H` de 2 à 8** :

   | bande, h00-h04 | 2 h | 8 h |
   |---|---|---|
   | masse **bid** | 81,0 M$ | **81,0 M$ — +0,0 %** |
   | masse ask | 91,8 M$ | 94,3 M$ (+2,7 %) |

   **Zéro palier bid ajouté sur la journée entière**, contre 59 121 côté ask.
   Parmi les paliers communs dont la masse bouge : **2 bid contre 353 577 ask**.
   *« Quadrupler la chauffe n'a pas rempli le côté bid d'un dollar. »*

   **La cause réelle est de la microstructure, pas de l'instrument** : le flux de
   pose est symétrique (part bid 0,5010 nuit / 0,4991 jour), mais la **durée de
   vie** ne l'est pas — nuit bid **6,25 s** / ask **8,27 s** (rapport 0,76) ;
   jour 5,88 / 6,49 (0,91). Stock = flux × durée de vie : à flux égal, le carnet
   porte mécaniquement moins de bids la nuit.

   **Ce que `WARMUP_H = 8` apporte réellement** : **+11,5 % de paliers** dans la
   nappe large (3 204 → 3 571 par photo). Il ne corrige pas ce qu'on croyait.
   ⚠️ Son coût est **contesté** : ~3 min/jour-symbole selon l'ADR qui le mesure,
   ~25 min/jour-symbole selon le programme. Non réconcilié.

   Conséquence à porter : **ne pas écarter les premières heures** — ce serait
   jeter de la donnée réelle. Et toute corrélation impliquant un déséquilibre de
   carnet doit être lue **à heure contrôlée**, le cycle journalier valant environ
   un écart-type.
2. **Un agrégat par côté, jamais partagé.** Avec un dictionnaire commun, un ask
   posé au prix d'un bid existant est fondu dans l'entrée du bid : le carnet
   paraît sain et la masse est fausse. 472 continuités rompues sur 535.
3. **Un palier vide doit quitter le carnet**, sinon il occupe un rang et déplace
   le mid — 3,36 % des photos fausses, médiane 1 $, max 10,5 $.
4. **L'horloge doit être monotone** et avancer sur le maximum courant : les
   horodatages joints ne sont pas croissants dans l'ordre du fichier. Comparer
   au dernier vu faisait tomber la cadence à 55 photos/h au lieu de 3 600.
5. **Un `update` n'a pas d'instant propre** — lui donner `t_term` propulse
   l'horloge en fin de journée.
6. **`work/` gonfle d'environ 15 Gio par passage et ne se nettoie pas.** Mesuré
   à 21 Go de résidus le 04/08.
7. **`data/` est dans `.gitignore` et n'y entre jamais.**

---

## 9. Acquisition temps réel — ce que chaque venue publie

Profondeur publique, et portée relative qui en découle :

| venue | profondeur | portée |
|---|---|---|
| Binance, Coinbase | carnet complet | ±0,4 % |
| OKX | 400 paliers | ±0,069 % |
| Bybit | 200 paliers | ±0,039 % |
| **Hyperliquid (L2 public)** | **20 paliers/côté** | **±0,031 %** |

### `nSigFigs` — et il dépend du SYMBOLE

`l2Book` rend toujours 20 paliers ; `nSigFigs` regroupe les prix et étend la
portée. **Le pas dépend de l'ordre de grandeur du prix** — mesuré en direct le
04/08 sur l'enregistreur (7 venues × 2 symboles, 14 flux synchronisés) :

| | pas BTC (64 232 $) | % du mid | pas ETH (1 875 $) | % du mid |
|---|---|---|---|---|
| natif | 1 $ | 0,03 % | 0,1 $ | 0,005 % |
| `nSigFigs = 4` | 10 $ | 0,30 % | **1 $** | **0,053 %** |
| `nSigFigs = 3` | 100 $ | 3,03 % | **10 $** | **0,533 %** |

**Les rôles s'inversent d'un symbole à l'autre.** Une table mesurée sur BTC ne
se transpose pas.

Autre effet mesuré : `BOOK_KEEP = 0,05` élague à ±5 % du mid, ce qui **tronque
de moitié** le flux `nSigFigs=3` sur ETH (18 paliers remontés au lieu de 40),
et son mid remonté est quantifié (`1875.00` exactement).

`WsLevel` porte trois champs : `px`, `sz`, **`n`** (nombre d'ordres) — d'après
la documentation officielle. **Non vérifié par moi.** `n` est compté **après
agrégation**, donc inutilisable pour reconstituer une masse par ordre sur la
grille de production dès qu'on emploie `nSigFigs`.

### Protocoles d'intégrité — un par venue, ils ne se ressemblent pas

| venue | mécanisme | resynchronisation |
|---|---|---|
| Binance | chaînage `U`/`u`/`pu` + photo REST | photo REST puis rejeu du tampon |
| Bybit | snapshot/delta chaînés par `u` | **réabonnement au topic**, pas de photo REST |
| OKX | `prevSeqId` | réabonnement au canal |
| Coinbase | **aucune séquence** | — |
| Hyperliquid | photo complète à chaque message | sans objet |

### Pièges d'acquisition déjà payés

1. **Chemin Binance non routé = panne SILENCIEUSE.** La connexion s'ouvre, les
   souscriptions sont acquittées (`{"result":null}`), et **aucune donnée** n'est
   servie. `…/ws/btcusdt@aggTrade` → 0 message ; `…/market/ws/…` → 21 msgs/10 s.
2. **Le depth et l'aggTrade ne prennent pas le même chemin.** Le routé est
   obligatoire pour `aggTrade` et muet pour le depth.
3. **`orderbook.500` est refusé par Bybit en linear** — « handler not found ». → 200.
4. **OKX publie `checksum: 0`** : la validation CRC32 est inactive, l'intégrité
   repose sur `prevSeqId` seul.
5. **L'appariement inter-venues se fait sur l'écart RELATIF au mid**, jamais sur
   le prix absolu. Basis mesuré contre Binance : Bybit −0,7 bp · OKX −0,3 bp ·
   Hyperliquid −0,9 bp · **Coinbase −9,0 bp** (spot).
6. **0xArchive : la photo est fausse, les diffs sont bons.** Photo 88 $ sous
   quatre venues qui s'accordent à 8 $ près ; `diffs_applied: 0`. Reconstruit
   depuis les diffs seuls, l'écart médian passe de 35,50 $ à **0,00 $**.

### Ce que l'API publique Hyperliquid ne donne pas

* **Pas de L4.** `orderUpdates` et `openOrders` sont limités à sa propre adresse
  — **sauf** que `orderUpdates` accepte un portefeuille **tiers nommé** :
  1 513 mises à jour en 45 s pour trois portefeuilles. Aucune autre venue.
* Seul `trades` porte les adresses des contreparties.
* ⇒ Le L4 vient d'un **nœud non-validateur** (`--write-order-statuses
  --write-fills --write-raw-book-diffs`) ou d'une archive. **Le nœud ne produit
  aucun historique** : il démarre le jour où on le lance.

---

## 10. L'environnement

```
Python 3.10.7        C:\Python\Python310\python.exe   (aussi sur le PATH)
numpy 2.2.6 · pandas 2.3.3 · pyarrow 25.0.0 · scipy 1.15.3
sortedcontainers 2.4.0 · orjson 3.11.9 · websockets 16.1.1
```

Épinglé dans `requirements.txt`, vérifié le 04/08 par imports, relecture d'un
parquet de 32,5 M lignes et selftest des garde-fous.

**numpy, pandas et scipy sont au plafond de Python 3.10** — les versions
suivantes exigent 3.11+. Changer d'interpréteur est une décision séparée.

GPU : **GTX 1060, Pascal sm_61** → ni RAPIDS, ni cuDF, ni cuML. XGBoost et
PyTorch fonctionnent.

Disque, relevé le 04/08 : `C:` **311 Go libres** · `H:` 1,1 To · `E:` 209 Go.

---

## 11. Le régime de dégradation du flux d'affichage — TRANCHÉ

Il a longtemps circulé deux versions contradictoires. Elles sont levées :
**ce ne sont pas deux versions, ce sont deux étages de la même chaîne.**

| étage | cadence | ce qu'il voit |
|---|---|---|
| **l'écran** | `SAMPLE_MS` | ce que le navigateur reçoit |
| **l'archive** | `SAMPLE_MS × ARCH_EVERY` | une rangée sur quatre |

**Conséquence à ne jamais perdre : l'écran et l'archive ne subissent pas la même
dégradation.** Une grandeur peut survivre à l'un et mourir à l'autre. Tout test
d'admissibilité doit nommer **lequel des deux** il vise.

**Le plafond de paliers** n'est pas un nombre unique non plus : le flux est
d'abord filtré sur la magnitude médiane de la rangée, puis plafonné par
**l'union de deux règles** — les plus gros par valeur, et les plus proches du
mid. Un troisième plafond, plus petit, existe encore mais porte sur un **autre
objet** : l'endpoint d'archive HTTP, qui sous-échantillonne et détruit la
cadence. On lit le flux brut, jamais lui.

> ⚠️ **Un chiffre de plafond a circulé dans les documents de cadrage sans exister
> dans aucun code ni aucun rapport.** Il a été retiré. Les valeurs réelles se
> lisent dans `sec-recorder.js` (`:457` magnitude, `:470` filtre médiane,
> `:487-494` plafonds) — **À RE-MESURER contre le code, pas à recopier.**

### 11 bis. Le filtre par la médiane CENSURE, et de façon corrélée — PIÈGE

Ce n'est pas du bruit, c'est de la **censure**, et elle n'est pas neutre.

* **la probabilité d'être censuré décroît avec la masse.** Un palier proche de la
  médiane entre et sort du registre : sa présence continue est fragmentée, son
  âge tronqué. Un gros mur n'est jamais censuré. **L'erreur de mesure sur la
  persistance porte donc le signal de taille** — une couche affichée telle quelle
  ré-encode la taille, sous couvert de mesurer la durée ;
* **le seuil est MOBILE.** Un palier peut quitter le registre **sans que sa
  propre masse ait bougé**, parce que le reste du carnet s'est épaissi. La
  persistance mesurée dépend alors de l'état global du livre. **La grandeur cesse
  d'être locale**, ce qu'une grandeur de palier doit être.

**Deux mesures à faire, et un test binaire ne suffit pas** — « ça survit ou
pas » ne voit ni l'un ni l'autre :

```
M1   ε(k,t) = âge_censuré − âge_vrai        distribution par décile de masse
     frag(k) = interruptions de continuité par unité de temps, par décile
     lecture : si E[ε] varie de façon MONOTONE avec la masse, la persistance
               dégradée porte le signal de taille et n'est pas admissible telle
               quelle — quel que soit le correctif appliqué ensuite
```

```
M2   chaque sortie du registre se range dans exactement une cause :
       PROPRE   la masse du palier a baissé et franchi le seuil
       EXOGENE  |v_k(t) − v_k(t−δ)| < tol  ET  médiane(t) > médiane(t−δ)
     la fraction EXOGENE qualifie toute archive déjà collectée : elle dit ce que
     valent ses persistances. Elle garde sa valeur même si l'acquisition change.
```

**Correctif candidat — l'hystérésis de suivi.** Une fois un palier entré au
registre, on continue de l'enregistrer sous le seuil jusqu'à extinction. Ça
préserve la continuité de la trajectoire sans refaire l'acquisition. **Trois
coûts, à mesurer avant de l'adopter, jamais à supposer :**

1. **le registre devient dépendant du chemin.** Le produit est 100 % navigateur,
   chaque visiteur ouvre sa propre connexion : un visiteur arrivé pendant la vie
   d'un mur ne l'a jamais vu franchir le seuil, donc ne le suit pas. **Deux
   visiteurs ne voient pas la même couche.** Atténuation : amorcer le registre à
   la connexion avec tout ce qui est au-dessus du seuil — le biais résiduel
   devient « les connexions récentes sous-déclarent les vieux petits murs » ;
2. **la sémantique de l'archive change.** Une persistance mesurée avant et après
   n'est pas la même grandeur : le manifeste doit porter le drapeau, sinon deux
   générations se concatènent en silence ;
3. **la taille du registre suivi** — « ça ne coûte presque rien » est une
   hypothèse, elle se simule sur un jour.

---

## 12. Ce que personne n'a jamais ouvert

* les **73 Gio d'ordres rejetés** — 89 % des soumissions, objet de l'article
  joint au jeu ;
* le symbole **SOL** — `sol_orders_202512.tar.xz` existe (6,3 Go) et est intact ;
* les **quatre mois de transactions** (oct. 2025 → jan. 2026, 250+ coins).

Les itérations précédentes ont travaillé sur 5 à 12 jours d'un ou deux symboles
— **par limite de ce qui avait été construit, pas par limite de données.**
