# Plan de la phase d'exploration

> Document de **cadrage**. Son régime n'est pas fixé ici : il est celui que
> posent `00_Prompt_MapDee.md` §9 et `01_Cahier_des_charges.md` §8 — cadrage
> réécrit, rapport de mesure gelé et corrigé par errata. Ce document ne s'octroie
> aucune licence propre ; c'est par les licences locales qu'une doctrine se perd.
>
> **Et la ligne entre les deux se trace ainsi** : un cadrage décrit une
> **intention**, et une intention change. Un rapport décrit une **mesure**, et
> une mesure ne change pas. **Tout document qui porte un chiffre issu de nos
> données est un rapport, quel que soit son nom** — y compris celui-ci, le jour
> où il en portera un.
>
> Depuis le 05/08/2026, le §8 porte **des chiffres issus de nos données** — le
> chronométrage du premier jour-symbole construit, chauffe active. Par la règle
> ci-dessus, ce paragraphe est donc un **rapport** : ses chiffres ne se
> réécrivent pas, ils se corrigent par ajout, avec leur source citée.

---

## 1. L'objet d'étude

**Ce n'est pas le spoofing. C'est la physique de la liquidité.**

Le spoofing en est un cas particulier — au même titre que le layering,
l'absorption, le rechargement, la résilience, ou la liquidité simplement
sincère. Formuler l'objet par le spoofing enfermerait le projet dans une seule
définition, et une définition d'**intention**, qui ne s'observe pas.

L'objet, énoncé pour être mesurable :

> **Les mécanismes dynamiques du carnet qui permettent d'inférer le DEVENIR
> d'une liquidité posée.**

La différence n'est pas rhétorique, elle débloque :

| | statut |
|---|---|
| « ce mur est-il un leurre ? » | une **intention**. Ne s'observe pas. Toute définition en est une convention discutable — c'est ce qui a produit quatre cibles dégénérées. |
| « que devient cette masse ? » | un **fait**. Elle est annulée, exécutée, rechargée, ou elle tient. **Se mesure sans rien inférer.** |

On mesure le devenir, on cherche ce qui le précède, et l'intention reste hors
du périmètre — on ne la nomme pas, on ne la revendique pas.

### Le rappel qui commande tout le reste

On apprend sur Hyperliquid, où la vérité est observable. On **applique sur
Binance**, où elle ne l'est pas : c'est là que se fait le volume, c'est là qu'on
exécute, et c'est de là que sort le flux de l'affichage.

**Un mécanisme qui ne traverse pas n'est pas un demi-résultat : il ne sert ni à
afficher ni à trader.** Il va au journal. D'où un livrable qui n'était pas dans
la liste et qui devrait y être en permanence :

> **un verdict de traversée par mécanisme** — existe-t-il côté Binance, oui,
> non, ou sous condition d'une approximation à démontrer.

C'est l'objet de C8, et c'est pour ça qu'il démarre en semaine 1.

---

## 2. Les hypothèses

Elles sont **emboîtées** : chacune suppose la précédente. C'est ce qui rend
l'échec informatif — une hypothèse qui tombe dit exactement ce qui reste
possible, et il n'y a pas de sauvetage post-hoc à inventer.

### H0 — le devenir est mesurable sans ambiguïté

> À chaque instant, la variation de masse à un palier se décompose en
> **exécuté / retiré / ajouté**, et cette décomposition est **stable et
> reproductible**.

**Pourquoi ce n'est pas acquis** : c'est calculable depuis le carnet et les
transactions seuls, mais le flux d'affichage **censure** — le filtre par la
médiane retire des paliers, et la probabilité d'être retiré décroît avec la
masse (`FAITS.md` §11 bis). Une décomposition faite sur un flux censuré porte le
signal de taille dans son erreur.

**Si H0 tombe** : il n'y a rien à typer, et le projet n'a pas d'objet mesurable.
On répare l'acquisition ou on s'arrête.

### H1 — le devenir laisse une trace avant

> Une liquidité destinée à être **retirée** présente une dynamique différente
> d'une liquidité destinée à être **exécutée**, et cette différence est visible
> **avant** que le devenir ne se réalise.

C'est le cœur. Tout le reste en dépend.

**Si H1 tombe** : il n'y a pas de mécanisme prédictif dans la dynamique du
carnet. Le projet devient descriptif — une carte de ce qui s'est passé, sans
anticipation. Ce serait un résultat, pas un échec, mais ce ne serait pas le
produit visé.

### H2 — la trace survit sans identité

> Cette différence reste visible **sans le L4** — sans identifiant d'ordre, sans
> identité de porteur, sans cycle de vie complet.

C'est la première projection : du laboratoire vers l'écran.

**Si H2 tombe** : la vérité se fabrique mais ne s'affiche pas. Valeur de
recherche, aucun produit. La question devient « existe-t-il un observable de
substitution », et c'est un autre programme.

### H3 — la trace survit au changement de marché

> Cette différence est **stable entre deux places** — apprise sur Hyperliquid,
> valide sur Binance.

C'est la seconde projection, et elle porte le plafond structurel : sans identité
sur Binance, elle ne se valide jamais contre la vérité, seulement contre un
proxy.

**Si H3 tombe** : produit sur Hyperliquid seul. L'objectif de recherche survit
entier ; le périmètre commercial se réduit.

### Ce que chaque hypothèse coûte à tester

| | testable dès | coût | tombe si |
|---|---|---|---|
| **H0** | le mois construit | faible | la décomposition n'est pas reproductible, ou son erreur corrèle à la masse |
| **H1** | banc synthétique, **avant toute donnée de marché** | faible d'abord, élevé ensuite | aucune méthode ne dépasse son plancher de détection |
| **H2** | après H1 | moyen | la trace disparaît quand on retire les colonnes L4 |
| **H3** | après H2, exige les deux places | élevé | la relation change de signe d'une place à l'autre |

**H1 se pré-teste sur le banc synthétique.** On y injecte une dynamique connue et
on mesure si une méthode la retrouve. Ça ne dit pas si le phénomène existe dans
le marché — ça dit si on **saurait le voir**. C'est très en amont, et c'est
gratuit.

---

## 3. La carte des inconnues

Quatre niveaux. Et un avertissement qui vient de la session du 04/08 :
**la colonne « certain » ne contient que ce qui a été vérifié par nous, sur
notre instrument.** Des affirmations tenues pour certaines pendant des semaines
se sont révélées fausses le même soir — dont le rôle prêté à la chauffe.

| niveau | ce que ça veut dire |
|---|---|
| **certain** | vérifié par nous, reproductible en minutes |
| **probable** | mesuré ailleurs, mécanisme plausible, non re-vérifié chez nous |
| **possible** | argument théorique, aucune mesure |
| **inconnu** | ni mesuré ni argumenté |

| | niveau |
|---|---|
| le format de la source, sa couverture, ses volumétries | **certain** |
| la granularité en blocs de la place | **certain** |
| la cadence de notre reconstruction | **certain** |
| l'empreinte et la garde contre le mélange de générations | **certain** |
| la décomposition exécuté / retiré / ajouté est calculable sans L4 | **probable** — le code existe, jamais validé sur nos données |
| le filtre par la médiane censure de façon corrélée à la masse | **probable** — mécanisme établi par lecture du code, ampleur non mesurée |
| **la présence d'un signal dans la dynamique** | **inconnu** |
| **le transfert vers Binance** | **inconnu** |
| **la généralisation à d'autres symboles, d'autres régimes** | **inconnu** |
| l'existence d'un quatrième comportement non nommé | **inconnu** |
| le plancher de détection de toute méthode | **inconnu** — et c'est ce qui rend tout négatif ininterprétable aujourd'hui |

Rien de ce qui touche au **marché** n'est au-dessus de « inconnu ». C'est normal
à ce stade, et ça doit rester écrit.

---

## 4. La hiérarchie des risques

Elle a une conséquence directe sur l'ordre du travail : **on teste le risque le
plus fort en premier, et parmi les risques égaux, le moins cher d'abord.**

| risque | gravité | ce qu'il coûte s'il se réalise tard | atténuation |
|---|---|---|---|
| **aucun phénomène observable (H1)** | **très fort** | le projet entier | le pré-tester sur le banc synthétique, avant toute donnée de marché |
| **la trace ne survit pas sans L4 (H2)** | **fort** | tout ce qui a été construit hors ligne | **C8**, en semaine 1 : appliquer le filtre d'admissibilité **dès la conception d'une grandeur**, jamais à la fin |
| **le transfert vers Binance (H3)** | **fort** | le produit, pas la recherche | **C8**, en semaine 1 : établir sur papier ce qui existe des deux côtés. Et l'écrire comme plafond dès maintenant ; ne jamais promettre une validation contre la vérité |
| **la mesure est censurée à la source (H0)** | **fort** | toutes les mesures de présence | les deux mesures de `FAITS.md` §11 bis, tôt |
| **les définitions sont mauvaises** | **moyen** | on rejuge les candidats déjà passés | définir le **devenir** (observable) plutôt que l'intention ; geler par ADR |
| **le bootstrap est invalide** | **moyen** | tous les intervalles publiés | mesurer la fraction de paires intra-unité avant É4 |
| **performances machine, place disque** | **faible** | du temps | mesuré, et le volume disponible dépasse le besoin d'un ordre de grandeur |

**Ce que ce tableau change dans le plan** : H1 était testé tard, après la
construction du mois et l'écriture des définitions. Il remonte — sa forme
pré-testable (le banc synthétique) ne dépend d'aucun des verrous.

**Et H2/H3 n'avaient aucun chantier.** Deux risques classés « fort », portés par
une seule ligne d'intention. C'est **C8** qui les porte désormais, et il tourne
en semaine 1 : sans lui, on peut finir la phase avec des mécanismes établis,
avec intervalle de confiance, répliqués sur deux symboles, et **tous
inutilisables** parce qu'ils n'existent pas côté Binance.

### Correction du 05/08 — C8 ne porte pas H2

Une version antérieure inscrivait C8 en atténuation de H2. **C'est faux** : C8
est du papier — il répond « cette grandeur est-elle *calculable* sans le L4 »,
pas « la *trace survit*-elle », qui est empirique et testable **après H1**
seulement. C8 atténue l'admissibilité et le volet papier de H3. **H2 n'a pas de
chantier dédié**, et il ne faut pas croire ce risque traité : son test est celui
du §2 — retirer les colonnes L4 et mesurer ce qui reste de la trace.

---

## 5. Les verrous

| verrou | ce qu'il bloque | ce qui l'ouvre |
|---|---|---|
| **V1 — pas de rejeu événementiel** | la renormalisation, donc tout candidat s'arrête à É2 | émettre à chaque changement du carnet, sur **quelques jours**, pas le mois |
| **V2 — la cible n'a pas de définition opératoire** | É4 en entier | littérature, puis écriture, puis gel |
| **V3 — le devenir n'a pas de définition opératoire** | le typage | **allégé par le §1** : on définit un fait observable, plus une intention |
| **V4 — validité du bootstrap inconnue** | tout intervalle de confiance | mesurer la fraction de paires intra-unité |
| **V5 — aucun observable de substitution démontré côté Binance** | **É1, donc l'admissibilité de toute famille de traits** — et in fine le produit | inventorier ce que Binance publie, et mesurer la traversée sur la fenêtre simultanée |

**V1 est moins cher qu'il n'en a l'air** : la renormalisation est une épreuve de
candidat, pas une table de production. Quelques jours à la cadence la plus fine
suffisent.

**V5 est le moins cher des cinq, et le plus tard découvert si on l'ignore.** Sa
première moitié est du papier — É1 se répond en trois questions, sans calcul. Sa
seconde moitié est une mesure courte, sur une fenêtre qui existe déjà.

---

## 6. Les chantiers — entrée, sortie, et forme de l'échec

**Chaque chantier produit un objet concret, et son échec est lui aussi un objet
publiable.** Un chantier qui ne produit rien n'a pas eu lieu.

### C0 — Littérature

* **entrée** : rien. Aucune donnée touchée.
* **sortie** : une note par comportement — définitions concurrentes, observables
  exigés, laquelle survit sans le L4.
* **échec** : « aucune définition de la littérature n'est calculable sur nos
  observables » → on définit nous-mêmes, et on le déclare comme tel.

### C1 — Instrument

* **entrée** : l'archive brute.
* **sortie** : le mois construit, deux symboles, **manifeste par artefact** ; et
  le rejeu événementiel sur quelques jours.
* **échec** : un contrôle croisé qui ne ferme pas → **on ne construit pas la
  suite**. Rapport de non-conformité, et on répare.

**La règle de la réserve est ASYMÉTRIQUE, et il faut la dire ainsi.** Une
formulation antérieure disait que la taille de la réserve serait « fixée par
l'écart-type ». C'est impossible dans cet ordre : l'ADR gèle des jours **avant**
que la mesure n'existe, et un jour déjà regardé ne peut plus y rentrer.

> L'`ADR-000` fixe la réserve, et elle ne bouge plus. **C6.1 ne la dimensionne
> pas — il dit si elle SUFFIT.** Si elle ne suffit pas, on ne peut qu'y **ajouter
> des jours jamais regardés**. Jamais en reprendre.

**Le premier lot s'arrête donc avant les jours de fin de mois** — ils sont la
seule réserve de jours jamais regardés, donc l'unique issue que la règle
asymétrique laisse ouverte. La construction s'ordonne :

1. construire la **première tranche**, hors jours de fin de mois ;
2. mesurer l'écart-type dessus (**C6**) ;
3. construire la **seconde tranche** seulement ensuite, une fois l'extension
   éventuelle actée.

Les jours de fin de mois ne sont **ni construits ni regardés** avant que
l'écart-type ne soit connu. Sans cette précaution, l'extension prévue par l'ADR
devient impossible et la réserve reste à sa taille initiale **par défaut, pas
par décision** — ce qui n'est pas la même chose, et ne se rattrape pas.

**Le troisième symbole, et ce qu'il apporte réellement.** Il n'apporte **aucune
puissance statistique**. L'unité de rééchantillonnage est le **JOUR**, et
l'écart-type qui gouverne la puissance est **inter-journalier** (C6) : ajouter un
symbole n'ajoute pas de jours. Ce qu'il apporte, et rien d'autre : un
**troisième témoin de signe** pour la réplication d'É4, qui n'en exige que deux.
La décision de le construire se prend sur cette base — un témoin de plus contre
~15 h de machine — **jamais sur une promesse de certification**.

### C2 — Regarder avant de mesurer *(jour de banc d'instrument seul)*

* **entrée** : le carnet reconstruit.
* **sortie** : un **atlas de trajectoires** — des courbes de masse à un palier,
  regardées une par une, pas un agrégat. Plus les distributions de toutes les
  grandeurs candidates, **avant** qu'aucune ne devienne une condition.
* **échec, et il faut le nommer d'avance** : « **aucune structure** » — les
  trajectoires ne montrent aucun régime distinguable à l'œil. C'est un résultat
  publiable, et il attaque H1 directement.

### C3 — Écrire et geler

* **entrée** : C0 et C2.
* **sortie** : la cible et le devenir en **définitions opératoires**, par ADR,
  **commité avant le premier calcul qui s'en sert**.
* **échec** : les définitions candidates échouent au garde-fou de dégénérescence
  → on redéfinit la condition, **jamais le modèle**, et on recommence.

### C4 — Banc synthétique

* **entrée** : les définitions gelées.
* **sortie** : par méthode — le rappel à faux positifs fixés, le **plancher de
  détection**, et le comportement dans le **bras nul**.
* **échec** : une méthode qui détecte dans le bras nul est **disqualifiée**, sans
  appel.

### C9 — Le harnais : automatiser le banc

**C'est le chantier primordial.** Le registre de `03` porte des dizaines de
grandeurs, et il faut **toutes** les explorer — à cinq résolutions, sur deux
symboles. À la main, c'est infaisable ; sans elles, rien n'arrive dans la carte.

**Ce qui rend l'automatisation possible** : aucune des cinq épreuves ne demande
un jugement. Chacune est un calcul à seuil fixe, et les seuils sont gravés
d'avance. C'est exactement pour ça qu'ils l'ont été.

| étage | ce qui est mécanique |
|---|---|
| **É0** | corrélation de rang entre candidats, deux à deux → doublons fondus |
| **É1** | déjà répondu dans la fiche → une lecture |
| **É2** | corrélation de rang contre les candidats retenus |
| **É3** | la même grandeur aux cinq résolutions → comparaison des signes et des rangs |
| **É4** | gain incrémental, IC de Student sur les jours, nul par décalage circulaire, réplication |

**Les quatre pièces à construire, dans cet ordre** :

1. **Le générateur synthétique.** Un carnet fabriqué qui émet **exactement le
   schéma de `deep`** — sinon une méthode validée sur synthétique ne tournerait
   pas telle quelle sur décembre, et le banc ne testerait rien. Il émet
   **l'observable et la vérité séparément** : la méthode ne voit que
   l'observable, le banc compare à la vérité. Déterministe à graine fixée, sans
   quoi le bras nul n'est pas comparable au bras injecté.
   Sa grille doit être **identique à celle de la production** — vérifié par un
   test qui compare bit à bit, jamais par un import de l'archive.
2. **Le registre des grandeurs.** La machine à états de la boucle : une ligne
   par candidat, son état, et **le chiffre qui l'a fait tomber**. En ajout seul,
   jamais en effacement. Il porte aussi le **nombre de candidats déclaré avant
   le premier calcul** — c'est la première protection contre la multiplicité.
   Sans ce fichier, « quoi ensuite » redevient un jugement, et une session
   retestera ce qu'une autre a déjà éliminé.
3. **Les cinq épreuves**, chacune avec son seuil et son refus. Une épreuve
   échouée arrête le candidat et écrit sa ligne.
4. **Le préflight.** Il refuse de démarrer si l'arbre git est sale, si le
   protocole n'est pas commité, si le périmètre touche un jour gelé, si un
   dossier porte deux générations, ou si un fichier obligatoire manque. **Il ne
   prévient pas, il bloque** — une règle en prose n'a jamais arrêté personne.

   **Correction du 05/08 (audit, I.5)** : le préflight passe **EN TÊTE des
   quatre pièces**, pas en quatrième — la seule construction jamais lancée l'a
   été avec `sale=True`, **consigné et non bloqué** : démonstration
   expérimentale de la règle qu'il incarne. Et son contrôle d'arbre propre doit
   **exclure les chemins de sortie déclarés** (le journal de construction
   s'écrit en continu), sinon il s'interbloque pendant toute construction
   longue.

**Ce qui ne dépend pas des données** : les quatre pièces se construisent et se
testent **sur carnet fabriqué**, où la vérité est connue. Elles peuvent donc
être écrites pendant que la construction tourne.

**Ce qui dépend des définitions** : É3 et É4 ne peuvent pas s'exécuter avant que
la cible n'ait sa définition opératoire (C3). Le harnais s'écrit avant, il ne
tourne qu'après.

* **entrée** : les fiches de `03`, et rien d'autre pour construire.
* **sortie** : une boucle qui prend une fiche, la passe par les cinq épreuves,
  écrit son verdict et son chiffre au registre, et enchaîne — jusqu'à ce qu'un
  critère d'arrêt la termine.
* **échec** : si une épreuve ne peut pas être rendue mécanique sans arbitrage,
  c'est le protocole qu'il faut corriger, pas le harnais qu'il faut assouplir.

### C5 — Protagonistes *(parallèle, ne dépend d'aucun verrou)*

* **entrée** : les transactions avec identité — déjà captées, jamais lues.
* **sortie** : qui pose, qui retire, qui agresse ; la persistance d'une identité
  d'un jour à l'autre.
* **échec attendu et à écrire d'avance** : **annuler beaucoup n'est pas un
  signe** — c'est le métier d'un teneur de marché. Un discriminant qui désigne
  les teneurs ne désigne rien.
* ⚠️ ce chantier **ne traverse pas** vers Binance. Il sert à comprendre et à
  fabriquer la vérité, pas à afficher.

### C6 — Les deux mesures d'incertitude

* **entrée** : le mois construit, hors réserve.
* **sortie** : l'écart-type inter-journalier sur l'unité jour, et la fraction de
  paires intra-unité.
* **échec** : si la fraction intra-unité est élevée, **le bootstrap est
  inutilisable en l'état** et É4 change d'outil avant de tourner.

### C7 — Admissibilité de la présence

* **entrée** : le mois construit.
* **sortie** : les deux mesures de `FAITS.md` §11 bis — distribution de l'erreur
  d'âge par masse, et décomposition des sorties de registre.
* **échec** : l'erreur varie de façon monotone avec la masse → la persistance
  dégradée n'est pas admissible, **et le pipeline d'acquisition doit changer**.

### C8 — Admissibilité à la traversée *(parallèle, ne dépend d'aucun verrou)*

C7 ne couvre qu'un cas particulier de l'admissibilité — la famille présence.
C8 porte **É1 en entier**, pour **toute** grandeur candidate : sans L4, traverse
vers Binance, tourne dans un navigateur, survit à la dégradation du flux.

* **entrée** : le catalogue des grandeurs candidates, et la documentation des
  observables publiés par chaque place. **Aucune donnée de marché touchée** —
  c'est du papier pour l'essentiel.
* **sortie** : la liste des grandeurs candidates, classées en **trois cases** :

  | case | ce que ça veut dire | suite |
  |---|---|---|
  | **traverse** | calculable sur les observables que Binance publie | admise au banc d'affichage |
  | **ne traverse pas** | exige le L4 ou l'identité — donc Hyperliquid seul | **réorientée** vers la fabrique de vérité, pas éliminée du programme |
  | **traverse sous condition** | traverse au prix d'une **approximation**, qui reste **à démontrer** | la démonstration est due **avant É4**, jamais après |

  Plus, en amont de ce classement, l'inventaire qui le fonde : **ce qui existe
  des deux côtés**, colonne par colonne.
* **échec** : « **aucune grandeur porteuse ne traverse** ». C'est H2 ou H3 qui
  tombe — H2 si l'obstacle est le L4, H3 s'il est la place. Ce n'est pas un
  échec de chantier : c'est le résultat que le chantier existe pour produire, et
  il vaut mieux l'apprendre en **semaine 1** qu'en P7.

⚠️ **C8 tourne TÔT et en parallèle**, comme C5. Il ne dépend d'aucun verrou,
d'aucune construction, d'aucune définition gelée. Une grandeur classée « ne
traverse pas » ne doit pas avoir coûté trois semaines de calcul avant de
l'apprendre. **La case « traverse sous condition » ne se vide pas d'elle-même** :
une approximation non démontrée compte comme « ne traverse pas ».

---

## 7. Les critères d'arrêt

Écrits **avant** de commencer, et non négociables après. Un critère d'arrêt
posé après avoir vu les résultats n'est pas un critère, c'est une justification.

| on arrête si | conséquence |
|---|---|
| **C2 ne montre aucune structure** sur les trajectoires brutes | H1 est attaquée à la racine. On ne construit pas de banc pour chercher ce qu'on ne voit pas. |
| **aucune méthode ne descend son plancher de détection sous l'amplitude plausible du phénomène** | on ne consomme **aucun jour de marché**. On n'a pas d'instrument, indépendamment de l'existence du phénomène. |
| **après le catalogue passé au banc, aucun candidat ne franchit É4** | on publie le catalogue avec les chiffres qui l'ont fait tomber, et on arrête. |
| **H0 tombe et l'acquisition ne peut pas être réparée** | il n'y a pas d'objet mesurable. |

**Le critère qui compte le plus est le deuxième**, et il est le moins intuitif :
il se prononce **avant** toute donnée de marché, sur le banc synthétique seul.
Il distingue « le phénomène n'existe pas » de « on ne saurait pas le voir » —
distinction que l'itération précédente n'a jamais pu faire, et qui lui a fait
fermer des pistes à tort.

**Ce qui ne compte PAS comme critère d'arrêt** : le nombre de jours passés, le
nombre de méthodes essayées, la fatigue. Un compte n'est pas un critère.

---

## 8. Dimensionnement

**Corrigé le 05/08/2026 sur le premier jour-symbole terminé, chauffe active**
(`20251201` BTC, phase `deep`, log `journal/construction/20260805-010706-decembre.log`).
L'extrapolation d'origine — ~30 h le mois — venait d'une mesure chauffe
désactivée et était **fausse d'environ un facteur deux**.

| poste | mesuré (jour 1, chauffe active) |
|---|---|
| extraction de l'archive | 82 s |
| scan des statuts (`hl_orders`, 116 M lignes) | 622 s |
| reconstruction + écriture `deep` (400 M lignes, 90 162 photos, 1,17 Go) | 3 595 s |
| **total jour-symbole** | **~72 min** |

Soit, en extrapolant **ce seul point** : tranche 1 (32 jours-symboles) ~38 h ;
le mois complet, deux symboles, **~55-60 h** — cohérent avec la mesure du
troisième bras (~53 min/jour-symbole, chauffe désactivée).

**Ce que ce point ne mesure pas encore**, et qui maintient la consigne
ci-dessous : le jour 1 tournait en phase `deep` avec les tables de statuts
**déjà écrites** — le poste « écriture des tables » et le poste `hl_book`
n'y figurent pas (ils n'apparaîtront qu'aux jours 08-16, phase `all`) ; et la
chauffe (les 8 premières heures du jour) n'est pas **isolée** dans le poste
reconstruction — le log ne la chronomètre pas séparément.

| poste (inchangé, non remesuré) | ordre de grandeur |
|---|---|
| ajouter un troisième symbole | +~50 % du mois |
| rejeu événementiel, quelques jours | quelques heures |
| place disque | ~1,2 Go de `deep` par jour-symbole en nappe large ; le volume disponible est deux ordres de grandeur au-dessus (325 Gio libres mesurés) |
| C0, C4 | jours-homme, machine négligeable |
| C8 | jours-homme ; C8.2 a coûté quelques minutes de machine |

**« Le coût dominant est le scan des statuts d'ordres » n'est pas établi dans le
régime de production.** L'affirmation vient d'un autre instrument, et la mesure
d'origine a été faite **chauffe désactivée** — elle ne mesure donc pas le régime
dans lequel le mois se construit. Tant qu'elle n'est pas refaite, elle vaut comme
hypothèse de travail, pas comme fait, et la répartition des postes ci-dessus peut
être fausse dans ses proportions autant que dans ses totaux.

> **Consigne, non négociable** : le premier lot est chronométré **chauffe
> active**, **poste par poste** — chauffe, scan des statuts, reconstruction du
> carnet, écriture. Un chronométrage global ne suffit pas : il ne dit pas quel
> poste domine. Sans cette mesure, on ré-extrapole le même biais et on
> redimensionne la phase sur un régime qui n'existe pas.

---

## 9. L'ordre

```
C0 littérature ──────────────────────────────┐
                                             ▼
C1 instrument ──► C2 regarder ──► C3 écrire et geler ──► C4 banc synthétique ──┐
   │  tranche 1 → C6 → tranche 2                                              ▼
   ├──► C6 incertitude ─────────────────────────────────────────────► BANC RÉEL
   ├──► C7 présence                                                    É0 → É4
   ├──► C5 protagonistes   (parallèle, ne dépend de rien)
   ├──► C8 traversée       (parallèle, papier, semaine 1)
   └──► C9 harnais         (parallèle — s'écrit sur synthétique,
                            ne tourne qu'après C3)
```

Cinq règles qui ne se contournent pas :

* **C0 avant C2.** Lire avant de regarder — une définition posée après avoir vu
  la distribution est un résultat déguisé.
* **C3 gelé et commité avant tout calcul de banc.**
* **C6 avant É4.** Un intervalle dont on ignore la validité ne conclut rien.
* **La première tranche de C1, puis C6, puis la seconde tranche.** Les jours de
  fin de mois — ceux sur lesquels l'`ADR-000` prévoit d'étendre la réserve — ne
  sont **ni construits ni regardés** avant que l'écart-type ne soit connu. Un
  jour regardé ne peut plus entrer dans la réserve : construire tout d'un coup
  fige la réserve à sa taille initiale **par défaut, pas par décision**.
* **C9 s'écrit pendant la construction.** Le harnais ne dépend d'aucune
  donnée pour être écrit — seulement pour tourner. L'écrire plus tard, c'est
  attendre les définitions les bras croisés, puis attendre le harnais.
* **C8 avant qu'une grandeur ne coûte cher.** Une grandeur qui ne traverse pas
  n'a pas à franchir É2, É3 ou É4 avant qu'on l'apprenne.

**C5 démarre tôt** : aucun verrou, le moins cher, et il porte la moitié de
l'objectif — les protagonistes.

**C8 démarre aussi tôt, et pour la raison inverse** : il ne porte rien de
l'objectif, il porte le **plafond**. C'est le seul chantier dont l'échec annule
le produit sans rien retirer à la recherche, et le seul qui se conclut en
jours-homme sans machine. Le faire en semaine 1 coûte des jours ; le faire en
fin de phase coûte la phase.

---

## 10. Ce qu'on ne fait pas

* aucun entraînement de modèle — la table se fige d'abord ;
* aucune mesure sur la réserve, ni construction, ni lecture ;
* aucun jour d'exploration ouvert avant que C3 ne soit gelé et commité ;
* aucun candidat testé sans sa fiche ;
* **aucune conclusion négative sans son plancher de détection** ;
* **aucun mécanisme retenu sans son verdict de traversée.** Un mécanisme qui ne
  vit que côté L4 est un résultat de laboratoire, pas un livrable : il est
  étiqueté comme tel et il va au journal.

---

## 11. Ce qui vous revient

| décision | pourquoi elle ne se prend pas seul |
|---|---|
| **le sort de l'enregistreur de production** | il se dégrade, et **chaque jour de panne est un jour de fenêtre de traversée perdu définitivement** (C8) — la fenêtre où les deux places sont observées ensemble ne se rattrape pas |
| **le troisième symbole** | choix de symboles, et ~15 h de machine — contre **un témoin de signe de plus**, et aucune puissance (§6, C1) |
| **la cible et le devenir**, une fois rédigés | ce sont les définitions du produit |
| **les seuils des critères d'arrêt §7** | ils engagent à abandonner |

**La largeur de la nappe est tranchée** — nappe **large**, décision du
04/08/2026, gravée dans `construire_decembre.ps1` avec sa raison à côté du
réglage. Elle ne bloque plus la construction. Contrepartie assumée : environ le
double de temps de rejeu, contre l'impossibilité d'élargir après coup.

**L'ordre de démarrage n'est plus un arbitrage non plus** : C0, C5 et C8 ne
dépendent d'aucun verrou et partent immédiatement. C5 est lancé — son protocole
est pré-enregistré dans `chantiers/C5-protagonistes.md`.

Tout le reste s'exécute sans arbitrage.
