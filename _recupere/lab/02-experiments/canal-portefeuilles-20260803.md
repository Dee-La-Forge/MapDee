# Le canal des portefeuilles — première exploration

**03/08/2026, 21 h 25** · BTC · jours 20251203, 04, 07
**EXPLORATOIRE.** Rien n'est certifié ici, et rien ne peut l'être : ces jours
sont ceux du verdict CAS D, déjà consommés. Toute certification d'un signal
fondé sur les portefeuilles devra se faire sur la réserve 17-23, jamais ouverte.

Piste ouverte par Meddy : *« Hyperliquid a les informations des transactions et
des wallets qui doivent être mises en relation avec le recorder. »*

---

## Le point de départ

Hyperliquid publie l'identité des deux contreparties de chaque transaction.
**Aucune autre venue ne le fait.** Le recorder s'y abonne depuis le début
(`recorder/adapters/hyperliquid.py`, souscription `trades`, champ `users`) et
**personne n'avait jamais lu ce champ**.

* 239 054 transactions le 03/08 sur BTC, **100 %** avec portefeuilles
* **19 707** portefeuilles distincts en un jour, 35 627 sur trois jours
* l'identité **persiste huit mois** : 33,5 % des portefeuilles actifs de
  l'archive de décembre 2025 tradent encore en août 2026, **41,9 %** parmi ceux
  dont la fuite dépasse 0,90

## Ce qui ne marche pas, et il fallait le savoir d'abord

**`flee_ratio` ne discrimine rien.** C'était l'idée évidente : un spoofeur
annule. Mesuré sur l'archive :

| population | n | ordres | % du notionnel | asymétrie | dist | âge |
|---|---|---|---|---|---|---|
| fuite HAUTE (≥ 0,7) | 264 | 1 711 267 | **99,85 %** | 0,025 | 0,001 | 30 s |
| fuite BASSE (≤ 0,3) | 99 | 78 877 | 0,15 % | 0,205 | 0,003 | 339 s |

La population « fuite haute » **est le marché** : 99,85 % de l'argent, côtés
équilibrés, collée au mid, durée de vie 30 s. C'est de la tenue de marché.
Annuler sans cesse n'est pas spoofer — c'est coter.

Et mesuré directement sur `hl_orders`, la fuite est **saturée à 0,99 pour tout
le monde**, quintile d'impact bas comme haut :

| quintile d'impact | n | fuite | % du flux | rho60 |
|---|---|---|---|---|
| q1 (bas) | 71 | 0,9952 | 0,0008 % | −0,065 |
| q5 (HAUT) | 71 | 0,9961 | 0,1061 % | **+0,174** |

`Spearman(impact, fuite) = +0,030`. **La signature espérée — annuler ET
déplacer le prix — ne sépare pas, parce qu'annuler est universel.**

## Ce qui marche

**Mesure**, sans fuite temporelle : `flux(w,t)` = notionnel posé par le
portefeuille `w` dans `]t−10s, t]`, bid moins ask ; cible = rendement du mid sur
`[t, t+H]`. Source `hl_orders` brut — **pas** les labels, qui sont conditionnés
au contact et sélectionneraient sur le futur. Contrôle d'heure de l'ADR-021
addendum 5 appliqué.

**L'impact varie fortement entre portefeuilles** — rho60 de −0,065 (p10) à
+0,210 (max), pour ~7 900 seaux par jour (écart-type d'échantillonnage 0,011).

**Et il PERSISTE d'un jour à l'autre :**

| | 03 → 04 (1 jour) | 03 → 07 (4 jours) |
|---|---|---|
| rho30 | **+0,937** | **+0,921** |
| rho60 | +0,865 | +0,863 |
| rho300 | +0,616 | +0,623 |

Les 20 meilleurs du jour 03 rendent **+0,225** de rho60 le jour 07, quand la
médiane de tous vaut −0,004. Les 20 pires rendent **−0,155**. **Les deux queues
persistent.** Ce n'est pas de la sur-adaptation : le classement se transporte.

## Le transfert HORS ÉCHANTILLON, une semaine plus tard

Ajouté à 22 h 20, sur les jours d'**exploration** 09 et 10 — jamais utilisés
pour cette question, et d'une autre semaine que les jours d'apprentissage.

| appris sur | testé sur | portefeuilles communs | Spearman rho60 |
|---|---|---|---|
| 03/12 | **09/12** | 318 | **+0,850** |
| 03/12 | **10/12** | 318 | +0,844 |
| 07/12 | 09/12 | 310 | +0,892 |
| 07/12 | 10/12 | 310 | +0,869 |
| 09/12 | 10/12 | 330 | +0,877 |

Et le classement se traduit en écart réel :

| testé sur | 20 meilleurs de la semaine du 03 | 20 pires | médiane de tous |
|---|---|---|---|
| 09/12 | **+0,183** | −0,123 | −0,009 |
| 10/12 | **+0,198** | −0,148 | −0,008 |

**Six jours d'écart, une semaine différente, et le classement tient à +0,85.**
Les deux queues se transportent. Ce n'est ni de la sur-adaptation, ni un régime
de marché particulier à une semaine.

## L'indice est-il UTILISABLE ? — le placebo change la lecture

Ajouté à 22 h 50. Un classement stable ne prouve pas qu'il serve. Test : bâtir
un indice à partir des 20 portefeuilles élus **sur les jours 03-07**, l'appliquer
aux jours **09-10**, et le comparer à trois contrôles.

**Le placebo n'est pas nul.** 200 tirages de 20 portefeuilles actifs au hasard,
H = 60 s, contrôlé par heure :

| | 09/12 | 10/12 |
|---|---|---|
| **placebo, médiane** | **+0,114** | **+0,113** |
| placebo, p95 | +0,173 | +0,185 |
| **ÉLUS (top 20)** | +0,185 | +0,197 |
| **PIRES (bottom 20)** | **−0,186** | **−0,197** |
| tout le monde (348 / 381) | +0,072 | +0,081 |

* tirages au hasard faisant aussi bien que les élus : **0,5 %** et **1,0 %** ;
* tirages au hasard faisant aussi mal que les pires : **0,0 %** et **0,0 %**.

## Ce que ça corrige dans ce qui précède

**La ligne de base n'est pas zéro, elle est à +0,11.** Vingt portefeuilles actifs
tirés au hasard prédisent déjà le prix à +0,11 — c'est le déséquilibre de flux
d'ordres, l'effet le mieux connu de la micro-structure. Les élus n'apportent que
**+0,07 au-dessus de cette base**.

Un premier essai avec un placebo UNIQUE avait donné +0,175 le 10/12, presque
autant que les élus : il aurait suffi à conclure que la sélection ne sert à rien.
C'était un tirage dans la queue haute. Un placebo unique ne prouve rien, ni dans
un sens ni dans l'autre.

**C'est la queue NÉGATIVE qui est remarquable.** −0,19 quand la base est +0,11 :
un écart de 0,30, qu'aucun des 200 tirages n'approche. Ces portefeuilles-là
anti-prédisent le prix de façon fiable et identifiable à l'avance — ce sont
vraisemblablement les teneurs qui s'opposent au mouvement, et ils se repèrent
mieux que ceux qui l'accompagnent.

## Combien ça vaut, en points de base

Un rho ne se dépense pas. Rendement du mid sur 60 s, par décile de l'indice,
jours 09 et 10 :

| jour | indice | décile haut | décile bas | **écart** |
|---|---|---|---|---|
| 09/12 | élus (on suit) | +2,57 bp | −1,68 bp | **+4,25 bp** |
| 09/12 | pires (on fade) | +2,47 bp | −2,09 bp | **+4,56 bp** |
| 10/12 | élus | +2,96 bp | −2,51 bp | **+5,47 bp** |
| 10/12 | pires | +2,62 bp | −2,57 bp | **+5,18 bp** |

Erreur-type ~0,3–0,4 bp : l'écart fait 12 à 15 erreurs-types.

> **CORRECTION du 03/08 à 22 h 55.** J'avais écrit ici « coût aller-retour
> typique 1,5 à 3 bp », puis conclu que **l'écart brut dépassait le coût**.
> **C'est faux, et le chiffre de coût était inventé.** Le tarif réel
> d'Hyperliquid est **0,035 % côté preneur** au palier de base, soit **7,0 bp**
> pour entrer et sortir en preneur (3,8 bp au meilleur palier de volume).
>
> **L'écart brut de 4 à 5 bp est donc INFÉRIEUR au seul coût de transaction.**
> Un aller-retour en preneur ne peut pas être rentable, quelle que soit la
> qualité du signal.

Ce n'est de toute façon pas une stratégie : c'est le **mid**, pas un prix
exécutable ; il faut traverser la fourchette **en plus** des frais ; et l'écart
ne se capte qu'aux déciles extrêmes, soit 20 % des instants.

La seule voie qui resterait est de **poster** au lieu de prendre — 1 bp de frais
maker au lieu de 3,5 — mais on n'est alors plus toujours servi, et le modéliser
honnêtement demande une file d'attente qu'on n'a pas. Le dire est une chose ;
le mesurer en est une autre, et ce n'est pas mesuré.

## LE BACKTEST EXÉCUTABLE : **NÉGATIF**, sans ambiguïté

03/08, 23 h 00. Preneur des deux côtés, aux prix réellement cotés de `hl_book`,
frais 7,0 bp, horizon 60 s, sans recouvrement, seuils calibrés sur la **veille**.
Classement appris sur 03-07, seuils sur le 09, testé sur le **10 et le 11**.

| jeu | jour | aller-retours | moyenne | t | gagnants |
|---|---|---|---|---|---|
| élus (on suit) | 10/12 | 550 | **−6,09 bp** | −13,5 | 20 % |
| élus | 11/12 | 684 | **−6,87 bp** | −20,3 | 18 % |
| pires (on fade) | 10/12 | 841 | **−5,94 bp** | −21,1 | 15 % |
| pires | 11/12 | 871 | **−6,25 bp** | −23,0 | 18 % |

**Les quatre cellules sont négatives, à 13 à 23 erreurs-types.** Ce n'est pas un
résultat ambigu qu'un réglage pourrait retourner.

### Les comptes se ferment, et ils expliquent pourquoi

| poste | bp |
|---|---|
| gain brut par aller-retour, sur le **mid** | **+2,5** |
| traversée de la fourchette (1 $ de tick sur 90 000 $) | −1,1 |
| frais preneur aller-retour (0,035 % × 2) | −7,0 |
| **attendu** | **−5,6** |
| **mesuré** | **−6,1 à −6,9** |

**Et une erreur de lecture de ma part, corrigée ici.** J'avais annoncé « 4 à
5 bp de gain brut ». C'est l'**écart entre deux déciles**, pas le gain d'un
aller-retour : le décile haut rend +2,6 bp et le bas −2,5 bp, donc une stratégie
qui joue les deux gagne la **moyenne**, ~2,5 bp. J'avais compté le double.

Au **meilleur palier de frais** (3,8 bp) : `2,5 − 1,1 − 3,8 = −2,4 bp`. Toujours
négatif.

### Le balayage d'horizons — l'objection que Meddy a soulevée

23 h 05. Conclure sur le seul horizon de 60 s était une faute de raisonnement :
**les frais sont fixes par aller-retour, l'écart de prix grandit avec
l'horizon.** Si l'écart montait à 12 bp sur une heure, les 7 bp deviendraient
payables. Cinq horizons déclarés à l'avance, tous rapportés.

**Sur 20 cellules : 18 négatives, 2 positives.** Les deux positives :

| jour | H | moyenne | n | erreur-type | t |
|---|---|---|---|---|---|
| 10/12 | 1800 s | +34,02 bp | **8** | ±28,98 | +1,17 |
| 11/12 | 3600 s | +10,39 bp | **2** | ±40,52 | +0,26 |

Deux et huit aller-retours. Ce ne sont pas des résultats — c'est ce qu'il reste
quand la règle de non-recouvrement vide l'échantillon.

**Là où le test a de la puissance :**

| horizon | moyenne | t | verdict |
|---|---|---|---|
| 60 s | −5,94 à −6,87 bp | −13 à −23 | **décisif** |
| 300 s | −4,08 à −7,07 bp | −2,8 à −5,8 | négatif |
| 900 s | −1,77 et −7,13 bp | −0,7 et −2,5 | négatif, plus faible |

**L'hypothèse est réfutée.** La perte reste autour de −5 à −7 bp — c'est-à-dire
le montant des frais. L'écart brut ne dépasse jamais 1 à 2 bp, **à aucun
horizon**.

La raison est mesurable : la corrélation décroît **plus vite** que la volatilité
ne croît. `rho` passe de 0,185 à 60 s à 0,072 à 300 s, soit un rapport de 0,39,
quand il aurait fallu 0,45 (= 1/√5) pour que le gain reste constant.

**Réserve honnête** : au-delà de 900 s le test ne conclut plus, faute
d'échantillon. On sait que ça ne paie pas jusqu'à 15 minutes ; au-delà, on ne
sait pas, et l'expérience telle que construite ne peut pas le dire.

### Ce que ça règle

Le signal est **réel** — il est reproduit hors échantillon, ses deux queues se
transportent, sa probabilité sous le placebo est inférieure à 1 %. Et il est
**trop petit pour être négociable à cet horizon avec ces coûts**. Les deux
propositions tiennent ensemble ; la seconde n'annule pas la première.

Ce résultat rejoint le backtest négatif de juillet (−10,8 bp) sur une population
pourtant **complémentaire** — murs qui tiennent alors, flux de portefeuilles
ici. Deux voies indépendantes, deux fois négatif.

## Et c'est calculable EN DIRECT — vérifié

Je craignais que non : l'indice se calcule sur les **poses d'ordres** avec
identité, et le flux public ne donne que les **transactions**. Testé sur le
WebSocket réel : la souscription `orderUpdates` **accepte un portefeuille tiers
nommé** et délivre ses poses en temps réel — **1 513 mises à jour en 45 s** pour
trois portefeuilles, avec prix, taille, côté, instant et `oid`.

Le montage tient donc debout : **classer hors ligne** sur l'archive L4 (le
classement persiste à +0,85 d'une semaine à l'autre, donc il ne se refait pas
souvent), puis **suivre les élus en direct** par `orderUpdates`.

## Les deux confondeurs écartés

**Ce n'est pas la dominance de flux.** L'effet le mieux connu de la
micro-structure est que le déséquilibre du flux d'ordres prédit le prix — un
gros acteur le reproduirait trivialement. Or :

* les 20 plus **gros** flux ont un rho60 médian de **−0,074** (ils s'opposent au
  mouvement : tenue de marché classique) ;
* les 20 plus fort **impact** portent **0,08 %** du flux — ils sont minuscules.

**Ce n'est pas le momentum.** Rendement passé (10 s) contre futur : +0,077 à
30 s, +0,057 à 60 s, **−0,003 à 300 s**. Un portefeuille qui ne ferait que
suivre le mouvement ne pourrait hériter que de cela — et rien du tout à 300 s,
où le signal vaut encore +0,14 pour les meilleurs.

## Ce que ça N'EST PAS — à lire avant d'y croire

1. **Ce n'est pas de la détection de spoofing.** La preuve manque, et elle
   manque dans le mauvais sens : les portefeuilles à impact n'annulent pas plus
   que les autres. Un spoofeur devrait se distinguer par là. Ils ne s'y
   distinguent pas.
2. **La causalité n'est pas établie.** Reste possible : ces portefeuilles
   **réagissent** à une information infra-10 s qui déplace ensuite le prix. Ils
   seraient rapides, pas manipulateurs. Pour une stratégie qui les SUIT, la
   distinction importe peu ; pour comprendre le marché, elle est décisive.
3. **Ce n'est pas une stratégie.** Un rho de 0,20 est une corrélation. Aucun
   coût, aucun slippage, aucun dimensionnement n'a été calculé.
4. **BTC seul, cinq jours** — 03, 04, 07 (semaine consommée) et 09, 10
   (exploration). Aucun autre symbole n'a été regardé.
5. **Hyperliquid seul.** Binance ne publie aucune identité : ce canal **ne se
   transfère pas** tel quel. Sa valeur sur Binance dépendrait du couplage des
   prix par arbitrage, non mesuré ici.

## Ce que ça change pour le programme

Le projet cherchait un signal dans la **forme du carnet** (E1, E2), qui exige de
la profondeur — d'où le carnet profond, l'élargissement de `SNAP_BAND`, et la
limite du flux public Hyperliquid.

Ce canal-ci ne demande **aucune profondeur**. Il demande une identité, qu'on
capte déjà, et une table de réputation qu'on peut construire hors ligne. C'est
une seconde voie, indépendante d'E1, et beaucoup moins chère à observer.

**Le transfert hors échantillon est fait** (section ci-dessus) : le classement
tient à +0,85 une semaine plus tard.

**Ce qui reste, et qui est le vrai verrou** : l'impact est **mesuré, pas
prédit**. Aujourd'hui, pour savoir qu'un portefeuille compte, il faut avoir
observé une journée entière de son activité contre le prix. Un signal qui exige
de connaître le futur ne sert à rien — sauf que la **persistance** le sauve
partiellement : le classement d'hier prédit celui de demain à +0,85, donc une
table de réputation construite hors ligne est utilisable en direct dès le
lendemain.

Reste à savoir **quels traits observables** portent cette persistance — taille
relative à sa propre norme, cadence de pose, asymétrie, distance au mid. C'est
la question suivante, et elle se traite sur 11-16 sans toucher à la réserve.
