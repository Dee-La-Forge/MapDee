# C8 — Admissibilité et traversée

> **Protocole PRÉ-ENREGISTRÉ.** Écrit et commité **avant** la mesure du §4.
> Les verdicts possibles et leurs critères sont fixés ici ; ils ne se
> renégocient pas après avoir vu un résultat.
>
> Chantier du `06_Plan_exploration.md`. Il ne dépend d'aucun verrou.

---

## 1. La question

On apprend sur Hyperliquid, on applique sur Binance. **Un mécanisme qui ne
traverse pas ne sert ni à afficher ni à trader** — il va au journal. Ce chantier
rend, pour chaque grandeur du registre, un **verdict de traversée** : traverse,
ne traverse pas, ou traverse sous condition d'une démonstration nommée.

Et il tranche la question qui commande le produit : **la décomposition
exécuté / retiré / ajouté est-elle reconstructible côté Binance ?** Si oui, le
socle traverse. Si non, le produit change de nature — et il vaut mieux
l'apprendre maintenant qu'en P7.

## 2. Ce que ce chantier ne fait pas

* il ne juge pas la **valeur** d'une grandeur — c'est le banc (É0-É4) ;
* il ne mesure pas la **dégradation du flux d'affichage** — c'est un inconnu
  **unique et partagé** (le régime exact vit dans le code du démon, hors dépôt,
  `FAITS.md` §11) : le porter fiche par fiche fabriquerait de la fausse
  précision. Tous les « traverse » ci-dessous sont **sous réserve de ce régime**,
  une fois, pour tous ;
* **il ne teste pas H2.** C8 répond « cette grandeur est-elle **calculable**
  sans le L4 » ; il ne peut pas répondre « la **trace survit**-elle » — ça,
  c'est empirique, testable après H1 seulement. Inscrire C8 en atténuation de
  H2 ferait croire le deuxième risque du projet traité alors qu'il ne l'est pas
  (audit du 05/08, I.10) ;
* il ne rouvre pas le plafond : sans identité de portefeuille sur Binance, la
  traversée ne se valide jamais contre la vérité, seulement contre un proxy.
  **À écrire dans tout rendu.**

## 3. Sortie n° 1 — la table de traversée (papier, verdicts des fiches + règle stricte)

Règle appliquée, celle du `06` : **une approximation non démontrée compte comme
« ne traverse pas »** — la case « sous condition » nomme sa démonstration, elle
ne se vide pas d'elle-même.

### Traverse *(sous réserve du régime de dégradation, unique et partagé)*

| fiche | pourquoi |
|---|---|
| **A1** OFI | diffs signés, des deux côtés, quelques opérations par événement |
| **A4** microprice | le haut du carnet — trivialement |
| **B1** hazard rate, **version palier** | les diffs suffisent. La version **ordre** ne traverse pas (L4) — ne jamais les nommer pareil |
| **B2** résilience | les diffs, fenêtre après l'événement |
| **B5** premier passage | le prix seul |
| **C3** diffusion anormale | le prix seul |
| **A3** décomposition e/r/a | **démonstration rendue le 05/08/2026** : mesure du §4, reconstructible 4/4 cibles (`journal/c8-rapport-20260805.md`). Limite portée : quantités **nettes** par fenêtre |
| **B3** réapprovisionnement (iceberg) | sa seule démonstration nommée était « hérite de A3 » — rendue avec elle. Même limite : détection sur quantités **nettes** |

### Traverse sous condition — la démonstration est nommée

| fiche | démonstration exigée |
|---|---|
| **A2** OFI localisé au mur | le mur jugé est-il dans la fenêtre de paliers que le flux d'affichage retient ? — dépend du régime, à mesurer |
| **A5** propagateur | une version dégradée qui survive sans la partie courte du noyau |
| **B4** absorption au contact | une définition opératoire du **contact** (C3/B7) ; et rappel : unité de sortie P8, pas une feature |
| **C1** concentration · **C2** forme/courbure | la correction de **censure** (F3) démontrée — le filtre par la médiane fabrique de la concentration apparente |
| **D1** ralentissement critique · **D2** cascades | tenue sous dégradation. *(La part de D2 héritée d'A3 est démontrée depuis le 05/08 ; sa condition propre reste.)* |

### Ne traverse pas

| fiche | pourquoi |
|---|---|
| **A6** auto-excitation (Hawkes) | exige l'événementiel fin ; la cadence d'affichage le détruit — sa fiche le dit. Reste utilisable **hors ligne**, côté vérité |
| **B1 version ordre** | exige `oid` et cycle de vie |
| **E1-E6** protagonistes, bloc entier | Binance ne publie aucune identité. **Fabriquent la vérité, ne s'afficheront jamais** — les confondre serait l'erreur la plus coûteuse du projet |

*(F et G sont hors table : contrôles d'instrument et cadre, pas des features.)*

**Lecture d'ensemble, à retenir** *(mise à jour du 05/08/2026 après la mesure
du §4)* : **8 traversent, 7 sous condition, 8 non.** Le chantier convergeait
sur deux preuves ; **la première est rendue** — la mesure du §4 a fait passer
A3 et B3, et réglé la part héritée de D2. Reste la seconde : la correction de
censure (C1, C2).

## 4. Sortie n° 2 — la mesure de reconstructibilité, PRÉ-ENREGISTRÉE

### Le fait déjà vérifié qui la rend possible

Vérifié le 05/08/2026 **sur la capture réelle**, pas sur la documentation : les
archives Binance de l'enregistreur portent, par ligne, les masses par palier
(`b`, `a`), le mid, la grille (`bs`), **et le flux exécuté par palier par
fenêtre (`x`)**. Les trois ingrédients existent. La question restante n'est pas
« les champs existent-ils » mais « **la décomposition qui s'en déduit est-elle
cohérente** ».

### L'estimateur

Par palier `k` et par fenêtre entre deux lignes consécutives :

```
Δm_k  = m_k(t) − m_k(t−1)          variation de masse
e_k   = x_k(t)                     exécuté (achats + ventes), porté par la ligne
net_k = Δm_k + e_k
a_k   = max(0, net_k)              ajouté   (net)
r_k   = max(0, −net_k)             retiré   (net)
```

**Limite écrite d'avance** : `a` et `r` sont des quantités **nettes** par
fenêtre — un ajout et un retrait égaux dans la même fenêtre s'annulent. C'est
vrai des deux côtés (Hyperliquid inclus) dès qu'on échantillonne ; seul le L4
donne le brut. La question de traversée porte sur l'estimateur **commun aux deux
places**, pas sur le brut.

**Attente écrite d'avance, pour ne pas la « découvrir »** : loin du prix,
`e ≈ 0` — les exécutions n'ont lieu qu'au contact. À distance, la décomposition
se réduit à ajouté/retiré ; la distinction annulé/mangé n'a de contenu **qu'au
contact**. C'est une propriété du marché, pas un défaut de l'estimateur.

### Le périmètre, déclaré avant le calcul

| | |
|---|---|
| **venues** | `BINANCE` (l'objet du verdict) et `HYPERLIQUID` (la référence de comparaison) |
| **symboles** | BTCUSDT et ETHUSDT |
| **jour** | **2026-08-02** — jour complet de capture, antérieur à la panne du 03/08 |
| **gels** | aucun : ces jours ne relèvent pas de la partition de décembre. Les fenêtres traversant un `gap` déclaré sont **exclues et comptées** |
| **stratification** | par **décile de distance au mid** — pas par la « bande d'étude » héritée, qui n'a pas de définition opposable (blocage B7) |

### Les verdicts, fixés maintenant

| verdict | critère |
|---|---|
| **NON reconstructible** | un des trois termes incalculable sur les données ; **ou** la **majorité** (> 50 %) des fenêtres actives est **incohérente** — `e_k > m_k(t−1)`, exécuté supérieur à la masse disponible, signature d'un désalignement temporel entre flux de transactions et flux de carnet |
| **reconstructible** | sinon. Le **taux d'incohérence** est publié par venue et par décile de distance, et la comparaison Binance ↔ Hyperliquid est publiée telle quelle |

Pourquoi 50 % et pas un seuil fin : si la majorité des fenêtres actives est
incohérente, l'estimateur décrit le désalignement, pas le marché — c'est le même
raisonnement que le garde-fou de dégénérescence. Un taux minoritaire est une
**borne de qualité à publier**, pas un motif d'échec.

### Ce que la mesure publie, verdict inclus

* le taux d'incohérence, par venue × symbole × décile de distance ;
* la part des fenêtres actives par terme (`e>0`, `r>0`, `a>0`), même découpage ;
* le nombre de fenêtres exclues pour `gap` ;
* la comparaison Binance ↔ Hyperliquid, sans seuil : elle informe C3, elle ne
  juge pas.

## 4 bis. Sortie n° 3 — le premier brouillon du schéma de la table

Relevé par l'audit du 05/08 (I.11) : le contrat central du projet — **la table**,
une valeur par `(instant, palier)` avec son `t_ref` — n'a aucun schéma, et il
était traité comme un livrable tardif. Or l'inventaire de ce chantier **est** sa
première moitié : colonne par colonne, ce qui existe des deux côtés, avec son
verdict de traversée.

La sortie n° 1 se rend donc **aussi** sous cette forme : une ébauche de schéma —
nom de colonne · observable source côté Binance · `t_ref` · verdict —
versionnée avec ce chantier. Elle ne fige rien : elle évite que le schéma
s'écrive en P5 en découvrant à ce moment-là ce qui ne traverse pas.

## 5. Suites, définies mais non lancées ici

* **C8.3 — la fenêtre simultanée** : le même estimateur sur les jours où les
  deux places sont captées ensemble. Courte, et elle ne grandit que si
  l'acquisition tourne.
* **C8.4 — le diagnostic de l'enregistreur de production** : son volume s'est
  effondré et des jours manquent. Chaque jour de panne est un jour de fenêtre de
  traversée **perdu définitivement**. Décision de périmètre chez Meddy.

## 6. Ce qui est interdit dans ce chantier

* déplacer un critère du §4 après avoir vu un résultat ;
* étendre le périmètre après avoir vu un résultat ;
* transformer la comparaison Binance ↔ Hyperliquid en verdict — elle n'a pas de
  seuil pré-enregistré, elle ne peut donc rien trancher ;
* vider une case « sous condition » sans la démonstration nommée.
