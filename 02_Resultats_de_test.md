# Résultats des itérations de TEST — pour comparaison seulement

> Annexe de `00_Prompt_MapDee.md`. **Lire son §0 avant ce fichier.**

**Aucun chiffre de ce document n'a valeur de fait établi.** Ce sont des
observations produites par deux prototypes exploratoires, sans protocole
pré-enregistré, sur un instrument dont l'audit a montré que trois garde-fous
sur cinq ne pouvaient pas échouer.

Ils servent à deux choses, et deux seulement : **ne pas redécouvrir** ce qui a
déjà été mesuré, et **savoir de combien une faute d'instrumentation peut
déplacer un résultat** (bloc H).

Quand tu ré-établiras l'un d'eux sous protocole propre, compare — et si l'écart
est grand, c'est une information sur l'instrument d'alors, pas forcément sur le
marché.


**Rappel du §0 : ce sont des chiffres de TEST.** Ils servent de **point de
comparaison**, pas de référence. Quand tu ré-établiras l'un d'eux sous protocole
propre, compare — et si l'écart est grand, c'est une information sur
l'instrument d'alors, pas forcément sur le marché.

Conditions communes, sauf mention contraire : hors-échantillon, split temporel
avec **embargo 60 min**, épisodes non chevauchants, réplication BTC/ETH,
confondeur géométrique retiré.

---

## A. P0 — survie au contact (28/07/2026, 3 jours, 29 h, BTC + ETH)

### A.1 Performance de classement

| symbole | label | n_test | AUC | lift top-décile |
|---|---|---|---|---|
| BTC | `y_flee` | 3 133 | **0,712** | 1,41× |
| ETH | `y_flee` | 9 416 | **0,667** | 1,29× |
| BTC | `y_reject` | 6 618 | 0,629 | 1,21× |
| ETH | `y_reject` | 14 344 | 0,551 | 1,08× |

`y_flee` réplique BTC↔ETH (écart 0,045, les deux > 0,66). `y_reject` ne réplique
que partiellement.

### A.2 Ablation — identique sur les 4 cellules

| cran ajouté | ΔAUC |
|---|---|
| TAILLE seule | **0,50 – 0,54** (la magnitude ne prédit rien) |
| **+ PRÉSENCE** (occupancy, persistance, âge) | **+0,067 à +0,106** — le saut le plus gros |
| + FORME (pic/résidu, turnover) | +0,045 (BTC flee) à −0,007 (ETH reject) |
| + FLUX historique | −0,007 à +0,011 — marginal |

### A.3 Déciles de score, hors-échantillon

| | D10 | D9 | … | D2 | D1 | base |
|---|---|---|---|---|---|---|
| BTC | **81,9 %** (1,36×) | 80,5 % | … | 37,5 % | 28,6 % (0,47×) | 60,4 % |
| ETH | **86,7 %** (1,30×) | 80,5 % | … | 53,5 % | 40,7 % (0,61×) | 66,7 % |

Classement monotone. **Calibration : ETH propre (ECE 0,026), BTC non
(ECE 0,118).** Le score BTC s'utilise comme rang, pas comme probabilité.

### A.4 Effet du seuil de matérialité `FLEE_MIN_FRAC = 0,20`

| | avant | après | couverture |
|---|---|---|---|
| BTC | 0,690 | **0,712** | 68 % → 57 % |
| ETH | 0,646 | **0,667** | 83 % → 73 % |

Sans ce seuil, `retiré > tradé = 0` était vrai **mécaniquement** : le label
mesurait surtout « y a-t-il eu du volume ici ».

### A.5 Observation restée inexpliquée

Les détections les plus fortes sont des murs **vieux (210–260 min) et présents
à 100 %**. Cela **inverse** la lecture naïve « persistance = engagement = réel ».
Non tranché.

---

## B. Backtest économique (29/07) — entrée au contact, sortie 150 s

Coûts : 8 bp aller-retour + 1 bp de glissement = **9 bp à battre**.

### B.1 Directionnel — négatif sans ambiguïté

| stratégie | BTC net | ETH net |
|---|---|---|
| fader TOUS les murs | **−10,8 bp** | **−9,6 bp** |
| filtre : 10 % les plus solides | −10,4 bp | −10,3 bp |
| contrôle aléatoire, même n | −12,0 bp | −9,4 bp |

Mouvement brut moyen après contact : **−1,8 bp (BTC) / −0,6 bp (ETH)** — un
ordre de grandeur sous les frais. Toutes les stratégies perdent, très au-delà de
l'incertitude (|t| de 15 à 49, clusterisé par mur).

**Correction d'une formule répandue dans le dossier.** Le `README` de
`sandbox/detect` écrit « le filtre ne bat pas le tirage au sort ». Vérifié dans
le rapport source, c'est **faux au singulier** :

| filtre 10 % les plus solides | BTC | ETH |
|---|---|---|
| filtre | −10,38 bp | −10,28 bp |
| contrôle aléatoire, même n | −12,01 bp | −9,39 bp |
| **apport du filtre** | **+1,63 bp** | **−0,89 bp** |

Le filtre **bat** le tirage au sort sur BTC et **perd** sur ETH. L'énoncé honnête
n'est pas « il ne bat pas le hasard » mais **« son apport ne réplique pas entre
les deux symboles »** — ce qui, au regard de la règle de réplication BTC/ETH du
programme, suffit à ne rien en conclure. La conclusion finale ne change pas ;
l'argument qui y mène, si.

### B.2 Coût de traversée — c'est là que le signal est

| décile de score de fuite | fraction du mur exécutée | contacts avec la moindre exécution |
|---|---|---|
| D1 — jugé le plus **SOLIDE** | 0,501 (BTC) · 0,437 (ETH) | **31 %** · **39 %** |
| D10 — jugé le plus **FRAGILE** | 0,097 · 0,085 | **8 %** · **8 %** |

**Rapport 5,1× sur les deux symboles.** Vue robuste (au moins une exécution,
oui/non) : 4–5×.

**Deux réserves à ne pas escamoter.** (1) La médiane est **nulle dans tous les
déciles** : dans plus d'un contact sur deux, rien ne s'exécute. (2)
`f_absorb_contact` partage le terme `traded` avec le label — c'est l'AUC
**ré-exprimée** en unités économiques, **pas un second témoin indépendant**.

### ⚠ B.3 — Ce bloc entier n'a jamais été audité

`DETTE-20260803.md` §A1 le classe **dette la plus dangereuse du dossier** :

> Le backtest économique n'a jamais été audité, et **il tournait sur le rejeu
> défectueux**. [...] **Un négatif non audité qui ferme une piste.**

Le rejeu en cause (`prod_like_rows`) accumulait **4 mesures par ligne sur 10 s
avec 1 mise à jour d'EMA**, quand la production en accumule **5 sur 2,5 s avec
4 mises à jour**. Les −10,8 bp du §B.1 **et** le 5,1× du §B.2 sortent tous deux
de cette archive-là.

**Ne rien conclure de ce bloc sans l'avoir refait.** C'est la première des trois
tâches que la DETTE exige avant tout nouveau tir.

---

## C. Sonologie (29/07) — testée équitablement, négative

ΔAUC du cran SONOLOGIE sur les 4 cellules : **+0,007 · +0,007 · +0,002 · +0,000**.

Isolément, deux descripteurs portent pourtant un vrai signal — au-dessus de
`f_persist` :

| descripteur | BTC | ETH |
|---|---|---|
| `f_spec_centroid` | 0,566 | 0,592 |
| `f_spec_flatness` | 0,547 | 0,583 |
| `f_coh_neighbours` (cohérence locale) | 0,498 | 0,511 — **nulle** |

Ils n'ajoutent rien parce qu'ils **ré-encodent la persistance dans une autre
langue**. Les ajouter fait monter BTC (0,712 → 0,720) sans bouger ETH :
signature de sur-ajustement. **Non retenus.**

---

## D. Expériences D1–D5, E1–E2, P1–P2 (03-04/08)

| exp. | résultat | verdict |
|---|---|---|
| **E1** oracle | **+0,866 sur un monde nul** (rho vrai = 0) — fenêtres recouvrantes | circulaire, **retiré** |
| **E2** encadrement | **100 %** des instants encadrés, même à seuil 32× plus strict | pas un événement |
| **D1** fuite (`flee > 0,5`) | **99,28 %** des murs, fraction annulée 1,000 du p10 au p90 | dégénéré |
| **D2** v1 fuite à l'approche | **100 %** (bug de filtre de bande) · v2 : 26,7 % sur tous les murs | corrigé |
| **D4** la queue | mur du décile supérieur **approché** disparaît **12 à 17 points** plus souvent qu'un mur identique non approché — **16 cellules sur 16**, 2 jours | **le meilleur acquis du projet précédent** |
| | sur *tous* les murs l'effet est **inverse** : l'approche les fait tenir | deux populations, deux signes |
| **D5** qui pose la queue | un mur a 4 porteurs, le **1er en détient 99,7 %** ; **10 portefeuilles portent 97,7 %** de la masse, les mêmes d'un jour à l'autre | concentration extrême |
| **P1** la porte s'ouvre, le prix passe | 4 jours stables et convaincants | **retourné par P2** |
| **P2** les deux portes au même instant | **+0,81 bp**, IC `[−1,35 ; +2,96]`, **t = 1,19**, 1 jour sur 4 de signe inverse | contient zéro |
| | **83 à 89 % des instants voient les DEUX portes s'ouvrir** | ce n'est pas une porte qui s'écarte, **c'est le carnet entier qui se retire** — jamais regardé |

### Canal des portefeuilles

| mesure | valeur |
|---|---|
| persistance à une semaine | **+0,85**, p < 1 % sous 200 placebos |
| backtest exécutable | **négatif sur les 4 cellules et 5 horizons** — −6 bp par aller-retour |
| cause | gain brut 2,5 bp contre **7 bp de frais preneur** |
| sélection adverse | être servi par un **croiseur** coûte **+1,15 bp** de plus — 183 004 fills, t de 30 à 41 |
| persistance d'identité | 33,5 % des wallets de déc. 2025 tradent encore en août 2026 ; **41,9 %** parmi les plus fuyants |

---

## E. M1 — retrait asymétrique (04/08, `recherche`, 4 jours BTC)

### E.1 Le résultat, et l'effet de la réparation du nul

| jour | rho | ancien nul (largeur) | nouveau nul (largeur) | avant | après |
|---|---|---|---|---|---|
| 20251209 | −0,0364 | 0,0447 | 0,1021 | hors | **dans** |
| 20251210 | −0,0669 | 0,0438 | 0,0967 | hors | hors |
| 20251211 | **+0,0375** | 0,0419 | 0,1101 | hors | **dans** |
| 20251212 | −0,0140 | 0,0471 | 0,1284 | dans | dans |

```
AGRÉGÉ : jours 4 · rho_moyen −0,01991
         IC95 Student [−0,08993 ; +0,05011] · exclut_zero FALSE
         jours_du_signe_prédit 3
n_effectif : 274 → 195
```

**Les rho sont inchangés.** Ce n'était pas la mesure qui était fausse, c'était le
jugement porté sur elle. Trois jours « significatifs » sur quatre sont devenus un.

### E.2 Calibration du nul — la preuve directe

Protocole : apparier l'asymétrie d'un jour au rendement d'un **autre** jour
(48 paires indépendantes par construction, autocorrélation réelle préservée).

| nul | taux de rejet | nominal |
|---|---|---|
| **corrigé** (décalage circulaire) | **1/48 = 2,1 %** | 5 % |
| ancien (permutation i.i.d.) | **19/48 = 39,6 %** | 5 % |

**L'ancien contrôle se trompait 4 fois sur 10.**

### E.3 Puissance — la limite qui gouverne la lecture

Effet injecté d'amplitude croissante, 20251209 :

| amplitude | rho obtenu | détecté |
|---|---|---|
| a = 0,05 | +0,025 | non |
| a = 0,10 | +0,085 | **OUI** |
| a = 0,20 | +0,201 | **OUI** |

> **Seuil de détection : |rho| > ~0,06.** Les rho observés valent −0,036,
> −0,067, +0,038, −0,014 : ils sont **à la frontière**. La conclusion honnête
> n'est pas « M1 ne détecte rien » mais **« M1 est sous-dimensionné pour un effet
> journalier inférieur à |rho| = 0,06 »**.

---

## F. M2 — les porteurs ne gagnent pas quand leur mur cède (04/08, BTC, 3 jours)

### F.1 Le garde-fou a levé DEUX FOIS avant qu'une ligne ne sorte

| version de l'événement | fréquence | verdict |
|---|---|---|
| « la masse tombe sous 20 % en 10 min » | **82,47 %** | REFUSÉ |
| « elle fuit à l'approche » (cible de D2) | **84,58 %** | REFUSÉ |
| **« le prix approche le mur »** | **13,7 à 17,0 %** | accepté |

### F.2 Population

| jour | approches | fuite parmi elles | part du porteur dominant |
|---|---|---|---|
| 20251209 | 15,8 % | 79,3 % | 0,918 |
| 20251210 | 13,7 % | 84,6 % | 0,959 |
| 20251211 | 17,0 % | 84,3 % | 0,951 |

### F.3 Le résultat — signe prédit à l'avance, obtenu à l'envers

```
GAIN à 60 s          moyenne 3 j       IC95 Student        exclut 0
EVENEMENT              −96,62 $      [−178,3 ; −15,0]        OUI
PLACEBO_MUR           −140,79 $      [−203,8 ; −77,8]        OUI
PLACEBO_INSTANT        −56,12 $      [−137,1 ; +24,9]        non

GAIN à 300 s
EVENEMENT             −340,70 $      [−733,5 ; +52,1]        non
```

> `GAIN > 0` était prédit si le retrait profite à son opérateur. Il est
> **NÉGATIF** et l'intervalle exclut zéro à 60 s. **Hypothèse réfutée.**

**`net_median = 0` partout** : dans ~80 % des événements, le porteur du mur **ne
trade pas du tout** autour de l'approche. La moyenne est portée par une minorité,
et cette minorité perd.

Ce que ça ne dit pas : ce n'est pas un P&L (marque au marché `net × rendement`,
ni file d'attente, ni inventaire) ; 3 jours et 1 symbole ; et **l'absence de gain
n'établit pas l'absence d'intention** — voir le gain *évité* du §12.

---

## G. Contrôles de données (`verifie_donnee`, 20251209)

```
cohérence interne        photos 118 722 · carnets_croisés 0 · cadence_ms_médiane 1002
                         trous > 60 s : 1 · saut_de_mid_max 0,111 %
profond ⊃ carnet         écart_relatif_médian 2,16e-08 · p95 5,44e-08 · paliers_absents 0
masse contre ordres      paliers_comparés 57 456 · rapport_médian 1,0000
                         p10 0,986 · p90 1,0 · part_à_10 %_près 0,8781
transactions ds fourch.  n 982 406 · part_dedans 0,6026 · âge_photo_médian 84 ms
fills réconciliés        oid_distincts 559 548 · part_retrouvée 0,9545
```

**4,55 % des `oid` exécutés n'existent pas dans `hl_orders`** — ~25 000 ordres
exécutés sans aucun statut enregistré. C'est l'explication la plus probable du
`rapport_p10 = 0,986`. Rapporté sans seuil, donc sans conséquence à l'époque.

---

## H. Défauts d'instrument mesurés — l'ordre de grandeur des biais

C'est le tableau le plus utile de cette annexe : il dit **combien coûte** une
faute d'instrumentation, donc jusqu'où un résultat peut être déplacé par elle.

| faute | effet mesuré |
|---|---|
| `prod_like_rows` reconstruit depuis un livre vide | voit **11,6 % des paliers** et **78,5 % de la masse** → médiane de bande **32× trop haute** → **26 murs détectés là où il y en a 153** |
| `SNAP_BAND` 0,4 % contre `DIST_MAX` 0,8 % | le recorder voyait 63 % des murs mais **43,6 % de leur masse** |
| chauffe de 2 h au lieu de 8 h | masse des 5 premières heures **6,5 % trop basse**, et **asymétriquement** : bid −11,9 %, ask −2,5 % |
| nul par permutation i.i.d. | bande **2,2 à 2,7× trop étroite** → 3 jours « significatifs » sur 4 au lieu de 1 |
| `est_mur = 8 × médiane` | **29,16 %** des paliers classés murs, médiane **163 par instant** — contre 2,08 % et 12 avec `quantile 0,98` |
| fenêtres recouvrantes ignorées | erreur-type fausse d'un **facteur 5,5** |
| agrégat de côtés partagé | **472 continuités rompues sur 535** |
| ordre carnet/horloge inversé | **2 144 couples faux**, dont un à 11,5 M$ |
| palier vide laissé dans le carnet | **3,36 %** des photos fausses |
| `break` de fin de fenêtre absent | dernier seau à mid 92 654 au lieu de 90 388 |

> Aucune de ces fautes n'était visible dans le résultat. Toutes ont été trouvées
> en auditant l'instrument, jamais en regardant la sortie. **C'est la
> justification de la règle du §10.**

