# 04/08/2026 — Audit du dépôt, et réparation de l'instrument

Première entrée. Le dépôt avait un mois d'existence et zéro ligne de journal :
c'est en soi un des résultats de l'audit.

L'audit portait sur la thèse du dépôt, énoncée en `QUESTION.md:42` :

> une mesure qui n'a pas passé son contrôle négatif ne s'exécute pas

**Elle n'était pas tenue.** Tout ce qui suit est mesuré, pas déduit.

---

## 1. Ce que l'audit a trouvé

### La donnée est bonne — et c'est le meilleur du dépôt

`socle/verifie_donnee.py --jours 20251209`, exécuté :

```
{"coherence interne":       photos 118722, carnets_croises 0, cadence_ms_mediane 1002,
                            trous_sup_60s 1, saut_de_mid_max_pc 0.111}
{"profond contient carnet": ecart_relatif_median 2.16e-08, p95 5.44e-08, paliers_absents 0}
{"masse contre ordres":     paliers_compares 57456, rapport_median 1.0000,
                            p10 0.986, p90 1.0, part_a_10pc_pres 0.8781}
{"transactions ds fourchette": n 982406, part_dedans 0.6026, age_photo_median 84 ms}
{"fills reconcilies":       oid_distincts 559548, part_retrouvee 0.9545}
```

La revendication de `QUESTION.md:48` est exacte : le carnet profond contient
`hl_book` à 2,2 × 10⁻⁸ près, zéro palier absent. Et `c3` — diffs contre statuts,
deux chaînes de production indépendantes — donne un rapport médian de **1,0000**
sur 57 456 paliers. Il n'y a rien à refaire côté données.

**Le problème était entièrement dans la couche de mesure et dans la couche
d'exécution des garde-fous.**

### Faute 1 — la bande nulle de M1 était 2,5× trop étroite

M1 tirait son nul par permutation i.i.d. de `rendement_bp`. Or les fenêtres se
recouvrent : deux observations consécutives partagent 41/42 de leur contenu.

```
acf(rendement) lag 1 = +0,96      acf(asymetrie) lag 1 = +0,73
```

Une permutation i.i.d. détruit cette autocorrélation. La bande obtenue valait
±0,022 = **1,96/racine(8227)** — c'est-à-dire exactement l'erreur-type naïve que
`unite_de_variance` déclare fausse d'un facteur 5,5, imprimée sur la même ligne
JSON que la correction (`n_effectif: 274`). Le dépôt calculait la correction,
l'affichait, et ne s'en servait pas.

Comparaison de trois nuls sur les séries exactes de M1 :

| jour | rho | nul i.i.d. | décalage circulaire | blocs 1 h |
|---|---|---|---|---|
| 1209 | −0,036 | **hors** ±0,022 | dans ±0,061 | dans |
| 1210 | −0,067 | **hors** | **hors** | **hors** |
| 1211 | **+0,038** | **hors** | dans | dans |
| 1212 | −0,014 | dans | dans | dans |

**M1 déclarait 3 jours « hors du nul » sur 4 — dont un au signe INVERSE de sa
propre prédiction.** C'est le scénario P1 → P2, une troisième fois.

### Faute 2 — le seul garde-fou appelé par M1 était inerte

```python
fenetres_disjointes(Q.t_fin_traits.to_numpy(),
                    Q.t_fin_traits.to_numpy(), f"M1 {day}")   # le MÊME tableau
```

La fonction teste `(b < a).sum()`. Avec `b is a`, c'est zéro par construction.
Vérifié sur trois entrées dont 10 000 tirages : **passe toujours**. Aucune
colonne `t_debut_cible` n'était jamais construite. Le garde-fou censé empêcher
la faute d'E1 (+0,866 sur un monde nul) était décoratif.

### Faute 3 — le « mur » n'était pas un mur

`est_mur = mag >= 8 × médiane de la bande` classait :

```
4 598 164 paliers de bande  ->  1 340 763 murs  =  29,16 %
mediane : 163 murs par instant, sur 555 paliers
```

La masse de la bande suit une loi de puissance :

```
f_mult = mag / mediane :  p50 = 1,0   p75 = 14,3   p90 = 63,6   p95 = 141   p99 = 854
```

Le seuil « ×8 » tombe **entre le p50 et le p75**, en plein corps de la
distribution. Pour atteindre le centile supérieur il aurait fallu « ×854 » — ce
qui montre que l'échelle était le problème, pas sa valeur.

C'est la faute d'origine de `sandbox/detect/` (les « événements » à 85-100 %),
atténuée mais pas éliminée : **assez rare pour passer le plafond de 60 % de
`evenement_rare`, trop fréquente pour vouloir dire quoi que ce soit**. Et
`est_mur` n'était de toute façon jamais soumis à ce garde-fou.

### Faute 4 — trois garde-fous sur cinq ne pouvaient pas échouer

| garde-fou | état au 04/08 |
|---|---|
| `controle_negatif` | **n'avait jamais été écrit** — annoncé en `garde:12`, absent du module |
| `fenetres_disjointes` | appelé avec le même argument deux fois → ne peut pas échouer |
| `unite_de_variance` | ne lève que sur `recouvrement < 1` : une faute de frappe, jamais de méthode |
| `equilibre_maker_taker` | vaut 0,5 **par arithmétique** (voir plus bas) |
| `evenement_rare`, `cible_utilisable` | corrects — mais personne ne les appelait |

Sur `equilibre_maker_taker`, mesuré :

```
role : {'maker': 491 203, 'taker': 491 203}      part maker = 0,500000
paires (ts, prix, taille) exactement {maker, taker} : 100 %
```

Chaque transaction est enregistrée **deux fois, une ligne par contrepartie**. La
part maker vaut 0,5 quoi qu'il arrive dans le carnet. Conséquence pratique :
`hl_fills` compte double, et toute mesure future qui en somme un volume sans le
savoir sera fausse d'un facteur 2.

---

## 2. Ce qui a été changé

### `garde/__init__.py` — `controle_negatif` écrit

Nul tiré par **décalage circulaire** : l'appariement `(x_t, y_t)` est détruit,
l'autocorrélation des deux séries reste intacte. Le décalage est toujours
supérieur au recouvrement, sans quoi une part de l'appariement d'origine
survivrait dans le « nul ».

La fonction **ne lève pas** quand la statistique tombe dans la bande — un
résultat dans le nul n'est pas une faute, c'est une réponse. Elle lève quand la
bande ne peut pas être construite honnêtement.

Son selftest encode la faute sur un monde dont la vérité est connue — deux
marches aléatoires **indépendantes** :

```
rho = +0,034
nul i.i.d.          largeur 0,063  ->  DECLARE SIGNIFICATIF   (faux)
nul par decalage    largeur 0,966  ->  ne le declare pas      (juste)
```

### `mesures/m1_retrait_asymetrique.py`

* branché sur `controle_negatif` ;
* `i_fin_traits` et `i_debut_cible` construits par des **chemins séparés**, de
  sorte que `fenetres_disjointes` compare deux quantités qui peuvent diverger.
  Vérifié : passe sur la conception actuelle, **lève** si l'on recule la cible
  d'un seul pas ;
* `RECOUVREMENT = (W_S + H_S) // PAS_S = 42`, et non `H_S // PAS_S = 30` : deux
  observations consécutives partagent la fenêtre de traits **et** l'horizon ;
* le contrôle `bs.nunique() != 1`, présent dans `socle.carnet` et perdu dans la
  recopie, est rétabli ;
* `len(Q) < 200` testé **après** le `dropna`, pas avant.

### `socle/carnet.py`

`MUR_MULT = 8.0` → `MUR_QUANTILE = 0.98`. Un mur est un palier du centile
supérieur de la bande **à cet instant**. Le quantile ne dépend pas de la forme
de la loi ; un multiple de la médiane en dépend entièrement.

`charge()` soumet désormais `est_mur` à `evenement_rare(plafond=5 %)`. Résultat :

```
murs : 95 739  (2,08 % des paliers, mediane 12 par instant)
avant :         29,16 %,           mediane 163 par instant
```

### `socle/verifie_donnee.py`

`equilibre_maker_taker` retiré. Remplacé par `lignes_par_transaction`, qui
mesure la **convention** au lieu de la maquiller en contrôle : il vaut 2, et
c'est une information dont les mesures futures ont besoin.

---

## 3. Le résultat, après réparation

`python mesures/m1_retrait_asymetrique.py --jours 20251209 20251210 20251211 20251212`

| jour | rho | ancien nul (largeur) | nouveau nul (largeur) | avant | après |
|---|---|---|---|---|---|
| 20251209 | −0,0364 | 0,0447 | 0,1021 | hors | **dans** |
| 20251210 | −0,0669 | 0,0438 | 0,0967 | hors | hors |
| 20251211 | **+0,0375** | 0,0419 | 0,1101 | hors | **dans** |
| 20251212 | −0,0140 | 0,0471 | 0,1284 | dans | dans |

```
{"AGREGE": {"jours": 4, "rho_moyen": -0.01991,
            "IC95_Student": [-0.08993, 0.05011], "exclut_zero": false,
            "jours_du_signe_predit": 3}}
```

`n_effectif` : 274 → 195.

**Les `rho` sont inchangés.** Ce n'était pas la mesure qui était fausse, c'était
le jugement porté sur elle. Trois jours « significatifs » sur quatre sont
devenus un.

### Verdict sur M1

**M1 ne détecte rien.** L'IC agrégé contient zéro, un jour sur quatre survit à
un nul correct, et un jour va dans le sens opposé à la prédiction.

Ce n'est pas un échec : c'est le premier résultat du dépôt auquel on puisse se
fier, y compris quand il est négatif. Le danger n'a jamais été que M1 ne trouve
rien — il était que l'instrument s'apprêtait à annoncer le contraire.

---

## 4. Ce qui reste ouvert

Rien de ce qui suit n'a été corrigé aujourd'hui.

**Mesure**

1. `m1` **recopie** `socle.carnet` (lignes 78-96 contre `charge()`), alors que
   `carnet.py:14` affirme « les mesures l'appellent, elles ne la recopient pas ».
   La duplication a déjà coûté un contrôle perdu (`bs.nunique`).
2. `PAS_MS = 10_000` est **faux**. Mesuré : `dt` médian = 10 366 ms, exactement
   10 000 dans 0,15 % des cas. Donc `W = 120 s` vaut en réalité 125,0 s (max
   348 s) et `H = 300 s` vaut 312,7 s (max 536 s). Or `hl_book` est cadencé à
   1 002 ms : une grille exacte à 10 000 ms était disponible sans coût, `deep`
   ré-échantillonne ~14× et le fait mal.
3. `Carnet.masse(i, k)` lève `IndexError` dès que `i` et `k` n'ont pas la même
   forme — soit les deux appels les plus naturels. Son selftest passe deux
   tableaux de même longueur et n'exerce jamais le chemin cassé.

**Contrôles**

4. `verifie_donnee.py` n'a **aucun seuil, aucune assertion**, avale toutes les
   exceptions (`:229-232`) et sort toujours en 0. C'est un rapport, pas un
   contrôle : il ne peut rien bloquer.
5. `c2` annonce l'inclusion et teste l'égalité. Empiriquement inoffensif
   aujourd'hui (`paliers_absents = 0`, p95 = 5,4 × 10⁻⁸), mais faux par
   construction si `hl_book` s'élargissait.
6. `c1` ne filtre pas l'âge de la photo. La médiane est de 84 ms, donc l'effet
   est faible, mais la queue n'est pas contrôlée et aucun seuil ne juge le
   60,26 %.
7. **4,55 % des `oid` exécutés n'existent pas dans `hl_orders`** — environ
   25 000 ordres exécutés sans aucun statut enregistré. C'est l'explication la
   plus probable du `rapport_p10 = 0,986` de `c3`. Rapporté sans seuil, donc
   sans conséquence.

**Honnêteté sur la correction du mur**

8. Définir le mur par un quantile rend sa fréquence **paramétrique** : elle vaut
   2 % parce que `MUR_QUANTILE = 0.98`, pas parce que le marché en décide. Le
   `evenement_rare` qui la contrôle est donc lui-même proche de la tautologie —
   sa valeur est la protection contre une régression, pas une découverte.

   Mesuré sur les cinq jours disponibles :

   ```
   20251208  2,09 %   par instant : min 10  med 11  max 12
   20251209  2,08 %                min 10  med 12  max 13
   20251210  2,08 %                min  9  med 12  max 13
   20251211  2,10 %                min 11  med 12  max 13
   20251212  2,08 %                min 10  med 11  max 12
   ```

   **Le compte de murs est désormais quasi constant : 9 à 13, toujours.**
   L'ancienne définition en donnait 95 à 208. On a donc échangé un compte
   variable mais dénué de sens (29 % du carnet) contre un ensemble rare et bien
   défini mais de cardinal fixe. **Conséquence : « combien de murs y a-t-il en
   ce moment » n'est plus un signal exploitable — il l'est par construction.**
   Seules leur POSITION et leur taille relative portent encore de
   l'information. C'est acceptable pour la question posée (« pourquoi le prix
   choisit-il un mur plutôt que l'autre »), qui est une question de position ;
   ça ne le serait pas pour une mesure qui voudrait compter. À rouvrir si une
   mesure future a besoin d'un compte variable.

**Dépôt**

9. Pas de `requirements.txt` ni de `pyproject.toml`. Le `__pycache__` versionné
   est `cpython-310` ; il n'y a pas de Python 3.10 sur la machine, et
   l'interpréteur par défaut échoue sur `ImportError: pyarrow`. Il a fallu
   chercher Anaconda (3.12 / pyarrow 16.1 / pandas 2.1.1 / numpy 1.26.2 /
   scipy 1.13.1) pour exécuter quoi que ce soit.
10. Pas de `tests/`. Les selftests sont des blocs `__main__`, non collectables,
    sans CI. Celui de `carnet` contient un check tautologique (`:145-148`
    d'origine) qui compare deux écritures de la même formule.
11. Base empirique très mince : `deep` = **5 jours, BTC uniquement**. Aucun ETH
    profond. `hl_fills` manque le 20251212. Et le 20251212 est un jour partiel
    (6 134 instants contre ~8 250) pondéré à égalité dans la moyenne agrégée.

---

## 5. Vérification de la correction elle-même

Corriger un instrument avec un instrument non vérifié ne vaut rien. Les
corrections ci-dessus ont donc été auditées à leur tour, sur trois questions.

### A. Régression — la MESURE a-t-elle bougé ?

Le refactor de la boucle de M1 (`i_fin_traits` / `i_debut_cible`) ne devait rien
changer au calcul. Vérifié :

```
20251209  rho -0.03635 (avant -0.03635)  n 8 227 (avant 8 227)  IDENTIQUE
20251210  rho -0.06685 (avant -0.06685)  n 8 248 (avant 8 248)  IDENTIQUE
20251211  rho +0.03754 (avant +0.03754)  n 8 255 (avant 8 255)  IDENTIQUE
20251212  rho -0.01397 (avant -0.01397)  n 6 134 (avant 6 134)  IDENTIQUE
```

### B. Calibration — le nul rejette-t-il 5 % quand il n'y a RIEN ?

Protocole : apparier `asymetrie` d'un jour au `rendement` d'un **autre** jour.
Ces paires sont indépendantes par construction, mais chacune garde son
autocorrélation réelle. C'est le monde nul, sans simulation. 48 paires (chaque
jour coupé en deux moitiés, croisements entre jours différents).

```
nul CORRIGE (decalage circulaire) :  1/48 =  2,1 %   (nominal 5 %)
nul I.I.D.  (ancien)              : 19/48 = 39,6 %   (nominal 5 %)
```

**L'ancien contrôle se trompait 4 fois sur 10.** C'est la preuve directe du
diagnostic, plus forte que la comparaison de largeurs de bande.

Le nouveau rejette 2,1 % : **légèrement conservateur, pas parfaitement
calibré**. Sur 48 paires l'intervalle binomial autour de 1/48 monte à ~11 %,
donc c'est compatible avec 5 % — mais on ne peut pas prouver mieux avec 48
paires, et il penche du côté prudent. Ce biais est probablement dû au fait que
le décalage circulaire préserve aussi les structures lentes (régime de
volatilité, saisonnalité intra-journalière) et les absorbe dans le nul.

### C. Puissance — a-t-on tué la détection ?

Effet injecté dans `y`, d'amplitude croissante, sur le 20251209 :

```
a = 0,05  ->  rho = +0,025   detecte = non
a = 0,10  ->  rho = +0,085   detecte = OUI
a = 0,20  ->  rho = +0,201   detecte = OUI
```

Seuil de détection : **|rho| supérieur à ~0,06**.

**C'est la limite qui gouverne la lecture de M1.** Les rho observés valent
−0,036, −0,067, +0,038, −0,014 : ils sont à la frontière, et un seul la
dépasse. La conclusion honnête n'est donc pas seulement « M1 ne détecte rien »,
mais :

> **M1 est sous-dimensionné pour un effet journalier inférieur à |rho| = 0,06.**
> Un effet réel de cette taille ne serait pas distinguable du bruit avec 4 jours.

Ce n'est pas la même phrase, et c'est celle qui doit figurer dans toute
conclusion tirée de M1.

---

## 6. Note de méthode

Consigne donnée aujourd'hui, à respecter dans ce dépôt : **ne pas présenter une
recommandation déjà arrêtée sous la forme d'un menu à trois options dont deux
sont volontairement mauvaises.** Quand la conclusion est claire, la donner
directement avec son raisonnement. N'ouvrir un choix que si les branches sont
réellement défendables, et alors les présenter à charge égale.

Le même principe vaut pour les mesures de ce dépôt : un contrôle dont on connaît
d'avance le résultat n'est pas un contrôle. C'est la faute qui a produit
`fenetres_disjointes(a, a)` et `equilibre_maker_taker = 0,5`.
