# D2 — la fuite à l'approche, et le contrôle qui retourne la lecture

**04/08/2026, 00 h 08** · BTC · entraîné sur 20251209, testé sur 10 et 11
**RÉPOND À : ADR-001** (détection = apprentissage supervisé)

---

## Pourquoi cette définition

`flee_ratio` de l'ADR-021 vaut **exactement 1,000 pour 99,28 % des murs**
(addendum 10) : il mesure que le prix n'est pas venu, pas une intention. La
définition conditionnelle à l'approche fait du retrait un **choix** :

    approche   le mid vient à moins de TOL du prix du mur, sous 10 min
    FUITE      à l'arrivée du prix, il reste moins de 20 % de la masse

## Le résultat brut

| | 10/12 | 11/12 |
|---|---|---|
| murs approchés | 24,8 % | 24,8 % |
| part FUITE (cible) | 0,267 | 0,222 |
| **AUC hors échantillon** | **0,735** | **0,766** |

Cible équilibrée, échantillon large (294 700 approches). Les traits qui portent :

| trait | AUC seul | |
|---|---|---|
| `f_mult` | 0,739 / 0,771 | taille relative à la médiane de bande |
| `f_taille_moy` | 0,727 / 0,768 | masse **par ordre** — un seul gros ordre |
| `f_croiss` | 0,588 / 0,608 | il grossit |
| `f_age` | 0,436 / 0,441 | un **vieux** mur fuit MOINS |

## LE CONTRÔLE, et il retourne la lecture

`f_mult` élevé désigne une valeur **extrême**, et les extrêmes reviennent vers
la moyenne : un tel palier rétrécirait **même sans que le prix vienne**. On
compare donc chaque mur approché à un mur de **même taille relative** lu au
**même délai**, non approché.

| quintile | mult médian | approché | NON approché | écart |
|---|---|---|---|---|
| 0 | 10,8 | 0,123 | 0,339 | **−0,216** |
| 1 | 19,3 | 0,138 | 0,414 | **−0,276** |
| 3 | 42,7 | 0,224 | 0,477 | **−0,254** |
| 4 | 81,9 | 0,334 | 0,434 | −0,100 |
| **5** | **356,5** | **0,763** | 0,647 | **+0,116** |

**Écart moyen pondéré : −0,125.** L'approche fait fuir davantage dans **7
cellules sur 30**.

### Ce que ça veut dire

**Un mur que le prix atteint tient MIEUX qu'un mur comparable que le prix
n'atteint pas.** Intuitif après coup : un mur que le prix va chercher est un mur
qui existe vraiment.

Donc **l'AUC de 0,74 mesure surtout la réversion des valeurs extrêmes**, pas une
fuite à l'approche. Le détecteur prédit « ce palier anormalement gros va
rétrécir » — ce qui est vrai, et n'est pas de la détection de manipulation.

### Sauf dans la queue

À **356× la médiane de bande**, l'approche fait bien fuir davantage : **0,763
contre 0,647**. C'est la seule population où la signature attendue apparaît.
Elle représente un sixième des murs, et c'est là — et seulement là — que la
question du spoofing garde du sens.

## Ce qui reste vrai malgré le contrôle

`f_taille_moy` — la masse **par ordre** — porte presque autant que `f_mult`
(0,73–0,77 seul). Un mur d'un seul gros ordre ne se comporte pas comme un mur de
cent petits. Ce trait-là n'est pas réductible à la taille, et il n'a pas encore
été soumis au contrôle de réversion. **C'est la mesure suivante.**

## `f_taille_moy` passé au même contrôle — 00 h 20

Demandé par Meddy. Deux volets.

**A. Ajoute-t-il à `f_mult` ?** Son AUC seul vaut 0,727. À l'intérieur de chaque
quintile de `f_mult` :

| quintile de `f_mult` | mult médian | AUC de `f_taille_moy` |
|---|---|---|
| 0 | 11,6 | 0,532 |
| 1 | 21,7 | 0,528 |
| 2 | 33,0 | 0,536 |
| 3 | 64,4 | 0,576 |
| **4** | **251,5** | **0,703** |

**Il n'ajoute rien sur les quatre premiers quintiles.** Son AUC apparente vient
de sa corrélation avec la taille. Il ne discrimine que **sur les plus gros
murs**.

**B. Réversion ou approche ?** Même contrôle, apparié sur la masse par ordre ET
le délai :

| quintile | masse/ordre médiane | approché | NON approché | écart |
|---|---|---|---|---|
| 0 | 23 838 $ | 0,128 | 0,320 | −0,192 |
| 2 | 86 506 $ | 0,205 | 0,445 | −0,241 |
| **4** | **671 861 $** | **0,715** | 0,628 | **+0,087** |

Écart moyen pondéré **−0,107**, l'approche fait fuir dans **7 cellules sur 25**.
Même forme que `f_mult` : il ne survit pas au contrôle, sauf dans sa queue.

## LA CONCLUSION CONSOLIDÉE

Les deux traits porteurs racontent la même chose, et c'est un résultat net :

> **La quasi-totalité des murs est de la profondeur RÉELLE** — le prix qui les
> atteint les fait tenir, pas fuir. **Seule une queue extrême se comporte comme
> une manipulation.**

Cette queue est mesurable et elle n'est pas négligeable :

| critère | murs | % des murs | % de la masse de bande |
|---|---|---|---|
| `f_mult` ≥ 350× | 103 537 | **8,3 %** | **51,2 %** |
| masse/ordre ≥ 500 k$ | 157 467 | **12,7 %** | **58,3 %** |

**Un dixième des murs porte plus de la moitié de la masse de la bande**, et
c'est exactement cette population qui fuit quand le prix arrive.

C'est un déplacement de la question, pas une réponse négative : **la détection
ne doit pas porter sur « les murs », mais sur cette queue-là.** Toutes les
mesures de la nuit — E1, E2, D1, D2 — la noyaient dans neuf dixièmes de
profondeur sincère.

## Trois cibles dégénérées en une nuit — le motif

E1 régressait le rendement sur une fonction du rendement. D1 prenait `flee > 0,5`
sur une variable saturée à 1,000. D2, première version, lisait la masse restante
dans une table **filtrée sur la bande** — or un mur approché quitte la bande,
donc paraissait toujours avoir disparu.

Trois causes différentes, un seul symptôme : **une classe à 100 %**. Et trois
fois, le calcul a été lancé avant que l'équilibre de la cible ne soit regardé.
Un contrôle de trois lignes — la cible a-t-elle deux classes en proportion
raisonnable ? — les aurait toutes attrapées.
