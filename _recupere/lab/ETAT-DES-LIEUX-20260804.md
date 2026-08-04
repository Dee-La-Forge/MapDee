# État des lieux — 04/08/2026, 00 h 50

Document de passation. Écrit à la demande de Meddy, vérifié fichier par fichier
et non de mémoire. Branche `certification-openbook-202512`, arbre propre,
**43 commits** depuis `8347810`.

---

## 1. CE QUI EST ÉTABLI, ET QUI TIENT

Ces faits ont été mesurés, contrôlés, et rien de ce qui a suivi ne les a
contredits.

**Le carnet profond existe et est validé.** `hl_deep` couvre la bande d'étude
(0,12–0,80 % du mid) sur **100 % des photos** ; `hl_book`, avec ses 20 paliers,
la couvrait sur **0 %** — sa portée médiane vaut 0,0215 % du mid. Le carnet
profond **contient** `hl_book` au même instant à `2,19e-08` d'écart relatif :
c'est de l'arrondi float32.

**Le rejeu était gravement biaisé.** `prod_like_rows` reconstruit le carnet
depuis un livre vide : mesuré le même jour à la même heure, il voit **11,6 % des
paliers** et **78,5 % de la masse**. Conséquence non corrigée : sa **médiane de
bande est 32× trop haute**, donc il détecte **26 murs là où il y en a 153**.
Toute la chaîne alimentée par le rejeu travaille encore avec ça.

**La production était aveugle à la moitié de son objet.** `SNAP_BAND` valait
0,4 % quand `DIST_MAX` vaut 0,8 % : le recorder voyait 63 % des murs mais
**43,6 % de leur masse**. Corrigé — `SNAP_BAND` se dérive maintenant de
`DIST_MAX`.

**Le flux public Hyperliquid n'est pas plafonné à 40 paliers.** `nSigFigs` porte
la portée à 0,306 % (pas de 10 $) ou **3,059 %** (pas de 100 $), et les **trois
résolutions s'abonnent simultanément** — vérifié sur le WebSocket réel.

**Hyperliquid publie l'identité des deux contreparties**, et `orderUpdates`
**accepte un portefeuille tiers nommé** : 1 513 mises à jour d'ordres en 45 s
pour trois portefeuilles. Aucune autre venue ne le permet. Le recorder capte ces
identités depuis le début (100 % des transactions, 19 707 portefeuilles par
jour) et **rien ne les lisait**.

**L'identité persiste huit mois.** 33,5 % des portefeuilles actifs de décembre
2025 tradent encore en août 2026 ; 41,9 % parmi les plus « fuyants ».

**Les murs qui fuient sont posés par une dizaine d'acteurs.** Dans le dixième
supérieur, un mur a 4 porteurs mais **le premier en détient 99,7 %** ; **dix
portefeuilles portent 97,7 % de la masse**, les mêmes d'un jour à l'autre, et
trois sont encore actifs aujourd'hui.

---

## 2. CE QUI A ÉTÉ INVALIDÉ, ET POURQUOI

**Le `flee_ratio` de l'ADR-021 ne mesure rien.** Il vaut **exactement 1,000 pour
99,28 % des murs**. Cause : la fenêtre de 30 s et la bande 0,12–0,80 % sont
incompatibles — le prix n'atteint pas ces paliers en trente secondes, donc rien
ne s'y exécute et tout ce qui s'y termine se termine par une annulation. **Il
mesure que le prix n'est pas venu.**

Conséquence en amont : `M(t) = Σ taille × flee` **est** la masse. Donc `I(t)`
d'E1 n'était pas un déséquilibre de masse *factice* mais un déséquilibre de
masse tout court. **La vérité L4 n'a jamais été dans le prédicteur**, contrairement
à ce que l'ADR annonce.

**E1 était circulaire.** La fenêtre de révélation recouvrait la cible : sur un
monde nul (vérité rho = 0), il rendait **+0,866**. Réparé (fenêtres disjointes à
`t+2W`, validé sur 12 mondes nuls), mais **son résultat a été retiré**.

**Le canal des portefeuilles ne paie pas ses frais.** Signal réel et reproduit
(+0,85 de persistance à une semaine, p < 1 % sous 200 placebos), mais le
backtest exécutable est **négatif sur les quatre cellules** (−6 bp par
aller-retour) et sur **cinq horizons**. Cause : le gain brut par aller-retour
vaut 2,5 bp contre **7 bp de frais preneur**.

**L'encadrement n'est pas un événement.** 100 % des instants sont encadrés, même
avec un seuil 32× plus strict que le protocole.

**Et le résultat le plus prometteur ne survit pas à son contrôle.** P1 (la porte
s'ouvre, le prix passe) donnait quatre jours stables et convaincants. P2, qui
compare les **deux** portes au même instant — donc à tendance, volatilité et
marché identiques — donne un IC qui **contient zéro** (+0,81 bp, [−1,35 ; +2,96],
t = 1,19) et **un jour sur quatre de signe inverse**.

---

## 3. LE DÉFAUT DE MÉTHODE, ET IL EST SYSTÉMATIQUE

**Quatre fois** dans la même nuit, un « événement » s'est révélé quasi universel
— et à chaque fois la mesure avait été construite **avant** que sa distribution
ne soit regardée.

| mesure | l'« événement » | fréquence réelle |
|---|---|---|
| E2 | encadrement | **100 %** |
| D1 | fuite (`flee > 0,5`) | **99,28 %** |
| D2 v1 | fuite à l'approche | **100 %** (bug de filtre de bande) |
| P2 | ouverture d'une porte | **85 %** |

Le symptôme était identique à chaque fois : **une classe à 100 %**. Un contrôle
de trois lignes — *l'événement est-il rare, la cible a-t-elle deux classes ?* —
les aurait tous attrapés. **Il n'est toujours pas dans le harnais.**

Autres fautes de la nuit, toutes documentées dans les commits : un chiffre de
coût inventé (1,5 bp au lieu de 7) qui retournait une conclusion ; un facteur
deux entre écart de déciles et gain par aller-retour ; deux horodatages d'ADR
inventés ; un script shell modifié pendant son exécution, qui a tué la chaîne de
construction.

---

## 4. CE QUI EXISTE DANS LE DÉPÔT

**Données** — `data/l4/openbook/`, 18 Go. `hl_orders` et `hl_book` pour 12 jours,
`hl_fills` pour 11, **carnet profond pour 5** (08 à 12, BTC seulement) dans
`deep/parts/`. Source brute intacte : `data/l4/openbook-202512/`, 188 Go.

**Jours** — 01-07 certification consommée (CAS D, lecture seule) · 08 banc
d'instrument · 09-16 exploration, dont **09-12 construits** · **17-23 réserve,
jamais ouverte**, gelée côté construction ET côté mesure.

**Vingt scripts d'expérience** écrits cette nuit dans `experiments/` : `e1_*`
(oracle, contrôle négatif, verdict), `e2_encadrement`, `d1` à `d5`, `p1`, `p2`,
`w_*` (canal portefeuilles : impact, indice, placebo, croisement, backtest,
sélection adverse).

**Neuf notes de laboratoire** dans `lab/02-experiments/`, une par mesure, avec
ses réserves.

**ADR-021** porte dix addenda datés, chacun écrit **avant** la mesure qu'il
encadre.

**Harnais** — `experiments/preflight.py`, **12 contrôles de comportement**,
chacun ayant échoué avant son correctif.

**Recorder** — actif, 4,1 h, bande 1,0 %, 10/10 flux, 1,47 M lignes.

---

## 5. LES DIX-HUIT POINTS OUVERTS

Les trois qui comptent :

1. **`prod_like_rows` ne consomme pas le carnet profond.** Médiane de bande 32×
   trop haute dans toute la chaîne de rejeu. C'est le plus gros morceau et il
   n'est pas entamé.
2. **Un seul symbole.** ETH et SOL n'ont pas de carnet profond ; le protocole en
   veut trois pour certifier.
3. **Le contrôle de dégénérescence de cible** n'est pas dans le harnais, alors
   qu'il aurait attrapé quatre erreurs sur quatre.

Les quinze autres sont au registre `lab/REGISTRE-20260803.md`, sections A à I.

---

## 6. SI QUELQU'UN REPREND

L'observation la plus riche et la moins exploitée : **83 à 89 % des instants
voient les deux portes s'ouvrir ensemble**. Ce n'est donc pas une porte qui
s'écarte pour laisser passer — c'est **le carnet entier qui se retire**. Ni P1
ni P2 ne l'ont regardé, et c'est peut-être là qu'est la cinétique.

Et avant toute nouvelle mesure : **regarder la courbe de masse d'un mur dans le
temps**, une par une, avant de décider ce qu'« ouvrir » veut dire. Les quatre
définitions essayées cette nuit ont toutes été posées à l'aveugle.

Avec un écart-type inter-journalier de 1,35 bp, il faut **une vingtaine de
jours** pour distinguer un effet de 0,8 bp de zéro. Il y en a quatre.
