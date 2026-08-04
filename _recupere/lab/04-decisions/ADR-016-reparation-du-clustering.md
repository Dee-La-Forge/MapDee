# ADR-016 — Réparation de l'unité statistique (v2)

**Date** : 2026-08-02 · **Statut** : **PROPOSÉ** — à valider par Meddy
· **Aucun run avant validation.**

> **La v1 de ce document, écrite le 02/08 vers 15 h, était FAUSSE sur ses deux
> points centraux.** Elle n'est pas effacée : elle est corrigée ici, et ses
> erreurs sont consignées ci-dessous. Le remplacement d'un document dont le
> diagnostic est réfuté n'est pas une réécriture de l'histoire — l'ERRATA et
> l'historique git portent la trace de la v1.

---

## Ce que la v1 disait de faux

**Erreur 1 — son diagnostic visait l'organe sain.** La v1 prescrivait de
réparer la règle d'ÉPISODE (coupure par seuil). Or la mesure établit qu'un
palier-épisode fait **au maximum 5 lignes** (médiane 1, moyenne 1,12), tandis
qu'un wallet en porte jusqu'à **5 161** (8,5 % de BTC). **La percolation vient
à 100 % de l'arête wallet.** Aucune modification de la règle d'épisode ne
pouvait la défaire.

**Erreur 2 — son critère ne discriminait pas, il forçait la réponse
arrangeante.** Le seuil « aucun cluster > 10 % » est **inatteignable par toute
option conservant l'arête wallet sur une journée entière** — le wallet seul
vaut déjà 8,53 % (BTC) et 10,90 % (ETH). Et il se satisfait **trivialement**
en réduisant tout en singletons : l'option « palier seul » le passe à 0,0 %
non parce qu'elle répare la dépendance, mais parce qu'elle la supprime.

Un critère que seule l'option la plus anti-conservatrice peut satisfaire n'est
pas un garde-fou.

**Ce que ça aurait coûté** : sous la configuration complète de la v1, la
barre 1 passait de **6/11 à 10/11** (BTC) et de **1/5 à 4/5** (ETH), *sur les
prédictions déjà archivées, sans une seule donnée nouvelle*. Le cas C serait
devenu une certification par un choix d'unité.

---

## Le problème, correctement énoncé

`cluster` = composante connexe de (palier-épisode ∪ wallet), et le wallet n'est
borné ni par jour ni par durée (`p3_target.py:127` : `sym + ":" + dom_wallet`).
Un acteur actif 11 jours soude ses 11 journées.

| | G | plus gros cluster | top-10 |
|---|---|---|---|
| BTCUSDT | 1 938 | **93,7 %** | 94,0 % |
| ETHUSDT | 610 | **95,7 %** | 96,0 % |

Le bootstrap ne mesure donc plus l'incertitude d'estimation : il joue à pile ou
face la présence d'un bloc.

**Symptôme qui avait alerté** : l'AUC est plus haute sur le test purgé (5 % des
données) que sur le test complet. La purge ne corrigeait pas une fuite — elle
fragmentait accidentellement le bloc.

---

## Découverte annexe, plus gênante que la percolation elle-même

Plafond de paires levé (`max_pairs_per_cluster` illimité), **tous les découpages
rendent le même point** :

| régime | point avec plafond 200 | point sans plafond |
|---|---|---|
| actuel (percolé) | **0,6366** | 0,6008 |
| session-wallet 15 min | 0,5988 | 0,6008 |
| palier seul | 0,6008 | 0,6008 |
| hiérarchique | 0,6008 | 0,6008 |

Aujourd'hui **46 239 paires sur 265 821 survivent au plafond (17 %)**, et
lesquelles dépend de la définition du cluster. **Le réglage en vigueur est celui
qui donne le point le plus élevé** ; toute unité plus fine le fait baisser de
0,036 (BTC).

Ce n'est pas le bootstrap qui déplaçait le résultat, c'est l'interaction
plafond × clustering. **Toute décision sur l'unité doit donc publier le
déplacement du point ET son sens.**

---

## Les options mesurées

| option | G (BTC/ETH) | plus gros | top-10 | largeur d'IC (BTC/ETH) |
|---|---|---|---|---|
| actuelle | 1 938 / 610 | 93,7 % / 95,7 % | 94,0 % / 96,0 % | 0,1229 / 0,2066 |
| wallet borné par jour | 4 402 / 1 178 | 13,4 % / 23,1 % | **83,8 % / 90,7 %** | — |
| **palier seul** | 54 365 / 20 658 | 0,0 % / 0,0 % | 0,1 % / 0,2 % | **0,0207 / 0,0342** |
| **session-wallet 5 min** | 25 227 / 10 184 | 1,4 % / 1,6 % | **8,2 % / 7,3 %** | 0,0345 / 0,0425 |
| session-wallet 15 min | 17 728 / 6 693 | 5,6 % / 5,9 % | 27,5 % / 34,9 % | 0,0390 / 0,0464 |
| session-wallet 30 min | 13 569 / 4 905 | 12,0 % / **58,3 %** | 53,1 % / 66,2 % | 0,0472 / 0,0566 |
| **bootstrap hiérarchique** | inchangé | inchangé | inchangé | **0,0577 / 0,0636** |

**Falaise de percolation : sur ETH, entre 20 et 30 min** (11,2 % → 58,3 %). Les
deux symboles ne cassent pas au même endroit — tout H ≥ 20 min est déjà hors
régime pour ETH.

**Toutes ces options RESSERRENT l'IC.** C'est un défaut, pas un gain : un
intervalle plus étroit obtenu en changeant l'unité d'indépendance n'est pas une
amélioration de puissance, c'est un déplacement d'hypothèse.

---

## Le critère d'acceptation — trois jambes qui poussent en sens opposés

La v1 n'en avait qu'une, et se passait en singletonisant. Chaque jambe punit
une triche différente.

### Jambe 1 — plafond de MASSE (punit le trop grossier)

Par symbole, sur la partition réelle : **masse du top-10 ≤ 25 % ET plus gros
cluster ≤ 5 %**.

Le top-10 est la vraie serrure : le max seul laisse passer « wallet borné par
jour » (13,4 % de max, mais **83,8 % de top-10**).

### Jambe 2 — plancher de COUVERTURE (punit le trop fin)

Sur monde synthétique à dépendance CONNUE : **couverture ≥ 0,93 pour un nominal
de 0,95**, à rho ∈ {0,5 ; 0,85 ; 0,98}. Mesuré, 300 réplicats :

| rho | unité fine | hiérarchique | wallet seul |
|---|---|---|---|
| 0,50 | 0,947 | 0,993 | 0,953 |
| 0,85 | **0,907** | 0,980 | 0,957 |
| 0,98 | **0,867** | 0,977 | 0,950 |

**Casser en singletons SOUS-COUVRE dès que la dépendance de haut niveau est
réelle** — exactement ce qu'un plafond de masse ne voit pas. Le hiérarchique
sur-couvre (0,977–0,993) : conservateur, jamais anti-conservateur.

### Jambe 3 — déclaration du DÉPLACEMENT (punit le choix intéressé)

Publier `|point@plafond − point@plafond levé|` et **le SENS** du déplacement.
**Un régime retenu qui REMONTE le point est disqualifié d'office.**

### Ce que les candidats donnent contre ce critère

- **session-wallet 15 min** — que la v1 recommandait — **ÉCHOUE la jambe 1**
  (top-10 27,5 % / 34,9 % pour un plafond de 25 %).
- **session-wallet 5 min** passe la jambe 1 (8,2 % / 7,3 %). Jambe 2 **non
  mesurée** : le monde synthétique n'a pas de structure temporelle, il ne peut
  pas produire de session qui se coupe.
- **palier seul** passe la jambe 1 et **échoue la jambe 2**.
- **hiérarchique** passe la jambe 2 franchement ; il ne touche pas à `cluster`,
  donc la jambe 1 reste celle de la partition sous-jacente.

**Aucun candidat ne passe les deux premières jambes de façon établie.**

---

## Décision proposée

1. **Ne PAS retenir « palier seul »** malgré son 0,0 % : il échoue la jambe 2,
   il rétrécit le plus (×2,5 à ×3,1), et il transforme le cas C en
   certification.
2. **Retenir le bootstrap hiérarchique** (wallet → épisode) comme régime de
   variance : implémenté, non intrusif (`cluster` inchangé, `_pair_boot` intact
   à l'octet près), conservateur sur la jambe 2.
3. **Laisser l'unité `cluster` EN L'ÉTAT** tant que la jambe 2 n'aura pas été
   mesurée pour les partitions session-wallet. Il faut pour cela un simulateur
   à bouffées d'activité par wallet, qui n'existe pas.
4. **Publier systématiquement le déplacement du point** sous plafond levé.

## Réserves

- Le nichage épisode ⊂ wallet est **imparfait sur données réelles** (pureté
  0,90 BTC / 0,89 ETH) : l'IC hiérarchique réel est **indicatif**, et le code
  l'imprime bruyamment.
- Seul `pairwise_auc` a reçu l'option. `regret_oracle`, `crps_skill`, `ece`,
  `ndcg_at_k` bootstrappent toujours `cluster` à un étage.
- **Rien de ceci ne rouvre un verdict.** Le cas C reste rendu. Une mesure sous
  une unité réparée serait une mesure NOUVELLE sur une unité NOUVELLE.
- Le commentaire mensonger de `p3_target.py:125-127` a été corrigé — **le
  commentaire, pas le code** : borner par jour déplacerait la partition, donc
  tout résultat publié. Ça se décide, ça ne se glisse pas.
