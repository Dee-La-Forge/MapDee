# D5 — qui pose les murs qui fuient : **une dizaine de portefeuilles**

**04/08/2026, 00 h 35** · BTC · jours 20251210 et 20251211
**RÉPOND À : ADR-001**

D4 a montré que la signature — un mur qui disparaît quand le prix arrive —
n'existe **que dans le dixième supérieur**, au-delà de ~278× la médiane de
bande. Trois questions posées par Meddy, trois réponses.

---

## 1. CONCENTRATION — un mur, un acteur

| | 10/12 | 11/12 |
|---|---|---|
| portefeuilles par mur, médiane | 4 | 4 |
| ordres par mur, médiane | 4 | 4 |
| **part du plus gros porteur, médiane** | **99,67 %** | **99,57 %** |
| murs où le premier fait > 80 % | **91,2 %** | **92,3 %** |
| murs à un seul portefeuille | 9,8 % | 7,2 % |

Un mur de la queue compte quatre porteurs — mais **le premier en détient
99,7 %**. Les trois autres sont de la poussière. Ces murs ne sont pas de la
profondeur agrégée : **c'est un acteur unique**, entouré de miettes.

## 2. RÉCIDIVE — toujours les mêmes

| | 10/12 | 11/12 |
|---|---|---|
| porteurs dominants distincts | 161 | 158 |
| **part de la masse portée par les 10 premiers** | **97,7 %** | **97,7 %** |

**Dix portefeuilles portent 97,7 % de la masse des murs de queue.** Et ce sont
les mêmes d'un jour à l'autre : **quatre des cinq premiers sont communs** aux
deux journées — `0x31dea2516bee`, `0xf5a523b17103`, `0xbb475febf78b`,
`0x335f45392f8d`.

**Et trois d'entre eux tradent encore aujourd'hui**, huit mois plus tard :

| portefeuille | transactions en août 2026 |
|---|---|
| `0x31dea2516bee…` | **20 262** |
| `0x335f45392f8d…` | 1 299 |
| `0xbb475febf78b…` | 788 |
| `0xf5a523b17103…` | absent |

Sur **36 854** portefeuilles distincts vus en août.

## 3. CROISEMENT — non, et c'est un résultat

| | 10/12 | 11/12 |
|---|---|---|
| murs où le porteur agresse dans le même seau de 10 s | 222 | 210 |
| part croisée parmi eux | 0,518 | 0,519 |

**Environ 1 % seulement** des murs de queue voient leur porteur agresser dans le
même seau, et **parmi eux c'est un tirage à pile ou face**.

Le porteur d'un mur de queue **n'agresse donc pas l'autre côté au même instant**.
La signature du croisement, mesurée plus tôt dans la nuit sur l'ensemble du
marché, ne s'applique pas à cette population.

**Réserve** : la fenêtre est le seau de 10 s. Un acteur qui poserait puis
agresserait trente secondes plus tard ne serait pas vu. La mesure ferme la
version instantanée, pas toutes.

## Ce que les trois réponses composent

> Les murs qui fuient à l'approche sont posés par **une dizaine de portefeuilles
> identifiables**, qui détiennent chacun **99,7 % du mur qu'ils posent**, qui
> **récidivent d'un jour à l'autre**, et qui **n'agressent pas simultanément de
> l'autre côté**.

C'est un objet beaucoup plus concret que tout ce que la nuit avait produit : non
plus une corrélation, mais **une liste de noms**, vérifiable, persistante, et
dont trois membres sont encore actifs huit mois après.

## Ce que ça ne dit toujours pas

Qu'il s'agisse d'une **manipulation**. Un très gros teneur qui cote seul un
palier et retire quand le prix arrive fait exactement ça, et c'est de la gestion
de risque. Pour trancher il faudrait montrer que le retrait **profite** à celui
qui l'opère — et la mesure du croisement, qui était la voie naturelle, vient de
répondre non dans sa version instantanée.

**La question suivante** : ces dix portefeuilles gagnent-ils quelque chose au
moment où leur mur disparaît ? Fenêtre élargie, position nette, et non plus
seulement l'agression du même seau.
