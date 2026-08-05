# C9 — Le harnais : spécification de bout en bout

> **Spécification, pas code.** Écrite le 05/08/2026, pendant la construction de
> décembre, comme `06` l'exige — le harnais s'écrit avant les définitions, il ne
> tourne qu'après C3.
>
> **Régime du document** : les décisions marquées **PROPOSÉ** attendent
> l'arbitrage de Meddy ; les décisions marquées **TRANSCRIT** ne décident rien —
> elles recopient ce qui existe déjà dans le code ou dans une ADR acceptée, avec
> leur source ; les décisions marquées **OUVERT** exigent une ADR avant le
> premier passage de l'épreuve concernée. Rien ici ne s'auto-valide.
>
> Source d'autorité : `05_Protocole_de_selection.md` (épreuves, seuils),
> `decisions/ADR-001` (métrique d'É4), `06_Plan_exploration.md` §C9 (les quatre
> pièces), `journal/registre-des-grandeurs.md` (états). En cas d'écart entre ce
> document et eux, **eux font foi** — et l'écart se corrige ici.

---

## 1. Ce que le harnais est, en une phrase

Une boucle qui prend une fiche de `03`, la fait passer par
**ÉS → É0 → É1 → É2 → É3 → É4**, écrit à chaque franchissement ou chute **une
ligne au registre avec son chiffre**, et enchaîne — jusqu'à épuisement des
candidats déclarés ou déclenchement d'un critère d'arrêt de `06` §7.

**La règle d'échec de `06`, reprise telle quelle** : si une épreuve ne peut pas
être rendue mécanique sans arbitrage, c'est le protocole qu'il faut corriger,
pas le harnais qu'il faut assouplir.

## 2. Les quatre pièces, dans l'ordre corrigé (audit I.5)

```
P0  préflight        refuse de démarrer — EN TÊTE, pas en quatrième
P1  générateur       carnet fabriqué, schéma deep, vérité séparée
P2  registre         machine à états — existe déjà, contrat transcrit ici
P3  épreuves         ÉS + É0..É4, seuils gravés, zéro jugement
```

### P0 — le préflight

**Il ne prévient pas, il bloque** — chaque contrôle est du code qui lève.
Contrôles, tous obligatoires :

1. arbre git **propre**, en excluant les **chemins de sortie déclarés**
   (`journal/construction/`, sorties du run courant) — sans cette exclusion il
   s'interbloque pendant toute construction longue (audit I.5) ;
2. `05` et `03` **commités**, et le hash inscrit dans chaque ligne de registre
   produite par le run ;
3. le périmètre demandé ne touche **aucun jour gelé** ni la **réserve**
   (17-23) — même contrôle que `lot.py`, appelé avant la première seconde ;
4. **aucun dossier à deux générations** (empreintes de manifeste homogènes sur
   le périmètre, `provenance_certifiee` vraie) ;
5. les fichiers obligatoires existent : registre, fiche du candidat, déclaration
   du nombre de candidats — `05` §5 : aucun calcul avant le registre ;
6. les deux garde-fous de `05` §3 sont **importables et testés** — un préflight
   qui référence un garde-fou absent doit échouer ici, pas à É4 ;
7. **le préflight se teste en échouant** : la suite de tests prouve que chacun
   des contrôles ci-dessus **peut** lever. Un garde-fou dont on n'a pas prouvé
   qu'il peut échouer est décoratif.

### P1 — le générateur synthétique

**Contrat de sortie.** Deux tables par run, même horloge :

* **l'observable** — exactement le schéma de `deep`. **TRANSCRIT** depuis
  `_recupere/construit/jour.py::_DeepWriter._SCHEMA`, qui ne vivait que là
  (décision D1, §3) :

  ```
  t    int64      instant de la photo
  coin string
  mid  float64
  bs   float64    pas de grille de la photo
  k    int32      palier = int(px // bs)
  mag  float32    masse du palier, en dollars (somme prix × taille)
  n    int16      nombre d'ordres agrégés au palier
  ```

  Parquet, compression zstd, photos par lots — la méthode candidate lit ceci
  et **rien d'autre**.

* **la vérité** — une table séparée `(t, k, mecanisme, params)` : quel
  mécanisme a été injecté, où, quand, à quelle amplitude. La méthode ne la voit
  jamais ; seul le banc compare.

**Déterminisme** : graine unique par run, inscrite dans la sortie ; deux runs à
même graine sont **identiques octet par octet**. Sans ça le bras nul n'est pas
comparable au bras injecté.

**Grille** : `bs = nice(mid × BIN_REL)` — la grille de la production, décision
D2 (§3). **Vérifiée par test, jamais par import de l'archive** : le test
d'acceptation compare, sur une grille de mids couvrant BTC et ETH, le `bs` émis
par le générateur au `bs` d'un artefact `deep` réel (BTC ~90 000 → 2,0), bit à
bit.

**Tests d'acceptation de P1** : schéma identique à un `deep` réel (comparaison
de schémas Arrow, pas des yeux) · déterminisme (deux runs, même graine, hash
égal) · bras nul = bras injecté à amplitude zéro · la vérité recoupe
l'observable (chaque injection déclarée est visible dans la masse au palier
déclaré).

### P2 — le registre

Il existe (`journal/registre-des-grandeurs.md`). Le harnais **écrit dedans, en
ajout seul**, au format qui y est défini :

```
date · nom · état · épreuve · LE CHIFFRE · périmètre · proposée par
```

Le harnais refuse d'écrire une élimination sans chiffre, refuse de modifier une
ligne, et inscrit le **plancher de détection d'ÉS même quand la méthode
passe** — c'est lui qui rend les négatifs futurs lisibles.

### P3 — les épreuves

Chaque épreuve est une fonction `fiche → (verdict, chiffre)` avec seuils
gravés, transcrits de `05` et `ADR-001` :

| épreuve | calcul | seuils (source) |
|---|---|---|
| **ÉS** | rappel à faux positifs fixés, plancher de détection, bras nul — sur P1 | bras nul détecte → disqualifiée ; plancher > amplitude plausible → écartée (`05` §8) |
| **É0** | Spearman candidat ↔ candidat, sur le périmètre de la fiche | `|ρ| ≥ 0,90` → même objet, on garde le moins cher (`05` §4) |
| **É1** | lecture de la fiche | quatre questions, règles cas par cas de `05` §4 |
| **É2** | Spearman candidat ↔ bloc retenu (témoin trivial inclus dès le départ) | `< 0,50` passe · `0,50-0,70` surveillance · `≥ 0,70` doublon présumé (`05` §4) |
| **É3** | la grandeur aux cinq résolutions, rejeu événementiel | même signe partout **et** ρ ≥ 0,60 contre l'échelle fine (`05` §4) — ⚠️ échelle fine contestée, D12 |
| **É4** | Spearman **partiel** candidat ↔ cible, contrôlé sur le bloc gelé du tour | unité = jour · Student bilatéral, IC 95 % publié · **BH 10 % sur les candidats seuls décide** · nul par décalage circulaire · même signe sur deux symboles (`ADR-001`) |

Les deux garde-fous de `05` §3 (événement < 60 %, classe minoritaire ≥ 5 % et
≥ 200 exemples) s'exécutent **avant** toute épreuve qui définit un événement ou
une cible binaire.

---

## 3. Les douze décisions de conception — recensées, plus « au minimum »

`ETAT.md` §1 en nommait sept « au minimum » et renvoyait à un détail qui
n'existe dans aucun rapport (référence pendante — constatée le 05/08). Voici le
recensement complet, chacune avec son statut.

| # | décision | statut |
|---|---|---|
| **D1** | **le schéma que le générateur émet** | **TRANSCRIT** au §2/P1 depuis `_DeepWriter._SCHEMA` — il ne vit plus seulement dans l'archive |
| **D2** | **la constante de grille** | **TRANSCRIT** : `BIN_REL = 2,5e-5`, arrondi `nice` 1/2/5/10 strict (`_recupere/construit/grille.py`, porté de la production `sec-recorder.js:443/233`). Le coefficient 2,5 ne sort jamais — c'était la grille fautive du 03/08. **PROPOSÉ** : promouvoir `grille.py` hors de `_recupere/` dans le harnais, avec son selftest — l'archive ne doit pas être une dépendance d'exécution |
| **D3** | **le modèle génératif du carnet** | **VALIDÉ par Meddy le 05/08/2026** : flux d'ordres sans intelligence (arrivées/annulations/exécutions en Poisson par palier, intensités décroissantes avec la distance au mid — le modèle standard de la littérature, type Smith-Farmer), calé par moments sur le jour de banc (`ADR-000`). Il est volontairement pauvre : ÉS teste « la méthode retrouve-t-elle une injection », pas « le générateur imite-t-il le marché ». Si le bras nul de ce modèle s'avère trop facile, montée en gamme vers un modèle queue-réactif — **par ADR**, pas en silence |
| **D4** | **les mécanismes à injecter** | **VALIDÉ par Meddy le 05/08/2026** : trois, alignés sur C0 — **leurre** (masse posée hors contact, retirée à l'approche du prix), **recharge** (masse ré-approvisionnée au même palier après exécution), **absorption** (masse tenue sous exécutions répétées). Chacun paramétré par une **amplitude** en multiple de la masse médiane locale — c'est l'axe du plancher de détection |
| **D5** | **la vérité à injecter** | tranché par la structure de P1 : la vérité d'ÉS est **le label d'injection**, mécanique et connue — elle n'est **pas** le « devenir », qui reste une définition produit (C3, Meddy). ÉS n'attend donc pas C3 ; seuls É3/É4 l'attendent |
| **D6** | **l'amplitude plausible du phénomène** | **MEDDY** — c'est un seuil de critère d'arrêt (`06` §7, §« décisions réservées »). La spec fixe seulement sa **forme** : déclarée en multiple de la masse médiane locale (même unité que D4), **avant** la première mesure de plancher, au registre. Les distributions C5 et la littérature C0 l'informent ; elles ne la décident pas |
| **D7** | **le vocabulaire d'états du registre** | **TRANSCRIT** : les états du registre font foi (`déposée`, `ÉS`…`É4`, `sous surveillance`, `doublon présumé`, `réorientée`, `éliminée`, `retenue`, `témoin trivial`). Les « deux schémas concurrents » : le format de ligne d'`05` §5 (5 champs) diverge de celui du registre (7 champs). **PROPOSÉ** : aligner `05` §5 sur le registre — 7 champs, l'état et le périmètre en plus ; c'est le registre qui est exécuté |
| **D8** | **la place d'ÉS** | **VALIDÉ par Meddy le 05/08/2026** : ÉS juge des **méthodes**, pas des grandeurs (levée de la conflation notée par `ADR-001`). Le banc n'a qu'une méthode centrale — la corrélation de rang (simple/partielle) — donc **un passage ÉS pour le banc lui-même**, avant tout candidat : il mesure aussi la stabilité du Spearman partiel quand le bloc grandit (incertitude n° 1 d'`ADR-001`). Toute méthode supplémentaire (un détecteur dédié d'un mécanisme) repasse ÉS pour son propre compte. Dans la boucle : ÉS est un **préalable par méthode**, É0-É4 s'enchaînent **par candidat** |
| **D9** | **le traitement des ex æquo** dans les rangs | **VALIDÉ par Meddy le 05/08/2026** : rangs moyens (mid-rank), le standard de Spearman — et le même partout (É0, É2, É4), sinon les trois épreuves ne calculent pas la même statistique |
| **D10** | **le nombre de candidats déclaré** | **VALIDÉ par Meddy le 05/08/2026** : **16 candidats** — les fiches de `03` partie I (A1-A6, B1-B5, C1-C3, D1-D2) — plus le **témoin trivial hors compte** (il n'est pas un test). Déclaré au registre le jour même. Tout ajout ultérieur rouvre le compte et le dit |
| **D11** | **les contrôles du préflight** | fixés au §2/P0 — la liste est la spec, toute extension s'ajoute par commit avant le run qui l'utilise |
| **D12** | **l'échelle la plus fine d'É3** | **OUVERT — ADR requise avant le premier passage d'É3** (audit I.9) : le barreau 100 ms tombe dans l'interdécile de la cadence de blocs (~87 ms) ; proposition portée à l'ADR : échelle fine = **grille de blocs native**, événementielle. Rien dans le harnais ne doit coder « 100 ms » en dur |

## 4. Ce que le harnais n'attend pas, et ce qu'il attend

**N'attend rien** : P0, P1, P2, ÉS, É0, É1, É2 — tout se construit et se teste
sur carnet fabriqué ou sur papier, pendant la construction.

**Attend** :

* **C3 gelé** — É4 (la cible) et la partie « cible » d'É3 ;
* **le rejeu événementiel** — É3 (`05` §9.1 : quelques jours, pas le mois) ;
* **D12 arbitrée** — le premier passage d'É3 ;
* **D6 déclarée** — la première mesure de plancher qui veuille conclure ;
* **la mesure de la fraction de paires intra-unité** (`05` §9.4) — préalable à
  É4, elle décide si l'IC vaut quelque chose. Elle se mesure sur le jour de
  banc, et le harnais la refuse manquante (contrôle P0.5).

## 5. Ordre de construction proposé

1. P0 préflight (avec sa suite de tests qui échoue) ;
2. P1 générateur + tests d'acceptation ;
3. P3/ÉS sur P1 — le passage ÉS du banc lui-même (D8), qui rend en même temps
   la mesure de stabilité du Spearman partiel ;
4. P3/É0-É2 (elles ne dépendent d'aucune définition) ;
5. P3/É3-É4 — squelettes avec refus explicite tant que C3/D12/D6 manquent :
   **le harnais doit refuser de les exécuter, pas les simuler**.
