# MapDee — cahier des charges

Document de **cadrage** : ce que le projet cherche, sous quelles règles, dans
quel ordre. Il est tenu à jour — il se réécrit, il ne s'annote pas ; l'état
antérieur est dans git. Il ne porte **aucun chiffre de mesure** : les faits
d'instrument et de donnée — schémas, volumétrie, cadences, corruptions, effets
mesurés d'un paramètre — sont dans `FAITS.md`, et nulle part ailleurs. Le banc de
sélection d'une grandeur est dans `05_Protocole_de_selection.md`.

## 1. L'objectif

Formulation du 04/08/2026, seule qui fait foi :

> Une cartographie temps réel des comportements et des protagonistes grâce aux
> principes de l'éconophysique et de la thermodynamique. Trouver les mécanismes
> qui permettent au prix de bouger, pourquoi il bouge, où il va et pourquoi il y
> va.

**Cartographie** : le livrable est une carte, pas un score. Une valeur par
`(instant, palier)`, plus des marqueurs discrets, chaque colonne portant son
`t_ref` — l'instant où la valeur devient connaissable. Le produit est une
**table** ; l'image en est un rendu.

**Comportements et protagonistes** : le sujet est le **typage**. Un mur annulé et
un mur mangé disparaissent de façon identique en masse et opposée en mécanique.
Une couche qui dirait seulement « il y a de la masse ici » n'ajouterait rien —
c'est précisément ce que la masse ne dit pas. **La heatmap n'existe pas encore :
elle est à fabriquer**, et elle ne vaudra que par ce typage.

**Mécanismes** : la question est physique, jamais morale. Le spoofing est un
moyen de la cinétique du prix, pas une fraude. On ne demande jamais « ce mur
est-il sincère » ; on demande pourquoi le prix, coincé entre deux murs, choisit
l'un plutôt que l'autre.

De là vient la matière première. Le carnet est un système à N corps hors
équilibre : de la masse y entre, y séjourne, en sort ; le prix s'y déplace en
rencontrant des obstacles qui résistent, cèdent ou se reforment. Flux et
conservation, potentiel et énergie libre, entropie, files d'attente, processus
auto-excités, résilience, premier passage, criticité, absorption : les familles
de candidats. `03_EconoPhysique.md` en est le réservoir, **jamais un plan** ; nul
concept n'entre dans le pipeline sur son élégance.

## 2. Le terrain : deux places, deux rôles

**Hyperliquid est le laboratoire.** Seule place qui publie le cycle de vie
complet d'un ordre — identité des contreparties, durée de vie exacte sans
reconstruction. C'est donc la seule où l'on puisse **fabriquer une vérité** : ce
mur a-t-il été annulé, ou mangé, et par qui. Les labels s'y fabriquent, et
nulle part ailleurs.

**Binance est le marché et le produit** : le volume, l'exécution, l'affichage. Le
produit final y vit de bout en bout. **Conséquence structurante : le transfert
HL → Binance est le programme**, pas une phase optionnelle ni tardive. On
entraîne contre la vérité Hyperliquid pour appliquer sur les observables que
Binance publie ; sans cette traversée, rien ne s'affiche.

Le plafond, à écrire dans tout rapport qui touche au transfert ou à l'affichage :

> **Sans identité de portefeuille sur Binance, la vérité forte n'y est pas
> calculable.** Le transfert ne se valide jamais contre la vérité, seulement
> contre un **proxy**.

Il est structurel, pas un manque de données ni d'effort : Binance ne publie pas
l'identité des ordres et ne le fera pas. Il borne le produit lui-même, pas
seulement une phase de recherche.

Ce que la traversée impose : toute grandeur doit exister **des deux côtés**.
Celle qui a besoin de l'identité d'un ordre, de son `oid` ou de son cycle de vie
sert à fabriquer la vérité (P2) — elle ne traversera jamais. Le filtre s'applique
**dès P3**, pas à la découverte en P7.

## 3. La séquence, et la porte

```
P0 ingestion → P1 carnet → P2 labels → P3 features → P4 dataset
   ──►  LA PORTE : la table s'affiche en temps réel, sans lookahead,
        sur la grille de la production  ──►
P5 entraînement → P6 validation → P7 transfert → P8 simulation
```

**P7 est dans le chemin critique.** La table doit s'afficher au-dessus du carnet
Binance, pas au-dessus de celui qui l'a entraînée. Chaque phase est indépendante
et ne dépend d'aucun résultat futur ; aucune ne commence tant que la précédente
n'est pas validée.

Trois conséquences dures de la porte : une grandeur qui ne s'affiche pas ne
s'entraîne pas ; la couche doit être juste **toute seule**, sans modèle, sinon un
modèle posé dessus apprendra ses défauts ; le ML se branche sur la **table**,
contrat entre la recherche et le modèle, qui se fige avant tout entraînement.

## 4. La discipline

Avant chaque développement, dans cet ordre et par écrit : **problème → hypothèses
→ critère de réussite → critère d'échec → métriques → tests synthétiques →
seulement ensuite du code.**

Interdits, sans exception : modifier une cible, une métrique ou un seuil après
avoir vu un résultat ; interpréter un résultat sans intervalle de confiance ;
mélanger développement et validation ; construire une mesure avant d'avoir
regardé la distribution de ce qu'elle mesure.

**Les deux garde-fous de dégénérescence** — obligatoires avant toute cible, trois
lignes de code, aucune exception :

| garde-fou | règle |
|---|---|
| l'événement est-il rare ? | fréquence **< 60 %** |
| la cible a-t-elle deux classes ? | **≥ 5 %** en minoritaire **et ≥ 200 exemples** |

C'est le défaut qui revient : des « événements » construits avant que leur
distribution ne soit regardée, et saturés à une classe.

Toute décision importante devient un **ADR** — contexte, alternatives, décision,
justification, conséquences. Aucun seuil ne se modifie après observation. Si une
règle change, elle change par ADR et **tous les candidats déjà jugés repassent**.

## 5. Le critère final — mécanique

Le but n'est pas l'AUC. Il n'est pas non plus une grandeur économique : ni points
de base, ni P&L, ni gain simulé. **Le critère est mécanique.** Une grandeur est
retenue si, et seulement si :

| condition | mesure |
|---|---|
| **renormalisation** | même signe aux cinq échelles — 100 ms · 500 ms · 1 s · 5 s · 20 s. Ce qui disparaît quand on change la résolution n'est probablement pas un phénomène. |
| **incertitude honnête** | IC de **Student** excluant zéro, unité de rééchantillonnage **le JOUR**, jamais l'observation |
| **contrôle négatif** | elle sort de sa bande nulle, tirée par **décalage circulaire** — jamais par permutation i.i.d. (§6) |
| **réplication** | même signe sur **deux symboles** |
| **falsifiabilité** | elle produit une **conséquence falsifiable sur la trajectoire du prix** |

**La cible est le déplacement du prix**, pas la fraction exécutée. Raison : un
spoof réussi n'est jamais exécuté. Une cible d'exécution récompense donc le spoof
raté et pénalise celui qui a fonctionné — elle mesure l'inverse du phénomène
étudié. Un gain sans conséquence sur la trajectoire n'est pas un gain.

## 6. Validation

Bootstrap, contrôles synthétiques, stress tests, analyses de sensibilité,
intervalles de confiance — pour chaque résultat, sans exception.

**Le nul se tire par décalage circulaire, jamais par permutation i.i.d.** La
permutation détruit l'autocorrélation et déclare significatif ce qui ne l'est
pas ; sur un monde nul réel elle se trompe un ordre de grandeur plus souvent que
le décalage. Ce n'est pas la mesure qui est fausse, c'est le jugement porté sur
elle.

**Un contrôle dont on connaît le résultat n'est pas un contrôle.** Un garde-fou
doit pouvoir échouer, être appelé, et être vérifié capable d'échouer. Annoncé
mais jamais écrit, appelé deux fois avec le même tableau, ou valant une constante
par arithmétique : il ne protège rien.

**Une conclusion négative se formule avec sa puissance** : pas « rien n'est
détecté », mais « l'instrument est sous-dimensionné pour un effet de cette
taille ».

## 7. Les données avant le modèle

Les données sont plus importantes que le modèle. Avant toute IA, prouver que les
horodatages sont cohérents, les reconstructions exactes, les labels corrects, les
appariements corrects, les unités statistiques indépendantes.

Chaque jeu produit porte son **empreinte** (hash du contenu) et son **manifeste**
— commit git, paramètres, versions des dépendances, empreinte des entrées. Une
règle de nommage doit rendre deux constructions différentes impossibles à
confondre ; un résultat se reproduit **exactement** plusieurs mois plus tard.
Chaque module possède selftests, tests synthétiques, contrôles positifs **et**
négatifs, et produit automatiquement rapport markdown, figures, tables, journal
des paramètres, empreinte git, empreinte des données, versions des dépendances.

**Modèles** : les plus simples possibles. Baseline → régression → gradient
boosting → ranking → deep learning, en ne montant d'un cran que si le gain est
significatif au sens du §5.

## 8. Doctrine documentaire

| type de document | régime | pourquoi |
|---|---|---|
| **rapport de mesure** — il porte des chiffres datés | **errata + renvoi**, jamais de réécriture | le réécrire détruit la pièce à conviction. Effacer une faute est pire que l'avoir commise. |
| **document de cadrage** — il dit la règle en vigueur | **réécriture** | un cadrage doit être à jour, jamais archéologique. Reconstituer la règle actuelle en empilant des amendements, ce n'est plus un cadrage. |

Git garde l'historique des deux. Le régime ne dispense de rien : un cadrage
réécrit dit **quand** et **pourquoi** la règle a changé. Trois conséquences : un
rapport publié ne se corrige pas en place ; un document qui affirme avoir été
écrit avant un résultat doit être **commité** avant, sinon son antériorité ne
vaut rien ; le `confighash` doit couvrir le code qui **rend le verdict**, pas
seulement celui qui calcule.

## 9. La règle qui prime sur toutes les autres

> **Toute conclusion négative conduit d'abord à un audit de l'instrumentation
> avant d'être interprétée comme une absence de phénomène.**

Vérifier dans cet ordre : données, labels, appariements, fuites d'information,
unités statistiques, protocoles de validation. **Ensuite** seulement, conclure.
Un résultat négatif produit par un instrument non audité n'est pas un résultat :
plusieurs « négatifs » du travail antérieur venaient de l'instrumentation, pas du
marché — et aucune de ces fautes n'était visible dans la sortie.
