# 03 — Éconophysique

## PARTIE I — Registre des grandeurs candidates

> **Reformatage du 05/08/2026.** L'ancien fichier était un empilement de
> sessions : ~300 noms, classés en étoiles attribuées par intuition, avec
> « potentiel » présent seize fois sous six noms. Il reste **dans git** et rien
> n'en est perdu — l'annexe B trace où chaque nom a été rangé.
>
> Ce document est maintenant un **registre de fiches**, au format qu'exige
> `05_Protocole_de_selection.md` §1. Il est ordonné par **utilité à
> l'exécution**, jamais par nouveauté.
>
> **Ce n'est toujours pas un plan.** Une fiche déposée n'est pas une grandeur
> retenue : elle est admise à passer É0 → É4. Rien n'entre dans le pipeline sur
> son élégance.

---

## Comment lire une fiche

Chaque fiche porte **huit lignes fixes** *(complétées le 05/08/2026 — blocage
B5 : `05` exige `coût` et le périmètre minimal déclarés dans la fiche avant
tout calcul)*. Les trois premières sont exigées par le protocole ; les
suivantes sont le pré-tri, fait sur papier, avant toute dépense.

| ligne | contenu |
|---|---|
| **mesure** | ce que la grandeur capte, en une phrase |
| **définition** | la formule ou la règle, sans ambiguïté |
| **observable** | ce qu'il faut avoir pour la calculer |
| **à l'exécution** | ce que ça change quand on doit poster, retirer ou traverser — **si cette ligne est vide, la fiche ne sert pas au produit** |
| **É1** | ✅ traverse vers Binance · ⚠️ traverse dégradée · ❌ fabrique la vérité seulement |
| **redite** | de quoi elle est probablement le doublon, à mesurer en É0 / É2 |
| **coût** | temps de calcul par jour-symbole. **Estimation a priori, pas une mesure** : déclarée pour départager en É0, corrigée dans la fiche à la première exécution |
| **périmètre minimal** | sur quoi É0 et É2 tournent pour ce candidat — déclaré ici, **avant** le calcul, et il ne s'étend pas après avoir vu un résultat |

**Les deux périmètres déclarés**, communs à É0 et É2, **jamais la réserve**
(17-23) :

* **J3** — les trois premiers jours d'exploration de la tranche 1 : **9, 10,
  11 décembre 2025**, BTC et ETH. Le défaut.
* **J8** — les huit jours d'exploration de la tranche 1 : **9 à 16 décembre
  2025**, BTC et ETH. Réservé aux grandeurs d'événements rares ou de régime,
  qui n'auraient aucun contenu sur trois jours — le choix se justifie dans la
  fiche, d'avance.

**Rappel des deux barres** que rien ne contourne. É1 : sans `oid`, sans identité,
sans cycle de vie, dans un navigateur, et sous la dégradation du démon —
2 500 ms, filtre `v > médiane`, 500 paliers. É2 : **corrélation de rang**
avec les candidats déjà retenus, témoin trivial inclus (barres 0,50 / 0,70) — le
gain incrémental, c'est **É4**, pas É2. *(Corrigé le 05/08 : ce rappel décrivait
É2 avec la définition d'É4, et « le bloc de persistance » n'existe pas dans
`05`.)* C'est cette seconde barre
qui a tué la sonologie, avec des descripteurs qui battaient pourtant la meilleure
grandeur connue **isolément**.

**Et l'avertissement qui vaut pour tout le bloc A.** Ce catalogue suppose partout
l'événementiel — « ordre par ordre », événements à quelques dizaines de
millisecondes. La chaîne d'affichage actuelle photographie à 2 500 ms. Toute
fiche marquée ⚠️ vit ou meurt sur une question qui n'est pas encore mesurée :
*que reste-t-il de cette grandeur après la dégradation ?*

---

# A. Le flux — ce qui décide du mouvement

C'est le bloc qui répond directement à la question du projet : **pourquoi le prix
choisit-il un mur plutôt que l'autre**. C'est aussi celui dont la plus grande
part traverse.

---

### A1 · Déséquilibre de flux d'ordres (OFI)

- **mesure** — la pression nette exercée par le flux, et non l'état statique du
  carnet.
- **définition** — somme signée des contributions de chaque événement : un ajout
  au bid et un retrait à l'ask poussent dans le même sens ; une exécution compte
  avec le signe de son agresseur. À accumuler sur une fenêtre.
- **observable** — les diffs de profondeur signés. Pas d'identité.
- **à l'exécution** — un OFI fortement négatif devant un mur ask dit que la
  pression monte contre lui : traverser tard coûte plus cher qu'attendre son
  effritement.
- **É1** — ✅ **traverse.** C'est la grandeur la mieux placée du registre : elle
  se calcule des deux côtés, sans identité, en quelques opérations par événement.
- **redite** — faible avec la persistance. C'est un flux, pas un état — c'est
  précisément ce qui la rend intéressante.
- **coût** — estimé : une passe linéaire sur les diffs, quelques opérations par
  événement — **minutes** par jour-symbole.
- **périmètre minimal** — **J3**.

---

### A2 · OFI localisé autour du mur

- **mesure** — la même pression, mais **restreinte au voisinage du niveau jugé**
  au lieu du haut du carnet.
- **définition** — OFI calculé sur une fenêtre de paliers autour du mur, et
  déclinée en *devant le mur* (entre le prix et lui) et *derrière le mur*.
- **observable** — les diffs, plus la grille de paliers commune à la production.
- **à l'exécution** — c'est le discriminant le plus direct entre deux murs qui
  encadrent le prix : celui devant lequel le flux se vide cède le premier.
- **É1** — ✅ **traverse**, sous réserve du plafonnement à 500 paliers : si le mur
  est hors des 500 paliers retenus, la grandeur n'existe pas à l'écran. À
  mesurer, pas à supposer.
- **redite** — faible. C'est la variante qui vaut le plus dans tout le catalogue,
  parce qu'elle est la seule à être **locale au mur** et non globale au carnet.
- **coût** — estimé : la même passe qu'A1 restreinte à une fenêtre de paliers,
  mais il faut d'abord situer le mur — **minutes** par jour-symbole.
- **périmètre minimal** — **J3**.

---

### A3 · Flux signé décomposé — exécuté / retiré / ajouté

- **mesure** — à chaque pas, la variation de masse d'un palier se décompose en
  trois termes : ce qui a été **mangé**, ce qui a été **annulé**, ce qui a été
  **ajouté**.
- **définition** — le terme exécuté vient des transactions au palier ; le net
  vient du diff ; les deux autres s'en déduisent par différence.
- **observable** — diffs de profondeur **croisés aux exécutions**. Pas
  d'identité, pas d'`oid`.
- **à l'exécution** — c'est **le cœur du produit**. Un mur qui fond parce qu'on
  le mange et un mur qui fond parce qu'on l'annule sont deux situations opposées :
  la première dit que la liquidité est réelle et se consomme, la seconde qu'elle
  n'a jamais eu l'intention d'être là. La heatmap actuelle affiche la masse et
  confond les deux.
- **É1** — ✅ **traverse**, et c'est le point à vérifier en premier côté Binance :
  la décomposition est-elle reconstructible en croisant les transactions agrégées
  et les diffs de profondeur ? Si oui, le socle du produit traverse.
- **redite** — aucune. Rien d'autre dans ce registre ne fait cette distinction.
- **coût** — estimé : une passe sur les diffs croisés aux exécutions, par
  palier — **minutes à dizaines de minutes** par jour-symbole selon la
  profondeur de bande. Point de repère, pas une mesure du même objet : la
  mesure C8.2 du 05/08 a fait l'équivalent Binance d'un jour complet en
  quelques minutes.
- **périmètre minimal** — **J3**.

---

### A4 · Microprice et distance au mur

- **mesure** — un prix de référence pondéré par les tailles des deux meilleures
  limites, plutôt que le milieu de la fourchette.
- **définition** — moyenne des deux meilleurs prix pondérée par les volumes
  **opposés**. Puis les écarts : microprice − mid, et distance mur → microprice.
- **observable** — le haut du carnet. Le moins cher de tout le registre.
- **à l'exécution** — le microprice penche du côté où le prix va aller à très
  court terme. Sur une entrée limite, il dit de quel côté poster.
- **É1** — ✅ **traverse**, trivialement.
- **redite** — faible, mais **attention** : c'est un déséquilibre statique, donc
  probablement corrélé au bloc de présence. À mesurer en É2.
- **coût** — estimé : le haut du carnet seulement — **secondes** par
  jour-symbole. Le moins cher du registre, ce qui en fait le départage d'É0
  contre tout doublon.
- **périmètre minimal** — **J3**.

---

### A5 · Propagateur d'impact

- **mesure** — chaque exécution pousse le prix, et cette poussée **décroît avec
  le temps**. Le propagateur est la forme de cette décroissance.
- **définition** — la variation de prix comme somme des exécutions passées,
  chacune pondérée par un noyau décroissant du délai écoulé.
- **observable** — les exécutions signées et le prix. Pas d'identité.
- **à l'exécution** — il donne le coût attendu d'un ordre agressif en fonction de
  sa taille et du temps sur lequel on l'étale. C'est directement du slippage.
- **É1** — ⚠️ **traverse dégradée.** Le noyau se calibre sur de l'événementiel ;
  à 2 500 ms, la partie courte du noyau — celle qui coûte le plus — est perdue.
  Calibrable hors ligne, applicable en direct sous forme figée.
- **redite** — faible.
- **coût** — estimé : la passe sur exécutions et prix est en **minutes**, mais
  la **calibration du noyau** est un ajustement — **dizaines de minutes** par
  jour-symbole, la plus chère du bloc A hors A6.
- **périmètre minimal** — **J3**.

---

### A6 · Auto-excitation (Hawkes, taux de branchement)

- **mesure** — les ordres et les annulations arrivent en **grappes** : un
  événement augmente temporairement la probabilité du suivant.
- **définition** — une intensité d'arrivée faite d'un fond constant plus la somme
  des contributions déclinantes des événements passés. Le taux de branchement
  est la fraction des événements déclenchés par d'autres.
- **observable** — le flux **événement par événement**, horodaté finement.
- **à l'exécution** — un taux de branchement élevé signale une cascade en cours :
  ne pas poster dedans, et si l'on doit traverser, le faire avant qu'elle ne
  s'amplifie.
- **É1** — ❌ à ce jour. L'estimation exige l'événementiel, et 2 500 ms le
  détruisent. Reclassable en ⚠️ **si et seulement si** le pipeline d'acquisition
  change — c'est une des deux branches ouvertes du chantier C7.
- **redite** — faible, mais l'estimation est fragile et coûteuse.
- **coût** — estimé : estimation par vraisemblance sur de l'événementiel —
  **heures** par jour-symbole. Hors ligne par construction (É1 ❌) : ce coût ne
  pèse sur aucun jour d'exploration tant que C7 n'a pas changé l'acquisition.
- **périmètre minimal** — **J3**, si un jour reclassée ⚠️ par C7. Sans objet
  d'ici là.

---

# B. La vie et la mort d'un mur

Le bloc qui alimente le **typage**. C'est aussi celui où le catalogue d'origine
était le plus fort et le plus incomplet à la fois : très bien sur la disparition,
muet sur le réapprovisionnement.

---

### B1 · Taux de disparition instantané (hazard rate)

- **mesure** — la probabilité qu'un palier disparaisse dans l'instant qui suit,
  sachant qu'il a déjà tenu jusque-là.
- **définition** — analyse de survie sur la durée de vie du palier, **sous
  censure** (voir F3). Décliné par covariable : masse relative, distance au prix,
  approche en cours.
  **Entrée au banc (correction du 05/08, II.2)** : soumise comme **écart à sa
  ligne de base**, pas comme taux brut — un mécanisme de seuil doit entrer
  monotone, sinon le contrôle de rang d'É4 l'élimine à tort.
- **observable** — au niveau du palier : les diffs suffisent. Au niveau de
  l'ordre : `oid` et cycle de vie, donc L4.
- **à l'exécution** — c'est la question qu'on se pose vraiment devant un mur :
  *va-t-il encore être là quand j'y arrive ?* Elle décide de poster derrière lui
  ou de ne pas compter dessus.
- **É1** — ⚠️ la version **palier** traverse ; la version **ordre** non. Les
  garder distinctes, ne jamais les nommer pareil.
- **redite** — forte avec la persistance : c'en est presque la définition
  différentielle. É2 sera sévère, et c'est normal.
- **coût** — estimé : durées de vie de paliers sous censure (F3 obligatoire) —
  **dizaines de minutes** par jour-symbole, l'estimateur de survie compris.
- **périmètre minimal** — **J3**.

---

### B2 · Résilience et temps de relaxation

- **mesure** — à quelle vitesse un palier vidé se **reforme**.
- **définition** — le temps caractéristique du retour de la masse vers son niveau
  antérieur après une exécution ou un retrait.
- **observable** — les diffs, sur une fenêtre après l'événement. Pas d'identité.
- **à l'exécution** — un carnet résilient absorbe : on peut traverser en plusieurs
  fois. Un carnet non résilient ne se reforme pas : la première tranche paie le
  prix de toutes les suivantes.
- **É1** — ✅ **traverse.**
- **redite** — moyenne à forte avec la persistance. À mesurer avant, pas après.
- **coût** — estimé : détection des événements puis fenêtre de retour par
  palier — **minutes** par jour-symbole.
- **périmètre minimal** — **J3**.

---

### B3 · Réapprovisionnement — la signature de l'iceberg

- **mesure** — un palier qui, **après avoir été exécuté**, se recharge à un
  montant comparable, plusieurs fois de suite.
- **définition** — compter les cycles exécution → recharge au même palier, avec
  leur délai et le rapport des tailles. Distinguer du simple repost par la
  régularité du montant et la brièveté du délai.
- **observable** — la décomposition A3. Pas d'identité, pas d'`oid`.
- **à l'exécution** — c'est la liquidité qu'on **ne voit pas mais qui sera là**.
  Elle change la taille traversable et le coût réel : le carnet affiche moins
  qu'il ne contient.
- **É1** — ✅ **traverse.** Famille probablement la plus rentable de tout le
  registre : elle complète le tiers manquant du vocabulaire visuel, elle
  traverse, et elle n'est pas de la persistance.
- **redite** — aucune. Absente de l'ancien catalogue.
- **coût** — estimé : une passe sur la sortie d'A3 pour apparier les cycles
  exécution → recharge — **minutes** par jour-symbole, **une fois A3 payée** :
  le coût réel est porté par A3, sa dépendance déclarée.
- **périmètre minimal** — **J3**.

---

### B4 · Taux d'absorption et fraction exécutée

- **mesure** — quelle part d'un mur est réellement **consommée** quand le prix
  vient au contact.
- **définition** — masse exécutée au palier rapportée à la masse présente à
  l'instant du contact.
- **observable** — exécutions au palier, plus une définition opératoire du
  contact.
- **à l'exécution** — c'est directement le **coût de traversée**. C'est la
  grandeur qui relie tout le reste à une unité économique.
- **É1** — ✅ traverse.
- **redite** — ⚠️ **piège connu** : cette grandeur partage son terme d'exécution
  avec la cible d'apprentissage. Ce n'est **pas** un second témoin indépendant.
  À traiter comme une **unité de sortie** (P8), pas comme une feature.
- **coût** — estimé : **minutes** par jour-symbole une fois le contact défini —
  mais la fiche est **incalculable tant que « contact » n'a pas de définition
  opératoire** (blocage B7) : le vrai coût est là, pas dans le calcul.
- **périmètre minimal** — **J8** : les contacts francs sur un mur jugé sont des
  événements rares, trois jours n'en porteraient pas assez pour une corrélation
  de rang. Déclaré d'avance pour cette raison, pas après un résultat.

---

### B5 · Temps de premier passage

- **mesure** — combien de temps avant que le prix atteigne un palier donné.
- **définition** — distribution du délai d'atteinte, conditionnée à la distance
  et à la volatilité courante.
- **observable** — la trajectoire du prix. Rien d'autre.
- **à l'exécution** — il donne l'horizon sur lequel un ordre limite a une chance
  d'être servi. Sans lui, « le mur va-t-il tenir » est mal posé : il faut savoir
  *jusqu'à quand*.
- **É1** — ✅ traverse.
- **redite** — faible. C'est une grandeur de **calibration d'horizon** plus qu'un
  signal, et c'est comme ça qu'il faut s'en servir.
- **coût** — estimé : le prix seul, distribution de délais d'atteinte —
  **secondes à minutes** par jour-symbole.
- **périmètre minimal** — **J3**.

---

# C. La forme du carnet

⚠️ **Bloc à haut risque de redite.** Tout ce qui suit mesure, par des chemins
différents, à quel point la liquidité est **concentrée et durable**. C'est très
exactement ce qu'a fait la sonologie avant d'apporter presque zéro. Aucune fiche
de ce bloc ne passe É2 sans un gain incrémental démontré.

---

### C1 · Concentration de la liquidité

- **mesure** — quelques gros murs, ou une liquidité diffuse.
- **définition** — indice de concentration sur les masses de la bande. L'entropie
  en est **une** écriture parmi d'autres ; l'indice de Herfindahl et la part du
  premier décile en sont d'autres, moins chères.
- **observable** — le carnet dans la bande.
- **à l'exécution** — un carnet concentré casse par sauts ; un carnet diffus
  glisse. Ça change la manière de découper un ordre, pas la direction.
- **É1** — ⚠️ le filtre `v > médiane` **censure par le bas**, donc il fabrique
  mécaniquement de la concentration apparente. Non mesurable en l'état sans
  correction (voir F3).
- **redite** — **forte**. C'est le représentant unique retenu pour toute une
  famille : entropie, énergie libre, flatness, indices de désordre, information
  de Fisher. É0 les fond ici.
- **coût** — estimé : un indice par photo de la bande — **minutes** par
  jour-symbole. Herfindahl et part du premier décile d'abord ; l'entropie
  n'apporte que si les deux versions bon marché échouent.
- **périmètre minimal** — **J3**.

---

### C2 · Forme et courbure du carnet

- **mesure** — la géométrie du profil de masse en fonction de la distance au
  prix : pente, convexité, ruptures.
- **définition** — dérivées première et seconde du profil cumulé, sur la grille
  de production.
- **observable** — le carnet dans la bande.
- **à l'exécution** — la pente **est** la fonction de coût : elle dit ce que coûte
  chaque tranche supplémentaire. C'est l'usage le plus direct de tout ce bloc.
- **É1** — ⚠️ dégradée par la censure et le plafond de paliers, comme C1.
- **redite** — **forte**. Représentant unique pour : courbure locale, potentiel,
  champ de forces, paysage énergétique, élasticité, pression mécanique, tension
  de surface, énergie stockée. Neuf noms, un calcul.
- **coût** — estimé : deux dérivées discrètes du profil cumulé par photo —
  **minutes** par jour-symbole.
- **périmètre minimal** — **J3**.

---

### C3 · Diffusion anormale du prix

- **mesure** — le prix diffuse-t-il normalement, ou plus lentement (il colle), ou
  plus vite (il court) ?
- **définition** — croissance du déplacement quadratique moyen avec l'horizon.
  Un exposant sous 1 indique un régime collant, au-dessus de 1 un régime
  directionnel.
- **observable** — le prix seul.
- **à l'exécution** — un régime collant favorise les ordres limites ; un régime
  directionnel les punit. C'est un réglage de style d'exécution, pas un signal
  d'entrée.
- **É1** — ✅ traverse.
- **redite** — **forte**. Représentant unique pour : Hurst, DFA, multifractales,
  dimension de corrélation, fractalité.
- **coût** — estimé : déplacement quadratique moyen sur le prix seul, une
  poignée d'horizons — **secondes** par jour-symbole.
- **périmètre minimal** — **J3**.

---

# D. Le régime — quand le système bascule

Bloc **spéculatif et non prioritaire**, conservé parce que sa question est la
bonne : un mur qui cède n'est pas un événement isolé mais souvent le premier
d'une série.

---

### D1 · Ralentissement critique

- **mesure** — un système qui approche d'une bascule met de plus en plus de temps
  à revenir à son état après une perturbation.
- **définition** — croissance de l'autocorrélation à retard court et de la
  variance de la masse de bande, sur une fenêtre glissante.
  **Entrée au banc (correction du 05/08, II.2)** : l'**écart** de ces deux
  grandeurs à leur ligne de base glissante — même raison que B1.
- **observable** — la série de masse.
- **à l'exécution** — un signal d'**avertissement**, pas d'entrée : il dit de
  réduire la taille, pas de prendre position.
- **É1** — ⚠️ à mesurer sous dégradation.
- **redite** — représentant unique pour : transitions de phase, bifurcations,
  catastrophes, Freidlin–Wentzell, grandes déviations.
- **coût** — estimé : autocorrélation et variance sur fenêtre glissante —
  **minutes** par jour-symbole.
- **périmètre minimal** — **J8** : une grandeur de régime n'a de contenu que si
  la fenêtre contient au moins un changement de régime — trois jours peuvent
  n'en porter aucun. Déclaré d'avance pour cette raison.

---

### D2 · Cascades

- **mesure** — la disparition d'un mur en déclenche-t-elle d'autres ?
- **définition** — distribution de la taille des grappes de disparitions
  rapprochées dans le temps et l'espace des prix.
  **Entrée au banc (correction du 05/08, II.2)** : la **taille de grappe**,
  quantité déjà monotone — même raison que B1.
- **observable** — la décomposition A3, sur toute la bande.
- **à l'exécution** — c'est le scénario du coût extrême : le slippage n'est pas
  la somme des paliers traversés si les suivants s'effacent à l'approche.
- **É1** — ⚠️ dépend de la finesse temporelle disponible.
- **redite** — représentant unique pour : percolation, avalanches
  auto-organisées, réseaux de réaction, fracture, milieux granulaires.
- **coût** — estimé : grappes de disparitions sur la sortie d'A3, toute la
  bande — **dizaines de minutes** par jour-symbole, une fois A3 payée.
- **périmètre minimal** — **J8** : les grappes de taille non triviale sont des
  événements rares — même raison que D1, déclarée d'avance.

---

# T. Le témoin trivial — hors compte, jamais retenable

### T0 · Masse brute au palier

Exigé par `05` §4 : le premier candidat se juge contre un témoin déclaré
d'avance, jamais contre le vide. Il entre dans le bloc de contrôle dès le
départ (É2 et É4), **ne passe pas les épreuves, ne peut jamais être retenu**,
et il est **hors du compte des 16 candidats** (D10).

- **mesure** — la masse affichée au palier, telle quelle. Volontairement pauvre.
- **définition** — `mag(k, t)`, la colonne de `deep`, sans transformation.
- **observable** — le carnet dans la bande. Rien d'autre.
- **à l'exécution** — aucune : c'est un plancher, pas une grandeur du produit.
- **É1** — ✅ traverse trivialement (sans objet : jamais retenable).
- **redite** — c'est lui, la redite-étalon : tout candidat corrélé `≥ 0,70` à
  T0 est une redite de présence (É2, correction du 05/08).
- **coût** — nul : une lecture de colonne.
- **périmètre minimal** — **J3**.

---

# E. Les protagonistes — ce qui ne traverse pas

**Tout ce bloc est marqué ❌.** Aucune de ces grandeurs n'existera jamais à
l'écran : Binance ne publie pas l'identité des ordres, et ne le fera pas. Elles
ne sont pas pour autant à jeter — elles **fabriquent la vérité** contre laquelle
tout le reste s'entraîne. Le confondre serait l'erreur la plus coûteuse du
projet.

*(Fiches au format d'`05` §1 depuis le 05/08/2026 — régularisation exigée par
`06` avant tout résultat C5 ; une version antérieure ne portait qu'un tableau
résumé. La ligne « à l'exécution » est structurellement vide dans ce bloc :
c'est sa définition, pas un oubli — la voie de sortie est l'observable de
substitution, en tête de bloc.)*

### E1 · Position en file

- **mesure** — le rang d'un ordre dans la queue de son palier.
- **définition** — position FIFO reconstruite par rejeu du cycle de vie des
  `oid` au palier, à chaque instant.
- **observable** — le L4 complet : `oid`, cycle de vie, ordre d'arrivée.
- **à l'exécution** — aucune directement : **fabrique la vérité** (qui sera
  servi, et donc quelle masse affichée est réellement atteignable).
- **É1** — ❌ fabrique la vérité seulement.
- **redite** — aucune côté vérité.
- **coût** — estimé : rejeu ordre par ordre — **heures** par jour-symbole ;
  c'est la grandeur la plus chère du bloc.
- **périmètre minimal** — **J3**.

### E2 · Âge et modifications

- **mesure** — durée de vie et nombre de reposts d'un `oid`.
- **définition** — `timestampDiff` des statuts terminaux, et chaînage des
  reposts au même palier par le même porteur.
- **observable** — les statuts d'ordres du L4 (la source de C5).
- **à l'exécution** — aucune directement : **fabrique la vérité** (patient
  contre nerveux — C5 a montré une médiane de vie NULLE : le tissu de fond
  meurt instantanément).
- **É1** — ❌.
- **redite** — avec B1 version ordre, volontairement : c'est sa vérité.
- **coût** — mesuré par C5 étape 1 : **~10-20 min** par jour-symbole.
- **périmètre minimal** — **J3**.

### E3 · Fragmentation

- **mesure** — combien d'ordres, et de porteurs, composent un mur.
- **définition** — compte d'`oid` et d'`userId` distincts au palier, à
  l'instant du jugement du mur.
- **observable** — statuts L4 joints au carnet reconstruit.
- **à l'exécution** — aucune directement : **fabrique la vérité** (un mur
  d'un acteur n'est pas un mur de dix).
- **É1** — ❌. *(La colonne `n` de `deep` en est l'ombre publique — compte
  d'ordres sans identité : premier candidat d'observable de substitution.)*
- **redite** — faible.
- **coût** — estimé : jointure statuts × paliers — **dizaines de minutes**
  par jour-symbole.
- **périmètre minimal** — **J3**.

### E4 · Dominance

- **mesure** — la part du premier porteur dans la masse du mur.
- **définition** — max sur les `userId` de (masse portée / masse du palier),
  à l'instant du jugement.
- **observable** — comme E3.
- **à l'exécution** — aucune directement : **fabrique la vérité** (typage du
  mur — c'est la grandeur de vérité centrale du produit).
- **É1** — ❌.
- **redite** — E3 en est le dénominateur ; à mesurer entre elles.
- **coût** — estimé : même jointure qu'E3 — **dizaines de minutes**.
- **périmètre minimal** — **J3**.

### E5 · Flux par acteur

- **mesure** — l'OFI restreint aux acteurs dominants, ou aux nouveaux
  entrants.
- **définition** — A1 recalculé sur le sous-ensemble des événements portés
  par les `userId` sélectionnés par E4.
- **observable** — statuts L4 signés par porteur.
- **à l'exécution** — aucune directement : **fabrique la vérité** (qui
  pousse).
- **É1** — ❌.
- **redite** — avec A1 par construction — c'est sa décomposition.
- **coût** — estimé : **minutes** une fois E4 payée.
- **périmètre minimal** — **J3**.

### E6 · Persistance d'identité

- **mesure** — un acteur se retrouve-t-il d'un jour à l'autre ?
- **définition** — recouvrement des ensembles d'`userId` actifs entre jours,
  pondéré par l'activité.
- **observable** — les `userId` des statuts, sur plusieurs jours.
- **à l'exécution** — aucune directement : **fabrique la vérité** (stabilité
  de la population — condition de tout typage qui prétend généraliser).
- **É1** — ❌.
- **redite** — aucune.
- **coût** — estimé : ensembles par jour puis intersections — **minutes**.
- **périmètre minimal** — **J8** : la persistance est une grandeur
  inter-jours, trois jours ne donnent que deux transitions. Déclaré d'avance.

**Le point dur, à écrire avant de mesurer** : *annuler beaucoup n'est pas un
signe* — c'est le métier d'un teneur de marché. Un discriminant qui désigne les
teneurs ne désigne rien.

**La seule voie de sortie** vers le produit : démontrer qu'une de ces grandeurs
a un **observable de substitution** calculable sans identité. C'est une mesure,
pas une intuition, et elle se fait sur la fenêtre où les deux venues sont
enregistrées simultanément.

---

# F. Les contrôles — ce ne sont pas des features

Elles ne prédisent rien. Elles disent si l'instrument ment. Les traiter comme des
candidates est la confusion que ce registre existe pour empêcher.

---

### F1 · Équation de continuité

Ce qui entre dans un palier moins ce qui en sort doit égaler sa variation de
masse. **Elle ferme, ou elle ne ferme pas.** Elle ne se teste pas contre une
cible : elle valide la reconstruction du carnet. Sa place est en P1.

### F2 · Renormalisation

Un phénomène réel survit au changement de résolution — 100 ms, 500 ms, 1 s, 5 s,
20 s. **C'est É3 du banc**, pas une grandeur. C'est le seul élément de l'ancien
catalogue qui protège au lieu de proposer un calcul de plus.

### F3 · Censure et troncature

Le filtre `v > médiane` coupe par le bas, et la probabilité d'être coupé décroît
avec la masse : la censure est **corrélée à ce qu'on étudie**. Un palier qui
rétrécit sort de l'observation avant de sortir du carnet. Correcteurs :
estimateur de survie sous censure à droite, modèle à hasards proportionnels,
estimateurs sous troncature à gauche pour les ordres présents avant le début
d'observation. Sans ça, **toute durée de vie mesurée sur le flux public est
fausse, et fausse dans le sens qui flatte les gros murs**.

### F4 · Biais de sélection par la durée

Échantillonner des objets à des instants donnés capture les objets longs bien
plus souvent que les courts. Une population sélectionnée sur la survie produit
**mécaniquement** des taux de disparition élevés. Correcteurs classiques :
repondération par l'inverse de la durée, correction du paradoxe de l'inspection.
À traiter **avant** d'interpréter tout taux de disparition, et notamment celui
qui a fermé le transfert.

### F5 · Fluctuation-dissipation

La réponse d'un système à une perturbation est reliée à ses fluctuations
spontanées. Sur un carnet, c'est un **test de cohérence** entre la résilience
mesurée après une exécution et la variabilité de la masse au repos. Si les deux
ne concordent pas, l'instrument est suspect avant que le marché ne le soit.

---

# G. Le cadre — ce qui conditionne l'usage de tout le reste

### G1 · Transfert de domaine

On apprend sur une distribution, on applique sur une autre. Outils :
repondération d'importance sous décalage des entrées, correction du décalage des
proportions, apprentissage de représentations invariantes. Et surtout **les
conditions d'impossibilité** — quand les supports ne se recouvrent pas, aucun
modèle ne franchit l'écart. La mesure préalable est un **recouvrement**, elle
n'exige aucun apprentissage, et elle peut trancher tôt.

Le plafond se dit dans tout rendu : sans identité côté Binance, la traversée ne
se valide jamais contre la vérité, seulement contre un proxy.

### G2 · Multiplicité des tests

**Défaut du protocole, pas une grandeur.** On jugera plusieurs dizaines de
candidats, sur cinq résolutions, sur deux ou trois symboles. À seuil nominal de
5 %, un sur vingt ressort « significatif » sans aucun phénomène — mécaniquement.
`05_Protocole_de_selection.md` exige un intervalle de confiance par candidat et
**aucune correction sur la collection**. À corriger là-bas : contrôle du taux de
fausses découvertes, nombre de candidats déclaré à l'avance, et É0 appliqué
sérieusement puisque fondre les doublons réduit le nombre de tests réellement
indépendants.

---

# Annexe A — Ordre de passage recommandé

Il découle des trois lignes É1, « à l'exécution » et « redite ». Il n'a rien à
voir avec l'intérêt intellectuel des fiches.

| rang | fiches | pourquoi |
|---|---|---|
| 1 | **A3** puis **B3** | traversent, ne redisent rien, et portent le typage — c'est le produit |
| 2 | **A1, A2** | traversent, coût faible, répondent à la question du projet |
| 3 | **F1, F3, F4** | contrôles : sans eux, les mesures suivantes ne sont pas interprétables |
| 4 | **B1, B2, B5** | traversent, mais redite probable — É2 décide |
| 5 | **A4, A5, C2** | utiles à l'exécution, dégradation à mesurer |
| 6 | **E1-E6** | vérité seulement — travail parallèle, jamais dans le produit |
| 7 | **C1, C3, D1, D2** | spéculatif ou fortement redondant — en dernier, si les rangs précédents laissent de la place |

---

# Annexe B — Où sont passés les ~300 noms

Traçabilité du fond É0. **Rien n'est supprimé : tout est rangé.** Une fusion se
conteste par un chiffre de corrélation, jamais par une opinion — et si une
mesure démontre qu'une fusion était abusive, elle se défait par ADR.

| fondus dans | noms d'origine |
|---|---|
| **C2** forme et courbure | potentiel, potentiel de marché, champ de forces, paysage énergétique, courbure locale, énergie potentielle, énergie stockée, élasticité, pression mécanique, viscosité, tension de surface, géométrie de l'information, courbure de Ricci, order book shape |
| **C1** concentration | entropie du carnet, énergie libre, information de Fisher, flatness spectrale, densité spectrale, théorie de l'information algorithmique, théorie spectrale |
| **C3** diffusion anormale | Hurst, DFA, multifractales, dimension de corrélation, fractales, diffusion, marche aléatoire |
| **D1** ralentissement critique | criticité, transitions de phase, bifurcations, catastrophes, Freidlin–Wentzell, grandes déviations, théorie des verres |
| **D2** cascades | percolation, avalanches auto-organisées, branchement, réseaux de réaction, fracture, milieux granulaires, réaction-diffusion, automates cellulaires |
| **A6** auto-excitation | Hawkes, self-exciting cancel process, taux de branchement, synchronisation, Kuramoto, résonance |
| **B1** taux de disparition | queue dynamics, files d'attente M/M/1 et M/G/1, survival analysis, théorie des extrêmes, temps de service, saturation |
| **A5** propagateur | impact, noyau de décroissance, Mori–Zwanzig, théorie de la réponse |
| **F5** fluctuation-dissipation | fluctuation-dissipation, réponse linéaire |
| **B5** premier passage | mean first passage time, Fokker–Planck, flux de probabilité, courant de liquidité, Boltzmann, théorie cinétique, transport optimal |

**Écartées, avec leur raison** — pas éliminées du dossier, mais sans fiche : les
sections empruntées à la turbulence, à la dynamique moléculaire, à la
biophysique, aux neurosciences théoriques, à la biologie évolutive, à
l'électromagnétisme, à la mécanique hamiltonienne, à la physique quantique
mathématique et à la topologie algébrique. Motif commun : **aucune ligne « à
l'exécution » ne peut être écrite pour elles.** Elles proposent une analogie, pas
une grandeur. Une seule ligne suffirait à les rouvrir — qu'on démontre ce qu'elles
changent quand on doit poster, retirer ou traverser.


---
---

## PARTIE II — ARCHIVE : le catalogue d'origine

> **Ce qui suit n'est plus le document de travail.** La partie I le remplace.
>
> Il est conservé intégralement, sans une ligne réécrite, pour trois raisons :
>
> 1. **la doctrine du dossier** — on n'efface pas, on range et on pointe. Une
>    fusion faite en partie I se conteste en revenant ici lire le texte
>    d'origine ;
> 2. **la traçabilité d'É0** — l'annexe B dit dans quelle fiche chaque nom a été
>    rangé ; cette partie dit ce que ce nom voulait dire, avec ses formules ;
> 3. **le détail que les fiches ne portent pas** — définitions développées,
>    écritures mathématiques, exemples. Une fiche tient en six lignes ; certaines
>    idées demandent une page pour être comprises avant d'être jugées.
>
> **Rien ici n'a valeur de plan, et rien n'y a été validé.** Les classements par
> étoiles, les jugements d'intérêt et les affirmations de nouveauté sont ceux du
> texte d'origine et sont explicitement désavoués par la partie I. La section
> XXXIX ci-dessous est l'addendum du 05/08/2026 : elle ajoute six familles
> absentes, dont cinq sont devenues des fiches et une — la multiplicité des
> tests — est un défaut du protocole de sélection, à corriger dans
> `05_Protocole_de_selection.md`.

---

Oui, mais **pas exactement comme dans ces slides**. En fait, ton projet est déjà plus riche que ce qu'elles présentent.

Ces slides résument les travaux de **Cont, Kukanov & Stoikov (2014)** :

* ne pas utiliser le déséquilibre statique du carnet (OBI),
* utiliser le **Order Flow Imbalance (OFI)**,
* éventuellement le cumuler (CSF),
* puis régresser le mouvement du prix sur ce flux.

C'est très adapté pour prédire le **prix à très court terme**.

Ton problème est différent.

---

## Ce qui est directement réutilisable

### 1. OFI

Oui.

Tu possèdes maintenant les **diffs du carnet** au niveau événementiel.

Tu peux calculer exactement

[
OFI_t=\sum e_n
]

où chaque ajout, retrait ou exécution modifie le flux.

C'est probablement une excellente feature.

---

### 2. Cumulative Signed Flow (CSF)

Oui également.

Au lieu de regarder seulement l'événement courant :

[
CSF=\sum OFI
]

sur les 1 s, 3 s ou 5 s précédentes.

Pour ton problème, je testerais plusieurs fenêtres :

* 500 ms
* 1 s
* 3 s
* 5 s

avant le contact.

---

### 3. Microprice

Très probablement.

Le microprice

[
P_\mu=
\frac{V_aP_b+V_bP_a}{V_a+V_b}
]

est souvent meilleur que le mid.

Tu peux en tirer

* microprice-mid
* microprice-wall
* distance mur→microprice

---

## Ce qu'il faut adapter

Les slides cherchent à prédire

[
\Delta P
]

Toi tu veux prédire

[
y_{post}
]

c'est-à-dire

> quelle fraction du mur survivra après le contact.

Donc les mêmes outils deviennent des **features**, pas la cible.

Par exemple

```
Avant contact

OFI = +3000

CSF = +12000

Microprice > Mid

=> probabilité élevée que
le mur ASK soit mangé
```

Le modèle apprend ensuite la relation avec **y_post**.

---

## Ce que je trouve encore plus intéressant pour toi

Grâce au deep book tu peux généraliser OFI.

Au lieu de

```
OFI niveau 1
```

tu peux calculer

```
OFI autour du mur
```

ou

```
OFI entre
0.1 % et 0.3 %
```

ou encore

```
OFI devant le mur
OFI derrière le mur
```

C'est beaucoup plus proche de ton problème.

---

## Ce que les slides ne couvrent

C'est là où ton projet devient original.

Tu disposes de :

* identité des wallets ;
* âge des ordres ;
* fragmentation ;
* nombre de modifications ;
* dominance d'un wallet ;
* historique du mur ;
* labels "survit / disparaît".

Tout cela n'existe pas dans le papier de Cont.

Tu peux donc construire des variantes comme

[
OFI_{dominant}
]

ou

[
OFI_{nouveaux\ wallets}
]

ou

[
OFI_{devant\ le\ mur}
]

ce qui est beaucoup plus spécifique au spoofing.

---

## Ce que je testerais en priorité

Avec ton nouveau pipeline, voici les premières features mathématiques que j'ajouterais :

1. **OFI** (0,5 s / 1 s / 3 s avant le contact).
2. **CSF** (flux cumulé).
3. **Microprice − Mid**.
4. **Distance Mur − Microprice**.
5. **OFI local autour du mur** (± quelques paliers autour du niveau concerné).
6. **OFI cumulé dans la bande P0** (celle que `hl_deep` couvre désormais à 100 %).

À mon avis, ces outils valent la peine d'être intégrés à ton banc d'essai. Ils sont bien établis dans la littérature sur la microstructure, et surtout ils sont **complémentaires** de tes variables actuelles (taille du mur, âge, fragmentation, identité, etc.). Le plus intéressant sera de mesurer leur **gain incrémental** : est-ce qu'ils améliorent réellement le classement (`AUC pairwise`, `D10/D1`, etc.) par rapport à ton jeu de features existant. C'est exactement le type de question que ton pipeline est maintenant capable de trancher de manière objective.


Oui. En réalité, **la microstructure moderne est remplie de concepts "physico-économiques"**. Beaucoup viennent directement de la mécanique statistique, de la théorie des files d'attente, des systèmes complexes ou de la théorie des réseaux.

Dans ton cas (détection de murs qui vont tenir ou disparaître), certains sont particulièrement intéressants.

---

# 1. Order Flow Imbalance (OFI) ⭐⭐⭐⭐⭐

Le plus connu.

Idée :

> ce ne sont pas les stocks qui comptent mais les flux.

Tu l'as déjà identifié.

---

# 2. Queue Imbalance ⭐⭐⭐⭐☆

Au lieu de regarder tout le carnet :

[
QI=\frac{V_{bid}-V_{ask}}{V_{bid}+V_{ask}}
]

mais uniquement sur quelques niveaux.

Très utilisé sur les futures.

---

# 3. Queue Position ⭐⭐⭐⭐⭐

Issu de la théorie des files d'attente.

Une idée simple :

si ton mur est

* premier de la file
* dixième
* centième

ce n'est pas le même risque d'être exécuté.

Pour ton problème c'est énorme.

---

# 4. Hawkes Process ⭐⭐⭐⭐⭐

Très utilisé en finance.

Les ordres s'auto-excitent.

Un ajout augmente la probabilité :

* d'autres ajouts,
* des annulations,
* des exécutions.

Mathématiquement :

[
\lambda(t)=\mu+\sum \phi(t-t_i)
]

Tu peux remplacer cette intensité par une feature.

---

# 5. Self Exciting Cancel Process ⭐⭐⭐⭐☆

Même idée mais pour les retraits.

Une rafale d'annulations annonce souvent :

* une liquidation,
* une panique,
* un spoofing.

---

# 6. Liquidity Pressure ⭐⭐⭐⭐⭐

Pas seulement OFI.

Une force :

[
F=\frac{\text{flow}}{\text{depth}}
]

Même flux

*

carnet fin

=

pression beaucoup plus forte.

Très physique.

---

# 7. Resilience ⭐⭐⭐⭐⭐

Un concept magnifique.

Le marché est un ressort.

Tu retires 500 BTC.

Question :

> combien de temps met le carnet à revenir ?

On mesure

[
\tau_{recovery}
]

Très étudié.

---

# 8. Relaxation Time ⭐⭐⭐⭐☆

Encore de la physique.

Après un choc :

combien de secondes avant retour à l'équilibre ?

---

# 9. Entropy ⭐⭐⭐⭐⭐

Le carnet est vu comme une distribution.

On calcule

[
H=-\sum p_i\log p_i
]

Un carnet très concentré

↓

faible entropie.

---

# 10. Spectral Density ⭐⭐⭐⭐☆

Tu avais déjà commencé.

Fourier

Wavelets

Spectre.

Très utilisé pour distinguer

* activité organique
* activité algorithmique.

---

# 11. Diffusion / Random Walk ⭐⭐⭐⭐☆

Mesurer

[
D=\frac{\langle x^2\rangle}{t}
]

Le prix diffuse-t-il normalement ?

ou

sub-diffusion ?

ou

super-diffusion ?

---

# 12. Persistence ⭐⭐⭐⭐⭐

Exposant de Hurst.

[
H
]

H>0.5

persistant.

H<0.5

anti-persistant.

---

# 13. Criticality ⭐⭐⭐⭐☆

Les marchés ressemblent parfois à un système critique.

Avalanches

Liquidations

Cascade.

Très proche des modèles de sable de Bak.

---

# 14. Branching Ratio ⭐⭐⭐⭐⭐

Issu des Hawkes.

Très utilisé.

Si

[
n=0.95
]

le marché est proche de l'instabilité.

---

# 15. Absorption Rate ⭐⭐⭐⭐⭐

Celui-ci me paraît particulièrement adapté à ton projet.

Au contact d'un mur :

[
\text{Absorption}
=================

\frac{\text{volume exécuté}}
{\text{flow arrivant}}
]

Très lié à ta cible.

---

# 16. Local Curvature ⭐⭐⭐⭐☆

Voir le carnet comme un potentiel.

La pente

et

la courbure

autour d'un mur.

---

# 17. Potential Field ⭐⭐⭐⭐⭐

Mon préféré pour ton projet.

On considère chaque mur comme une masse.

On construit

[
U(x)=\sum_i
\frac{V_i}{d_i^\alpha}
]

où

* (V_i) = taille
* (d_i) = distance

Le prix évolue dans un champ de potentiel.

Les gros murs créent des "puits".

Tu disposes maintenant du **deep book**, donc tu peux enfin calculer cela correctement.

---

# 18. Elasticity ⭐⭐⭐⭐☆

Même idée.

Le prix répond-il fortement

ou

faiblement

à un flux donné ?

---

# 19. Hazard Rate ⭐⭐⭐⭐⭐

Très intéressant.

Un mur est un objet vivant.

On estime

[
h(t)
====

P(\text{annulation dans }dt
\mid
\text{encore vivant})
]

C'est exactement de l'analyse de survie.

---

# 20. Mean First Passage Time ⭐⭐⭐⭐☆

Concept classique en physique.

Temps moyen avant que

* le prix touche le mur,
* ou que le mur disparaisse.

---

## Ceux que je pense vraiment adaptés à ton projet

Si je devais n'en retenir que quelques-uns, ce serait :

| Concept            | Intérêt |
| ------------------ | ------- |
| OFI                | ⭐⭐⭐⭐⭐   |
| Hawkes             | ⭐⭐⭐⭐⭐   |
| Queue Position     | ⭐⭐⭐⭐⭐   |
| Liquidity Pressure | ⭐⭐⭐⭐⭐   |
| Resilience         | ⭐⭐⭐⭐⭐   |
| Hazard Rate        | ⭐⭐⭐⭐⭐   |
| Potential Field    | ⭐⭐⭐⭐⭐   |
| Absorption Rate    | ⭐⭐⭐⭐⭐   |
| Entropy            | ⭐⭐⭐⭐☆   |
| Branching Ratio    | ⭐⭐⭐⭐☆   |

Ce qui est intéressant, c'est que **ton infrastructure actuelle (open book complet, identité des ordres, deep book, labels de survie)** permet enfin de calculer la plupart de ces quantités de façon fidèle. Beaucoup de travaux académiques doivent se contenter de carnets limités à 10–20 niveaux ou sans identité des ordres ; toi, tu peux construire des versions beaucoup plus riches de ces concepts et mesurer objectivement leur pouvoir prédictif sur **y_post** plutôt que sur le simple mouvement du prix.


Oui. En fait, il existe toute une "physique des carnets d'ordres". Beaucoup de ces concepts sont plus intéressants que les indicateurs techniques classiques, surtout avec les données Hyperliquid que tu possèdes.

En restant sur des concepts qui ont une vraie littérature scientifique :

### 1. Propagateur d'impact (Propagator Model) ⭐⭐⭐⭐⭐

L'idée est que chaque exécution pousse le prix, mais que cet impact décroît avec le temps.

[
\Delta p_t=\sum_i G(t-t_i),\epsilon_i,v_i^\alpha
]

où (G) est un noyau de décroissance.

C'est directement applicable à tes données.

---

### 2. Hawkes Process ⭐⭐⭐⭐⭐

Les ordres arrivent en grappes.

Un ordre augmente temporairement la probabilité d'autres ordres.

[
\lambda(t)=\mu+\sum_i \phi(t-t_i)
]

Très utilisé par JP Morgan, Citadel, etc.

Hyperliquid est idéal pour ça car tu as chaque événement.

---

### 3. Queue Dynamics

Traiter chaque file d'attente comme une naissance/mort :

* nouveaux ordres
* annulations
* exécutions

On obtient une vitesse de disparition.

Tu peux estimer :

* espérance de vie
* hazard rate
* demi-vie d'un mur

---

### 4. First Passage Time

Question :

> combien de temps faut-il pour qu'un mur soit touché ?

Très utilisé en physique.

Tu peux prédire

* survie
* temps avant exécution
* temps avant fuite.

---

### 5. Potentiel de marché

Considérer les gros murs comme un potentiel :

[
U(x)=\sum_i \frac{V_i}{|x-x_i|}
]

Le prix se déplace dans ce potentiel.

C'est rarement utilisé directement mais très intéressant.

---

### 6. Entropie du carnet

Mesurer le désordre.

Exemple

[
H=-\sum_i p_i\log p_i
]

avec

[
p_i=\frac{V_i}{\sum V}
]

Faible entropie

→ quelques gros murs

Grande entropie

→ liquidité diffuse.

---

### 7. Information géométrique

Voir le carnet comme une surface.

Mesurer

* pente
* courbure
* convexité.

Les papiers parlent souvent de :

Order Book Shape

---

### 8. Théorie des percolations

Très originale.

Chaque mur est un nœud.

Les exécutions propagent un "front".

Quand plusieurs murs disparaissent :

cascade.

Très proche d'une transition de phase.

---

### 9. Renormalisation

Regarder le carnet :

* à 100 ms
* 1 s
* 5 s
* 20 s
* 1 min

et voir ce qui reste invariant.

Tu as justement assez de données pour ça.

---

### 10. Flux de probabilité (Fokker–Planck)

Au lieu de prédire un prix.

Prédire la densité

[
P(price,t)
]

Très utilisé en finance quantitative.

---

### 11. Pression mécanique

Considérer le carnet comme un ressort.

Mur très gros

↓

pression importante

↓

prix repoussé.

On définit parfois

[
F=\frac{\Delta V}{\Delta x}
]

analogue d'une force.

---

### 12. Énergie potentielle

Un mur contient une énergie

[
E=V\times d
]

(volume × distance).

Tu peux mesurer

* énergie stockée
* énergie libérée lorsqu'il casse.

---

### 13. Diffusion anormale

Le prix n'est pas un Brownien.

Calculer

[
MSD(\tau)
]

si

[
MSD\propto\tau^\alpha
]

avec

* α=1 diffusion normale
* α<1 sous-diffusion
* α>1 super-diffusion.

---

### 14. Fractales

Le carnet possède souvent une dimension fractale.

On peut mesurer

* Hurst
* DFA
* multifractales.

---

### 15. Théorie des files d'attente

Très adaptée à Hyperliquid.

Chaque niveau est une queue M/M/1 ou M/G/1.

On obtient

* temps moyen avant exécution
* taux de service
* saturation.

---

## Ce qui me paraît le plus prometteur pour ton projet

Avec ce que tu as construit (ordre par ordre, identité des wallets, reconstruction du carnet, événements à ~87 ms), je me concentrerais sur :

1. **Order Flow Imbalance (OFI)** — mesurer la pression instantanée du flux.
2. **Hawkes Processes** — modéliser les cascades d'ordres et d'annulations.
3. **Queue Dynamics / Survival Analysis** — prédire la durée de vie des murs.
4. **Propagator Model** — relier les événements du carnet à l'impact futur sur le prix.
5. **Microprice** — utiliser un prix "équilibré" plutôt que le simple mid-price.
6. **Entropie et géométrie du carnet** — caractériser les régimes de marché (liquidité concentrée vs diffuse).

Le point intéressant est que ces approches ne sont pas de simples indicateurs : elles reposent sur une vision physique (flux, diffusion, survie, potentiel, files d'attente) et s'accordent particulièrement bien avec un flux événementiel complet comme celui d'Hyperliquid. C'est justement le type de données nécessaire pour les estimer correctement.


Oui. Si on va encore plus loin dans l'approche "physico-économique", il existe des concepts très puissants qui sont encore peu utilisés en crypto mais très présents en physique statistique, mécanique des fluides et théorie des systèmes complexes.

En lisant tout ce que tu développes (épisodes, absorption, fuite, murs, rang, etc.), je pense que certains pourraient être beaucoup plus intéressants qu'un simple OFI.

---

# 1. Flux de probabilité (Probability Current)

En physique statistique, on ne regarde pas où sont les particules mais où va la probabilité.

Au lieu de mesurer :

> il y a 100 BTC ici

on mesure

> combien de probabilité traverse ce niveau par seconde.

Sur un carnet :

[
J=\rho \times v
]

avec

* densité de liquidité
* vitesse des annulations/exécutions

Tu obtiens une véritable **vitesse de déplacement de la liquidité**.

---

# 2. Potentiel

Très utilisé en électrostatique.

On définit un potentiel

[
U(x)
]

Les prix "descendent" naturellement vers les minima.

Un énorme mur devient un puits de potentiel.

Puis lorsqu'il disparaît :

le potentiel saute.

Cela ressemble énormément aux spoofers.

---

# 3. Champ de forces

Chaque mur attire ou repousse le prix.

Comme des masses gravitationnelles.

[
F=-\nabla U
]

Le prix devient une particule.

Tu peux additionner les forces de tous les murs.

---

# 4. Diffusion

Le prix peut être vu comme une particule brownienne.

L'ordre flow change le coefficient de diffusion.

Tu peux mesurer

[
D(t)
]

qui représente la mobilité instantanée du marché.

---

# 5. Énergie libre

Une idée magnifique.

On définit

[
F=E-TS
]

où

* E = énergie du carnet
* S = désordre

Le marché choisit les états minimisant cette énergie.

Les spoofers injectent énormément d'énergie sans modifier réellement l'état.

---

# 6. Entropie

Tu peux mesurer

[
H=-\sum p_i\log p_i
]

de la répartition de la liquidité.

Un spoofeur réduit brutalement l'entropie.

Une absorption l'augmente.

---

# 7. Information de Fisher

Très utilisée pour détecter une transition de phase.

Elle explose avant :

* crash
* squeeze
* liquidation

sans connaître le futur.

---

# 8. Percolation

En physique des réseaux.

Question :

> existe-t-il un chemin de liquidité continu ?

Les trous du carnet deviennent un problème de percolation.

Très utilisé en science des matériaux.

---

# 9. Renormalisation

Une idée extrêmement profonde.

Un vrai phénomène doit survivre lorsqu'on change d'échelle.

Par exemple :

* carnet 20 ms
* carnet 100 ms
* carnet 500 ms

Si ton score disparaît en changeant la résolution :

ce n'est probablement pas un phénomène fondamental.

---

# 10. Temps de relaxation

Après une perturbation :

combien de temps faut-il au carnet pour revenir à son équilibre ?

[
\tau
]

Tu mesures

* disparition d'un mur
* temps de reconstruction

Les spoofers ont souvent un τ extrêmement faible.

---

# 11. Viscosité du marché

Très proche de ton idée.

Deux carnets peuvent avoir la même profondeur.

Mais l'un "coule" beaucoup plus vite.

On peut définir

[
\eta
]

comme une viscosité de liquidité.

---

# 12. Tension de surface

Très employée dans certains papiers de microstructure.

La frontière bid/ask est vue comme une interface.

Plus la tension est forte,

plus il est difficile pour le prix de traverser.

---

# 13. Transition de phase

Un carnet peut passer brutalement

de

stable

à

chaotique.

Comme :

* eau → vapeur

Tu peux rechercher des variables critiques.

---

# 14. Équations de continuité

Comme en mécanique des fluides.

La liquidité ne disparaît pas.

Elle vérifie

[
\frac{\partial \rho}{\partial t}
+
\nabla\cdot J
=============

S
]

avec

* ρ = densité de liquidité
* J = flux
* S = créations/annulations

Tu obtiens une conservation locale.

---

# 15. Théorie des files d'attente (Queueing Theory)

Très utilisée dans les bourses.

Chaque niveau du carnet devient une file M/M/1 ou M/G/1.

On peut calculer :

* temps d'attente
* probabilité d'exécution
* congestion
* stabilité

---

# 16. Réseaux de réaction (Reaction Networks)

Les événements deviennent des réactions chimiques :

```
Limit Order
      ↓

Order Book

      ↓
 Cancel

      ↓
 Execute
```

On étudie les vitesses de réaction.

---

# 17. Synchronisation (Kuramoto)

Les gros wallets peuvent devenir synchronisés.

Comme des oscillateurs.

Tu peux détecter :

* spoof coordonné
* cascades
* propagation

---

# 18. Théorie des avalanches (Self-Organized Criticality)

Comme les tas de sable.

Une minuscule annulation peut déclencher

* liquidation
* cascade
* sweep

Les tailles suivent souvent des lois de puissance.

---

## Ce que je regarderais en priorité dans ton projet

Avec les données Hyperliquid que tu possèdes (états d'ordres, identités des wallets, reconstruction fine du carnet, événements horodatés), je pense que les concepts les plus prometteurs sont :

1. **Équation de continuité de la liquidité** (conservation des flux).
2. **Flux de probabilité / courant de liquidité** plutôt qu'un simple déséquilibre statique.
3. **Potentiel et champ de forces** créés par les murs de liquidité.
4. **Temps de relaxation** après apparition ou disparition d'un mur.
5. **Entropie et énergie libre** pour distinguer une liquidité "naturelle" d'une liquidité artificielle.
6. **Transition de phase** pour détecter les changements brusques de régime avant les grands mouvements.

Ces approches ont un point commun : elles décrivent le carnet comme un **système dynamique** plutôt qu'une simple collection de niveaux de prix. C'est une façon de raisonner qui est très proche de ce que tu construis déjà avec les épisodes, les flux d'ordres et l'absorption, mais qui peut conduire à des variables nouvelles et potentiellement plus robustes que les indicateurs classiques de microstructure.

Oui. Si on monte encore d'un niveau, on quitte la microstructure classique (OFI, VPIN, Kyle...) pour entrer dans la **physique des systèmes hors équilibre**. C'est là que se trouvent probablement les idées les plus originales. Certaines n'ont quasiment jamais été appliquées sérieusement aux carnets crypto.

---

# 1. Théorie des grandes déviations (Large Deviation Theory) ⭐⭐⭐⭐⭐

Au lieu de modéliser les événements "moyens", on modélise les événements rares.

Par exemple :

> Quelle est la probabilité qu'un mur survive 40 secondes alors que tous meurent en 2 secondes ?

On obtient une fonction d'action

[
P(X)\sim e^{-I(X)}
]

où (I(X)) mesure à quel point un comportement est "contre nature".

Un spoof est précisément un événement à faible probabilité.

---

# 2. Théorie de Freidlin–Wentzell ⭐⭐⭐⭐⭐

Évolution la plus probable d'un système bruité.

Le prix n'est plus une marche aléatoire.

Il suit un chemin optimal dans un paysage de potentiel.

Les spoofers créent un nouveau minimum de potentiel.

Tu peux mesurer :

> quelle trajectoire devient soudainement la plus probable ?

---

# 3. Géométrie de l'information ⭐⭐⭐⭐⭐

On considère chaque carnet comme un point sur une variété.

La distance entre deux carnets n'est plus euclidienne.

On utilise la métrique de Fisher

[
g_{ij}
]

Les changements de régime deviennent des distances géométriques.

Très utilisé en physique quantique.

---

# 4. Théorie des catastrophes (René Thom) ⭐⭐⭐⭐⭐

Extrêmement intéressante.

Le marché reste stable.

Puis un paramètre change très peu.

Et tout saute.

Exemple :

* un mur perd 5 %

→ le prix explose.

Tu peux rechercher les surfaces de catastrophe :

* pli
* fronce
* cusp

Le spoof ressemble énormément à une catastrophe de type cusp.

---

# 5. Théorie des bifurcations

Quand le système change brutalement de dynamique.

Exemple

stable

↓

oscillations

↓

explosion

Les carnets vivent exactement cela.

---

# 6. Critical Slowing Down

Avant une transition de phase :

le système met de plus en plus longtemps à revenir à l'équilibre.

Tu mesures :

* autocorrélation
* temps de relaxation

Avant un gros mouvement cela augmente souvent.

---

# 7. Fluctuation-Dissipation

En physique :

les fluctuations disent comment le système réagira.

Dans un carnet :

beaucoup de petites fluctuations

↓

grande sensibilité future.

Très puissant.

---

# 8. Théorie des champs

Chaque niveau du carnet est un champ

[
\phi(x,t)
]

Les ordres deviennent

des excitations du champ.

Les annulations deviennent

des annihilations.

On obtient des équations différentielles.

---

# 9. Équation de Fokker–Planck ⭐⭐⭐⭐⭐

Tu ne prédis plus le prix.

Tu prédis la densité de probabilité.

[
\frac{\partial p}{\partial t}
=============================

-\frac{\partial}{\partial x}(Ap)
+
\frac12
\frac{\partial^2}{\partial x^2}(Bp)
]

Très utilisée en finance quantitative.

---

# 10. Équation de Boltzmann

Les ordres sont vus comme des particules.

Ils :

* apparaissent
* disparaissent
* se rencontrent

On obtient une cinétique complète.

---

# 11. Théorie cinétique des gaz

Incroyablement proche d'un carnet.

Ordres = molécules

Spread = température

Exécutions = collisions

Annulations = évaporation

Très peu exploré.

---

# 12. Réseaux de transport optimal (Optimal Transport)

Distance de Wasserstein

[
W(P,Q)
]

Elle mesure

combien "coûte"

transformer un carnet dans un autre.

Très supérieure aux distances classiques.

---

# 13. Courbure de Ricci

Oui.

On peut calculer la courbure d'un graphe de liquidité.

Les zones de forte courbure sont souvent

des points critiques.

---

# 14. Persistent Homology (Topological Data Analysis) ⭐⭐⭐⭐⭐

Une des méthodes les plus modernes.

On oublie les indicateurs.

On regarde

la TOPOLOGIE du carnet.

Elle détecte

* trous
* tunnels
* composantes

indépendamment du bruit.

Les spoofers modifient énormément cette topologie.

Très peu de travaux existent.

---

# 15. Théorie spectrale

Diagonaliser le carnet.

Les valeurs propres dominantes

décrivent

les modes naturels du marché.

Les spoofers créent

de nouveaux modes.

---

# 16. Résonance

Deux wallets peuvent entrer

en résonance.

Ils annulent et replacent leurs ordres

à la même fréquence.

Détection via FFT.

---

# 17. Dynamique Hamiltonienne

Construire une énergie

[
H(q,p)
]

avec

* q = position des murs

* p = flux

Puis étudier les trajectoires.

---

# 18. Théorie de Mori–Zwanzig

Réduit un système de millions de variables

à quelques variables lentes.

Très utile pour résumer un carnet immense.

---

# 19. Théorie des réseaux complexes

Construire un graphe

wallet ↔ prix ↔ temps

Puis mesurer

* centralité
* modularité
* communautés

Les spoofers apparaissent souvent comme des communautés très structurées.

---

# 20. Théorie de l'information algorithmique

Mesurer

la complexité de Kolmogorov

du carnet.

Un spoof

est souvent

très compressible.

Un marché naturel

beaucoup moins.

---

# Ce que je pense être les trois idées les plus révolutionnaires pour ton projet

Compte tenu de ce que tu as (historique complet des ordres Hyperliquid, identités de wallets, reconstruction du carnet, événements à très haute résolution), je regarderais en priorité :

1. **Topological Data Analysis (homologie persistante)** : transformer chaque instant du carnet en un objet topologique et détecter les changements de forme plutôt que de simples variations de volume. C'est très peu exploité en microstructure.

2. **Optimal Transport (distance de Wasserstein)** : comparer deux états du carnet par le "coût" nécessaire pour déplacer toute la liquidité d'un état à l'autre. Cela fournit une mesure géométrique beaucoup plus riche qu'une différence de volumes ou un déséquilibre.

3. **Large Deviation Theory** : modéliser explicitement les comportements extrêmement rares (murs qui apparaissent, persistent ou disparaissent d'une manière atypique). Comme le spoofing est précisément un phénomène rare, cette théorie est particulièrement adaptée.

Ces approches sont beaucoup plus profondes que les indicateurs classiques (OFI, micro-price, VPIN, Kyle λ). Elles cherchent à décrire le **système sous-jacent** plutôt qu'à construire un nouvel indicateur à partir des mêmes variables. C'est souvent là que naissent les véritables avancées méthodologiques.



Si on exclut tout ce qui a déjà été évoqué (Ising, percolation, criticalité, réseaux, ondelettes, multifractales, Hawkes, etc.), il reste encore énormément de concepts issus de la physique statistique, de la mécanique, de la théorie des systèmes complexes et de l'information qui ont été peu explorés en finance.

Je les classe par famille.

---

# I. Théorie des champs

Très peu utilisée en trading, pourtant extrêmement puissante.

### Functional Renormalization Group (FRG)

Étudie l'évolution des interactions selon l'échelle.

Application :

* liquidité locale → globale
* mur → cluster → marché entier

---

### Field Theory

Traiter le carnet comme un champ continu

[
\rho(p,t)
]

au lieu d'une liste d'ordres.

Permet :

* équations différentielles
* diffusion
* stabilité
* énergie

---

### Effective Field Theory

Ne modéliser que les interactions importantes.

Très utile lorsque le carnet contient des millions d'ordres.

---

### Landau Theory

Décrire les changements de régime.

Exemple :

marché calme

↓

marché instable

↓

cascade

---

### Ginzburg-Landau

Version dynamique.

Excellent pour :

* apparition
* disparition
* déplacement des murs.

---

# II. Théorie des verres (Spin Glass)

Une mine d'or.

---

### Spin Glass

Marché rempli d'agents incompatibles.

Les minima locaux deviennent :

* faux murs
* pièges
* spoofing.

---

### Energy Landscape

Chaque configuration du carnet possède une énergie.

Le marché cherche les minima.

Tu peux rechercher :

* vallées
* cols
* barrières.

---

### Replica Symmetry Breaking

Utilisé lorsque plusieurs états stables coexistent.

Très intéressant pour :

plusieurs murs concurrents.

---

### TAP equations

Approximation très utilisée en physique.

Jamais vue en order book.

---

# III. Physique hors équilibre

Probablement la famille la plus prometteuse.

---

### Non-equilibrium Thermodynamics

Le carnet n'est jamais à l'équilibre.

On mesure :

* flux
* production d'entropie
* dissipation.

---

### Onsager Reciprocity

Relations entre deux flux.

Exemple :

annulations

↔

créations.

---

### Jarzynski Equality

Comparer

travail injecté

vs

travail réellement dissipé.

---

### Crooks Fluctuation Theorem

Détecter les trajectoires improbables.

Excellent pour le spoofing.

---

### Fluctuation-Dissipation Theorem

Comment une petite perturbation influence le marché.

---

# IV. Turbulence

Très peu exploitée.

---

### Kolmogorov Cascade

Propagation de l'information entre échelles.

Mur

↓

cluster

↓

marché

---

### Intermittency

Explosions très rares.

Typique :

flash spoofing.

---

### Structure Functions

Comparer la rugosité du carnet.

---

### Shell Models

Approximation de turbulence.

Très rapide.

---

# V. Dynamique moléculaire

Le carnet devient un gaz.

---

### Lennard-Jones Potential

Interaction attractive/répulsive entre murs.

---

### Molecular Dynamics

Simulation des ordres comme particules.

---

### Hard Sphere Model

Ordres incompressibles.

---

### Brownian Dynamics

Propagation aléatoire des petits ordres.

---

### Langevin Equation

Très adaptée :

[
m\ddot x+\gamma\dot x+\eta(t)
]

---

### Fokker-Planck

Distribution des états du carnet.

---

# VI. Géométrie différentielle

Très rarement utilisée.

---

### Ricci Curvature

Mesure la courbure du réseau de liquidité.

---

### Information Geometry

Distance entre deux états du carnet.

Très intéressante.

---

### Fisher Metric

Comparer deux distributions.

---

### Wasserstein Geometry

Comparer deux carnets.

Excellent candidat.

---

### Optimal Transport

Déplacement minimal de liquidité.

Très pertinent.

---

# VII. Théorie de l'information

---

### Fisher Information

Mesure la quantité d'information contenue.

---

### Transfer Entropy

Direction réelle de l'information.

HL

→

Binance ?

---

### Directed Information

Encore plus adaptée.

---

### Partial Information Decomposition

Qui apporte réellement l'information ?

---

### Active Information Storage

Mémoire du marché.

---

### Predictive Information

Information utile pour le futur.

---

### Minimum Description Length

Compression maximale des features.

---

# VIII. Théorie du contrôle

---

### Optimal Control

Quelle action minimise le coût ?

---

### Model Predictive Control

Recalcul permanent.

---

### Hamilton-Jacobi-Bellman

Politique optimale.

---

### Pontryagin Principle

Version continue.

---

### Viability Theory

Zones où un mur peut survivre.

---

# IX. Dynamique des systèmes

---

### Lyapunov Exponents

Mesure du chaos.

---

### Koopman Operator

L'un des sujets les plus en vogue.

Transformer un système non linéaire en opérateur linéaire.

Très puissant.

---

### Dynamic Mode Decomposition

Extraction automatique des modes.

---

### Delay Embedding (Takens)

Reconstruire la dynamique cachée.

---

### Attractors

Vers quels états revient le carnet ?

---

### Basin of Attraction

Où finit un mur ?

---

# X. Théorie des catastrophes

Très adaptée aux liquidations.

---

### Fold Catastrophe

---

### Cusp Catastrophe

---

### Butterfly Catastrophe

---

### Swallowtail

---

### Hyperbolic Umbilic

---

# XI. Synchronisation

---

### Kuramoto Model

Synchronisation entre acteurs.

---

### Phase Locking

Synchronisation HL/Binance.

---

### Chimera States

Une partie synchronisée.

L'autre non.

---

# XII. Automates cellulaires

---

### Game of Life

---

### Lattice Gas Automata

---

### Lattice Boltzmann

Peut représenter un flux d'ordres.

---

# XIII. Fracture

---

### Fiber Bundle Models

Quand un mur casse.

---

### Crack Propagation

Propagation des retraits.

---

### Avalanche Models

Très utile.

---

# XIV. Biophysique

---

### Chemotaxis Models

Les ordres suivent un gradient.

---

### Predator-Prey

Maker

vs

Taker.

---

### Population Dynamics

Naissance

Mort

Migration.

---

# XV. Électromagnétisme

---

### Potentiel

---

### Champ électrique

---

### Champ magnétique

---

### Dipôles

Deux murs opposés.

---

### Multipoles

Structure globale.

---

### Lignes de champ

Visualisation de la liquidité.

---

# XVI. Topologie

Très moderne.

---

### Persistent Homology

Détecter les structures persistantes.

---

### Mapper Algorithm

Organisation du carnet.

---

### Betti Numbers

Nombre de trous dans la liquidité.

---

### Morse Theory

Points critiques.

---

### Simplicial Complexes

Interactions multiples.

---

# XVII. Théorie spectrale

---

### Laplacian Spectrum

---

### Spectral Gap

---

### Random Matrix Theory (version avancée)

---

### Resolvent Analysis

---

### Free Probability

---

# XVIII. Grandes déviations

Extrêmement pertinente.

---

### Large Deviation Theory

Probabilité des événements très rares.

---

### Rate Functions

---

### Freidlin-Wentzell Theory

Transitions rares.

---

# XIX. Concepts émergents (2020–2025)

* Neural Operators
* Physics-Informed Neural Networks (PINNs)
* Graph Neural Fields
* Operator Learning (DeepONet)
* Score-Based Diffusion Models
* Schrödinger Bridges
* Mean Field Games
* Neural ODE
* Neural SDE
* Controlled Diffusion Models
* Causal Representation Learning
* Stochastic Thermodynamics
* Information Bottleneck
* Entropic Optimal Transport
* Graph Ricci Flow
* Persistent Laplacians
* Koopman Autoencoders
* Diffusion Maps
* Dynamic Graph Signal Processing

## Les 10 concepts qui me semblent les plus prometteurs pour ton problème

Au vu de ton objectif (détecter des murs réels/spoofés, comprendre leur dynamique, puis transférer d'Hyperliquid vers Binance), je mettrais en priorité :

1. **Koopman Operator** (dynamique non linéaire → linéaire)
2. **Optimal Transport / Wasserstein** (évolution de la liquidité)
3. **Large Deviation Theory** (événements rares comme le spoofing)
4. **Persistent Homology** (structures de liquidité qui persistent)
5. **Transfer Entropy** (causalité Hyperliquid → Binance)
6. **Stochastic Thermodynamics** (création/destruction d'information dans le carnet)
7. **Spin Glass / Energy Landscape** (multiples états stables des murs)
8. **Mean Field Games** (interaction de milliers de traders)
9. **Dynamic Mode Decomposition (DMD)** (modes dominants du carnet)
10. **Schrödinger Bridges** (transport probabiliste optimal entre deux états du carnet)

Ces approches sont encore très peu présentes dans la littérature sur les carnets d'ordres, ce qui en fait des pistes originales si elles sont validées empiriquement. L'important reste toutefois la même discipline que celle que tu avais adoptée : chaque concept doit être transformé en **feature ou modèle testable** et évalué sur un protocole hors échantillon rigoureux, plutôt que retenu pour son élégance théorique.

Oui. Si on va encore plus loin, on quitte l'éconophysique "classique" pour entrer dans les domaines qui sont aujourd'hui actifs en recherche (physique statistique, théorie des systèmes complexes, géométrie, neurosciences, mécanique quantique mathématique, etc.). Voici une liste de concepts rarement cités mais qui pourraient être adaptés à un carnet d'ordres.

---

# XX. Théorie des verres complexes

### p-spin models

Généralisation des spin-glass.

Interactions à 3,4,5... agents.

Idée :

un mur n'est pas influencé par un autre mur mais par des groupes de murs.

---

### Random Energy Model (REM)

Chaque état du carnet possède une énergie aléatoire.

Détecter les vallées profondes.

---

### Generalized Random Energy Model (GREM)

Hiérarchie des états.

Parfait pour

mur

↓

cluster

↓

zone

↓

marché.

---

# XXI. Mécanique hamiltonienne

### Hamiltonian Systems

Construire un Hamiltonien du carnet.

L'évolution minimise l'énergie.

---

### Symplectic Geometry

Très utilisée pour les systèmes conservatifs.

---

### Hamiltonian Monte Carlo

Explorer efficacement les états possibles.

---

### Action Principle

Le marché suit-il une trajectoire de moindre action ?

---

# XXII. Physique quantique (mathématique)

Sans prétendre que le marché est "quantique".

On emprunte uniquement les outils.

---

### Path Integrals (Feynman)

Toutes les trajectoires possibles d'un mur.

---

### Density Matrix

Etat probabiliste du carnet.

---

### Decoherence

Quand un mur cesse d'influencer le marché.

---

### Quantum Graphs

Propagation de l'information.

---

### Wigner Distribution

Analyse temps-fréquence très fine.

---

### Husimi Transform

Version plus robuste.

---

# XXIII. Théorie cinétique

Très prometteur.

---

### Boltzmann Equation

Distribution des ordres.

---

### BGK Approximation

Approximation rapide.

---

### Enskog Theory

Gaz denses.

Le carnet est justement dense.

---

### Chapman-Enskog Expansion

Passage

microscopique

↓

macroscopique.

---

### BBGKY Hierarchy

Hiérarchie des corrélations.

---

# XXIV. Physique des milieux granulaires

Le carnet ressemble énormément à un matériau granulaire.

---

### Jamming Transition

Blocage de liquidité.

---

### Force Chains

Chaînes de support.

---

### Compaction

Compression des ordres.

---

### Granular Temperature

Agitation locale.

---

### Shear Banding

Zones où tout casse.

---

# XXV. Physique des interfaces

---

### KPZ Equation

Croissance des interfaces.

Très utilisée en physique statistique.

---

### Edwards-Wilkinson

Version linéaire.

---

### Surface Roughening

Rugosité du carnet.

---

### Front Propagation

Propagation des murs.

---

# XXVI. Réaction-Diffusion

Très sous-utilisée.

---

### Fisher-KPP

Propagation des ordres.

---

### Gray-Scott

Création/destruction.

---

### Turing Patterns

Structures spontanées.

---

### Brusselator

Oscillations.

---

### Oregonator

Cycles.

---

# XXVII. Synchronisation avancée

---

### Master Stability Function

Quand un marché devient synchronisé.

---

### Explosive Synchronization

Liquidation.

---

### Adaptive Kuramoto

Synchronisation variable.

---

### Phase Oscillators

Ordres vus comme oscillateurs.

---

# XXVIII. Théorie des réseaux avancée

---

### Hypergraphs

Interaction de plusieurs murs.

---

### Multiplex Networks

Plusieurs couches :

spot

perp

options

---

### Temporal Networks

Réseaux évolutifs.

---

### Simplicial Networks

Interactions de haut ordre.

---

### Graph Curvature

Courbure du carnet.

---

### Ollivier-Ricci

Très récente.

---

### Forman Curvature

Rapide.

---

# XXIX. Géométrie de l'information

---

### Bregman Divergence

---

### Jensen-Shannon Geometry

---

### α-connections

---

### Dually Flat Geometry

---

### Amari Geometry

Très puissante.

---

# XXX. Théorie des probabilités moderne

---

### Stein Method

Comparer deux distributions.

---

### Coupling Theory

Comparer deux marchés.

---

### Exchangeable Processes

---

### Martingale Transport

---

### Skorokhod Embedding

---

### Malliavin Calculus

Très avancé.

---

### Rough Paths

Pour signaux très irréguliers.

---

### Signature Transform

Très utilisé aujourd'hui.

---

# XXXI. Théorie des files d'attente

Extrêmement adaptée.

---

### Jackson Networks

---

### BCMP Networks

---

### Queueing Fields

---

### Priority Queues

---

### Heavy Traffic Theory

---

### Fluid Limits

---

### Diffusion Limits

---

# XXXII. Théorie des extrêmes

---

### Peaks Over Threshold

---

### Pickands Process

---

### Hill Estimator

---

### Generalized Pareto

---

### Extremal Index

---

### Tail Dependence

---

# XXXIII. Théorie des systèmes auto-organisés

---

### SOC (Self Organized Criticality)

---

### Sandpile Models

---

### Forest Fire Model

---

### Earthquake Models

---

### Olami-Feder-Christensen

---

# XXXIV. Physique des polymères

---

### Self Avoiding Walk

---

### Worm Like Chain

---

### Polymer Collapse

---

### Percolating Polymers

---

# XXXV. Neurosciences théoriques

Oui.

---

### Hopfield Networks

Mémoire collective.

---

### Attractor Networks

---

### Neural Fields

---

### Wilson-Cowan

---

### Mean Field Brain Models

---

# XXXVI. Biologie évolutive

---

### Replicator Dynamics

Très intéressant.

---

### Evolutionary Stable Strategy

---

### Moran Process

---

### Wright-Fisher

---

### Adaptive Dynamics

---

# XXXVII. Théorie des jeux avancée

---

### Mean Field Games

---

### Differential Games

---

### Stochastic Games

---

### Anonymous Games

---

### Potential Games

---

### Congestion Games

---

# XXXVIII. Systèmes complexes modernes

---

### Adaptive Networks

---

### Coevolutionary Dynamics

---

### Edge Dynamics

---

### Network Controllability

---

### Reservoir Computing

---

### Echo State Networks

---

### Critical Reservoirs

---

# XXXIX. Mathématiques modernes

---

### Topological Data Analysis

(encore plus profond)

* Zigzag Persistence
* Mapper Graphs
* Reeb Graphs
* Morse-Smale Complexes
* Persistent Laplacian

---

### Optimal Transport avancé

* Sinkhorn
* Schrödinger Bridge
* Dynamic OT
* Unbalanced OT
* Wasserstein Gradient Flow

---

### Analyse harmonique

* Curvelets
* Shearlets
* Ridgelets
* Scattering Transform (Mallat)
* Synchrosqueezing
* Empirical Mode Decomposition (EMD)
* Hilbert-Huang Transform
* Variational Mode Decomposition (VMD)

---

# XL. Concepts très récents (2022–2025)

* Neural Operators (FNO)
* Koopman Neural Networks
* Neural Controlled Differential Equations
* Signature Kernels
* Graph Neural Operators
* Physics-Informed Graph Networks
* Neural Stochastic Differential Equations
* Stochastic Normalizing Flows
* Diffusion Transformers
* Continuous Normalizing Flows
* Neural Processes
* Set Transformers
* Equivariant Neural Networks
* Causal Diffusion Models
* Latent Force Models
* Sparse Identification of Nonlinear Dynamics (SINDy)
* Dynamic Causal Modeling
* Energy-Based Models
* Score Matching
* Neural Collapse Theory

---

## Les "armes secrètes" les plus originales

Si je devais sélectionner des concepts que l'on voit **presque jamais** appliqués aux carnets d'ordres mais qui pourraient être particulièrement féconds, je retiendrais :

1. **SINDy** (Sparse Identification of Nonlinear Dynamics)
2. **Signature Transform** (Rough Paths)
3. **Persistent Laplacian** (Topological Data Analysis)
4. **Schrödinger Bridges** (Optimal Transport)
5. **Graph Ricci Curvature** (géométrie des réseaux)
6. **Adaptive Kuramoto** (synchronisation des acteurs)
7. **KPZ Equation** (croissance des murs)
8. **Jamming Transition** (blocage de liquidité)
9. **Boltzmann Kinetic Equation** (distribution des ordres)
10. **Energy-Based Models** (modélisation énergétique des états du carnet)
11. **Replicator Dynamics** (compétition entre stratégies de traders)
12. **Scattering Transform de Mallat** (représentation stable des microstructures)
13. **Koopman Operator + DMD** (décomposition des modes dynamiques)
14. **Mean Field Games** (interactions entre une multitude d'agents)
15. **Rough Path Theory** (analyse de trajectoires extrêmement irrégulières)

Ces approches sont parmi les plus sophistiquées des systèmes dynamiques et de la physique mathématique contemporaine, et elles offrent souvent un cadre conceptuel plus riche que les méthodes statistiques classiques lorsqu'il s'agit de décrire des interactions complexes et des évolutions temporelles fines.

Pour un projet comme le tien (microstructure de marché, éconophysique, recherche scientifique, reproductibilité), je privilégierais moins des "plugins magiques" que des outils spécialisés. En pratique, voici ce qui apporte le plus de valeur.

### 1. Recherche scientifique (indispensable)

* **Semantic Scholar** — trouver rapidement les meilleurs articles et les travaux liés.
* **OpenAlex** — explorer les réseaux de citations.
* **arXiv** — pour les prépublications en physique, IA et mathématiques.
* **Crossref** — retrouver précisément DOI et références.

C'est probablement le type d'outil le plus rentable pour découvrir des concepts originaux.

---

### 2. Recherche de code

* **GitHub Search / GitHub Copilot**
* **Sourcegraph**

Très utile pour retrouver des implémentations de :

* Hawkes
* Koopman
* SINDy
* Optimal Transport
* Persistent Homology
* Scattering Transform
* etc.

---

### 3. Mathématiques

* **Wolfram Mathematica / Wolfram Alpha**
* **Maple**
* **SageMath**

Pour :

* dériver des équations,
* vérifier des démonstrations,
* manipuler des systèmes dynamiques.

---

### 4. Physique

Les ressources suivantes sont excellentes :

* INSPIRE-HEP (même hors physique des particules, beaucoup de concepts mathématiques)
* arXiv (cond-mat, stat, econ)
* HAL
* CERN Document Server

---

### 5. Analyse topologique

Si tu t'orientes vers la topologie des carnets :

* Ripser
* Gudhi
* Dionysus
* giotto-tda

---

### 6. Dynamique non linéaire

Pour Koopman, SINDy, DMD :

* PySINDy
* PyDMD
* PyKoopman

---

### 7. Optimal Transport

* POT (Python Optimal Transport)
* GeomLoss
* OTT-JAX

---

### 8. Graphes complexes

* PyTorch Geometric
* DGL
* NetworkX
* graph-tool

---

### 9. Éconophysique

Bibliothèques utiles :

* powerlaw
* statsmodels
* arch
* ruptures
* tick (Hawkes)
* pyunicorn

---

### 10. IA scientifique

Pour générer des hypothèses :

* Elicit
* Consensus
* ResearchRabbit
* Connected Papers
* Litmaps

Ces outils permettent souvent de découvrir des idées qu'une recherche classique ne fait pas ressortir.

---

## Si je devais n'en garder que 10

1. Semantic Scholar
2. ResearchRabbit
3. Connected Papers
4. Elicit
5. GitHub Copilot
6. Wolfram Mathematica
7. PySINDy
8. PyKoopman
9. POT (Optimal Transport)
10. Gudhi (Topological Data Analysis)

---

## Pour TON projet

Vu ton objectif (détecter des structures dans un carnet d'ordres Hyperliquid/Binance), je construirais une "boîte à outils" composée de :

* **Recherche** : Semantic Scholar + ResearchRabbit + arXiv.
* **Mathématiques** : Wolfram.
* **Implémentations** : GitHub Copilot + Sourcegraph.
* **Topologie** : Gudhi.
* **Dynamique** : PyKoopman + PySINDy.
* **Transport** : POT.
* **Graphes** : PyTorch Geometric.
* **Microstructure** : tick (Hawkes).

Cette combinaison couvre pratiquement toutes les approches modernes que tu explores (physique statistique, systèmes dynamiques, topologie, transport optimal, graphes et IA scientifique). Elle est beaucoup plus puissante qu'un simple assistant généraliste, car elle t'aide à la fois à **trouver des idées**, **les relier à la littérature**, **les implémenter** et **les tester** de manière reproductible.

---

# XXXIX. Ce que ce catalogue ne contient pas

> **Addendum du 05/08/2026.** Écrit après relecture intégrale du fichier. Il
> n'annule rien de ce qui précède : il ajoute six familles absentes, dont
> plusieurs sont **plus proches du problème** que la moitié des sections
> ci-dessus.
>
> Deux différences de forme, volontaires. **Aucune étoile** — le classement par
> intuition est ce que `01_Cahier_des_charges.md` interdit, et ce que
> `00_Prompt_MapDee.md` §10 reproche nommément à ce fichier. Et chaque famille
> porte sa **réponse É1** : traverse-t-elle vers Binance, ou ne sert-elle qu'à
> fabriquer la vérité. Une idée dont on sait déjà qu'elle ne s'affichera jamais
> n'est pas éliminée — elle est **étiquetée**, et on ne dépense pas dessus comme
> si elle allait au produit.
>
> Les cinq premières familles s'ajoutent au catalogue. **La sixième n'est pas un
> candidat** : c'est un défaut du protocole de sélection lui-même, et il se
> corrige dans `05_Protocole_de_selection.md`, pas ici.

---

## 1. Le transfert de domaine

**Le trou le plus grave.** Trois mille lignes sur la physique du carnet, et pas
une sur le fait qu'on **apprend sur une distribution et qu'on applique sur une
autre**. C'est pourtant le programme entier : la vérité se fabrique sur
Hyperliquid, le produit vit sur Binance.

Ce que la littérature apporte, et qui manque ici :

- **`covariate shift`** — la distribution des entrées change, la relation
  entrée→sortie ne change pas. Traité par repondération d'importance : on donne
  aux exemples HL le poids qu'ils auraient dans la population Binance. Suppose
  qu'on sache estimer le rapport des densités, ce qui n'est pas gratuit.
- **`label shift`** — l'inverse : la fréquence des comportements change (il n'y a
  pas la même proportion de leurres sur les deux places), la signature d'un
  comportement donné ne change pas. Correction par estimation des proportions.
- **`domain adaptation` adverse** — apprendre une représentation dont un
  discriminateur ne peut plus dire de quelle place elle vient. Séduisant et
  dangereux : ça détruit aussi ce qui est réellement spécifique à une venue.
- **`invariant risk minimization`** — ne retenir que les relations stables à
  travers les environnements. C'est exactement le critère de réplication d'É4,
  formulé comme objectif d'apprentissage au lieu d'un test a posteriori.
- **les théorèmes d'impossibilité.** La partie la plus utile. Ils disent à quelles
  conditions le transfert **ne peut pas** marcher — typiquement quand le support
  des deux distributions ne se recouvre pas. Le savoir avant de dépenser vaut
  mieux que de le découvrir en P7.

**Ce que ça donne concrètement, avant tout modèle** : une mesure de recouvrement
entre les deux venues sur les grandeurs qu'on prétend transférer. Elle se fait
sur la fenêtre simultanée, elle ne demande aucun apprentissage, et elle peut
tuer ou valider la démarche en quelques heures.

**É1 — sans objet, c'est le cadre.** Ce n'est pas une feature : c'est la
discipline qui conditionne l'usage de toutes les autres.

---

## 2. La censure et la troncature

Le catalogue mentionne « survival analysis » en une ligne, à propos du hazard
rate. Il ignore le problème qui rend l'analyse de survie nécessaire : **les
données sont censurées**, et la censure n'est pas aléatoire.

Le filtre du démon (`v > médiane`) **coupe par le bas**. La probabilité qu'un
palier soit censuré décroît avec sa masse — donc la censure est corrélée à la
variable étudiée. Un mur qui rétrécit disparaît de l'observation *avant* de
disparaître du carnet, et il disparaît d'autant plus tôt qu'il était petit. Toute
durée de vie mesurée sur ce flux est biaisée, dans un sens qui flatte les gros
murs.

Ce qu'il faut ajouter :

- **`Kaplan–Meier`** — estimateur de la fonction de survie sous censure à droite.
  C'est le point de départ, et il est bon marché.
- **`Cox`, hasards proportionnels** — l'effet d'une covariable sur le risque
  instantané, sans supposer de forme à la survie de base. La covariable qui
  compte ici est l'approche du prix.
- **estimateurs sous troncature à gauche** — pour les ordres déjà présents quand
  l'observation commence. C'est le problème de la chauffe, formulé proprement.
- **censure informative** — le cas où l'événement qui vous fait sortir de
  l'échantillon est lié à ce que vous étudiez. C'est exactement notre cas, et
  c'est celui où les estimateurs naïfs échouent le plus silencieusement.

**É1 — traverse.** La censure est un défaut de la chaîne d'affichage, donc elle
existe surtout **côté production**. Les correcteurs s'appliquent là où on en a
le plus besoin.

---

## 3. L'échantillonnage biaisé par la durée

Famille distincte de la précédente, et elle a un nom : **`length-biased
sampling`**. Si on échantillonne des objets en les observant à des instants
donnés, on capture les objets longs bien plus souvent que les courts — un objet
qui vit dix fois plus longtemps a dix fois plus de chances d'être vu. La
population observée n'est pas la population réelle.

C'est un classique de la fiabilité, de l'épidémiologie et de la théorie du
renouvellement, avec des correcteurs connus (repondération par l'inverse de la
durée, estimateurs de type Horvitz–Thompson, correction du paradoxe de
l'inspection).

**Pourquoi ça compte ici, précisément.** Une population sélectionnée sur la
survie, dont l'instant de contact est daté en retard, produit **mécaniquement**
des taux de disparition très élevés. C'est la piste la mieux étayée pour
expliquer le constat qui a tué le transfert — et le catalogue ne donne aucun
outil pour la traiter, alors que c'est le point non statué qui commande le reste
du dossier.

**Un corollaire à écrire avant de mesurer** : le biais s'inverse selon qu'on
échantillonne des *ordres à un instant* ou des *ordres sur une fenêtre*. Fixer
l'unité d'échantillonnage avant, pas après.

**É1 — traverse, et c'est un contrôle autant qu'une feature.** À traiter comme
un contrôle d'instrument (P1) avant d'en tirer quoi que ce soit.

---

## 4. La liquidité cachée et les icebergs

Le vocabulaire visuel du produit est **iceberg · spoof · absorption**. Le
catalogue traite abondamment du deuxième et du troisième, et **ignore le
premier**. C'est un tiers du livrable.

Ce qu'il y a à ajouter :

- **la signature du réapprovisionnement** — un palier qui, après avoir été
  exécuté, se recharge à un montant comparable, plusieurs fois de suite. C'est
  la trace observable d'un ordre à quantité affichée partielle, et elle se voit
  **sans identité** : c'est du niveau, pas de l'ordre.
- **l'estimation du volume caché** — combien un palier a réellement absorbé au-
  delà de ce qu'il affichait. C'est le pendant exact du taux d'absorption, et ça
  se relie directement au coût de traversée, donc au critère final du projet.
- **le délai de recharge** — le temps entre l'exécution et le réapprovisionnement.
  Il distingue un iceberg d'un simple repost opportuniste.
- **la distinction avec le spoof, qui est le point dur** : les deux produisent une
  masse qui varie fortement. Le leurre disparaît **sans avoir été exécuté**, la
  liquidité cachée disparaît **en ayant été exécutée et revient**. C'est encore
  la décomposition exécuté / retiré / ajouté qui les sépare — et elle se calcule
  sans le L4.

**É1 — traverse.** Le réapprovisionnement est un phénomène de palier, visible
dans les diffs de profondeur croisés aux exécutions. C'est probablement la
famille la plus rentable de cet addendum : elle complète le produit, elle
traverse, et elle n'est pas de la persistance déguisée.

---

## 5. La surveillance de marché et la définition réglementaire

Le catalogue est 100 % physique et 0 % régulation. Or ce qu'un régulateur
appelle **layering** ou **spoofing** a des définitions **opératoires**, écrites,
appliquées, et parfois éprouvées devant un tribunal — donc avec des observables
nommés et des seuils explicites. C'est très exactement la matière de C0, et
c'est plus proche du sujet que la courbure de Ricci.

Pistes à sourcer et à dater en C0, sans les traiter comme acquises ici :

- l'interdiction du spoofing dans le droit américain (Dodd–Frank, disposition sur
  les pratiques de négociation perturbatrices) et la jurisprudence qui en a
  précisé les éléments constitutifs ;
- le cadre européen sur les abus de marché et ses indicateurs de manipulation,
  qui listent des motifs de comportement plutôt que des formules ;
- les méthodologies de détection publiées par les plateformes de surveillance et
  par les bourses elles-mêmes.

**Ce qu'on en tire, et ce qu'on n'en tire pas.** On en tire des **définitions
candidates écrites avant d'avoir vu nos données** — c'est le seul ordre qui
protège de la cible dégénérée. On n'en tire **pas** une cible : le droit exige
une **intention**, que nous ne mesurons pas et que le projet a explicitement
renoncé à chercher (« jamais : ce mur est-il sincère »). La définition
réglementaire sert de point de départ mécanique, pas de vérité.

**É1 — variable selon la définition retenue.** Certaines exigent l'identité de
l'auteur, donc ne traversent pas ; d'autres sont purement comportementales au
niveau du palier. C'est précisément ce que C0 doit trancher, définition par
définition.

---

## 6. ⚠️ Ce qui n'est pas un candidat : la multiplicité des tests

**Ce point ne s'ajoute pas au catalogue. C'est un défaut de
`05_Protocole_de_selection.md`, et il se corrige là-bas.**

Le protocole exige, pour chaque candidat, un intervalle de confiance qui exclut
zéro. Il n'exige **aucune correction sur l'ensemble des candidats**. Or on va
juger plusieurs dizaines de grandeurs, sur cinq résolutions, sur deux ou trois
symboles. À seuil nominal de 5 %, un candidat sur vingt ressort « significatif »
en l'absence totale de phénomène — mécaniquement, sans aucune faute de calcul.

Autrement dit : le protocole est armé contre le fait de **se mentir sur un
candidat**, et désarmé contre le fait de **se mentir sur la collection**. C'est la
même faute que celle qui a produit quatre événements dégénérés en une nuit,
transposée à l'échelle du banc.

Ce qu'il faut y écrire :

- **contrôle du taux de fausses découvertes** — Benjamini–Hochberg comme plancher,
  parce qu'il est simple et qu'il tolère la dépendance positive entre candidats
  corrélés, ce qui est notre cas ;
- **le nombre de candidats jugés se déclare avant**, comme le nombre d'essais
  d'Optuna. Une famille testée « en plus, pour voir » après coup fausse la
  correction ;
- **É0 fait déjà une partie du travail** : fondre les doublons à |ρ| ≥ 0,90 réduit
  le nombre de tests réellement indépendants. C'est un argument de plus pour ne
  pas sauter cette épreuve.

---

## Récapitulatif, et ce que ça change au tri

| famille | ce qu'elle répond | traverse ? |
|---|---|---|
| transfert de domaine | est-ce que ce qu'on apprend a une chance de servir | c'est le cadre |
| censure / troncature | nos durées de vie sont-elles mesurables sur le flux public | oui, et c'est là que ça sert |
| échantillonnage biaisé par la durée | notre population est-elle celle qu'on croit | oui, comme contrôle d'abord |
| liquidité cachée / icebergs | le tiers manquant du vocabulaire visuel | oui |
| surveillance de marché | les définitions écrites avant nos données | selon la définition |
| multiplicité des tests | *(défaut du protocole, pas un candidat)* | — |

Trois de ces six familles ne sont pas des features : ce sont des **contrôles** et
un **cadre**. Cette distinction est celle que `00_Prompt_MapDee.md` §10 demande
de tenir, et que le reste de ce fichier traite comme interchangeable.

Et le tri É2 s'applique à cet addendum comme au reste : **aucune de ces familles
n'est dispensée de montrer son gain incrémental par-dessus le bloc de
persistance.** Une idée nouvelle qui redit la persistance dans une sixième langue
reste un doublon, même quand elle vient d'une littérature qui manquait.
