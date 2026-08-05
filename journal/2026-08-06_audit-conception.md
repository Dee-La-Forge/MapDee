# Audit de conception — 06/08/2026

> **Rapport de mesure.** Il porte des constats datés : il ne se réécrit pas, il
> s'errate. Aucun fichier de code n'a été modifié — la construction et la
> capture tournaient pendant l'audit.
>
> **Périmètre** : le dépôt tel qu'il est au commit de `claude/audit-app-design-cmscw3`.
> Lu : les six documents de cadrage, les cinq ADR, les cinq chantiers, le paquet
> `harnais/` (12 modules, 10 fichiers de test), `_recupere/construit/`,
> `_recupere/recorder/`, les scripts PowerShell, le registre et les sorties JSON
> d'ÉS.

---

## 0. Ce qui a été vérifié par exécution, et ce qui ne l'est pas

Conformément à `ETAT.md` §2, chaque constat porte son statut.

| statut | ce que ça veut dire |
|---|---|
| **VÉRIFIÉ** | reproduit par exécution dans cet audit, la commande est donnée |
| **LU** | constat sur le texte d'un fichier — se revérifie en l'ouvrant |
| **JUGEMENT** | raisonnement, pas mesure. À contester. |

Environnement de vérification : Python 3.11, numpy 2.4.6, scipy 1.17.1,
pyarrow 25.0.0 — **pas les versions épinglées** de `requirements.txt`
(3.10.7 / numpy 2.2.6 / scipy 1.15.3). Aucun des constats ci-dessous ne dépend
d'une différence de version : ils portent sur la structure du calcul, pas sur
une valeur numérique fine.

**Suite de tests** : `python -m pytest harnais/tests -q` →
**64 passés, 2 ignorés, 24 s**. Voir F12 pour les deux ignorés.

---

## 1. Les cinq constats qui arrêtent quelque chose

### F1 — `boucle.tour()` **lève** dès que J3 et J8 coexistent — VÉRIFIÉ

C'est le constat le plus urgent, parce qu'il se déclenche **exactement au
moment prévu par la file de reprise** : quand la construction livre les jours
12-16 et que le périmètre J8 devient complet.

`e0_reel.aligne()` (harnais/e0_reel.py:102) groupe les séries **par longueur** et
aligne chaque groupe séparément — J3 et J8 sortent donc avec des longueurs
différentes, ce qui est correct et voulu. Mais `boucle._avance_un`
(harnais/boucle.py:85) compare ensuite **tout candidat vivant à tout autre**,
sans regarder le périmètre :

```python
rho = spearman(series[nom], series[autre])
```

`spearman` finit sur `np.corrcoef(rx, ry)` : deux vecteurs de tailles
différentes → `ValueError`. Cette exception **n'est pas** `RefusEpreuve`, donc
`tour()` (harnais/boucle.py:137) ne l'attrape pas et le tour entier meurt.

Reproduit :

```
=== D. tour() sur des series de longueurs differentes (J3 + J8) ===
  longueurs: {'A1': 3000, ..., 'D1': 8000}
  !! tour() LEVE: ValueError all the input array dimensions except for the
     concatenation axis must match exactly
```

Conséquences :

1. **aucun candidat n'est jugé** — le tour s'arrête au premier candidat J3 qui
   rencontre D1 (J8), c'est-à-dire au premier de la liste ;
2. si le tour avait commencé par un dépôt, **le registre porte déjà ses lignes**
   quand le crash arrive. Il n'y a ni transaction ni rollback, et le registre
   est en ajout seul par construction : un tour à moitié écrit ne se retire pas.

`05` §4 dit « le même périmètre sert à É0 et à É2 **pour un candidat donné** ».
Il ne dit **rien** du cas où deux candidats ont des périmètres différents — ce
n'est donc pas seulement un défaut de code, c'est un **trou de protocole**.
Trois candidats sont en J8 (B4, D1, D2), treize en J3 : le cas est le cas
nominal, pas un bord.

*Ce que ça n'est pas* : ce n'est pas un problème d'alignement temporel qu'on
règle en tronquant. Corréler A1 (3 jours) à D1 (8 jours) n'a pas de sens même
avec des longueurs égalisées ; il faut décider **par ADR** si É0 se fait sur
l'intersection des périmètres, ou si É0 ne compare que des candidats de même
périmètre. Le code ne peut pas trancher ça tout seul.

### F2 — un NaN dans une série **élimine** des candidats, avec `ρ=nan` — VÉRIFIÉ

`stats.spearman` ne se protège pas des NaN. `rangs()` les classe (rankdata les
met en fin), `np.corrcoef` rend `nan`. Et dans la boucle :

```python
if abs(rho) < SEUIL_E0_DOUBLON:
    continue          # nan < 0.90 est FAUX → on n'entre pas ici
...
registre.ajouter(..., "éliminée", "É0", f"ρ={abs(rho):.3f} — même objet …")
```

`abs(nan) < 0.90` vaut `False`, donc le chemin d'élimination est pris. Reproduit :

```
rho(NaN, y) = nan  -> abs(rho) < 0.90 ? False  => la boucle ELIMINE
```

Le registre écrirait `ρ=nan — même objet que X, on garde le moins cher`. Une
élimination définitive, avec un chiffre qui n'en est pas un, dans un fichier
qui ne se corrige que par ajout.

Le garde-fou d'`e0_reel.aligne()` retire les photos NaN — mais il ne couvre pas
tout : une série **entièrement** NaN rend `garde` entièrement faux, toutes les
séries deviennent vides, et `spearman` sur deux vecteurs vides rend `nan`
(VÉRIFIÉ). On retombe sur le même chemin, pour **tous** les candidats.

Le cas n'est pas théorique : `b1_hazard` est `nan` partout si `presents_prec`
est nul, `d1_ralentissement` si la masse de bande est constante sur la fenêtre,
`a4_microprice` si un côté est vide dans la bande. Sur 6 jour-symboles réels,
au moins un jour dégradé suffit.

### F3 — É2 et É0 n'ont pas la même sémantique du NaN — VÉRIFIÉ / JUGEMENT

Même valeur `nan`, deux comportements opposés :

* É0 (`boucle`) : `abs(nan) < 0.90` → faux → **élimine** ;
* É2 (`epreuves.e2:86`) : `if rho > pire` → faux → `pire` reste `0.0` → le
  candidat **passe** à É3 avec `ρmax=0.000`.

Un candidat dont la série est cassée est donc éliminé à É0 et déclaré propre à
É2, selon le point où le NaN apparaît. Aucune des deux réponses n'est un refus.
`05` §5 exige un chiffre sur toute décision ; ici le chiffre existe mais ne
mesure rien.

### F4 — `c2_courbure` ne calcule pas une courbure : c'est un contraste à 2 bins — VÉRIFIÉ

`extracteurs.c2_courbure` (harnais/extracteurs.py:202) :

```python
cum = np.cumsum(s.profil, axis=1)
return np.diff(cum, n=2, axis=1).mean(axis=1)
```

La moyenne des différences secondes d'une somme cumulée **télescope**. Le
résultat est algébriquement égal à :

```
(profil[:, 15] - profil[:, 1]) / 14
```

Les quatorze bins intermédiaires **s'annulent exactement**. Reproduit :

```
c2      : [ -6.72365  -10.8957   -7.021514 -18.022269 -15.139267]
2 bins  : [ -6.72365  -10.8957   -7.021514 -18.022269 -15.139267]
identique: True
```

La docstring annonce « convexité moyenne du profil cumulé de masse en
distance ». Ce qui est calculé est la différence entre le bin le plus lointain
et le deuxième bin, divisée par 14 — c'est-à-dire à peu près l'inverse d'une
mesure de forme : **toute l'information de forme est dans les bins qui
disparaissent**. La fiche C1 est « concentration » et C2 « forme et courbure » ;
sous cette formule, C2 mesure surtout la masse lointaine, ce qui la rapproche de
T0 plutôt que de C1.

Ça n'est pas un bug d'exécution — le code tourne, rend des nombres, et les
tests passent. C'est un écart entre l'intention déclarée et le calcul. Il
arriverait jusqu'à un verdict d'É0/É2 sans jamais lever.

### F5 — le `protocole_hash` du préflight n'est écrit nulle part — LU

`preflight.run()` se termine par :

```python
return {"protocole_hash": _git(depot, "rev-parse", "--short", "HEAD").strip()}
```

et sa docstring dit « Rend le hash du protocole **à inscrire dans chaque ligne
de registre du run** ».

Or `registre.ajouter()` a sept champs — `date, nom, etat, epreuve, chiffre,
perimetre, proposee_par` — et **aucun** n'est le hash. `boucle` n'appelle jamais
le préflight et ne reçoit jamais son retour ; `e0_reel` l'appelle, imprime le
hash à l'écran, et le jette. Aucune ligne du registre actuel ne porte de
commit.

`01_Cahier_des_charges.md` §8 : « le `confighash` doit couvrir le code qui
**rend le verdict**, pas seulement celui qui calcule. » Aujourd'hui il ne couvre
ni l'un ni l'autre au niveau de la ligne : la seule trace est la date, et
plusieurs versions du code peuvent partager une date. C'est le seul manquement
d'audit trouvé qui contredit frontalement une exigence écrite du cahier des
charges.

---

## 2. Le point de méthode le plus lourd

### F6 — ÉS n'a pas validé la méthode du banc. Elle a validé un autre détecteur. — VÉRIFIÉ (traçage d'appels) / JUGEMENT (portée)

C'est le constat qui a le plus de conséquences, parce que trois lignes du
registre en dépendent et qu'elles gouvernent l'interprétation de tous les
futurs négatifs.

**Le fait.** La statistique d'ÉS est `_rho_run_v2` (harnais/es_campagne_v2.py:85) :
masse au palier étiqueté `k*`, normalisée par la médiane des voisins à même
distance du mid, corrélée à un label binaire de présence, Student sur 8 runs.

Traçage des appels dans tout le dépôt :

```
_rho_run_v2 → es_campagne_v2.py, es_campagne_v3.py, es_campagne_v4.py
              ET NULLE PART AILLEURS
```

`boucle.py`, `epreuves.py`, `extracteurs.py` n'importent que `stats.spearman`,
`stats.spearman_partiel`, `stats.student_jours`. **Aucune ligne du chemin
É0→É4 n'exécute la statistique validée par ÉS.**

**Ce qui transfère réellement**, et il faut le dire, c'est réel :

* `student_jours` — l'unité « le jour », l'IC, la p-value : même code ;
* la table de puissance (`d ≳ 1,2` sur 8 jours) — c'est une propriété de
  Student, indépendante de la statistique d'entrée ;
* la dérive en `k/n` du Spearman partiel — propriété de `spearman_partiel`
  lui-même, mesurée sur lui. La règle `n ≥ 100 k` est fondée.

**Ce qui ne transfère pas** :

* les **planchers de détection** (0,5× absorption, 1,0× recharge, 8,0× leurre).
  Ils caractérisent un détecteur *informé du lieu*, sur une grandeur *construite
  pour le mécanisme*. Ils ne disent rien de la sensibilité d'A1, B1, C1… à
  l'absorption, parce que ces grandeurs ne sont pas cette statistique ;
* la ligne du registre « leurre ÉCARTÉ — **aucun négatif leurre ne sera
  interprétable avec cette méthode** ». Prise au mot, elle affirme une propriété
  du banc. Elle est établie pour `_rho_run_v2`, pas pour le banc.

**Le sens dans lequel c'est encore vrai**, et c'est important : ÉS reste une
borne **optimiste** — le détecteur d'ÉS connaît `k*`, les candidats ne le
connaîtront pas. Un mécanisme qu'un détecteur informé ne trouve qu'à 8× ne sera
pas trouvé mieux par un détecteur aveugle. Donc « leurre écarté » **tient comme
borne supérieure de sensibilité**, ce qui est le sens utile. Ce qui ne tient
pas, c'est la lecture symétrique : « absorption ADMIS à 0,5× » ne garantit
**rien** sur ce que le banc réel détectera à 0,5×.

Formulation qui serait exacte, à porter au registre par ajout :

> plancher mesuré **pour le détecteur d'ÉS informé du lieu**, borne optimiste ;
> la sensibilité du banc É0-É4 sur les 16 candidats n'est pas mesurée.

### F7 — le bras nul du leurre porte un biais de −0,14 non corrigé — VÉRIFIÉ (lecture du JSON produit)

`journal/es-campagne-v4-20260805.json` :

```json
"leurre": {"moyenne": -0.1376, "ic95": [-0.3110, +0.0358],
           "taux_fausses_detections": 0.0, "passe": true}
```

Le bras nul est déclaré passé sur deux conditions (es_campagne_v4.py:116) :
l'IC contient 0, **et** le taux de fausses détections est ≤ 10 %. Les deux sont
satisfaites. Mais :

* la moyenne du nul est **−0,138**, soit 80 % de la demi-largeur de l'IC. Ce
  n'est pas un estimateur centré, c'est un estimateur biaisé dont le bruit
  suffit à couvrir zéro **sur 16 graines** ;
* le taux de fausses détections est exactement **0,000**, et il est calculé
  **unilatéralement** — `s["p_value"] < ALPHA and s["moyenne"] > 0`. Un
  estimateur biaisé vers le bas produit mécaniquement FP = 0 vers le haut.
  Le FP nul n'est pas un signe de calibration ici, c'en est le contraire ;
* `CENTRES["leurre"] = False` : le biais n'est pas soustrait. Il est donc
  reporté tel quel sur les bras injectés, où il **retranche 0,14 à chaque ρ**.

Le plancher leurre à 8,0× est donc mesuré sous un décalage systématique
défavorable. La conclusion pratique — « la méthode n'est pas calibrée pour le
leurre » — reste juste ; c'est le **chiffre 8,0** qui n'est pas une sensibilité
propre, et v3 a déjà montré que le centrer casse le FP. Le dire ainsi au
registre serait plus solide que de publier un plancher.

Deux points connexes, plus petits :

* **n = 16, pas 32.** `GRAINES_NUL_V4` fait 32 graines, dont 16 vont à la
  calibration de μ⁰ et 16 à la vérification. Le rapport et `ETAT.md` parlent de
  graines neuves — c'est exact — mais l'IC de vérification repose sur 16
  points, pas 32. Pour l'absorption, μ⁰ = −0,368 est estimé sur 16 points
  (erreur type ≈ 0,09) puis soustrait comme une **constante** à tous les bras :
  le plancher 0,5× hérite de cette incertitude, qui n'est propagée nulle part ;
* le FP bootstrap rééchantillonne **avec remise** 16 valeurs pour former des
  échantillons de 8, et teste leur moyenne contre 0. Ce n'est pas un taux
  d'erreur de type I calibré : c'est une mesure de la distance entre la moyenne
  empirique de ces 16 nuls et zéro. Avec 16 tirages, le résultat est largement
  déterminé par le signe de cette moyenne.

### F8 — un « jour » synthétique fait 600 photos, un jour réel en fait 345 600 — LU

`es_campagne.DUREE_S = 150.0`, `PAS_MS = 250` → 600 photos par run. Un
jour-symbole réel à 250 ms fait 86 400 / 0,25 = **345 600 photos**, soit 576×
plus.

Ça n'invalide pas la table de puissance (elle est en unités « jour »), mais ça
touche les planchers : la précision d'un ρ par run croît avec √n. Un plancher
mesuré sur 600 photos est plus pessimiste que le même sur 345 600 — ce qui joue
en faveur de la prudence, donc ne casse rien. À écrire quand même : les
planchers ne sont pas transposables tels quels, dans un sens **ni** dans
l'autre.

---

## 3. Les extracteurs — deux confusions structurelles

### F9 — la bande est centrée sur le mid **courant** : elle glisse avec le prix — VÉRIFIÉ

`extracteurs.charge` (harnais/extracteurs.py:67) filtre à chaque photo :

```python
garde = np.abs((k + 0.5) * bs - mid) <= mid * dist_max
```

`mid` est le mid **de cette photo**. La fenêtre d'observation suit donc le prix.
Conséquence mécanique : chaque déplacement du mid de X paliers fait **entrer**
X paliers d'un côté et **sortir** X paliers de l'autre — sans qu'aucun ordre
n'ait bougé. Or `add`, `rem`, `disparus`, `presents_prec` sont tous calculés en
comparant l'ensemble des paliers *vus* d'une photo à l'autre. Ils comptent donc
le glissement de fenêtre comme du flux d'ordres.

Mesuré sur un carnet **zero-intelligence sans aucune injection**, généré par
`harnais/generateur.py` (graine 7, 300 s, 1 200 photos) :

```
rho(taux de disparition BRUT, |delta mid|) = 0.424
rho(B1 · hazard rate, |delta mid|)         = 0.452
```

0,42-0,45 de corrélation de rang entre une grandeur du banc et le mouvement du
prix, **sur un livre où rien ne réagit au prix**. Ce n'est pas un phénomène,
c'est la fenêtre.

Pourquoi ça compte particulièrement ici : `01` §5 pose que **la cible est le
déplacement du prix**. Une grandeur mécaniquement couplée à |Δmid| par sa
définition d'observation arrivera à É4 avec une corrélation à la cible qui ne
vient pas du marché. Et É0/É2, qui ne voient pas la cible, ne peuvent pas
l'attraper : ils corrèlent les candidats entre eux, et *tous* les candidats de
bande partagent ce même artefact — ce qui les rend **artificiellement
semblables**, donc candidats à l'élimination mutuelle à É0 au seuil 0,90.

Atténuations réellement présentes dans le code, à porter au crédit :

* B1 et D1 entrent « en écart à leur ligne de base » (correction II.2), ce qui
  retire la dérive lente — pas les à-coups, qui sont précisément ce qui
  corrèle ;
* la mesure ci-dessus est faite sur un mid synthétique peu mobile. Sur données
  réelles l'effet peut être plus faible **ou** plus fort ; il n'est pas mesuré.

C'est le constat qui mériterait une mesure dédiée avant le premier É0 réel :
recorréler chaque série extraite à |Δmid| **sur le jour de banc**, et publier
la table. C'est bon marché, et ça se fait avant que le registre n'écrive quoi
que ce soit.

### F10 — le palier du mid (`k0`) est exclu des deux côtés — LU / VÉRIFIÉ partiellement

Dans `charge` (harnais/extracteurs.py:109) :

```python
for cote, sel in ((0, kk < k0), (1, kk > k0)):
```

Les lignes à `kk == k0` ne sont dans **aucun** des deux côtés. Elles sont donc
absentes de `m_tot`, `herf`, `best_k`, `best_m`, `add`, `rem` — donc de A1, A4,
C1, T0. Mais elles **sont** comptées dans `s.profil` (ligne 118-120, qui utilise
`kk` sans filtre de côté), donc dans C2. Et dans la boucle de transitions
(ligne 130), `cote = 0 if k < k0 else 1` range `k0` **du côté ask** — donc `k0`
contribue à `rem`/`add` par un chemin et pas par l'autre.

Trois traitements différents du même palier dans la même fonction.

Ce que ça vaut en pratique dépend de la fréquence des lignes à `k0` dans le
`deep` réel, que je n'ai pas pu mesurer (pas d'artefact sur cette machine).
L'ordre de grandeur : à BTC ≈ 90 000 $ et `BIN_REL = 2,5e-5`, `bs = nice(2,25)
= 2 $`. Un spread de quelques dollars signifie que **meilleur bid et meilleur
ask tombent souvent dans le même palier ou dans des paliers adjacents** — donc
que `k0` porte régulièrement le haut du carnet. Si c'est le cas, ce sont les
paliers **les plus informatifs** qui sont silencieusement retirés d'A1, A4, C1
et T0.

**Et le générateur ne peut pas le révéler** : il dépose exclusivement à
`k0 ± d` avec `d ≥ 1` (harnais/generateur.py:138). Vérifié — sur 200 photos
synthétiques, **zéro** ligne à `k0`, 0,000 % de la masse. Le banc synthétique
n'a donc jamais exercé le cas, par construction. C'est un exemple net de la
limite d'ÉS notée en F6 : le générateur ne couvre pas la région que les
extracteurs traitent de façon incohérente.

*Une mesure d'une ligne sur le premier `deep` livré tranche* : quelle fraction
des lignes, et quelle fraction de la masse, portent `k == floor(mid/bs)`.

---

## 4. Hygiène de code et d'instrument

### F11 — `epreuves.e0()` est testé mais jamais exécuté ; la boucle en a une seconde version — LU

`epreuves.e0` existe, est couvert par deux tests (`test_epreuves.py:12,17`), et
n'est appelé **par aucun code de production** : `boucle` importe `e1, e2, e3,
e4` et `SEUIL_E0_DOUBLON`, puis réimplémente É0 en ligne (harnais/boucle.py:79-100).

Les deux versions ne font pas la même chose :

| | `epreuves.e0` | la boucle |
|---|---|---|
| coût inconnu | `couts.get(nom, 0.0)` → l'autre est réputé **gratuit** | `cout_rang` de la fiche, toujours présent |
| ex æquo | non traité | ordre de déclaration de `03` |
| candidats déjà éliminés | comparés quand même | exclus du jeu |

La boucle a raison sur les trois points (le commentaire ligne 76-79 documente
même le bug attrapé). Le problème n'est pas la logique : c'est que **les tests
unitaires d'É0 valident une fonction que le banc n'appelle pas**. La logique
réellement exécutée n'est couverte que par le test d'intégration.

`SEUIL_E3_RANG = 0.60` est également déclaré et jamais lu (É3 lève toujours).

### F12 — deux tests s'auto-ignorent sur toute machine sans `data/` — VÉRIFIÉ

```
SKIPPED harnais/tests/test_generateur.py:28: aucun artefact deep construit sur cette machine
SKIPPED harnais/tests/test_grille.py:45:     aucun artefact deep construit sur cette machine
```

Ce sont **exactement** les deux contrôles annoncés par `ETAT.md` §4 : « grille
et schéma vérifiés **bit à bit** contre un artefact `deep` réel ». Ce sont aussi
les deux qui portent l'histoire la plus coûteuse du projet — la grille en deux
exemplaires divergents, 76 % de paliers faux sur ETH (`harnais/grille.py:10-12`).

Un test qui s'ignore silencieusement quand sa donnée manque relève exactement de
`01` §6 : « un contrôle dont on connaît le résultat n'est pas un contrôle ». La
suite affiche « 64 passés » et ne dit pas que les deux seuls contrôles
bit-à-bit n'ont pas tourné. Il n'y a pas de CI (`.github/` absent) : rien
n'exécute jamais ces deux tests hors de la machine de Meddy.

*Le correctif tient en une variable d'environnement* : `MAPDEE_EXIGE_DEEP=1`
qui transforme le skip en échec, positionnée sur la machine qui a `data/`.

### F13 — l'enregistreur de production ne s'importe pas depuis ce dépôt — LU

`_recupere/recorder/` importe `gondetect.config` dans six fichiers
(`engine.py:27`, `run.py:26`, `store.py:23`, `server.py:15`,
`adapters/base.py:19`, `adapters/binance.py:16`). Le paquet `gondetect`
n'est pas dans le dépôt. `_recupere/construit/__init__.py:17` documente que la
migration a remplacé « les imports `gondetect.*` par `construit.*` » — **pour
`construit/` seulement**. `recorder/` n'a pas été migré.

Conséquence : le code qui **acquiert la donnée** n'est pas reproductible depuis
le dépôt, alors que le code qui la **transforme** l'est. Toutes les constantes
qui définissent la capture — `SNAP_MS`, `SNAP_BAND`, `BIN_REL`, `STALE_MS`,
`FLUSH_MS`, `VENUES`, `REF_VENUE` — vivent hors dépôt et hors manifeste.
`empreinte.py` enregistre `SNAP_MS` et `BIN_REL` dans les manifestes, ce qui
couvre la valeur mais pas le code qui l'applique.

C'est le pendant exact du constat qui a fait naître `construire_decembre.ps1` :
« une fabrication dont la recette n'est pas versionnée n'est pas
reproductible ». Il s'applique encore à l'acquisition.

### F14 — écriture bloquante dans la boucle d'événements du recorder — LU / JUGEMENT

`store.Writer.flush()` appelle `gzip.compress(..., compresslevel=6)` puis
`open(...).write()` **de façon synchrone**, et `engine.flush_loop`
(engine.py:230) l'appelle depuis une coroutine sans `run_in_executor`. Pendant
la compression, la boucle asyncio est arrêtée : ni lecture WebSocket, ni
`sample_loop`.

De même, `sample_loop` (engine.py:202) parcourt l'intégralité des deux
dictionnaires de carnet de **10 flux** à chaque tick de 100 ms, dans la boucle.

Deux effets attendus, cohérents avec ce que le diagnostic C8.4 a déjà observé
(« Binance en resync 5 fois en 40 min ») :

* de la **gigue** sur l'horodatage des photos — or `01` §7 exige de prouver que
  les horodatages sont cohérents avant toute IA ;
* `sample_loop` fait `nxt += period` **avant** le sleep : après un blocage,
  `nxt` est en retard et la boucle rattrape en rafale, produisant plusieurs
  photos quasi simultanées au lieu de déclarer un trou. Le retard est absorbé
  silencieusement, alors que la doctrine du fichier est « les trous sont
  écrits ».

À mesurer avant d'en conclure quoi que ce soit : la distribution des écarts
`t[i+1] − t[i]` sur une journée de capture. Si elle est propre, ce constat
tombe.

### F15 — petits défauts, sans conséquence de verdict — LU

| | |
|---|---|
| **périmètre du perdant** | `boucle.py:92-95` : quand É0 élimine `autre`, la ligne de registre porte `f["perimetre"]` — le périmètre **du candidat testé**, pas du perdant. Une élimination J8 peut s'inscrire « J3 ». |
| **motif d'attente inexact** | `boucle.py:71` rend « en attente des données du périmètre … (construction en cours) » pour A2 et B4, qui attendent en réalité **les définitions de B7**. Le motif exact est dans `extracteurs.ABSENTS` et n'est pas remonté. |
| **É1 gratuit, mais inaccessible** | `05` §4 : « seul É1 est réellement du papier ». Dans la boucle, É1 est **après** É0, qui exige des données : les 6 candidats sans extracteur n'obtiendront jamais leur verdict É1, qui ne coûte pourtant rien. |
| **`student_jours` dégénéré** | `stats.py:69` : si tous les coefficients journaliers sont identiques et non nuls, `p_value = 0.0` — donc retenu par BH à coup sûr. Cas rare, mais c'est un `0.0` exact issu d'une dégénérescence, pas d'une mesure. |
| **série constante** | `spearman` rend `0.0` sur une série constante (VÉRIFIÉ). Elle traverse É0 et É2 en silence, alors qu'une grandeur constante sur un jour est un défaut d'instrument. |
| **É0 en O(N²) avec relecture du registre** | `etat_courant()` relit et reparse **tout** le registre à chaque appel, dans la boucle interne d'É0 : ~256 lectures complètes pour 16 candidats. Et chaque paire est corrélée deux fois, chaque `spearman` recalculant les rangs à zéro (2 × `rankdata` sur ~2 M points). Sans conséquence de justesse ; à surveiller quand le catalogue grandira. |
| **jours 09-11 chargés deux fois** | `e0_reel.series_du_perimetre` boucle par périmètre : J3 = 09-11 et J8 = 09-16 se recouvrent, les six jour-symboles communs sont relus intégralement. |
| **`log` inutilisé** | `es_campagne_v4._rhos_nuls(tmp, graines, log)` reçoit `log` et ne s'en sert pas : la calibration de 32 carnets est muette. |
| **message de log faux** | `construire_decembre.ps1:132` imprime « ECHEC sur **08-31** » pour la tranche 08-16. Dans un journal qui sert de pièce. |
| **`aligne()` regroupe par longueur** | `e0_reel.py:107` : deux périmètres de longueur égale par coïncidence seraient alignés comme s'ils partageaient un index. L'hypothèse « même longueur ⇒ même index » n'est pas contrôlée. |

---

## 5. Ce qui est solide, et qu'il faut dire

Un audit qui ne liste que des défauts donne une image fausse. Ce qui suit a été
vérifié et tient :

**La discipline de refus est réelle.** `RefusEpreuve`, `GardeFouViole`,
`PreflightError`, `RegistreRefus` : quatre familles d'exceptions qui lèvent au
lieu d'avertir. `check_gardefous_peuvent_lever()` prouve à **chaque run** que
les garde-fous savent échouer, pas seulement dans la suite de tests — c'est la
réponse directe et correcte à `01` §6, et je n'ai pas vu beaucoup de projets qui
la mettent en œuvre.

**Le bras nul strict du générateur est juste.** `_applique_injections` sort
immédiatement sur `amplitude <= 0` sans toucher le dict, précisément pour ne
pas décaler la consommation du générateur aléatoire (generateur.py:170-172). Le
raisonnement est correct et le commentaire l'explique. *Réserve* : la
réciproque n'est pas vraie — le bras **injecté** ajoute des paliers, donc change
le nombre d'appels à `rng.random()` dans la boucle d'annulations, donc diverge
du chemin aléatoire du nul. Les deux bras ne sont pas appariés en bruit. Avec 8
graines ça se moyenne, mais la variance des planchers en est augmentée.

**Le registre est structurellement en ajout seul.** `registre.ajouter` insère
après la dernière ligne de table et ne peut pas en réécrire une : ce n'est pas
une convention, c'est la seule opération que le module sait faire. Le refus
d'un état hors vocabulaire et d'une élimination sans chiffre est appliqué au
bon endroit.

**Le préflight ne s'auto-exempte pas.** `SORTIES_DECLAREES` est étroit et
justifié fichier par fichier ; `check_manifestes` refuse **et** la provenance
non certifiée **et** l'hétérogénéité des paramètres — c'est-à-dire le mélange
de générations, qui est exactement la faute qui a invalidé les mesures de la
nuit du 04→05/08.

**Le refus d'É3 et d'É4 est un vrai refus.** `e3()` et `e4_refus()` lèvent avec
leur raison, et rien dans le code ne code 100 ms en dur en attendant l'ADR
D12. Un squelette rendant un verdict approximatif aurait été bien plus
dangereux.

**Les corrections de la nuit sont dans le code, pas seulement dans les
documents.** Le vidage de `flow` sur désynchronisation (`state.reset`), le
vidage sur rebase de grille (`engine.update_bs`), le contrôle d'existence de
l'interpréteur dans le `.ps1`, le verrou d'instance : chacune de ces
corrections est une ligne qui échoue bruyamment, conformément à `ETAT.md` §6.
C'est la bonne réponse au constat « une règle écrite en prose n'arrête
personne ».

**Un point de doctrine qui mérite d'être noté** : le projet applique à ses
propres documents la règle qu'il applique aux données (errata contre
réécriture, `01` §8), et `ETAT.md` §2 liste ce qui a été présenté comme établi
sans l'être. Cette section est plus rare et plus utile que tout le reste de
l'appareil de contrôle.

---

## 6. Ordre suggéré, si l'ordre a une valeur

Ce n'est pas une décision — c'est un classement par « ce qui bloque quoi ».

1. **F1** — se déclenche quand la construction livre J8, c'est-à-dire dans les
   heures qui viennent. Demande un arbitrage de protocole (É0 sur intersection,
   ou É0 intra-périmètre), pas seulement un correctif ;
2. **F2 / F3** — un NaN écrit une élimination définitive dans un fichier en
   ajout seul. À traiter **avant** le premier tour réel, pas après ;
3. **F5** — trois lignes (un champ de plus au registre, le hash passé à la
   boucle). Sans lui, aucune ligne du registre n'est rattachable à son code ;
4. **F6 / F7** — reformuler les trois lignes ÉS du registre **par ajout**, dans
   les termes de ce qui a été réellement mesuré. Ne demande aucun calcul ;
5. **F9 / F10** — deux mesures bon marché sur le premier `deep` livré : la
   corrélation de chaque série à |Δmid|, et la fraction de masse à `k0`. Toutes
   deux se font avant le premier É0, et toutes deux peuvent changer
   l'interprétation d'un verdict ;
6. **F4** — décider si C2 doit mesurer une forme ; si oui, la formule est à
   réécrire, et c'est un changement de fiche, donc d'`03` ;
7. **F12 / F13** — hygiène de reproductibilité. Ne bloque aucun calcul, mais
   `F13` est la dernière zone du pipeline qui n'est pas dans le dépôt.

**F8, F11, F14, F15** : au fil de l'eau, ne bloquent rien.

---

## 7. Ce que cet audit n'a pas fait

Par honnêteté sur sa propre portée :

* **aucune donnée réelle n'a été lue** — il n'y a pas de `data/` sur la machine
  d'audit. Tous les constats sur les extracteurs sont établis soit par lecture
  du code, soit sur carnet synthétique. F10 en particulier **attend une mesure**
  pour être quantifié ;
* **les campagnes ÉS n'ont pas été rejouées.** F7 s'appuie sur le JSON produit
  le 05/08, pas sur une réexécution ;
* **`_recupere/construit/jour.py` (811 lignes) n'a été lu qu'en partie** — le
  schéma `deep` et la structure du writer. Les trois défauts que `ETAT.md`
  §3 bis signale déjà (taux de jointure jamais appelé, lignes illisibles jetées
  sans compteur, compteur de qualité mélangeant deux causes) n'ont pas été
  revérifiés : ils sont déjà connus et déjà écrits ;
* **aucun des documents de cadrage n'a été audité pour sa cohérence interne** —
  les ~65 points d'hygiène recensés par l'audit du 05/08 ne sont pas repris ici ;
* **les versions ne sont pas celles épinglées** (§0). Une exécution sous
  Python 3.10.7 / numpy 2.2.6 / scipy 1.15.3 pourrait donner des valeurs
  numériques différentes de celles reproduites ici, mais aucun des constats ne
  repose sur une valeur fine — F1 et F2 sont des chemins de contrôle, F4 est une
  identité algébrique, F9 est un ordre de grandeur.
