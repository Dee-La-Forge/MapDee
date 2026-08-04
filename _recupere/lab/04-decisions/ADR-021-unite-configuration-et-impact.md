# ADR-021 — Changer d'unité : la CONFIGURATION, pas le mur

**Date** : 2026-08-03, 10 h 15 · **Statut** : **GELÉ** avant toute mesure.
Décidé avec Meddy après le verdict CAS D et sept audits adversariaux.

> Aucune donnée d'exploration n'a été ouverte à l'écriture de ce document. Les
> seuls chiffres cités sont descriptifs, issus des jours 01-07 déjà consommés.

---

## Pourquoi on change

Le jalon demande : **« entre ces deux murs, lequel est le plus factice ? »**

Trois mesures disent que la question est mal posée.

**1. Elle n'a le plus souvent pas de réponse.** `y_post` vaut exactement 0 sur
**89,6 %** des lignes, et seules **2,90 %** des paires sont départageables
(|y_i − y_j| > 0,10). Le test dépense sa puissance sur des comparaisons entre
objets équivalents.

**2. Les objets SONT équivalents.** Sur les 7 jours, 417 901 murs — **22,7 %**
du jeu — ont le profil de spoof : moins de 60 s de vie, **×65** la taille des
ordres durables, et **98,6 % de fuite**. Départager deux murs qui fuient tous
les deux à 98,6 % n'a pas de contenu.

**3. La cible récompense l'échec du spoofeur.** Un spoof réussi n'est jamais
exécuté — c'est son but. `y_post` élevé désigne donc un mur qui a été *consommé*,
c'est-à-dire un spoof RATÉ ou un ordre sincère. On apprend à reconnaître ce
qu'on ne cherche pas.

**Ce qui intéresse le projet, c'est l'IMPACT que la configuration produit, même
combinée** — pas le classement de ses composants.

## Le changement d'unité

| | jalon (ADR-019) | ADR-021 |
|---|---|---|
| unité | **un ordre** (palier-instant) | **un instant** et tout ce qui entoure le prix |
| cible | fraction exécutée après contact | **déplacement du prix** sur un horizon |
| direction | « confondeur » (`f_side`) | **intrinsèque** |
| deux murs équivalents | se comparent (indécidable) | **s'additionnent** |

## Définitions FIGÉES

Fixées ici, avant la première mesure. Aucune ne se renégocie après.

**Grille** — un instant tous les **10 s**, la cadence de l'archive de
production. Par symbole.

**Bande** — les paliers à **0,12 % à 0,80 %** du mid, de part et d'autre. C'est
la bande P0 déjà en vigueur pour la sélection des événements.

**Mur** — un palier dont la taille affichée est **≥ 4× la médiane** des paliers
de la bande à cet instant (`WALL_MULT`, déjà en vigueur).

**Factice** — un mur dont les ordres ont été **retirés plutôt qu'exécutés** dans
les 30 s suivant le contact. C'est `flee_ratio`, la vérité L4.

**Masse factice** d'un côté à l'instant t :
`M(t, côté) = Σ_murs (taille affichée × prix × flee_ratio)`

**Déséquilibre** : `I(t) = (M_bid − M_ask) / (M_bid + M_ask)`, dans [−1, +1].

**Cible** — rendement du mid à horizon H : `r(t,H) = (mid(t+H) − mid(t)) / mid(t)`.
**Horizons figés : H ∈ {30 s, 60 s, 300 s}.** Les trois sont rapportés, aucun
n'est choisi après coup.

**Hypothèse directionnelle** — un mur d'achat factice simule de la demande et
pousse le prix **vers le haut**. Donc `I(t) > 0` prédit `r(t,H) > 0`.
**Le signe est prédit à l'avance.** Un effet de signe opposé est un ÉCHEC, pas
une découverte à réinterpréter.

## Deux expériences, dans cet ordre

### E1 — L'ORACLE : le plafond existe-t-il ?

**Explicitement NON CAUSAL, et c'est assumé.** `flee_ratio` n'est connu
qu'après ; E1 utilise la vérité L4 comme si on l'avait à l'instant t.

**Question** : si l'on savait PARFAITEMENT quels murs sont factices, leur
déséquilibre prédirait-il le prix ?

**Pourquoi d'abord** : si la réponse est non, aucune qualité de détection ne
sauve le programme — il n'y a rien à exploiter en aval. Si oui, on connaît le
**plafond** de ce qu'une détection parfaite rapporterait.

**Mesure** : corrélation de Spearman entre `I(t)` et `r(t,H)`, aux trois
horizons, par symbole et par jour, IC par bootstrap sur les jours.

**E1 ne certifie rien.** C'est une mesure de faisabilité.

### E2 — L'ENCADREMENT (la question de Meddy)

**Question** : quand le prix est pris entre un mur d'achat et un mur de vente,
lequel cède, et est-ce prévisible ?

**Encadrement** — à l'instant t, au moins un mur de chaque côté dans la bande.
**Céder** — le premier des deux paliers que le mid **traverse** dans l'heure.
Si aucun n'est traversé, l'événement est écarté (compté à part).

**Pourquoi c'est mieux posé** : la cible est **binaire et à peu près
équilibrée**, la paire n'est pas arbitraire — c'est le marché qui l'a formée —,
et la réponse EST la direction.

**Le piège nommé à l'avance** : la version naïve redécouvrirait « le prix casse
le côté le moins épais ». On rapporte donc SYSTÉMATIQUEMENT le résultat à
taille égale — la taille est un contrôle, pas un trait. Note : la taille ne
prédit rien (`f_mult` 0,4953, mesuré le 03/08), ce qui rend le piège moins
probable mais ne dispense pas du contrôle.

**Première mesure, avant tout le reste** : **combien d'encadrements par jour ?**
S'il y en a cinquante, il n'y a pas de statistique et E2 s'arrête là.

## Ce qui n'est PAS figé ici, et pourquoi

**Aucun seuil de décision.** On ne sait pas dans quel régime d'effet on est ;
poser une barre maintenant serait arbitraire. Les seuils seront pré-inscrits
dans un ADR séparé, **après** l'exploration et **avant** d'ouvrir le moindre
jour de certification.

C'est la séquence correcte : explorer librement sur un jeu, figer le protocole
complet, tirer une fois sur un jeu jamais ouvert.

## Partition des jours — révision de l'ADR-020

| jours | statut |
|---|---|
| 2025-12-01 → 07 | CERTIFICATION CONSOMMÉE — lecture seule, verdict CAS D |
| 2025-12-08 | BANC D'INSTRUMENT — validation d'ingestion uniquement |
| **2025-12-09 → 16** | **EXPLORATION** — E1, E2, conception de traits, libre |
| **2025-12-17 → 23** | **RÉSERVE DE CERTIFICATION — jamais ouverte** |
| 2025-12-24 → 31 | réserve libre |

Les jours 17-23 ne sont ni construits, ni étiquetés, ni regardés, **tant que le
protocole n'est pas pré-inscrit**. Le garde-fou `_refuse_si_gele` sera étendu à
cette tranche.

## Ce que ça ne fait pas

* **Ça ne rouvre pas le CAS D.** Le verdict du 03/08 reste rendu, sur sa
  question, avec ses défauts documentés.
* **Ça ne contredit pas le backtest négatif** de juillet (−10,8 bp en fadant
  tous les murs). Celui-ci mesurait des murs qui TIENNENT — durée de vie
  médiane 859 s — c'est-à-dire l'exact complément de la population visée ici
  (médiane 27 s). E1 le retestera sur la bonne population, et un nouveau
  négatif serait cette fois concluant.
* **Ça n'abandonne pas la vérité L4.** Elle cesse d'être la CIBLE et devient un
  INGRÉDIENT : elle sert à savoir quels murs étaient factices. Sans elle, E1
  est impossible.

---

# ADDENDUM du 03/08/2026, **19 h 56** — une définition figée n'est pas calculable

> **Correction d'horodatage, 20 h 10.** Cet en-tête portait « 20 h 30 », une
> heure que j'ai écrite sans la vérifier — et qui était alors dans le FUTUR.
> L'heure réelle est celle du commit `c90c8c2`, **19 h 56**. Sur un document
> dont toute la valeur est son antériorité, inventer l'heure est la faute
> qu'aucun garde-fou ne rattrape : `provenance.py` existe précisément parce
> que la nuit du 01→02/08, quatre documents « antérieurs à l'heure près »
> n'avaient jamais été commités. La faute reste écrite ici.

_Écrit **avant** d'avoir mesuré quoi que ce soit sur un jour d'exploration.
Aucun jour 09-16 n'a été construit à cette heure ; le seul jour touché est le
08, banc d'instrument. Cet addendum sert à ce que le choix soit daté et
opposable, pas à s'accorder une marge après coup._

## Le trou

Le corps fige : **« Factice — un mur dont les ordres ont été retirés plutôt
qu'exécutés dans les 30 s suivant LE CONTACT. »**

Mais E1 pose sa grille **tous les 10 s**, pas sur des contacts. À un instant
donné, la quasi-totalité des murs de la bande n'a jamais été contactée : la
définition ne leur attribue aucun `flee_ratio`, et `M(t, côté)` n'est pas
calculable. La contradiction est interne au document, entre le §Définitions et
le §Grille.

Elle vient de ce que `flee_ratio` a été repris du jalon précédent, où l'unité
ÉTAIT l'événement de contact. C'est précisément l'unité que l'ADR-021 quitte.

## Les deux lectures possibles

**(a) Ne garder que les murs contactés.** Fidèle à la lettre. Mais cela
réintroduit la sélection sur contact — la population même dont l'ADR-021 dit
qu'elle « récompense l'échec du spoofeur » (§Pourquoi on change, point 3), et
qui vide la bande à presque chaque instant.

**(b) Généraliser au temps courant.** `flee_ratio(t, palier)` = la fraction de
la taille POSÉE à cet instant dans ce palier dont l'ordre se termine par un
**retrait** plutôt que par une **exécution**, dans les 30 s qui suivent `t`.

Sur un mur effectivement contacté à `t`, (b) redonne (a) : c'est la même
quantité, le contact n'étant qu'un choix particulier de `t`.

## Ce qui est retenu, et pourquoi

**(b).** Trois raisons, dans l'ordre :

1. **(a) rend E1 vide.** Une définition qui ne s'évalue pas sur sa propre grille
   n'est pas une définition, c'est une erreur de rédaction.
2. **(b) est la généralisation stricte de (a)**, pas une définition
   concurrente : elle ne relâche aucun critère, elle lève seulement le
   conditionnement sur le contact.
3. **(b) est exactement ce que le corps dit chercher** — « l'IMPACT que la
   configuration produit » à un instant, pas le devenir d'un événement.

Restent figés sans changement : la grille 10 s, la bande 0,12 %–0,80 %, le
seuil de mur `WALL_MULT` = 4×, la fenêtre de 30 s, les horizons {30, 60, 300} s,
le signe prédit à l'avance, et le fait qu'E1 ne certifie rien.

## La réserve qui va avec

Sous (b), un mur dont **aucun** ordre ne se termine dans les 30 s a un
`flee_ratio` non pas nul mais **indéfini** : rien ne s'est produit, ni retrait
ni exécution. Les compter à 0 les déclarerait sincères sans preuve, et
gonflerait le dénominateur de `I(t)` d'une masse muette.

**Ils sont donc écartés de `M(t, côté)` et comptés à part.** Leur proportion
est rapportée avec le résultat — si elle est majoritaire, E1 ne mesure qu'une
minorité de la configuration et le dira.

---

# ADDENDUM 2 du 03/08/2026, **19 h 59** — `WALL_MULT` est mal cité dans le corps

> **Correction d'horodatage, 20 h 10.** Portait « 20 h 50 », inventé de la même
> façon. Heure réelle : commit `0622d64`, **19 h 59**.

_Toujours avant toute mesure. Trouvé en écrivant `e1_oracle.py`._

Le §Définitions fige : **« Mur — un palier dont la taille affichée est ≥ 4× la
médiane des paliers de la bande à cet instant (`WALL_MULT`, déjà en vigueur). »**

**`WALL_MULT` vaut 8,0**, pas 4 (`config.py:40`, « comme le JS »). Le seuil sert
déjà à la sélection des candidats dans `dataset.py:89`. La phrase se contredit
elle-même : le nombre écrit et la constante nommée ne coïncident pas.

**Retenu : 8,0**, la valeur RÉELLEMENT en vigueur — c'est ce que la parenthèse
déclare vouloir, et c'est le seuil sous lequel tout le reste du projet a été
mesuré. Prendre 4 aurait fabriqué un seuil neuf, jamais employé ailleurs, au
moment précis où l'on prétend ne rien renégocier.

Effet : le critère est **plus sévère**, donc moins de murs et moins d'instants
avec un `I(t)` défini. C'est une perte de puissance, pas un gain — on ne
s'accorde rien.

**Vérifié dans la foulée, et exact : la bande.** Le corps écrit 0,12 %–0,80 %
et `DIST_MIN_MULT × TOL = 0,0012`, `DIST_MAX = 0,0080` le confirment au chiffre
près. Seul `WALL_MULT` était mal cité.

---

# ADDENDUM 3 du 03/08/2026, 20 h 25 — l'instrument fabrique un faux `I(t)` la nuit

_Mesuré sur le **banc 20251208** uniquement, dont c'est la fonction (ADR-020).
Aucun jour d'exploration n'est construit à cette heure. La règle de décision
ci-dessous est écrite **avant** de connaître le résultat du remède._

## Ce qui a été mesuré

Le carnet profond, construit avec `WARMUP_H = 2`, part d'un livre VIDE deux
heures avant minuit. La masse de la bande P0 sur les cinq premières heures vaut
**6,5 % de moins** que sur le reste de la journée (médianes horaires,
permutation à 20 000 tirages, **p < 0,0001**).

Un déficit uniforme serait sans conséquence : `I(t)` est un RAPPORT, il
s'annule. **Il n'est pas uniforme.**

| | h00–h04 | h05–h23 | déficit |
|---|---|---|---|
| bid | 81,0 M$ | 91,9 M$ | **11,9 %** |
| ask | 91,8 M$ | 94,2 M$ | 2,5 % |

**`I(t)` médian : −0,0724 sur h00–h04 contre −0,0117 ensuite.** Un écart de
**−0,0606**, supérieur à l'écart-type horaire de `I(t)` (0,0541).

L'instrument fabrique donc, la nuit, un déséquilibre directionnel d'environ un
écart-type — **exactement la quantité qu'E1 corrèle au rendement**. Mesurer E1
sur ces heures reviendrait à corréler un artefact d'ingestion avec le prix, et
un résultat positif y serait indiscernable d'un succès réel.

## Ce qu'on ne sait pas encore, et le test qui tranche

Rien ne dit encore si c'est un **artefact** ou une vraie structure de marché :
les heures creuses UTC pourraient réellement avoir des bids plus minces.

Le test qui les sépare : **allonger la chauffe**. Un artefact de démarrage à
froid recule ; une structure de marché ne bouge pas. On passe `WARMUP_H` de 2 à
**8** — le déficit s'éteint à h05, soit 7 h après le début de la chauffe — et on
reconstruit le même jour, le même symbole.

## Règle de décision, figée AVANT de connaître le résultat

> **Accepter `WARMUP_H = 8`** si l'écart de `I(t)` médian entre les cinq
> premières heures et le reste tombe **sous l'écart-type horaire de `I(t)`**
> mesuré sur le reste de la journée.
>
> **Sinon**, écarter d'E1 les heures contaminées, le dire dans le résultat, et
> publier le coût en instants perdus.

Le coût de la première branche est du **temps de calcul** (~3 min par jour et
par symbole). Celui de la seconde est de la **donnée** (21 % des instants). On
ne choisit pas la branche après avoir vu laquelle arrange.

---

# ADDENDUM 4 du 03/08/2026, 20 h 42 — le remède n'a pas marché, et l'artefact n'en était pas un

_L'addendum 3 posait une règle et un diagnostic. **La règle est respectée, le
diagnostic était faux.** Les deux se lisent ensemble._

## Le résultat de la règle

| chauffe | écart de `I(t)` | écart-type horaire | verdict |
|---|---|---|---|
| 2 h | 0,0606 | 0,0541 | **REFUSE** |
| 8 h | **0,0649** | **0,0652** | **ACCEPTE** |

La règle est satisfaite. **Mais elle l'est pour la mauvaise raison** : l'écart
n'a pas diminué, il a *augmenté* (0,0606 → 0,0649). C'est le dénominateur qui a
grandi davantage. Une marge de 0,5 % sépare l'acceptation du refus.

## Le remède n'a rien changé là où il devait

Comparaison directe des deux constructions, **mêmes instants, même jour** :

| bande P0, h00–h04 | 2 h | 8 h | gain |
|---|---|---|---|
| masse bid | 81,0 M$ | 81,0 M$ | **+0,0 %** |
| masse ask | 91,8 M$ | 94,3 M$ | +2,7 % |

Et sur la journée entière : **zéro** palier bid ajouté dans la bande, 59 121 du
côté ask. Parmi les paliers communs dont la masse a bougé dans la bande :
**2 bid contre 353 577 ask**.

Quadrupler la chauffe n'a pas rempli le côté bid d'un dollar. **L'hypothèse du
démarrage à froid est réfutée** pour la bande.

## Ce que c'était vraiment

Le flux de POSE dans la bande est symétrique, nuit comme jour (part bid 0,5010
contre 0,4991). Mais un stock ne vaut pas un flux : **stock = flux × durée de
vie**.

| durée de vie médiane, bande | bid | ask | rapport |
|---|---|---|---|
| nuit h00–h04 | 6,25 s | 8,27 s | **0,76** |
| jour h05–h23 | 5,88 s | 6,49 s | 0,91 |

**La nuit, les bids meurent 24 % plus vite que les asks ; le jour, 9 %.** À flux
égal, le carnet porte donc mécaniquement moins de bids la nuit. C'est de la
micro-structure, pas un défaut d'ingestion.

## Ce qui en découle

1. **E1 tourne sur TOUTES les heures.** Écarter les cinq premières jetterait de
   la donnée réelle. La seconde branche de l'addendum 3 devient sans objet — non
   parce qu'elle arrange, mais parce que sa prémisse est fausse.
2. **`WARMUP_H = 8` est conservé quand même.** Il ajoute 11,5 % de paliers dans
   la nappe large (3 204 → 3 571 par photo) pour ~3 min par jour-symbole. Il ne
   corrige pas ce qu'on croyait, il corrige autre chose.
3. **`I(t)` a un cycle journalier propre**, d'environ un écart-type entre nuit
   et jour. Ce n'est pas un biais à retirer, c'est une composante du signal —
   mais elle doit être **rapportée avec le résultat d'E1** : une corrélation
   entre `I(t)` et le rendement pourrait n'être qu'un effet d'heure de la
   journée partagé par les deux. Le contrôle correspondant est à prévoir.

## Ce que cet épisode dit de la méthode

Deux fois en une heure j'ai conclu trop vite : d'abord « la chauffe est
résorbée » (le profil horaire ne pouvait pas voir un déficit uniforme), puis
« c'est l'instrument » (le test de flux mesurait l'entrée, pas le stock).
Les deux fois, c'est une mesure supplémentaire — et non un raisonnement — qui a
tranché. La règle pré-inscrite a fait son travail : elle m'a forcé à mesurer le
remède au lieu de le supposer efficace.

---

# ADDENDUM 5 du 03/08/2026, 20 h 58 — le contrôle d'heure, spécifié avant tout résultat

_Écrit alors que les jours 09-12 sont en cours de construction et qu'aucun rho
n'existe. C'est le dernier moment où ce contrôle peut être pré-inscrit._

## Le confondeur

L'addendum 4 établit que `I(t)` porte un **cycle journalier** d'environ un
écart-type : la nuit, les bids meurent plus vite, donc le carnet penche.

Le rendement du mid, lui, porte **aussi** un cycle journalier — la volatilité et
la dérive ne sont pas les mêmes à 3 h UTC qu'à 15 h. C'est une régularité connue
de tous les marchés.

**Deux séries qui partagent un cycle journalier sont corrélées sans qu'aucune ne
cause l'autre.** E1 tel que défini au corps mesurerait cette corrélation-là et
la lirait comme un plafond de détection. C'est un piège classique, et il est
d'autant plus dangereux ici qu'il donnerait un résultat POSITIF.

## Le contrôle

Pour chaque symbole et chaque jour, en plus du rho brut :

> **rho contrôlé** — corrélation de Spearman entre les **résidus** de `I(t)` et
> de `r(t,H)` après retrait, pour chacune des 24 heures UTC, de la **médiane de
> cette heure**. Toute composante commune à une heure donnée disparaît ; ce qui
> reste est la co-variation **à l'intérieur** des heures.

## Ce qui fait foi, décidé maintenant

> **C'est le rho CONTRÔLÉ qui fait foi.** Le rho brut est publié à côté, pour
> que l'écart soit lisible.
>
> Si `|rho contrôlé|` est nettement inférieur au rho brut, la corrélation brute
> était principalement un effet d'heure, et **il faut le dire ainsi**.
>
> Si les deux coïncident, le cycle journalier n'explique rien et le résultat
> brut tient.

Le signe reste prédit à l'avance, comme au corps : `I(t) > 0` prédit
`r(t,H) > 0`. Le contrôle ne change ni le signe attendu, ni les horizons, ni la
bande, ni `WALL_MULT`, ni la règle des murs muets.

## Pourquoi maintenant et pas après

Parce qu'après, il serait impossible de distinguer « j'ai ajouté un contrôle
légitime » de « j'ai ajouté un contrôle qui donne le résultat que je préfère ».
Les jours 09-12 sont en cours de construction ; aucun `I(t)` d'exploration n'a
été calculé, aucun rendement n'a été regardé.

---

# ADDENDUM 6 du 03/08/2026, 21 h 50 — E1 était CIRCULAIRE. Définition corrigée.

_Le résultat obtenu sur le jour 20251209 (+0,081 / +0,050 / +0,053) est **NUL et
retiré**. Il a été produit avant que le défaut ne soit connu ; il n'est pas
réinterprété, il est jeté._

## Le défaut

Le corps définit **factice** par ce qui arrive à l'ordre « dans les 30 s
suivant » — et la cible est `r(t,H)`. **Les deux fenêtres se recouvrent.**

Or ce qui décide du sort d'un ordre est en grande partie le mouvement de prix
pendant cette fenêtre : le côté que le prix traverse est **mangé**, l'autre est
**retiré**. `M(t, côté) = Σ taille × flee_ratio` est donc une lecture du
rendement déguisée en prédicteur, et `I(t)` mesure ce qui vient de se passer.

**Mesuré** sur un monde construit — carnet strictement symétrique à `t`, mid en
marche aléatoire pure, aucune information prédictive, **vérité rho = 0** :

| | 30 s | 60 s | 300 s |
|---|---|---|---|
| rho brut | **+0,866** | +0,627 | +0,236 |
| rho contrôlé (addendum 5) | +0,754 | +0,538 | +0,176 |

Le contrôle d'heure n'y peut rien : le confondeur est **intra-heure**.

C'est le piège `f_absorb_contact` du P0, réinventé — celui que
`hl_features.py:17` documente depuis des semaines comme « −27,5 pts d'edge
mensonger ».

## La correction : DISJOINDRE les deux fenêtres

Soit `W = 30 s` la fenêtre de révélation (inchangée).

> **murs** — observés à l'instant `t`, dans la bande, selon `WALL_MULT`.
> **factice** — révélé sur `]t, t+W]` : retiré plutôt qu'exécuté. Inchangé.
> **cible** — `r(t+W, H) = (mid(t+W+H) − mid(t+W)) / mid(t+W)`.
>
> Le rendement commence **où la révélation finit**. Aucun recouvrement.

La question posée devient : *« si l'on savait, à `t+W`, quels murs présents à
`t` étaient factices, cela prédirait-il le prix APRÈS `t+W` ? »* C'est toujours
un oracle — non causal et assumé —, mais ce n'est plus une tautologie.

Ce qui **ne change pas** : la grille de 10 s, la bande 0,12–0,80 %,
`WALL_MULT = 8`, `W = 30 s`, les horizons {30, 60, 300} s, le signe prédit à
l'avance, la règle des murs muets, le contrôle d'heure de l'addendum 5.

## Critère de validation, exigé AVANT toute nouvelle mesure

> **Le code corrigé doit rendre un rho indiscernable de zéro sur le monde
> construit ci-dessus**, aux trois horizons, brut comme contrôlé.
>
> Seuil : `|rho| < 0,05` sur les trois. Au-dessus, la correction est
> insuffisante et **aucun résultat réel n'est lu**.

C'est la leçon de la soirée : une règle pré-inscrite ne suffit pas si le
protocole qu'elle encadre est circulaire. Il faut un **contrôle négatif
exécutable** — un monde où l'on connaît la réponse — attaché à la mesure
elle-même.

## RÉVISION du critère, 22 h 05 — il était mal spécifié

Le critère ci-dessus (`|rho| < 0,05` sur **un** monde) ne peut pas distinguer un
**biais** d'un **bruit**. Mesuré sur 12 mondes nuls, médiane du rho contrôlé :

| départ du rendement | H=30 s | H=60 s | H=300 s |
|---|---|---|---|
| `t + W` | **+0,035** | +0,020 | +0,004 |
| `t + 2W` | +0,009 | +0,005 | −0,015 |
| `t + 3W` | +0,002 | −0,001 | −0,007 |

Disjoindre les fenêtres a fait tomber l'artefact de **+0,75 à +0,035** — pas à
zéro. Cause du résidu : la fenêtre de flee d'un instant capte aussi les
événements des murs observés à `t+10 s` et `t+20 s`, dont le sort dépend de
mouvements allant jusqu'à `t+50 s`, donc au-delà d'un départ posé à `t+30 s`.

**Le départ passe donc à `t + 2W` (60 s).** Le biais y est dans le bruit.

Et un fait qui compte au moins autant : **l'étalement ne bouge pas** — p5–p95
d'environ ±0,05 aux trois départs. C'est le bruit propre d'**un jour** sur des
fenêtres recouvrantes, irréductible.

> **Aucun rho journalier inférieur à ~0,05 n'est interprétable seul.** Seule
> l'agrégation sur les jours l'est — ce que le corps exigeait déjà en imposant
> un bootstrap sur les jours, et dont on comprend maintenant la raison
> quantitative.

**Critère corrigé, qui remplace celui de l'addendum 6 :**

> Le contrôle négatif tourne sur **au moins 12 mondes** (`experiments/e1_controle_negatif.py`)
> et rapporte **médiane ET étalement**. On exige `|médiane| < 0,02` aux trois
> horizons. L'étalement n'est pas un critère : c'est la **barre de bruit** à
> publier à côté de tout résultat journalier.

## ADDENDUM 7, 22 h 35 — l'IC du corps sous-couvre ; il passe à Student

Le corps demande « **IC par bootstrap sur les jours** ». Couverture **mesurée**
(2 000 répétitions, écart-type journalier 0,05, nominal 95 %) :

| jours | bootstrap | Student t |
|---|---|---|
| 4 | **80 %** | 94 % |
| 6 | 85 % | 95 % |
| 8 | 88 % | 95 % |
| 12 | 89 % | 95 % |

Le bootstrap sur peu d'unités **sous-couvre systématiquement**. À 4 jours il
rend un intervalle large de 0,075 là où le t fait **0,143** — deux fois trop
étroit, donc il déclarerait un effet significatif deux fois trop souvent.

> **L'IC qui fait foi est celui de Student sur les valeurs journalières.** Le
> bootstrap est publié à côté, pour que l'écart reste lisible.

C'est un **élargissement** de l'intervalle, décidé avant tout résultat : il rend
la conclusion plus difficile, jamais plus facile. C'est le même phénomène que la
réserve **C3** du registre (couverture 0,900 pour 0,95), restée sans correctif
depuis le 02/08 — elle en a un maintenant, au moins pour l'unité « jour ».

**Conséquence chiffrée** : avec le bruit propre d'un jour à ±0,05, il faut
`|rho moyen| > ~0,07` sur 4 jours, ou `> ~0,05` sur 8 jours, pour que l'IC
exclue zéro.

## Ce que le défaut dit du chiffre retiré

L'artefact pur produit **+0,75** ; la donnée réelle a produit **+0,08**. Le
réel est donc très en dessous de ce que la seule circularité fabriquerait.
**On n'en conclut rien** — une mesure fausse ne devient pas informative parce
qu'elle est basse. Elle est refaite.


---

# ADDENDUM 8 du 03/08/2026, 23 h 15 — E2 : l'encadrement n'est pas un événement

_Écrit après la « première mesure, avant tout le reste » que le corps exigeait,
et avant toute mesure de prédiction._

## Ce que la mesure d'arrêt devait trancher

Le corps dit : **« Première mesure, avant tout le reste : combien d'encadrements
par jour ? S'il y en a cinquante, il n'y a pas de statistique et E2 s'arrête
là. »**

Réponse, BTC, jours 09-11 : **24 856 encadrements, soit 100,0 % des instants.**

L'arrêt était prévu pour le cas « trop peu ». C'est le cas inverse qui se
produit, et il disqualifie tout autant la formulation.

## Pourquoi, et ce n'est pas un défaut de seuil

| seuil de mur | murs par photo | % des paliers de bande | encadrements |
|---|---|---|---|
| **×8** (ADR) | 151 | 26,4 % | 8 290 / 8 290 |
| ×32 | 76 | 13,3 % | 8 290 / 8 290 |
| ×128 | 24 | 4,2 % | 8 290 / 8 290 |
| ×256 | 16 | 2,8 % | 8 290 / 8 290 |
| ×512 | 9 | 1,6 % | 7 937 / 8 290 |

**Même à 256× la médiane — trente-deux fois plus strict que l'ADR — tous les
instants restent encadrés.** Un carnet liquide porte toujours de gros paliers
des deux côtés dans une bande de 0,12 % à 0,80 %. Le mur le plus proche est
d'ailleurs systématiquement au bord intérieur de la bande (distance médiane
**0,00121** des deux côtés, pour une borne à 0,0012).

Conséquence directe : « lequel cède » dégénère en « le prix bouge-t-il de
0,12 % vers le haut ou vers le bas d'abord ». Mesuré : **49,8 %, 50,1 %,
54,2 %** de côté bid. Un tirage à pile ou face, comme attendu.

## Ce que ça invalide, et ce que ça ne touche pas

**Invalidé** : l'encadrement comme **critère de sélection**. Il ne filtre rien,
il décrit l'état permanent du marché. La phrase du corps — « la paire n'est pas
arbitraire, c'est le marché qui l'a formée » — est fausse : le marché forme
cette paire à chaque instant.

**Intact** : la cible. Elle est **binaire et remarquablement équilibrée**
(49,8–54,2 %), avec **~8 300 événements par jour**. C'est exactement ce que le
corps annonçait vouloir, et ce n'est pas fréquent.

## E2, reformulé

> **L'encadrement n'est pas une condition, c'est le cadre.** La question devient :
> **la configuration des murs à l'instant `t` prédit-elle quel côté le mid
> traverse en premier ?**
>
> Cible inchangée : premier palier traversé dans l'heure, bid ou ask.
> Population : tous les instants, plus de sélection.
> Le piège nommé au corps reste en vigueur : rapporter le résultat **à taille
> égale**, la taille étant un contrôle et non un trait.

Rien d'autre ne bouge — bande, `WALL_MULT`, fenêtre d'une heure, et le fait
qu'E2 ne certifie rien.

## Ce que je ne fais pas

**Je ne retouche pas `WALL_MULT` pour rendre l'encadrement rare.** Le tableau
ci-dessus montre qu'il faudrait aller au-delà de ×512 pour y arriver, et
choisir un seuil par l'effet qu'il produit sur le comptage serait exactement la
dérive que ces documents existent pour empêcher.


---

# ADDENDUM 9 du 03/08/2026, 23 h 25 — E2 sans le caractère FACTICE ne teste rien

_Objection de Meddy : « as-tu pris en compte les éléments de spoofing pour
diriger le prix ? » Non — et l'omission rend la mesure d'arrêt muette sur
l'hypothèse. Écrit avant toute mesure incluant `flee_ratio`._

## Ce que la mesure d'arrêt a fait, et ce qu'elle n'a pas fait

Elle a compté des **murs**, définis par la seule taille (`≥ WALL_MULT × médiane`).
Elle n'a **jamais lu `flee_ratio`**. Le 49,8 / 50,1 / 54,2 % obtenu ne dit donc
pas « pas de signal » — il dit **« aucun signal n'a été utilisé »**.

## Pourquoi mélanger les deux populations garantit 50/50

Les deux ont des effets **opposés**, et le corps de l'ADR le dit déjà :

* un mur d'achat **sincère** absorbe les ventes : il **retient** le prix
  au-dessus de lui, donc le côté ask cède ;
* un mur d'achat **factice** simule une demande : il **pousse** le prix vers le
  haut (§Hypothèse directionnelle), donc le côté ask cède aussi.

…sauf qu'un mur factice est **retiré** à l'approche, donc il ne retient rien et
le prix le traverse. Les deux mécanismes tirent en sens contraire sur la même
variable observée. Les agréger sans les distinguer les annule.

## E2 complété

> Pour chaque instant `t`, le mur le plus proche de chaque côté reçoit son
> `flee_ratio`, révélé sur `]t, t+W]` (W = 30 s), **selon la définition
> généralisée de l'addendum 1**.
>
> **Prédicteur** : le déséquilibre de masse FACTICE entre les deux murs,
> `(M_bid − M_ask) / (M_bid + M_ask)` — le même `I(t)` qu'E1, restreint aux deux
> murs encadrants.
>
> **Cible** : quel côté le mid traverse en premier, sur `[t+2W, t+2W+1 h]`.
>
> **Signe prédit à l'avance**, cohérent avec le corps : `I(t) > 0` (masse
> factice surtout côté bid) prédit que le prix monte, donc que **l'ASK cède**.

## La circularité, nommée avant de mesurer

C'est le piège qui a détruit E1 (addendum 6), et il se reproduit ici sous une
forme plus directe encore : **un mur que le prix traverse est EXÉCUTÉ**, donc sa
fuite est basse. Mesurer la fuite sur une fenêtre qui recouvre la traversée
reviendrait à lire la réponse.

D'où le départ de la cible à **`t + 2W`**, exactement comme E1 corrigé — et pour
la même raison mesurée : à `t+1W` l'artefact résiduel valait encore +0,035 sur
un monde nul.

## Le contrôle négatif qui doit passer AVANT toute lecture

Comme pour E1 : un monde construit où le carnet est symétrique et le mid une
marche aléatoire pure doit rendre une proportion **indiscernable de 50 %**.
Au-dessus, la mesure est circulaire et **aucun résultat réel n'est lu**.


---

# ADDENDUM 10 du 04/08/2026, 00 h 45 — le « factice » n'a jamais rien mesuré

_Découvert en construisant le détecteur D1, qui répond à l'ADR-001. C'est le
défaut le plus profond de l'ADR-021, et il touche E1 comme E2._

## Le fait

`flee_ratio` des murs de la bande, jour 20251210, 821 506 murs :

| centile | 1 | 5 | 25 | 50 | 75 | 99 |
|---|---|---|---|---|---|---|
| flee | **1,0000** | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 |

**99,28 % des murs ont un `flee_ratio` exactement égal à 1,000.** Ce n'est pas
une variable, c'est une constante.

## Pourquoi — et ce n'est pas un défaut de mesure

| distance au mid | flee moyen | % exactement à 1,000 |
|---|---|---|
| 0,132 % | 0,9995 | 97,7 % |
| 0,240 % | 0,9998 | 99,4 % |
| 0,412 % | 1,0000 | 99,9 % |
| 0,704 % | 1,0000 | **100,0 %** |

**La fenêtre de 30 s et la bande 0,12–0,80 % sont incompatibles.** Le prix
n'atteint pas ces paliers en trente secondes : rien ne s'y exécute, donc tout ce
qui s'y termine se termine par une annulation.

**`flee_ratio` ne mesure pas une intention de retrait. Il mesure que le prix
n'est pas venu.** C'est une propriété de la distance et de la volatilité, pas du
poseur d'ordre.

## Ce que ça invalide, en amont

`M(t, côté) = Σ taille × flee_ratio`. Avec `flee ≈ 1` partout, **`M` EST la
masse**. Donc :

* **`I(t)` d'E1 n'était pas un déséquilibre de masse FACTICE — c'était un
  déséquilibre de masse tout court.** Le corps de l'ADR-021 croyait introduire
  la vérité L4 dans le prédicteur ; numériquement, elle n'y a jamais été.
* **Même chose pour E2** (addendum 9) : les quintiles de `I` étaient des
  quintiles de déséquilibre de taille.
* Le §« Ça n'abandonne pas la vérité L4 — elle devient un INGRÉDIENT » est
  factuellement faux sur ce jeu : l'ingrédient est constant.

Ça n'annule pas les mesures — elles restent justes pour ce qu'elles ont
réellement calculé — mais **elles ne portaient pas sur ce qui était annoncé**.

## Ce que ça implique pour la définition de « factice »

Un mur qu'on annule **sans que le prix soit jamais venu** n'est pas
nécessairement une manipulation : c'est le fonctionnement normal d'une cotation
qu'on rafraîchit. La définition utile doit être **conditionnelle à
l'approche** :

> Parmi les murs que le prix **approche**, lesquels disparaissent **avant**
> d'être touchés ?

C'est la seule formulation où « retiré » porte une information sur l'intention,
parce que le retrait y devient un choix et non une conséquence de l'inaction du
prix.

**Rien n'est mesuré sous cette définition pour l'instant.** Elle est écrite ici
avant tout résultat, comme les précédentes.
