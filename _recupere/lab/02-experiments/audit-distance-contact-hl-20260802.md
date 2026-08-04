# AUDIT ADVERSARIAL — le banc P3 mesure-t-il la survie AU CONTACT ?

_02/08/2026. Audit en LECTURE SEULE (aucun fichier de `gondetect/` ni
`experiments/` modifié). Tous les chiffres ci-dessous ont été **remesurés** par
l'auditeur avec `E:\Python\Python310\python.exe` sur le jeu du jalon
(`p3_dataset.build_hurdle()`, 83 035 lignes) et les prédictions archivées
`data/cache/p3-preds-*-512be8b879ef.parquet`._

---

## VERDICT

**OUI — le banc du jalon mesure bien la survie d'un mur AU CONTACT.** La
prémisse qui a déclenché cet audit est fausse, et elle l'est pour une raison
identifiable : **elle confond deux distances différentes**, mesurées à deux
instants différents, portées par deux colonnes différentes.

- `dist` (= `dist_obs`, distance **à l'observation**) : **100,00 %** des
  83 035 lignes sont dans la bande P0 `[0,12 % ; 0,80 %]`, médiane 0,18 %.
  Aucune exception, sur aucun des deux symboles. Le filtre de distance de P0
  **existe bien en P3** — il vit dans `gondetect/hl_labels.py:552`
  (`ok = (d >= self.dist_min) & (d <= self.dist_max)`, avec
  `dist_min = DIST_MIN_MULT × TOL` et `dist_max = DIST_MAX` repris de
  `config.py`). Le grep qui n'a rien trouvé cherchait dans `p3_target.py` /
  `hl_features.py` / `p3_dataset.py` — le filtre est en amont, dans la fabrique
  de labels.
- `f_dist` (feature, distance **à `i*`, la dernière rangée d'archive
  strictement antérieure au contact**) : médiane 0,045 %, 96,9 % (BTC) /
  96,1 % (ETH) sous 0,12 %. **Les chiffres de l'énoncé sont exacts** — mais
  cette grandeur n'est pas la distance de sélection. C'est la distance
  résiduelle *juste avant le contact*, et elle est petite **par définition du
  contact** (`|mid − lvl|/lvl < TOL = 0,06 %`).

Un mur à 0,045 % du mid en `f_dist` n'est donc pas « un mur déjà collé au prix
qu'on n'aurait pas filtré » : c'est **le même mur**, observé à 0,18 % du mid en
médiane, que le prix est venu chercher **627 s plus tard** (BTC ; 439 s ETH), et
qu'on photographie 10 s avant l'impact.

**MAIS l'audit a touché un vrai défaut, ailleurs et plus grave** : l'instrument
qui définit le contact côté HL est **117 × plus grossier** que ce que
`hl_labels.py` documente et suppose. Détail en §5. Ce défaut n'invalide pas la
question posée par le banc ; il déplace le sens de « juste avant le contact » et
il produit une **sélection de population sur la durée de vie des ordres** qui,
elle, n'est écrite nulle part.

---

## 1. Reproduction des chiffres de l'énoncé — CONFORMES

`build_hurdle()` : 83 035 lignes (BTC 59 826 + ETH 23 209), couverture globale
99,0 %, identique au rapport du jalon.

Quantiles de `f_dist` (distance à `i*`) :

| quantile | 0,1 % | 1 % | 5 % | 10 % | 25 % | **50 %** | 75 % | 90 % | 95 % | 99 % | 99,9 % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BTCUSDT | 0,000006 | 0,000013 | 0,000067 | 0,000119 | 0,000274 | **0,000451** | 0,000574 | 0,000731 | 0,000943 | 0,002078 | 0,003154 |
| ETHUSDT | 0,000010 | 0,000011 | 0,000053 | 0,000099 | 0,000247 | **0,000433** | 0,000576 | 0,000779 | 0,001050 | 0,002637 | 0,004320 |

Part sous 0,12 % : **BTC 96,89 % · ETH 96,05 %**. Part sous `TOL` (0,06 %) :
BTC 80,94 % · ETH 79,31 %. Part au-dessus de 0,8 % : **0,00 %** (aucune ligne).
Médiane 0,00045 ≈ 0,045 % du mid. **Tout est reproduit au chiffre près.**

Quantiles de `dist` (distance à l'observation, moyenne de `dist_obs` sur les
ordres du palier-instant) :

| quantile | 0,1 % | 5 % | 25 % | **50 %** | 75 % | 95 % | 99,9 % |
|---|---|---|---|---|---|---|---|
| BTCUSDT | 0,001201 | 0,001242 | 0,001442 | **0,001805** | 0,002527 | 0,004356 | 0,007614 |
| ETHUSDT | 0,001201 | 0,001246 | 0,001448 | **0,001790** | 0,002521 | 0,004536 | 0,007676 |

Part dans `[0,0012 ; 0,008]` : **100,0000 %** des deux côtés. Part sous 0,12 % :
**0,0000 %**. Au niveau ORDRE (avant agrégation, 221 285 ordres relus depuis
`hl_labels_*.parquet`), `dist_obs` va de 0,001200 à 0,007998 — les deux bornes
exactes du filtre.

---

## 2. Comment le contact est-il défini côté P3 ?

Chaîne lue (`hl_labels.py`) :

1. **Candidature** (`_scan_orders`, l. 543-596) : un ordre `open` est retenu si
   `dist_min <= |px − mid(t_place)|/mid <= dist_max`, s'il ne traverse pas le
   prix, et s'il n'est pas un re-placement du même wallet au même palier sous
   400 s. **C'est le filtre P0, appliqué à l'ordre individuel.**
2. **Observation** (`_build_events`, l. 688-691) : `t_obs` = première photo du
   carnet `hl_book` **postérieure au placement**. `mid_obs` = le mid de cette
   photo. `dist_obs = |px − mid_obs|/mid_obs` (l. 835).
3. **Contact** (l. 714-720) : `_first_touch_ms` cherche, **strictement après
   `i_obs`** et dans un horizon d'1 h, la première photo où
   `|mid − lvl|/lvl < TOL`. Le critère est repris à l'identique de
   `labels.first_touch` (P0).
4. `y_post` (`p3_target.aggregate`, l. 108) = `(filled − filled_pre) / placed`,
   où `filled_pre` ne compte que les exécutions à `t < t_contact` et `filled`
   celles jusqu'à `t_contact + 30 s`.

**Un mur à 0,045 % du mid EST-il « touché » au sens de P0 ?** Oui — mais ce
n'est pas la bonne question, parce que ce 0,045 % n'est **pas** l'état à
l'observation. À l'observation, le mur est à 0,18 % (médiane) et **jamais** sous
0,12 %.

**Le prix VIENT-il le toucher ?** Mesuré directement, en cherchant sur la nappe
d'archive 10 s (celle qui porte les features) la première rangée entre `t_obs`
et `t_contact` où `|mid − lvl|/lvl < TOL` :

> **le palier est déjà dans la bande ±TOL dès la rangée de `t_obs` dans
> 1,16 % des cas (BTC) et 1,60 % (ETH).**

Autrement dit **98,4 à 98,8 % des observations sont faites hors de la bande de
tolérance**, et le prix est bien venu ensuite. La lecture « le banc regarde la
profondeur là où le prix se trouve déjà » est **infirmée pour ~98,5 % de la
population**.

---

## 3. Le point décisif — y a-t-il une fenêtre temporelle réelle ?

`t_contact − t_obs`, sur le jeu du jalon (83 035 palier-instants) :

| | min | 1 % | 10 % | 25 % | **50 %** | 75 % | 90 % | 99 % | moyenne |
|---|---|---|---|---|---|---|---|---|---|
| BTCUSDT | 61 s | 62 s | 125 s | 250 s | **627 s** | 1 629 s | 2 755 s | 3 512 s | 1 035 s |
| ETHUSDT | 62 s | 62 s | 63 s | 188 s | **439 s** | 1 192 s | 2 321 s | 3 455 s | 830 s |

Au niveau ORDRE (221 285 ordres) : médiane **501 s** (BTC) / **251 s** (ETH),
minimum 61,45 s.

**Part des lignes avec `t_contact − t_obs` < 60 s : 0,0000 %.** Il n'existe pas
une seule observation contemporaine de son propre contact.

Comparaison au côté Binance (~930 s, écart médian `i → j` cité dans
`dataset.py:117`) : **même ordre de grandeur**, HL étant plutôt *plus court*
(627 s / 439 s contre ~930 s). L'écart s'explique par la géométrie (bande
identique) et par la volatilité du jour, pas par un défaut de construction.

**Réponse : oui, la fenêtre est réelle, et « après le contact » a un sens.**
`y_post` retranche bien un `filled_pre` qui court sur une fenêtre médiane de
8 à 10 minutes, pas sur zéro.

---

## 4. Le résultat dépend-il de cette population ? (AUC stratifiée)

Recalcul avec `p3_metrics._build_pairs` + `_pair_boot`, mêmes paramètres que le
jalon (`window_ms=300 000`, `decidable=0,10`, `max_pairs_per_cluster=200`,
`n_boot=400`), graine déterministe fixée à 20 260 802 (donc **non comparable au
millième** aux cellules du rapport, qui utilisent `_seed(sym, day, scope)` ;
les points restent du même ordre). Pooling sur tous les folds — sans risque de
paire inter-folds, chaque jour n'appartenant qu'à un seul fold de test.

### 4.a — stratification par `f_dist` (proches < 0,12 % vs lointains ≥ 0,12 %)

**Périmètre LODO PURGÉ (celui qui fait foi) :**

| symbole | strate | n | G | AUC témoin [IC95] | AUC ranker [IC95] | paires |
|---|---|---|---|---|---|---|
| BTC | tout | 3 346 | 1 468 | 0,704 [0,626 ; 0,760] | 0,740 [0,644 ; 0,794] | 1 909 |
| BTC | proches (96,5 %) | 3 230 | 1 426 | 0,697 [0,627 ; 0,752] | 0,722 [0,663 ; 0,793] | 1 759 |
| BTC | **lointains (3,5 %)** | **116** | **52** | 0,640 [0,200 ; **1,000**] | 0,580 [0,417 ; **1,000**] | **50** |
| ETH | tout | 1 162 | 498 | 0,665 [0,408 ; 0,733] | 0,793 [0,704 ; 0,868] | 962 |
| ETH | proches (95,4 %) | 1 109 | 468 | 0,721 [0,402 ; 0,769] | 0,747 [0,496 ; 0,809] | 596 |
| ETH | **lointains (4,6 %)** | **53** | **35** | 0,836 [0,726 ; 0,984] | 0,849 [0,697 ; 1,000] | **159** |

**Périmètre FULL (non purgé, plus de puissance) :**

| symbole | strate | n | G | AUC témoin [IC95] | AUC ranker [IC95] | paires |
|---|---|---|---|---|---|---|
| BTC | proches | 57 967 | 1 884 | 0,633 [0,606 ; 0,726] | 0,713 [0,690 ; 0,781] | 43 329 |
| BTC | lointains | 1 859 | 101 | 0,552 [0,363 ; 1,000] | 0,582 [0,464 ; 1,000] | 1 136 |
| ETH | proches | 22 293 | 580 | 0,632 [0,487 ; 0,683] | 0,700 [0,630 ; 0,781] | 8 440 |
| ETH | lointains | 916 | 42 | 0,742 [0,665 ; 0,990] | 0,685 [0,611 ; 1,000] | 590 |

**LA PUISSANCE MANQUE, et le signe s'inverse entre symboles.** Les lointains
pèsent 3,1-4,6 % des lignes, 35 à 101 clusters, 50 à 1 136 paires ; tous leurs
IC touchent 1,000 et la plupart contiennent 0,5. Le point est **plus bas** que
les proches sur BTC (−0,06 à −0,13) et **plus haut** sur ETH (+0,05 à +0,11).
Deux symboles, deux signes contraires : **on ne peut rien conclure de cette
strate**, et il faut le dire ainsi plutôt que de choisir le côté qui arrange.

Note de sémantique, importante pour l'interprétation : « `f_dist` lointain » ne
veut PAS dire « mur lointain ». Les deux strates ont la même distance
d'observation (médiane `dist_obs` 0,00220 vs 0,00259). Ce qui les distingue,
c'est la **vitesse d'arrivée du prix dans la dernière rangée avant le contact**.
Les lointains ont un `t_contact − t_obs` presque doublé (1 942 s vs 1 065 s sur
BTC) et un `y_post` moyen plus élevé (0,128 vs 0,092 BTC ; 0,285 vs 0,122 ETH).

### 4.b — stratification par la VRAIE distance de sélection (`dist_obs`)

C'est la stratification que l'énoncé cherchait. Quartiles, périmètre FULL :

| symbole | strate | n | G | AUC témoin | AUC ranker | paires |
|---|---|---|---|---|---|---|
| BTC | Q1 (le plus proche) | 14 957 | 362 | 0,499 [0,153 ; 0,750] | 0,644 [0,384 ; 0,897] | 844 |
| BTC | Q2 | 14 956 | 452 | 0,592 [0,515 ; 0,825] | 0,668 [0,533 ; 0,876] | 1 606 |
| BTC | Q3 | 14 956 | 713 | 0,583 [0,478 ; 0,698] | 0,710 [0,675 ; 0,871] | 3 931 |
| BTC | Q4 (le plus lointain) | 14 957 | 1 046 | 0,678 [0,647 ; 0,766] | 0,740 [0,715 ; 0,813] | 14 063 |
| ETH | Q1 | 5 803 | 92 | 0,628 [0,000 ; 1,000] | 0,639 [0,591 ; 1,000] | 366 |
| ETH | Q2 | 5 802 | 127 | 0,609 [0,228 ; 1,000] | 0,577 [0,000 ; 1,000] | 440 |
| ETH | Q3 | 5 802 | 207 | 0,652 [0,590 ; 0,976] | 0,709 [0,634 ; 0,964] | 850 |
| ETH | Q4 | 5 802 | 342 | 0,647 [0,420 ; 0,696] | 0,735 [0,637 ; 0,837] | 2 431 |

Gradient croissant sur BTC (témoin 0,499 → 0,678 ; ranker 0,644 → 0,740), plat
et non significatif sur ETH. **À manier avec précaution** : le nombre de
clusters et de paires varie d'un facteur 17 entre Q1 et Q4 (les murs proches
touchent vite, donc leurs contacts se concentrent dans peu de clusters —
percolation déjà documentée le 02/08). Le gradient d'AUC est **confondu avec un
gradient de puissance**. À retenir comme piste, pas comme mesure.

Association directe `f_dist` ↔ cible, pour information : Spearman
ρ = **−0,014** (BTC) / **+0,028** (ETH) contre `y_post` — non monotone (déciles
en U). `f_dist` n'est plus le confondeur géométrique que P0 avait dû neutraliser ;
c'est devenu une grandeur quasi inerte vis-à-vis de la cible. `dist_obs`, elle,
donne ρ = +0,078 / +0,068 — et elle est **correctement exclue** des features
(`l4_only_excluded` du jalon).

---

## 5. Explications innocentes cherchées — une trouvée, un défaut réel derrière

### 5.a — « Le L4 n'a pas la même notion de distance que la nappe agrégée » — NON

Vérifié : `hl_labels.py:552` et `dataset.py:93` calculent **la même chose**,
`|px − mid|/mid`, avec les **mêmes constantes** importées de `config.py`. La
seule différence est l'unité (un ordre vs un palier de la nappe). L'agrégation
`p3_target.aggregate` prend la moyenne des `dist_obs` du palier-instant, ce qui
ne peut pas sortir de la bande. **Ce n'est pas l'explication.**

### 5.b — « `f_dist` est recalculée à un autre instant » — OUI, c'est L'explication

`features.extract_obs` (l. 270) : `f_dist = |lvl − mid[i]|/mid[i]` à la rangée
d'extraction `i`. Et `hl_features.features_at_contact` (l. 145-146) fixe
`i = i* = j − 1`, la dernière rangée d'archive **strictement antérieure à
`t_contact`** (règle anti-fuite du module). `f_dist` est donc la distance à
~10 s du contact, pas à l'observation. Le contact impose
`|mid − lvl|/lvl < 0,0006` ; 10 s plus tôt, on est encore dedans ou tout près.
**Médiane 0,00045 : c'est exactement ce qu'on doit trouver.** Aucune anomalie.

### 5.c — Le défaut RÉEL trouvé en chemin : la grille de contact est 117× trop grossière

`hl_labels.py:47-52` et `:82-86` documentent un carnet à **~537 ms** et des
« photos » quasi continues. **Les données réellement utilisées par le jalon n'ont
pas cette cadence.** Mesuré sur les trois racines L4 présentes sur disque :

| racine | `hl_book` 2026-05-08 BTC | photos/jour | dt médian |
|---|---|---|---|
| `data/l4/cache/.../marvingozo/.../versions/1` (Kaggle) | oui | **159 966** | **537 ms** |
| `data/l4/perps10` (celle des prodrows, et des labels du jalon) | oui | **1 373** | **62 642 ms** |
| `data/l4/relance` | oui | 1 380 | 62 637 ms |

Les 16 fichiers `hl_labels_*_stats.json` du jalon portent tous
`book_dt_ms_median ≈ 62 640` et `book_snaps ≈ 1 375`. **Le jalon a été étiqueté
sur une grille de contact à ~63 s.** Conséquences mesurées :

1. **`t_contact` est systématiquement EN RETARD.** Contre-mesure sur le seul
   jour où les deux cadences existent (BTC 2026-05-08, 11 224 labels), en
   recalculant le premier contact sur le carnet fin 537 ms :
   `t_contact(63 s) − t_contact(537 ms)` = médiane **33 s**, moyenne **135 s**,
   q90 **304 s**, q99 **2 570 s** (43 min). 0,20 % seulement sont ≤ 0. Aucun
   contact du jalon n'est introuvable sur le carnet fin (0,00 %) — le contact
   existe, il est juste daté trop tard.
   Mesure indépendante et concordante sur la nappe 10 s des prodrows,
   **sur les 16 (sym, jour)** : retard médian **30 s** (BTC) / **30 s** (ETH),
   moyenne 130 s / 128 s, q90 280 s.
2. **C'est la cause mécanique du `f_dist` minuscule.** Côté Binance,
   `dataset.py` cherche le contact sur la MÊME série 10 s que les features :
   par définition de « première rangée dans ±TOL », la rangée `j−1` est
   forcément **hors** de la bande, d'où le plancher dur `f_dist ≥ TOL = 0,0006`
   déjà relevé dans `s6_transfer.py:62`. Côté HL, contact et features viennent
   de **deux séries différentes** (carnet 63 s vs nappe reconstruite 10 s) :
   rien n'impose ce plancher, et 80,9 % des lignes tombent sous lui. **Le défaut
   d'appariement d'ADR-012 documenté par S6 (OVL 0,19) et le « 96,9 % sous
   0,12 % » de cet audit sont le même fait, vu de deux côtés.**
3. **Sélection non déclarée sur la durée de vie des ordres.** `t_obs` est la
   première photo après le placement : sur une grille 63 s, `t_obs − t_place` a
   une médiane de **31,8 s** (BTC) / 30,5 s (ETH) et un maximum de 247 s. Tout
   ordre mort avant sa première photo est écarté comme « invisible » — sur BTC
   2026-05-08 : **319 994 candidats sur 546 252, soit 58,6 %**. Or
   `hl_labels.py:55-57` mesure lui-même que la durée de vie médiane d'un ordre
   au repos est de **21 s**. Le banc ne retient donc, pour l'essentiel, que les
   ordres ayant **survécu au moins ~30-60 s** — c'est-à-dire une sélection
   directement sur la grandeur étudiée. (Avec la grille 537 ms documentée, cette
   perte aurait été marginale ; l'affirmation est ici une **inférence**, non une
   mesure : je n'ai pas rejoué le scan L4 complet sur la racine Kaggle.)
4. **13,2 % des labels** (BTC 13,17 % / ETH 13,78 %) n'ont **jamais** de rangée
   dans la bande ±TOL sur la nappe 10 s entre `t_obs` et `t_contact` : les deux
   instruments ne sont pas d'accord sur l'instant du contact. Ce sont
   très largement les lignes à `f_dist ≥ TOL` (19,1 % / 20,7 %).

Aucun de ces quatre points ne rend le banc circulaire ni ne détruit la question
posée. Tous les quatre sont **non écrits** dans les rapports du jalon.

---

## 6. Ce que ça implique pour le verdict du jalon (cas C)

Je ne rouvre pas le verdict. Ce qui suit est l'implication, à charge et à
décharge.

**À décharge — l'objection qui a déclenché cet audit ne tient pas.** Le banc du
jalon 1 mesure bien « un mur observé à 0,12-0,80 % du prix, survit-il quand le
prix vient le chercher 7 à 10 minutes plus tard ? ». Le verdict **cas C** n'est
pas fondé sur une population dégénérée : la population est **exactement** celle
de P0 sur l'axe de la distance d'observation, 100 % dans la bande, 0 % déjà au
contact. Il n'y a **rien ici qui justifie de rouvrir le cas C**, et le
faire sur la base de « 96,9 % des murs sont collés au prix » serait rouvrir un
verdict sur une lecture fausse.

**À charge — deux réserves à consigner, qui ne changent pas le verdict mais
changent ce qu'on a le droit d'en dire :**

1. **Le cas C se lit « le rang n'est pas certifiable À CETTE MAILLE
   D'ÉVÉNEMENT » (ADR-011:48-51).** Cet audit ajoute une précision au mot
   « maille » : la maille n'est pas seulement « palier-instant agrégé sur 60 s »,
   c'est **« palier-instant dont le contact est daté sur une grille de 63 s, et
   dont l'ordre sous-jacent a survécu à sa première photo »**. Un cas C obtenu
   sur cette maille dit encore moins qu'on ne croyait sur la maille visée par le
   programme. C'est une raison **de plus** de tenir le cas C, pas une raison de
   le contester.
2. **La strate qui pourrait faire bouger le résultat n'est pas mesurable en
   l'état.** Les lointains (3-5 % des lignes, 35-101 clusters) donnent des IC
   allant jusqu'à 1,000 et des signes opposés BTC/ETH. Toute affirmation du type
   « le signal vient (ou ne vient pas) des murs lointains » est aujourd'hui
   **indéterminable**, et doit être déclarée telle plutôt que tranchée.

**Recommandation, hors périmètre de cet audit et sans valeur d'arbitrage** :
avant tout nouveau run, trancher explicitement une question de doctrine —
faut-il redater `t_contact` sur la nappe 10 s (celle qui porte déjà les
features), ce qui rétablirait le plancher `f_dist ≥ TOL` symétrique de Binance
et supprimerait le retard médian de 30 s ? Ce n'est **pas** un correctif à
glisser : cela déplacerait `t_contact`, donc `filled_pre`, donc `y_post`, donc
tout résultat publié. Cela se décide.

---

## Annexe — reproductibilité

Scripts d'audit (scratchpad, non versionnés — aucun fichier du dépôt modifié) :

| script | ce qu'il mesure |
|---|---|
| `build_set.py` | `p3_dataset.build_hurdle()` → `hurdle.parquet` (83 035 lignes) |
| `q1.py` | quantiles `f_dist` / `dist` / `t_contact − t_obs` par symbole |
| `q2.py` | mêmes grandeurs au niveau ORDRE, relues des `hl_labels_*.parquet` |
| `q3.py` | retard de `t_contact` et « déjà au contact à `t_obs` » sur la nappe 10 s |
| `q4.py` | AUC pairwise stratifiée (`_build_pairs` + `_pair_boot`, graine 20 260 802) |
| `q5.py` | contre-mesure 537 ms vs 62,6 s sur BTC 2026-05-08 |

Fichiers lus : `data/cache/hl_labels_*.parquet` (16),
`data/cache/hl_prodrows_*.jsonl.gz` (16),
`data/cache/p3-preds-{BTCUSDT,ETHUSDT}-512be8b879ef.parquet`,
`data/l4/{perps10,relance,cache/...}/hl_book/hl_book_2026-05-08.parquet`.

Écritures : ce fichier uniquement.
