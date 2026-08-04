# MapDee — le programme

Dépôt : `C:\Users\DyBoo\Desktop\-MapDee-` · `github.com/Dee-La-Forge/MapDee`

Ce document dit **ce qu'on cherche et sous quelles règles**. Il ne porte aucun
chiffre : les chiffres vivent dans `FAITS.md`, et aucun n'est un acquis.

---

## 0. L'objectif

> **Une cartographie temps réel des comportements et des protagonistes, par
> l'éconophysique et la thermodynamique. Trouver les mécanismes qui font bouger
> le prix : pourquoi il bouge, où il va, et pourquoi il y va.**

Formulation de Meddy, 04/08/2026. C'est la seule qui fait foi. Toute autre
formulation trouvée dans le dépôt est périmée.

Le carnet est traité comme un **système à N corps hors équilibre** : de la masse
y entre, y séjourne, en sort ; le prix s'y déplace en rencontrant des obstacles
qui résistent, cèdent ou se reforment. On cherche la **mécanique** de ce
déplacement, et **qui** l'opère.

Deux moitiés, également importantes :

* **les comportements** — ce qu'un gros ordre posé au carnet *fait* dans le
  temps : il est annulé, il est mangé, il se recharge. Trois disparitions
  identiques en masse et opposées en mécanique.
* **les protagonistes** — **qui** pose, qui retire, qui agresse. Hyperliquid
  publie l'identité des deux contreparties de chaque transaction ; aucune autre
  place ne le fait.

La question sous sa forme la plus concrète, dans les mots de Meddy :

> **quand le prix se retrouve coincé entre deux murs, pourquoi choisit-il l'un
> plutôt que l'autre.**

## 1. Ce que ce n'est pas

Trois confusions à écarter d'emblée, parce que chacune a déjà coûté du temps.

| ce n'est pas | pourquoi |
|---|---|
| **de la détection de fraude** | on ne demande jamais « ce mur est-il sincère ». Le spoofing est traité comme un **moyen de la cinétique du prix**, pas comme un délit à dénoncer. |
| **de la prédiction de prix** | on ne cherche pas un signal d'alpha. On cherche des mécanismes, et une carte de ces mécanismes. |
| **une heatmap de plus** | une couche qui dirait « il y a de la masse ici » n'ajoute rien. La masse ne dit pas si un palier a été annulé ou mangé — c'est précisément la distinction qui porte le sujet. |

## 2. Les deux places, et leurs deux rôles

**Hyperliquid est le laboratoire.** C'est la seule place au monde qui publie le
cycle de vie complet d'un ordre — placement, durée de vie exacte, terminaison,
et l'identité des deux contreparties d'une transaction. C'est donc la seule où
l'on puisse **fabriquer une vérité** : ce mur a-t-il été annulé, ou mangé, et
par qui. Les labels se fabriquent là, et nulle part ailleurs.

**Binance est le marché.** C'est là que le volume se fait, là qu'on exécute, et
là que la couche doit s'afficher.

**Conséquence, et elle est structurante : la traversée HL → Binance n'est pas
une phase tardive dont on pourrait se passer — c'est le programme.** On apprend
contre la vérité Hyperliquid pour appliquer sur des observables que Binance
publie, lui.

**Le plafond qui va avec, à écrire dans tout rapport qui touche à l'affichage :**

> Sans identité de portefeuille sur Binance, la vérité forte n'y est pas
> calculable. La traversée ne pourra jamais être validée **contre la vérité**,
> seulement contre un **proxy**.

Ce plafond est structurel : Binance ne publie pas l'identité des ordres et ne le
fera pas. Il borne le produit, pas seulement une phase de recherche.

**Ce que ça impose à toute grandeur : elle doit exister des deux côtés.** Une
grandeur qui a besoin de l'`oid`, de l'identité d'un ordre ou de son cycle de
vie complet sert à **fabriquer la vérité** — elle ne traversera jamais. Le
filtre s'applique dès P3, pas en P7.

## 3. Le produit est une table, pas une image

L'image en est un rendu. Une même source, trois consommateurs : **la carte**,
**la base d'apprentissage**, **le journal**. On conçoit la table d'abord.

Forme : **une valeur par `(instant, palier)`**, plus des marqueurs discrets sur
les niveaux qui le méritent. Chaque colonne porte son **`t_ref`** — l'instant où
la valeur devient connaissable. C'est ce qui empêche la fuite temporelle, et ce
projet a déjà rendu un résultat massif sur un monde nul faute de l'avoir fait.

Contraintes non négociables, décidées ici et pas après :

1. **Inférence sans L4.** Le L4 fabrique la vérité et entraîne ; il n'existe pas
   à l'écran.
2. **Client-side, temps réel.** Le calcul doit tenir dans un navigateur, à la
   cadence du flux.
3. **Zéro lookahead.** Voir `t_ref` ci-dessus.
4. **La grille de la production** — `nice(mid × BIN_REL)`, celle de
   `_recupere/construit/grille.py`. Deux mondes sur deux grilles ne sont
   comparables en rien.
5. **Survivre à la dégradation du flux d'affichage.** À **mesurer**, jamais à
   supposer. Le régime exact est dans `FAITS.md`.

**La heatmap n'existe pas encore. Elle est à fabriquer.**

### Quand les objectifs s'opposent

Ils s'opposeront. Trois, et l'ordre ci-dessous tranche. **Ne jamais arbitrer
autrement sans un ADR.**

| conflit | qui gagne | pourquoi |
|---|---|---|
| une réponse juste mais **non affichable** | **l'affichage** | elle va au journal, pas au produit |
| l'affichage exigerait de **dénaturer la question** — un indicateur joli et vide | **la question** | c'est ce qui distingue ce projet d'une heatmap de plus |
| une piste exige d'**abandonner la traversée** vers Binance | **la traversée** | sans elle, rien ne s'affiche et rien ne se trade (§2) |

## 4. Le critère

**Il n'est ni l'AUC, ni un gain économique.** Le critère est **mécanique** :
une grandeur est retenue si elle produit une **conséquence falsifiable sur la
trajectoire du prix** — où il va — et si elle survit aux quatre contrôles :

| | |
|---|---|
| **renormalisation** | même signe aux cinq échelles d'observation |
| **unité** | le **JOUR**, jamais l'observation ; IC de **Student** |
| **contrôle négatif** | sortie d'une bande nulle tirée par **décalage circulaire**, jamais par permutation i.i.d. |
| **réplication** | même signe sur **deux symboles**. Un effet qui n'apparaît que sur un symbole est un sur-ajustement. |

Décision du 04/08/2026 : **il n'y a pas de traduction économique obligatoire.**
Ni points de base, ni P&L, ni gain simulé. Une explication mécanique n'a pas à
se convertir en profit pour valoir.

## 5. La matière première

`03_EconoPhysique.md` catalogue les concepts. Ce n'est **pas** un plan : c'est le
réservoir dans lequel les candidats sont puisés. Les familles qui portent le
sujet : flux et conservation · potentiel et paysage d'énergie · entropie et
information · files d'attente et hazard rate · processus auto-excités ·
résilience et rhéologie · diffusion et temps de premier passage · criticité et
transitions de phase · absorption.

Trois avertissements, qui comptent autant que la liste :

* le catalogue classe ses concepts **par intuition**, ce que la méthode interdit ;
* il escalade **par nouveauté** plutôt que par pertinence ;
* il compte beaucoup de doublons — le même objet sous plusieurs noms. C'est
  l'épreuve É0 du banc qui les fond.

**Ne pas confondre quatre choses** que le catalogue traite comme
interchangeables : une **feature** va en P3 · un **contrôle d'instrument**
(l'équation de continuité : elle ferme ou elle ne ferme pas) va en P1 · une
**unité de sortie** va en P8 · un **critère de falsification** est transverse.

Et le meilleur du catalogue n'est pas une feature : c'est la **renormalisation**.
Un vrai phénomène survit au changement d'échelle. C'est la seule ligne qui
protège au lieu de proposer un calcul de plus, et c'est devenu l'épreuve É3.

Aucun concept n'entre sur son élégance. Chacun dépose sa fiche et passe le banc.

## 6. La séquence, et la porte

```
P0 ingestion → P1 carnet → P2 labels → P3 features → P4 dataset
                                             │
                   ┌─────────────────────────┴─────────────────────────┐
                   │  LA PORTE — la table s'affiche, en temps réel,    │
                   │  sans lookahead, sur la grille de production      │
                   └─────────────────────────┬─────────────────────────┘
                                             │
        P5 entraînement → P6 validation → P7 traversée → P8 simulation
```

**P7 est dans le chemin critique** (§2). La table doit s'afficher au-dessus du
carnet Binance, pas au-dessus de celui qui l'a entraînée : une grandeur
admissible est une grandeur qui **survit à la traversée**.

Trois conséquences dures :

* **une grandeur qui ne s'affiche pas ne s'entraîne pas** — le filtre
  d'admissibilité s'applique dès P3 ;
* **la couche doit être juste toute seule, sans modèle.** Si elle n'apporte rien
  comme visualisation honnête du carnet, un modèle posé dessus apprendra ses
  défauts ;
* **le ML se branche sur la table**, pas sur la donnée brute. La table est le
  contrat entre la recherche et le modèle ; elle se fige avant tout
  entraînement.

## 7. Le statut de tout ce qui précède MapDee

**MapDee est une refonte, pas une reprise.** Deux itérations ont précédé, toutes
deux exploratoires. **Aucun de leurs chiffres n'est un acquis** — y compris les
résultats négatifs : un négatif produit par un instrument non audité n'est pas
un résultat.

`_recupere/` est du matériel importé de dépôts morts, conservé parce que le
reconstruire coûterait des semaines. **Ce n'est ni une bibliothèque du projet ni
une dépendance : c'est une réserve de pièces détachées.** Rien n'en sort sans
avoir été relu. Ses ADR n'ont **aucune autorité** ici — les ADR de MapDee vivent
dans `decisions/` et repartent de zéro.

Ce qui vaut d'être repris de l'itération précédente n'est pas un résultat, c'est
une **discipline** : des seuils pré-enregistrés jamais baissés, des audits
adversariaux, des fautes publiées sans en retirer aucune. Son propre verdict :
*la barre a tenu, la traçabilité et la publication des réserves ont lâché.*

## 8. Le défaut qui revient, et les deux garde-fous

Quatre « événements » ont été construits **avant** que leur distribution ne soit
regardée, dans une seule nuit. Symptôme identique à chaque fois : **une classe à
100 %**.

Deux garde-fous, trois lignes de code, **obligatoires avant toute cible** :

* l'événement doit être **rare** — au-delà de 60 %, ce n'est pas un événement,
  c'est l'état normal du marché ;
* la cible doit avoir **deux classes** — au moins 5 % en minoritaire et au moins
  200 exemples.

Ils sont implémentés dans `_recupere/garde/`.

Et la règle qui prime sur toutes les autres :

> **Toute conclusion négative conduit d'abord à un audit de l'instrumentation
> avant d'être interprétée comme une absence de phénomène.**

Vérifier dans cet ordre : les données, les labels, les appariements, les fuites
d'information, les unités statistiques, les protocoles. **Ensuite** conclure.

Corollaire : **un contrôle dont on connaît d'avance le résultat n'est pas un
contrôle.** L'audit de ce dépôt a trouvé trois garde-fous sur cinq incapables
d'échouer.

## 9. La doctrine documentaire

Deux natures de document, deux régimes. La confusion des deux a produit un
document de cadrage portant six affirmations désavouées, lu en premier par
chaque session.

| | régime |
|---|---|
| **rapport de mesure** — il porte des chiffres datés | **jamais réécrit.** Le réécrire détruit la pièce à conviction. Errata daté et renvoi. |
| **document de cadrage** — programme, méthode, plan | **réécrit.** Il doit être à jour, pas archéologique. |

Git garde l'historique des deux : rien n'est réellement effacé.

Trois conséquences : un document qui affirme avoir été écrit **avant** un
résultat doit être **commité avant**, sinon son antériorité ne vaut rien · toute
décision importante devient un **ADR** (contexte, alternatives, décision,
justification, conséquences) · l'empreinte de configuration doit couvrir **le
code qui rend le verdict**, pas seulement celui qui calcule.

## 10. Les données

Tout est dans **`FAITS.md`** : source, volumétrie, couverture, corruptions,
pièges de reconstruction, environnement, et ce qui reste à mesurer. Rien n'y est
un acquis — le fichier le dit en tête.

Les connexions temps réel et les sources historiques sont dans
**`04_Endpoints.md`** : URLs, souscriptions, protocoles d'intégrité, pièges de
connexion déjà payés.

Deux points de périmètre qui ne se trouvent nulle part ailleurs :

* **la convention de gel des jours** est fixée par `decisions/ADR-000` ;
* **`data/` est dans `.gitignore` et n'y entre jamais.**

## 11. Ce qui bloque aujourd'hui

À traiter avant, pas pendant.

1. **L'épreuve de renormalisation n'est pas exécutable.** Elle demande l'échelle
   la plus fine ; les tables actuelles n'y descendent pas. Il faut un rejeu
   **événement par événement**, pas une dérivation des tables existantes.
2. **La cible n'est pas encore posée.** Décision du 04/08 : c'est le
   **déplacement du prix**, pas la fraction exécutée — un spoof réussi n'est
   jamais exécuté, donc une cible d'exécution récompenserait le spoof **raté**.
   Reste à l'écrire en définition opératoire.
3. **Les patterns n'ont pas de définition opératoire.** Le vocabulaire existe —
   annulé, mangé, rechargé — mais nommer n'est pas définir. Tant que ce n'est
   pas écrit, il n'y a rien à entraîner et rien à falsifier. Deux routes :
   la littérature, puis l'observation des trajectoires brutes sur le jour de
   banc. **Jamais l'inverse** : définir après avoir regardé, c'est fabriquer une
   cible dégénérée.

## 12. Répartition des rôles

| | |
|---|---|
| **Meddy** | tout **achat** et toute **dépense** · les **décisions produit** · le **choix des places et des symboles** · l'arbitrage de tout conflit non prévu ici |
| **le co-chercheur** | tout le reste : ingestion, reconstruction, labels, features, modèles, validation, intégration, rapports |

**Ne jamais engager une dépense ni passer une commande.** Ne jamais trancher
seul une décision produit : la remonter avec ses options.

Et une règle de forme : quand une conclusion est claire, la donner
**directement** avec son raisonnement. **Ne pas présenter une recommandation
déjà arrêtée sous la forme d'un menu dont deux branches sont mauvaises.**
N'ouvrir un choix que si les branches sont réellement défendables — et alors les
présenter à charge égale.

## 13. Ordre de lecture

| | quand |
|---|---|
| ce document | en premier |
| `01_Cahier_des_charges.md` | la méthode et les interdictions — avant de coder |
| `FAITS.md` | la donnée et ce qu'il reste à mesurer |
| `04_Endpoints.md` | avant toute connexion |
| `05_Protocole_de_selection.md` | le banc — avant de proposer une grandeur |
| `decisions/` | les ADR de MapDee |
| `03_EconoPhysique.md` | au moment de P3 seulement |
| `02_Resultats_de_test.md` | **ne pas lire pour se documenter.** Chiffres des itérations de test, sur un instrument reconstruit depuis : **aucun n'a valeur de fait**. Il ne sert qu'à une chose — savoir ce qui avait été trouvé avant, quand on vient de re-mesurer la même grandeur et qu'on veut comparer. Jamais comme point de départ. |
| `_recupere/lab/` | archives des dépôts morts — sans autorité, à consulter, jamais à citer comme acquis |
