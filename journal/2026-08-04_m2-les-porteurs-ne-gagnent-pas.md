# 04/08/2026 — M2 : les porteurs ne gagnent pas quand leur mur cède

Deuxième entrée. Elle consigne une mesure, deux défauts de données, et une
leçon de méthode qui vaut plus que la mesure.

---

## 0. Ce qui a précédé, et que j'aurais dû faire d'abord

J'ai passé la première moitié de la nuit à réparer l'instrument de `recherche`
sans avoir lu `sandbox/detect/lab/`. Meddy me l'a ordonné, et la lecture a
montré que **deux de mes contributions étaient des redécouvertes** :

| ce que j'ai « trouvé » | ce qui était déjà écrit |
|---|---|
| l'expérience de chauffe (2 h / 8 h / 16 h) | **ADR-021 addendum 4**, 03/08 20 h 42 : même mesure, même conclusion. La nuit, les bids meurent 24 % plus vite que les asks (6,25 s contre 8,27 s) — c'est de la micro-structure, pas l'instrument |
| « M2 = entre deux murs, lequel le prix choisit-il » | **P2**, 04/08 01 h 20 : IC `[−1,35 ; +2,96]`, contient zéro, un jour sur quatre au signe inverse |

Deux heures de calcul pour retrouver un résultat documenté. La règle qui en
sort : **lire le laboratoire avant de proposer une mesure**, pas après.

Et un acquis que j'avais ignoré, qui est le meilleur du projet précédent :
**D4** — un mur du décile supérieur que le prix approche disparaît 12 à 17
points plus souvent qu'un mur identique non approché, 16 cellules sur 16 sur
deux jours de test. Sur *tous* les murs l'effet est inverse : l'approche les
fait **tenir**. Deux populations, deux signes.

---

## 1. La mesure — M2

Question reprise mot pour mot de `d5-qui-pose-la-queue`, restée sans réponse :

> Pour trancher il faudrait montrer que le retrait **profite** à celui qui
> l'opère.

Population de D5, reprise telle quelle : mur = masse ≥ 8 × médiane de bande,
puis décile supérieur de `f_mult`. Prendre une définition à moi aurait rendu le
résultat incomparable à D4 et D5.

### Le garde-fou a levé DEUX FOIS avant qu'une seule ligne ne sorte

| version de l'événement | fréquence mesurée | verdict |
|---|---|---|
| « la masse tombe sous 20 % en 10 min » | **82,47 %** | REFUSÉ |
| « elle fuit à l'approche » — la cible de D2 | **84,58 %** | REFUSÉ |
| **« le prix approche le mur »** | **13,7 à 17,0 %** | accepté |

La première version mesurait la **durée de vie** de ces murs (~27 s), pas une
intention. La seconde n'est pas une erreur de code : c'est le comportement
mesuré de la queue, et D4 le documente — *« la cible est très déséquilibrée
dans la queue (86-90 % de fuite), c'est le CONTRÔLE qui porte le résultat, pas
elle »*. Le 26,7 % de D2 est la moyenne sur **tous** les murs.

Conditionner sur « il a fui » revenait donc à conditionner sur « le prix s'est
approché », déguisé. L'événement retenu est l'**approche** ; la part qui fuit
est rapportée, pas utilisée comme condition.

C'était la cinquième et la sixième occurrence de la faute qui a tué E2, D1,
D2v1 et P2. **Le garde-fou porté depuis `gondetect/cible.py` les a arrêtées
avant qu'elles ne produisent un chiffre.** C'est exactement ce que le point
ouvert n°3 du document de passation réclamait.

### Le résultat

BTC, jours 20251209-11, unité de rééchantillonnage = le jour, IC de Student.

```
              approches   fuite parmi elles   part du porteur dominant
20251209        15,8 %          79,3 %                0,918
20251210        13,7 %          84,6 %                0,959
20251211        17,0 %          84,3 %                0,951
```

La concentration de D5 est **confirmée** : le premier porteur détient 92 à 96 %
du mur (D5 mesurait 99,7 % avec sa propre jointure), sur 41 à 47 portefeuilles
dominants.

```
GAIN a 60 s          moyenne 3 jours        IC95 Student        exclut 0
EVENEMENT              -96,62 $           [-178,3 ; -15,0]        OUI
PLACEBO_MUR           -140,79 $           [-203,8 ; -77,8]        OUI
PLACEBO_INSTANT        -56,12 $           [-137,1 ; +24,9]        non

GAIN a 300 s
EVENEMENT             -340,70 $           [-733,5 ; +52,1]        non
```

> **Le signe était prédit à l'avance : `GAIN > 0` si le retrait profite à son
> opérateur. Il est NÉGATIF, et l'intervalle exclut zéro à 60 s.
> L'hypothèse est réfutée.**

Un chiffre compte autant que le résultat : **`net_median = 0` partout**. Dans
environ 80 % des événements, le porteur du mur **ne trade pas du tout** autour
de l'approche. La moyenne est portée par une minorité, et cette minorité perd.

### La lecture la plus simple

Ces portefeuilles se comportent en **teneurs de marché subissant la sélection
adverse** — ils perdent sur leurs fills, ce que la fourchette compense. C'est ce
que décrit `selection-adverse-20260803` : le teneur perd dans les deux cas,
+1,15 bp de plus quand il est servi par un croiseur. Retirer leur mur ne leur
rapporte rien.

### Ce que ça ne dit pas

* **Ce n'est pas un P&L.** C'est une marque au marché de la position échangée :
  `net × rendement`. Ni file d'attente, ni inventaire, ni horizon de couverture.
* **Trois jours, un symbole.** L'IC de Student sur 3 unités est très large.
* **L'absence de gain n'établit pas l'absence d'intention.** Un acteur peut
  retirer pour ne pas être exécuté — éviter une perte n'apparaît pas dans une
  mesure de gain réalisé. C'est précisément le retournement que
  `extrapolation-croisement` propose : *« mesurer le gain ÉVITÉ plutôt que le
  gain réalisé »*. M2 mesure le second.

---

## 2. Deux défauts de données, trouvés en chemin

### L'archive s'arrête le 12 décembre à 17 h 40 UTC

> ⚠️ **CORRIGÉ le 04/08/2026** — voir
> `2026-08-04_le-12-decembre-l-archive-ne-s-arrete-pas.md`.
> Mesuré : les **31 jours** de diffs sont présents, et le **14 décembre se
> reconstruit parfaitement** (8 307 instants, amplitude de prix normale).
> **L'archive ne s'arrête pas.** Le 12 a bien un défaut, mais local — 11 minutes
> de mid figé vers 19 h. Le texte ci-dessous est conservé tel quel, il n'est pas
> réécrit.

```
                dernier instant reel       ensuite
ETH   2025-12-12 17:40:36.114              mid FIGE a 3 074,95
BTC   2025-12-12 17:40:35.554              mid FIGE a 90 187,50
```

**Les deux symboles s'arrêtent à la même seconde** — c'est la fin des données,
pas la reconstruction. Les fichiers horaires 18-23 existent (30 à 96 Mo de
diffs, 6 à 27 Mo de statuts), le rapport `remove/new` y vaut 1,000, mais leur
contenu ne produit plus de carnet cohérent : **8 476 949 carnets croisés** sur
ETH, et un enregistrement portant un horodatage **du 11 décembre**.

**Conséquence** : `deep_20251212_*` contient une centaine d'instants fantômes
après 17 h 40, à mid constant. Ils polluent toute mesure qui utilise ce jour —
y compris le `deep_20251212_BTC` fabriqué par l'ancien projet, et l'agrégat de
M1 qui pondère ce jour comme les autres. **Le 12 est exploitable jusqu'à
17 h 40 (73 % de la journée), inutilisable après.**

Non corrigé à cette heure.

### `book_hors_heure` : un incident isolé, pas une structure

```
ETH 08 : 33      ETH 09 : 98 009      ETH 10 : 18      ETH 11 : 46
```

Le 09 est seul. Hypothèse testée et **réfutée** : la multiplicité des statuts
par `oid` a bien explosé ce jour-là (5 467 → 68 447 doublons), mais leur écart
médian vaut **0,0 s** et seuls 17 dépassent la tolérance de 300 s. La cause
reste inconnue. L'effet est borné : 8 261 photos profondes contre 8 285 et
8 286 chez ses voisins, soit **0,3 %**.

---

## 3. Ce qui reste ouvert

1. **Le gain ÉVITÉ**, pas le gain réalisé. C'est le retournement que le projet
   précédent désigne comme la voie la plus prometteuse : le seuil à franchir
   n'est plus 7 bp de frais mais **zéro**, parce que la décision de poster ou
   de retirer existe déjà.
2. **Les jours 13-16 et 24-31**, en cours de fabrication, portent M1 de 5 à
   24 jours — et le projet précédent chiffre à « une vingtaine » ce qu'il faut
   pour distinguer un effet de 0,8 bp de zéro.
3. **Nettoyer le 12 décembre** après 17 h 40, ou l'écarter.
4. **Trois typologies de murs jamais confrontées** : la queue de D4
   (`f_mult ≥ 278`), le profil « spoof » d'ADR-021 (22,7 %, vie < 60 s, ×65 la
   taille), et les « invisibles » de l'instrument (vie 38 s, ×16, fuite 87,5 %).
   Personne ne sait si c'est le même objet.
