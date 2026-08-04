# ADR-012 — ANNEXE DE MISE EN ŒUVRE (écrite AVANT le premier chiffre de transfert)

**Date** : 2026-08-02, 05 h 45 · **Statut** : à valider par Meddy · **Auteur** : Claude

ADR-012 fixe les **seuils** de la porte S6. Il ne fixe pas tous les **choix
d'implémentation**. Ce document les fige avant exécution, pour la même raison
qu'ADR-013 a été écrit avant de relire le jalon : un choix fait après lecture
d'un résultat n'est plus un choix, c'est un arbitrage déguisé.

**Aucun chiffre de transfert HL→Binance n'existe au moment où ces lignes sont
écrites.** Vérifié : aucun rapport dans `lab/`, aucune ligne de log, aucun
message de commit. La porte n'a jamais tourné.

## 1. Le modèle transféré

Le **témoin logistique** (`p3_models.TrivialWitness`), entraîné sur **tout**
Hyperliquid (11 jours BTC, 5 jours ETH), par symbole.

Pourquoi lui : le lambdarank a échoué sa barre au jalon (1/11 folds), il ne
reste que le témoin ; et ADR-010 l'avait pré-écrit — « le témoin devient le
modèle de production, plus simple, plus transférable, moins cher ».

**Pas de LODO ici.** Le jeu d'évaluation est une autre bourse, un autre mois :
il n'y a rien à purger, aucune fuite possible. Le modèle voit tout HL, comme le
ferait un modèle de production.

## 2. Le score transféré est LINÉAIRE

Le témoin est une logistique sur les **deltas** de features de paires. Sa
décision sur une paire est `w·(x_i − x_j)`, donc son score par ligne est
`s(x) = w·x_std` : l'intercept et le centrage s'annulent dans la différence.
C'est `TrivialWitness.score`, déjà écrit et vérifié par selftest. **L'imputation
et la standardisation sont celles apprises sur HL**, appliquées telles quelles à
Binance — c'est la définition même d'un transfert : on ne réajuste rien sur la
cible.

## 3. Les features communes — 18, et pourquoi pas 19

Le banc du jalon en compte 19. Binance en produit 18 : **`f_gap_rows` n'existe
pas** de ce côté (c'est un compteur de trous propre au pipeline P3 d'HL). Les
18 autres sont produites par la MÊME fonction (`dataset.build_events`) des deux
côtés, donc identiques par construction :

`f_mult`, `f_logmag`, `f_dist`, `f_side`, `f_occ`, `f_conv`, `f_peak_ratio`,
`f_persist`, `f_age`, `f_turnover`, `f_absorb_hist`, `f_withdraw_hist`,
`f_wd_ratio_hist`, `f_spec_flatness`, `f_spec_tonality`, `f_spec_centroid`,
`f_spec_flux`, `f_coh_neighbours`.

**Le témoin est donc ré-entraîné sur ces 18 colonnes**, pas sur les 19 du
jalon : comparer un modèle à 19 features avec une évaluation à 18 serait
malhonnête. Le chiffre HL de référence est recalculé sur le même banc à 18.

`f_absorb_contact` reste INTERDITE des deux côtés (circularité, registre).

## 4. La cible côté Binance

`y = 1 − flee_ratio = tradé / (tradé + retiré)` au contact.

C'est **exactement** le « proxy commun » du prérequis d'ADR-012, celui dont le
rang a été montré suivre `y_post` sur HL le 01/08 (Spearman +0,2024 / +0,1635,
IC par cluster excluant 0). `dataset.py:93` définit
`flee_ratio = retiré/(retiré + tradé)` : le complément est le proxy, sans
retraitement.

Le label BINAIRE est écarté : mesuré saturé sur les deux venues (98,5 % HL,
21/21 Binance), pour une raison de fond — à 100 ms un palier se renouvelle
5 à 30 fois par fenêtre.

## 5. Appariement des populations

ADR-012 exige d'apparier par quantiles de `f_dist`, `f_mult`, `side`, heure UTC.
Mise en œuvre figée :

- **quartiles** de `f_dist` et de `f_mult`, bornes calculées sur la population
  **HL** (la référence), appliquées aux deux ;
- `side` tel quel (2 modalités) ; heure UTC en **6 blocs de 4 h** ;
- cellule = (quartile_dist × quartile_mult × side × bloc_horaire) ;
- on **sous-échantillonne HL** pour épouser la distribution de cellules de
  Binance (Binance est la population cible et la plus petite), graine `12345` ;
- les cellules absentes d'un des deux côtés sont écartées **des deux**, et leur
  poids est déclaré dans le rapport.

## 6. Les métriques — identiques au jalon, sans variante

`pairwise_auc` : fenêtre **300 000 ms**, décidabilité **0,10**, plafond **200**
paires par couple de clusters, **400** tirages, bootstrap **par clusters de
base**. Clusters : `episode` côté Binance (il n'y a pas de wallet), `cluster`
côté HL.

**Le p de permutation (200 tirages) est calculé et publié en plus de l'IC**,
leçon du diagnostic de puissance de cette nuit : le bootstrap par cluster est
très conservateur quand quelques clusters portent l'essentiel. Il est
**informatif, jamais décisoire** — les barres d'ADR-012 restent les barres.

## 7. Les barres — inchangées, recopiées d'ADR-012

1. **Absolue** : AUC pairwise Binance **≥ 0,55** ET IC95 excluant 0,5.
2. **Rétention** : `edge_Binance ≥ 0,50 × edge_HL`, edge = AUC − 0,5, mesurés
   sur les populations **appariées**, même modèle, même bootstrap.
3. **Les deux symboles** doivent passer les deux barres.
4. **Cas dégradé** : < 60 clusters Binance dans une cellule → « PUISSANCE
   INSUFFISANTE », relance unique quand le recorder aura ≥ 7 jours, pas de
   troisième passage.

## 8. Réserves à publier avec le verdict, quel qu'il soit

- **Venue et époque sont confondues** (HL = mai 2026, Binance = fin juillet).
  Un échec ne dira pas lequel des deux a tué le transfert. Écrit dans ADR-012
  dès le 31/07.
- **Biais de sélection Binance** : la bande du recorder est **±0,4 %** quand le
  détecteur travaille jusqu'à **0,8 %**, et la médiane de référence est calculée
  sur ±0,4 % au lieu de ±10 %. Conséquence mesurée : population trois fois plus
  rare et six fois plus concentrée qu'HL. C'est un artefact d'instrument, pas
  une propriété du marché.
- **4 jours d'archive Binance** seulement (07-29 → 08-01).

---

# AMENDEMENT — passage 2, décidé par Meddy le 02/08 après le NO-GO du passage 1

**Statut** : accepté (Meddy, option B) · **Écrit avant le second run.**

## Ce qu'a rendu le passage 1

NO-GO : BTC AUC 0,4922 (p de permutation 0,63 — le hasard), ETH 0,5209
(p 0,040 — un souffle réel, très sous la barre). Rapport
`s6-2026-08-02T033041Z-929874ea6df1.md`, conservé, **non rétracté**.

## Pourquoi un second passage, et pourquoi ce n'est pas un troisième essai

Le passage 1 a comparé des features qui **ne mesurent pas la même chose** d'une
venue à l'autre. Ce n'est pas une découverte d'après-coup : `bn_medium.py:85`
le documente depuis le **01/08**, donc avant que le moindre chiffre de transfert
n'existe.

> « MÉDIANE. `med` est calculée sur les paliers de la bande ±0,4 %, pas ±10 %.
>   Elle est donc plus HAUTE qu'en prod. »

Or `f_mult = magnitude / med` et `f_logmag = log1p(mag/med)`. Un même mur ne
rend donc pas le même nombre selon la bourse — et dans un score linéaire, une
feature dont l'échelle change **déforme le poids de toutes les autres**.

Précédent du dossier, exactement de même nature : le 01/08, les 6 jours de
relance avaient un book 116× trop dense ; la réponse fut **« dégrader
l'instrument, jamais les seuils »** (`90d35de`), validée sur un jour de
recouvrement. On corrige ici l'instrument, pas la barre.

## Les trois corrections, et rien d'autre

1. **Retrait des deux features dépendantes de `med`** — `f_mult` et `f_logmag`,
   soit le bloc **TAILLE**. Le banc passe de 18 à **16 features**.
   Coût attendu en signal : **nul**. P0 a mesuré ce bloc seul à **AUC 0,50-0,54
   sur les quatre cellules** — « la magnitude d'un mur ne prédit rien ». On
   retire deux features incomparables dont on sait déjà qu'elles n'apportent
   rien. Aucune des 16 restantes ne dépend de `med` (vérifié une à une :
   distances, présence, ratios internes à la rangée, descripteurs normalisés).

2. **L'appariement n'utilise plus `f_mult`** — apparier deux populations sur une
   grandeur qui n'a pas la même définition des deux côtés aligne deux choses
   différentes. Cellule = quartiles de `f_dist` × `side` × bloc de 4 h UTC.

3. **Correction d'un défaut de MON implémentation, pas du programme** : au
   passage 1, le sous-échantillonnage de HL a réduit la référence ETH à
   **G = 35 clusters, IC [0,000 ; 1,000]** — une référence inutilisable, donc
   une barre 2 sans valeur. La taille de l'échantillon apparié est désormais
   **maximisée** sous la distribution cible (N = min sur les cellules de
   disponible/proportion) au lieu d'un plafond arbitraire.

## Ce qui NE bouge pas

Les deux barres (0,55 avec IC excluant 0,5 ; rétention ≥ 50 %), les deux
symboles exigés, le cas dégradé à 60 clusters, la métrique, les graines, la
cible, le modèle transféré. **Aucun seuil n'est touché.**

## Engagement

Ce passage est le **dernier**. Quel que soit son verdict, il fait foi et clôt
S6 sur ces données. Toute correction ultérieure exigerait une porte nouvelle,
sur des données nouvelles.
