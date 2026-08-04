# 04/08/2026 — Le 12 décembre : l'archive ne s'arrête pas

Première entrée de MapDee. Elle corrige une affirmation héritée qui, prise pour
argent comptant, aurait coûté **la moitié du mois de données**.

Conformément à la doctrine du dossier, l'entrée corrigée **n'est pas réécrite** :
`2026-08-04_m2-les-porteurs-ne-gagnent-pas.md` §2 reste tel quel, et pointe
désormais ici.

---

## 1. Ce qui était écrit

> **L'archive s'arrête le 12 décembre à 17 h 40 UTC.**
> ETH 2025-12-12 17:40:36.114 → mid FIGÉ à 3 074,95
> BTC 2025-12-12 17:40:35.554 → mid FIGÉ à 90 187,50
> Les deux symboles s'arrêtent à la même seconde — c'est la fin des données.
> [...] Leur contenu ne produit plus de carnet cohérent : 8 476 949 carnets
> croisés sur ETH.
>
> — journal du 04/08, §2

Lu littéralement, ça condamne les 19 derniers jours de décembre. Sur 31 jours
dont 7 sous scellés, ça ramène le matériel exploitable de **24 jours à 12**.

## 2. Ce qui a été mesuré

Deux vérifications indépendantes, en lecture seule, aucun jour de la réserve
(17-23) touché. Script : `v12.py`, scratchpad, non versionné.

### 2.a — Les diffs bruts : les 31 jours sont là

Balayage des membres de `book_diffs_202512.tar` (46,2 Gio) :

```
20251201 .. 20251231   →   24 fichiers horaires par jour, 31 jours sur 31
                           aucun trou, aucun jour manquant
```

Volumes par jour : de **0,45 à 2,23 Gio**. Les jours légers — 13, 20, 21, 27,
28 — sont **exactement les week-ends**. C'est de la saisonnalité de marché, pas
un défaut d'archive.

### 2.b — Le 14 décembre se reconstruit parfaitement

C'est la preuve directe : il est *postérieur* à la coupure annoncée.

| jour | instants | mid min | mid max | plus longue série de mid identique |
|---|---|---|---|---|
| 20251210 | 8 290 | 91 584,5 | 94 441,5 | 13 |
| 20251211 | 8 297 | 89 250,5 | 93 532,0 | 12 |
| **20251212** | **6 176** | 89 459,5 | 92 727,5 | **65**, à partir de 19:01:41 |
| **20251214** | **8 307** | 87 588,5 | 90 427,5 | 54, à partir de 03:54:25 |

Le 14 porte **8 307 instants**, une amplitude de prix normale (2 839 $) et un
carnet cohérent. Il n'a rien d'un jour mort.

## 3. Ce qui est vrai, et ce qui ne l'est pas

**Vrai** : le 12 décembre a un défaut réel. Il est court — 6 176 instants contre
~8 290 — et son mid reste figé sur 65 instants consécutifs à partir de 19 h 01,
soit environ **onze minutes**. C'est un incident de cette soirée-là.

**Faux** : que l'archive s'arrête là. Elle porte les 31 jours, et le jour suivant
disponible se reconstruit normalement.

**L'explication la plus probable** : l'affirmation d'origine portait sur
**l'ancienne archive** du projet précédent — reconstruite depuis une autre source
— et non sur le jeu de données Zenodo aujourd'hui sur disque, dont le
`README.md` déclare « Book diff data (Dec 2025) is **complete** — no gaps ». Les
deux ont été confondus. Non tranché plus finement : ça ne changerait pas la
conclusion.

## 4. Ce que ça change

> **24 jours constructibles**, pas 12. Décembre entier moins les sept jours de
> la réserve (17-23).

C'est au-dessus du seuil que le projet précédent avait lui-même chiffré — « une
vingtaine de jours » pour distinguer un effet de 0,8 bp de zéro, avec un
écart-type inter-journalier de 1,35 bp.

Réserves à porter dans toute construction future :

* **le 12 décembre est diminué** — 6 176 instants sur ~8 290, soit 75 % de la
  journée, plus onze minutes de mid figé le soir. Le pondérer à égalité dans une
  moyenne journalière est une faute ; l'agrégat de M1 la commettait déjà ;
* **rien n'est établi sur les jours 15, 16, 24-31** — leurs diffs existent et
  sont de taille normale, mais **aucun n'a été reconstruit**. Le premier lot
  devra les passer aux contrôles croisés avant d'être utilisé.

## 5. La leçon de méthode

Une affirmation datée, chiffrée et écrite de bonne foi a survécu telle quelle
d'un dépôt à l'autre, et elle était fausse dans son périmètre le plus large.
Elle allait faire jeter la moitié d'un mois de données.

La vérification a coûté **quatre minutes**.

> Avant de renoncer à une donnée sur la foi d'une note, ouvrir la donnée.
> C'est la même règle que « toute conclusion négative conduit d'abord à un audit
> de l'instrumentation » — appliquée à l'inventaire au lieu de la mesure.
