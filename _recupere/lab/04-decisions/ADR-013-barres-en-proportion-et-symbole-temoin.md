# ADR-013 — Barres en PROPORTION, et symbole TÉMOIN vs CERTIFIANT

**Date** : 2026-08-02, 04 h 15 · **Statut** : ACCEPTÉ (Meddy) · **Décideur** : Meddy
· **Écrit AVANT lecture du moindre chiffre du run de relance** — le run lancé à
04:03:58 a été **tué à 04:11, avant qu'il n'écrive un rapport**. Aucun verdict de
la relance n'avait été observé par qui que ce soit au moment où ces deux règles
ont été tranchées. C'est la condition qui donne sa valeur à cet ADR.

## Contexte

Le jalon 1 du 01/08 a rendu le **cas C** (puissance insuffisante) et déclenché la
relance pré-engagée d'ADR-011 §C : +6 jours BTC-only (2026-05-09 → 2026-05-14).
BTC passe donc de 5 à **11 jours**, ETH reste à **5**.

En vérifiant comment la grille est *exécutée* avant de relire le verdict, deux
écarts sont apparus entre ADR-010/011 (le texte) et `p3_train.py` (le code).

## Défaut 1 — la barre se desserrait toute seule quand le banc grandit

`p3_train.py` figeait `BAR1_MIN_FOLDS = 4` et `BAR2_MIN_FOLDS = 3` en **comptes
absolus**, testés par `bar1[s] >= 4`. Les seuils d'ADR-010 (« ≥ 4/5 folds »,
« ≥ 3/5 folds ») sont pourtant des **fractions** :

| folds | barre 1 en compte | ce que ça vaut |
|---|---|---|
| 5 (jalon initial) | ≥ 4 | **80 %** — la barre voulue |
| 11 (après relance) | ≥ 4 | **36 %** — une autre barre |

La difficulté **diminuait automatiquement à mesure qu'on accumule des données**.
C'est l'inverse de ce qu'on veut : accumuler achèterait le verdict. Le commentaire
du code (« seuils absolus gravés (conservateur) ») n'était vrai que dans le sens
*moins de folds* ; dans le sens *plus de folds*, il est anti-conservateur.

### Décision 1

Les deux barres sont exprimées en **proportion des folds**, invariante à la
taille du banc :

```
barre 1 : succès >= ceil(0.8 × n_folds)     (80 % — reproduit 4/5 à n=5)
barre 2 : succès >= ceil(0.6 × n_folds)     (60 % — reproduit 3/5 à n=5)
```

À n = 5, les seuils sont **identiques aux seuils pré-enregistrés** (4 et 3) : ce
n'est pas un nouveau critère, c'est l'expression correcte du critère existant.
À n = 11 : barre 1 ≥ **9**, barre 2 ≥ **7**.

## Défaut 2 — ETH bloquait une certification dont on l'avait déjà dispensé

ADR-011 §C, écrit avant la relance, dit :

> ETH reste à 5 (pas d'autre source gratuite) et **devient témoin de réplication
> directionnelle, pas de certification**.

Cette phrase n'existait nulle part dans le code. `p3_train.py:348` faisait
`all(... for s in syms)` : la barre exigeait **chaque** symbole, ETH compris. ETH
étant à 0/5 à la barre 1 sans donnée nouvelle, le run allait re-rendre **C**
mécaniquement, quel que soit BTC — un verdict produit par une règle qu'on avait
explicitement décidé d'abandonner.

### Décision 2

Un symbole **CERTIFIE** s'il dispose du **jeu de jours complet**
(`n_folds == max(n_folds)`). Les autres sont des **TÉMOINS** : leurs cellules
sont calculées, publiées et lisibles dans le rapport, mais **ne conditionnent
aucune barre**.

Conséquence sur le cas D (« un point d'AUC < 0,5 → arrêt et autopsie ») : D n'est
déclenché que par un symbole **certifiant**. Une cellule témoin sous 0,5 est
listée à part, bruyamment, en **alerte non bloquante** — un témoin alerte, il ne
décide pas.

**Rétro-compatibilité** : à jeu égal (tous les symboles au même nombre de jours),
tous certifient et la règle D s'applique à tous. Le comportement du jalon à
5 jours est donc **inchangé** — le verdict C du 01/08 reste ce qu'il était.

## Ce que ces deux décisions NE sont pas

Ce ne sont **pas** des assouplissements opportunistes. La décision 1 **durcit** la
barre par rapport à ce que le code appliquait (36 % → 80 %). La décision 2 aligne
le code sur une décision déjà gelée le 30/07. Les deux ont été prises **sans
qu'aucun chiffre du run de relance n'ait été produit**, ce qui est précisément la
condition qu'ADR-010 et ADR-011 imposent à toute règle.

## Conséquences

- `confighash` change (le hash couvre config + code) : le rapport de la relance
  ne sera pas confondu avec celui du 01/08.
- Le rapport publie désormais la liste des symboles **certifiants** et des
  **témoins**, et le seuil effectif de chaque barre pour chaque symbole.
- La **clause de fin de boucle** d'ADR-011 §C est inchangée et s'évalue sur les
  symboles certifiants : si la barre 1 ne passe pas sur BTC après cette relance,
  le verdict FINAL est « non certifiable à cette maille d'événement », sans
  troisième essai.
- Toute future relance asymétrique (un symbole enrichi, pas l'autre) est couverte
  par la même règle, sans nouvel arbitrage.
