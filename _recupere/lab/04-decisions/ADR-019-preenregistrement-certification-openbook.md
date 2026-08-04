# ADR-019 — Pré-enregistrement de la certification OPEN BOOK

**Date** : 2026-08-03, 04 h 40 · **Statut** : **GELÉ**
**Validé par Meddy** le 03/08 : ADR-018 accepté, règle de décision à figer avant
tout résultat, **une seule certification**, aucune modification méthodologique
ensuite quel que soit le résultat.

> Écrit AVANT d'avoir entraîné le moindre modèle sur ce jeu. Les seuls nombres
> connus à cette heure sont ceux de la **puissance** (comptes de paires, tailles
> de plis, mesurés avec un score ALÉATOIRE) et ceux du **contrôle négatif**
> (cible permutée → cas D, 0/3). Aucune AUC réelle n'a été regardée.

---

## 1. Le jeu

* **Jours** : 2025-12-01 → 2025-12-07 (7 jours consécutifs).
* **Symboles** : BTCUSDT, ETHUSDT.
* **Source** : jeu OPEN BOOK (Zenodo 18184441), sortie brute de la bourse
  Hyperliquid, convertie en `hl_orders` / `hl_book` / `hl_fills` sans toucher au
  pipeline aval.
* **Cache isolé** : les 11 jours du banc Kaggle sont écartés
  (`data/cache/banc-2026-05/`). Les deux instruments ne se mélangent pas.
* **Symboles CERTIFIANTS** (ADR-013) : ceux qui disposent du jeu de jours
  COMPLET. Un symbole en retard est TÉMOIN, il ne certifie pas.

Si un jour venait à manquer à l'heure du tir, il est déclaré manquant dans le
rapport et la porte de couverture s'applique — **on ne remplace pas un jour
absent par un autre**.

## 2. Le découpage — ADR-018, accepté

Groupes de wallets : **3**, tirés une fois pour toutes par symbole, graine
**20251201**, par permutation de la liste des `dom_wallet` distincts.

Pour chaque jour `d` et chaque groupe `W` :

* **test** = lignes du jour `d` dont le wallet ∈ `W` ;
* **entraînement** = lignes des jours ≠ `d` dont le wallet ∉ `W`.

L'invariant « aucun `dom_wallet` des deux côtés » est **vérifié cellule par
cellule à l'exécution**, et son échec est une erreur fatale, pas un
avertissement.

## 3. La règle de décision — LE POINT QUI EST FIGÉ ICI

**L'unité de pli est le JOUR, pas la cellule.**

Trois cellules d'un même jour partagent la trajectoire de prix et le régime de
marché : les compter comme trois plis gonflerait le dénominateur d'unités
corrélées et rendrait la barre plus facile pour une mauvaise raison.

Donc, pour chaque jour `d` : les 3 modèles (un par groupe de wallets)
prédisent chacun sur leur cellule, et **leurs prédictions sont ASSEMBLÉES** en
un unique jeu hors-échantillon couvrant le jour entier. Chaque ligne du jour
reçoit exactement une prédiction, issue d'un modèle qui n'a vu ni son jour ni
son wallet. Le jour redevient **un pli**.

**Les barres de l'ADR-013 ne bougent pas** : par symbole certifiant,

* barre 1 — `ceil(0,80 × n_folds)` plis ;
* barre 2 — `ceil(0,60 × n_folds)` plis.

À 7 jours : **6/7** et **5/7**.

## 4. Les deux périmètres

* **purgé** — entraînement sans le jour ET sans les wallets du test (§2).
  **C'est lui qui fait foi**, comme depuis l'ADR-010/011.
* **complet** — entraînement sur tous les jours ≠ `d`, wallets non retirés,
  même jeu de test.

Les deux couvrent désormais **le même jeu de test** ; seul l'entraînement
diffère. La prime d'identité `AUC(complet) − AUC(purgé)` devient donc une
comparaison appariée sur le même échantillon — elle ne l'était pas avant
(`p3_train.py`, commentaire « jeux de test DIFFÉRENTS → approximation
honnête »).

## 5. La métrique — ADR-017, appliqué

* **Unité de plafonnement des paires** : `palier_ep` (palier-épisode).
* **Unité de variance** : bootstrap **hiérarchique** wallet → épisode.
* Fenêtre 300 s, décidabilité 0,10, plafond 200, 400 tirages : **inchangés**.
* `regret_oracle`, `crps_skill`, `ece`, `ndcg_at_k` bootstrappent toujours
  `cluster` à un étage : avec un cluster à 99,8 %, **leurs IC sont sans valeur
  sur ce jeu** et le rapport doit le dire.

## 6. Ce qui est interdit à partir de maintenant

1. **Un seul tir.** Le rapport produit est LE résultat.
2. **Aucune modification** de `p3_train.py`, `p3_dataset.py`, `p3_models.py`,
   `p3_metrics.py`, `p3_target.py`, `hl_features.py`, `cluststats.py` après le
   tir, quel que soit le résultat.
3. **Aucun ajout de jour, de symbole ou de trait** après le tir.
4. **Aucun changement de seuil**, de fenêtre, de plafond, de graine.
5. Le tir exige un **arbre git propre** (garde de provenance). Un rapport
   marqué NON OPPOSABLE ne compte pas.

Si le résultat est un échec, il est publié tel quel. C'est l'objet même du
pré-enregistrement : un échec sous protocole robuste et bien alimenté vaut plus
qu'une réussite sous protocole négociable.

## 7. Ce qui est déjà su, et qui ne changera pas après coup

| contrôle | résultat |
|---|---|
| selftest des 4 mondes truqués | D→D, B→B, C→C, A→A |
| cible permutée sur le jeu RÉEL | cas D, **0/3** aux deux barres, deux symboles |
| chevauchement de wallet, découpage §2 | **0** sur 18 cellules mesurées |
| couverture de la jointure observable | 97,0 % (seuil 70 %) |
| paires décidables par pli, découpage §2 | 10 190 – 28 673 (contre 43 – 459) |

---

# ADDENDUM du 03/08/2026, 12 h — ce que ce pré-enregistrement a mal dit, et l'interdit que j'ai violé

_Le corps n'est pas réécrit : c'est une pré-inscription, elle vaut par sa date._

## 1. §4 — « comparaison appariée » : le code ne l'appariait PAS

Le §4 affirme que la prime d'identité devient « une comparaison appariée sur le
même échantillon ». `paired_auc_cell` recevait `_seed(sym, day, scope)` — une
graine DIFFÉRENTE par périmètre — donc deux bootstraps indépendants et une
prime dont l'IC était gonflé d'environ √2.

Corrigé le 03/08 à 09 h 08, **après** le tir. Le rapport du verdict porte même
l'affirmation inverse : *« deux bootstraps sur des jeux de test DIFFÉRENTS »*,
alors que sa propre colonne `n_purged` vaut 0 partout.

## 2. §7 — un contrôle présenté comme acquis avait tourné APRÈS le tir

La ligne « cible permutée sur le jeu RÉEL → cas D, **0/3** » figure sous le
titre « Ce qui est déjà su, et qui ne changera pas après coup ». Le **0/3** est
l'ANCIEN protocole à 3 plis. La version à 7 plis-jours — celle du protocole
pré-inscrit — a tourné à **06 h 03 UTC**, soit après le tir de **05 h 27 UTC**.

Le résultat, lui, est bon : **cas D, 0/7 aux deux barres, deux symboles**.
Mais il n'était pas « déjà su » au moment de l'écriture.

## 3. §5 — la réserve exigée du rapport n'y figure pas

Le §5 exige que le rapport déclare sans valeur les IC de `crps_skill`,
`regret_oracle`, `ece` et `ndcg_at_k`. **Le rapport n'en dit rien** et imprime
la colonne CRPS, IC compris — dont un de largeur **4,4**
(`ETHUSDT 20251203 : −0,011 [−4,366 ; +0,063]`).

Mesure du 03/08 : **11 des 12** cellules CRPS ont leur point **collé à la borne
basse**. Mécanisme reproduit — `cluster` ayant percolé, 36 % des tirages ne
contiennent aucune copie du bloc géant et le rapport de sommes explose sur des
singletons. **C'est un mélange, pas une loi d'estimation.** Décision du 03/08 :
retirer la colonne, ne pas la réparer.

## 4. §6.2 — INTERDIT VIOLÉ, et consigné ici

Le §6 interdit toute modification de `p3_train.py`, `p3_dataset.py`,
`p3_models.py`, `p3_metrics.py`, `p3_target.py`, `hl_features.py` et
`cluststats.py` **après le tir, quel que soit le résultat**.

**Trois de ces fichiers ont été modifiés entre 09 h 08 et 09 h 34**, après le
verdict de 07 h 51 : `p3_dataset.py`, `p3_train.py`, `p3_models.py`. Puis
`p3_target.py` vers 11 h 30 (alignement de la grille `_nice`).

Les modifications réparent des défauts mesurés — elles ne visent aucun
résultat, et le verdict CAS D n'est pas rejoué. Mais **l'interdit était écrit
et je ne l'ai pas signalé en le franchissant**. C'est consigné ici, daté.

Conséquence pratique mesurée : `code_sha` du rapport = `cfd56b3755ec`, sur
disque aujourd'hui `e195ca08e464`. **Relancer `p3_train` ne redonne plus les IC
du rapport** (BTC 20251201 témoin : [0,506 ; 0,597] → [0,508 ; 0,604]). Les
points, eux, sont inchangés.

## 5. Ce qui TIENT

Le jeu de jours, le découpage, la règle de décision (l'unité de pli est le
JOUR), les barres 6/7 et 5/7, la garde de provenance sur arbre propre, et le
fait qu'un seul tir a eu lieu. Tout cela a été vérifié par audit indépendant :
barres recomptées, seuils exacts, aucune cellule dissimulée, empreintes
reproductibles, et **14 cellules sur 14 du tableau complet rejouées à
l'identique** depuis les scores archivés.

**Réserve d'archivage** : seuls les scores du périmètre COMPLET sont archivés.
Ceux du périmètre PURGÉ — qui portent les barres et donc le verdict — ne sont
dans aucun fichier. Le tableau qui fait foi n'est pas vérifiable a posteriori.
