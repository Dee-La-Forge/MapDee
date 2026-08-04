# L'unité statistique du jalon — problème, options, et ce que chacune fait au verdict

_02/08/2026. Tous les chiffres de ce document ont été **recalculés par un
auditeur indépendant** sur les mêmes données, pas repris de mes mesures.
Aucune décision n'est prise ici._

---

# 1. LE PROBLÈME

## 1.1 L'unité statistique s'est effondrée

Le jalon regroupe les événements en clusters — composantes connexes de
(palier-épisode ∪ wallet dominant) — et c'est cette unité que le bootstrap
rééchantillonne pour produire les intervalles de confiance.

| | G | plus gros cluster |
|---|---|---|
| BTCUSDT | 1 938 | **93,7 % des événements** |
| ETHUSDT | 610 | **95,7 %** |

Un seul cluster porte presque tout. Le bootstrap ne mesure donc plus
l'incertitude d'estimation : il joue à pile ou face la présence d'un bloc.

## 1.2 D'où vient la soudure — et d'où elle ne vient PAS

| brique | taille |
|---|---|
| palier-épisode | **maximum 5 lignes** · médiane 1 · moyenne 1,12 |
| wallet | jusqu'à **5 161 lignes** (8,5 % de BTC) · top-10 = 43,6 % BTC / 52,0 % ETH |

**La percolation vient à 100 % de l'arête wallet.** Aucune modification de la
règle d'épisode ne peut la défaire — c'est l'organe sain.

Cause immédiate, `gondetect/p3_target.py:125-127` :

```python
# le wallet est scopé par (sym, day) : deux jours ne partagent une identité…
wal = g.sym.astype(str) + ":" + g.dom_wallet.astype(str)
```

**Le commentaire annonce un bornage par jour. Le code ne le fait pas.** `day`
n'apparaît nulle part dans la clé. Un acteur actif sur 11 journées soude ses
11 journées.

## 1.3 Le symptôme qui avait alerté

À modèle, graine et métrique identiques, l'AUC est **plus haute** sur le test
purgé (5 % des données) que sur le test complet — BTC 0,7032 contre 0,6370.
Ce n'était pas une fuite d'identité absente : c'est que **la purge fragmentait
accidentellement le bloc**.

## 1.4 Ce que le problème NE remet PAS en cause

Le verdict du jalon est **robuste** : sur douze graines de plafond de paires,
la barre 1 vaut **5-6/11** sur BTC (seuil 9) et **0-1/5** sur ETH (seuil 4).
Le cas C n'était pas marginal.

---

# 2. LES OPTIONS

## 2.1 Ce que chacune fait à la percolation

| option | G (BTC/ETH) | plus gros cluster | critère « < 10 % » |
|---|---|---|---|
| **actuelle** — wallet toutes journées | 1 938 / 610 | 93,7 % / 95,7 % | ❌ |
| **A** — wallet borné par jour | 4 402 / 1 178 | 13,4 % / 23,1 % | ❌ |
| **B** — palier-épisode seul, sans wallet | 54 365 / 20 658 | 0,0 % / 0,0 % | ✅ |
| **C** — épisode ∪ session-wallet 15 min | 17 728 / 6 693 | **5,6 % / 5,9 %** | ✅ |
| C′ — même chose à 30 min | 13 569 / 4 905 | 12,0 % / 58,3 % | ❌ |
| **D** — bootstrap hiérarchique (wallet → épisode) | inchangé | inchangé | s.o. |

**Falaise de percolation entre 15 et 30 minutes** — à connaître : l'option C
est stable à 15 min et s'effondre à 30.

## 2.2 Ce que chacune fait aux intervalles

Largeur d'IC sur le test complet, même score archivé, seul le groupe change :

| régime de bootstrap | BTC | ETH |
|---|---|---|
| actuel (dégénéré) | 0,1229 | 0,2066 |
| **B** — épisode seul | **0,0221** | **0,0337** |
| **C** — ep ∪ session 15 min | 0,0357 | 0,0438 |
| wallet seul | 0,0549 | 0,0489 |
| **D** — hiérarchique | **0,0682** | **0,0801** |

**L'option B rétrécit les intervalles d'un facteur 2,5 à 3,1** par rapport aux
références qui conservent la dépendance par acteur. Elle jette la grosse
dépendance (wallet, jusqu'à 5 161 lignes) et conserve la négligeable (épisode,
5 lignes au plus).

## 2.3 Ce que chacune fait au VERDICT

Barre 1, seuils inchangés (9/11 sur BTC, 4/5 sur ETH). Le cluster n'entre ni
dans les folds ni dans l'entraînement — uniquement dans la métrique : ces
chiffres sont donc le résultat exact, pas une approximation.

| configuration | BTC | ETH | |
|---|---|---|---|
| purge actuelle + clustering actuel — **le jalon** | **6/11** | **1/5** | échec |
| purge actuelle + option B | 8/11 | 2/5 | échec |
| **purge restreinte + option B** | **10/11** | **4/5** | **PASSE** |
| purge restreinte + option C | 8/11 | 4/5 | échec BTC |

*(purge restreinte = wallets dominants sur ≥ 2 jours ; survivants 5,6 % → 10,4 %
BTC et 5,0 % → 9,4 % ETH.)*

**Une seule combinaison fait passer le verdict — et c'est celle qui rétrécit
le plus les intervalles.** Sur les prédictions déjà archivées, sans une seule
donnée nouvelle.

---

# 3. CE QUI DISQUALIFIE LE CRITÈRE PRÉ-ENREGISTRÉ

ADR-016 avait gravé « aucun cluster > 10 % des événements ». Ce critère est
défectueux, pour deux raisons mesurées :

1. **Le wallet seul vaut déjà 8,53 % (BTC) et 10,90 % (ETH).** Toute option
   conservant l'arête wallet sur une journée entière échoue mécaniquement. Le
   critère ne sélectionne pas une réparation : il **force** l'abandon du wallet,
   c'est-à-dire l'option la plus anti-conservatrice.
2. **Il se satisfait trivialement par la singletonisation.** L'option B le passe
   à 0,0 % — non parce qu'elle réparerait la dépendance, mais parce qu'elle la
   supprime.

Un critère d'acceptation portant sur le seul plus gros cluster ne mesure pas ce
qu'on croit. Il devrait porter sur la **masse du top-10** et sur une
**couverture de bootstrap simulée**.

---

# 4. CE QUE JE RECOMMANDE

**Ne pas appliquer l'option B**, malgré le fait qu'elle passe le critère écrit.
Elle le passe pour la mauvaise raison, elle rétrécit les intervalles d'un
facteur 3, et elle transforme un échec en certification sans donnée nouvelle.

**Deux candidats défendables, et aucun ne rachète le verdict :**

- **Option C** (épisode ∪ session-wallet 15 min) — passe le critère sur les
  deux symboles, conserve l'unité par acteur défendue depuis ADR-004, laisse
  BTC à **8/11 : le verdict C tient**.
- **Option D** (bootstrap hiérarchique wallet → épisode) — ne touche pas à
  `cluster`, ~15 lignes dans `p3_metrics._pair_boot`, garde la maille fine pour
  le point et la dépendance de haut niveau pour la variance. Intervalles les
  plus larges de la table, donc les plus prudents.

**C et D sont combinables**, et c'est probablement la bonne réponse : C répare
l'unité, D rend la variance honnête.

ADR-016 est à **réécrire**, pas à exécuter : son diagnostic (réparer les
épisodes) et son critère (10 % sur le plus gros cluster) sont tous deux faux.

---

# 5. CE QUE CE DOCUMENT NE FAIT PAS

Il ne rouvre aucun verdict. Le cas C reste rendu, S6 reste NO-GO. Une
certification sous une unité réparée serait une **mesure nouvelle sur une unité
nouvelle**, à déclarer comme telle.

Et il ne tranche rien : le choix entre C, D, ou les deux, appartient à Meddy —
d'autant que la tentation d'y toucher après avoir vu le tableau du §2.3 est
précisément ce contre quoi tout ce dossier a été construit.
