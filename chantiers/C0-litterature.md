# C0 — La littérature : leurre, liquidité cachée, absorption

> **Chantier ouvert le 05/08/2026.** Sa sortie alimente **B7** — les
> définitions de « mur », « contact », « bande d'étude » — et les définitions
> opératoires des comportements (annulé / mangé / rechargé, `05` §9.3).
>
> **Régime, et honnêteté du document** : ce qui suit est une **synthèse
> d'orientation** écrite de mémoire de la littérature, pas une lecture. Chaque
> référence est à **relire à la source avant de fermer quoi que ce soit** — une
> citation de mémoire a le statut d'une piste, jamais d'un fait. Les
> définitions proposées sont toutes **PROPOSÉ** : `05` §9.3 impose la
> littérature **puis** l'observation des trajectoires brutes sur le jour de
> banc, dans cet ordre, et B7 ne se ferme qu'après les deux.

---

## 1. Le leurre (spoofing / layering)

**Ce que dit le droit** — la seule définition qui fasse autorité hors
académie : le Dodd-Frank Act (§747, 7 U.S.C. §6c(a)(5)(C)) définit le spoofing
comme *« bidding or offering with the intent to cancel the bid or offer before
execution »* — l'**intention d'annuler avant exécution**, pas l'annulation
elle-même. Le règlement européen MAR (596/2014, annexe II et règlement délégué
2016/522) liste les indicateurs du layering : ordres **sans intention
d'exécution**, à des prix étagés, **du côté opposé** à l'ordre qu'on veut faire
exécuter, annulés après l'exécution de celui-ci.

**Ce que dit la recherche empirique** — les traits mesurables récurrents des
cas documentés (Coscia 2015, Sarao ; études sur données coréennes et
taïwanaises, p. ex. Lee, Eom & Park sur le KRX) :

* **asymétrie de côté** : grosse masse affichée d'un côté, exécution de l'autre ;
* **durée de vie courte** conditionnée à l'approche du prix — l'ordre est
  retiré quand le risque d'exécution devient réel ;
* **taille anormale** relative à la profondeur locale (c'est ce qui rend le
  leurre visible — il doit être vu pour agir) ;
* **taux ordre/exécution extrême** — mais **c'est le métier d'un teneur de
  marché aussi** : `03` §E le dit déjà, un discriminant qui désigne les teneurs
  ne désigne rien. La littérature de surveillance bute exactement là.

**Ce qui en découle pour nous** : le leurre n'est pas définissable par
l'annulation seule ni par le taux d'annulation (interdit comme discriminant,
`03` A/B). La forme défendable est **conditionnelle à l'approche du prix** :
masse posée hors contact, retirée *quand le prix s'approche*, jamais exécutée.
C'est la forme injectée par le générateur de C9 (D4).

## 2. La liquidité cachée (iceberg / recharge)

**Littérature établie** — les ordres iceberg sont le mécanisme le mieux
documenté du lot : Esser & Mönch (« The navigation of an iceberg »), Frey &
Sandås (impact des icebergs dans le carnet), De Winne & D'Hondt (Euronext),
Bessembinder, Panayides & Venkataraman (coût/bénéfice de cacher). Constats
robustes à travers les places :

* la partie visible (*peak*) se **recharge au même prix** après exécution, à
  montant régulier et délai bref — c'est **exactement la signature de B3** ;
* la détection publique passe par les **cycles exécution → recharge**, jamais
  par une observation directe (la partie cachée n'est pas diffusée) ;
* les exécutions contre iceberg **dépassent la masse affichée** au moment de
  l'exécution — sur nos données Binance, c'est lisible dans la mesure C8.2 :
  des fenêtres où `e > masse affichée` existent (0,06-0,11 %), et une partie
  d'entre elles n'est pas du désalignement mais de la liquidité cachée. **À ne
  pas trancher sans mesure** — les deux causes se ressemblent.

**Ce qui en découle** : « recharge » se définit par un **cycle** (exécution au
palier, retour de la masse à un niveau comparable, délai court, répétition),
pas par un état. Les paramètres du cycle (délai, tolérance de montant, nombre
minimal de répétitions) se lisent sur le jour de banc — pas dans la
littérature, qui donne la forme et non les constantes de cette place.

## 3. L'absorption

C'est le terme le **moins standardisé** des trois — la littérature académique
parle de **résilience** (Degryse et al. ; Large, « Measuring the resiliency of
an electronic limit order book ») et d'**impact** (Bouchaud, Farmer & Lillo ;
Obizhaeva & Wang pour la dynamique offre/demande). Deux quantités voisines et
distinctes :

* **absorption au contact** (notre B4) : la masse d'un palier est consommée par
  exécutions **sans que le prix ne le traverse** — flux exécuté élevé, déplacement
  faible. Le pendant littérature est l'écart entre **impact virtuel et impact
  réel** (Farmer et al., « What really causes large price changes ») : le carnet
  affiché prédit mal le déplacement, parce que la liquidité se reconstitue ;
* **résilience** (notre B2) : la **vitesse de reformation** après consommation.

La distinction absorption/résilience recoupe la décomposition **e/r/a** d'A3 —
mangé sans céder (e élevé, masse stable) contre rechargé après avoir cédé.
C'est pour ça qu'A3 est le socle : les deux notions s'écrivent dans ses termes.

## 4. Les trois définitions de B7 — formes proposées, constantes à mesurer

Règle commune, tirée de la méthode du projet : **une forme se choisit dans la
littérature, une constante se lit sur le jour de banc** — jamais l'inverse, et
jamais après avoir vu un résultat d'épreuve.

### « mur » — PROPOSÉ

Un palier de la bande dont la masse est **anormale relativement à sa
localité** et qui **persiste** :

```
mur(k, t) :  mag(k, t) ≥ M × médiane_locale(t)   pendant ≥ P photos
```

`médiane_locale` = médiane des masses de la bande à la même photo, même côté.
La littérature ne fournit pas de « mur » canonique — elle fournit la leçon que
la taille **absolue** ne se compare pas entre symboles ni entre régimes, d'où
la forme relative (même logique que `taille_p99_sur_med` des fiches C5).
**M et P se lisent sur les distributions du jour de banc.**

### « contact » — PROPOSÉ

Deux variantes à départager par l'observation (`05` §9.3 en exige la
confrontation, pas le choix a priori) :

* **contact-exécution** : première exécution au palier (`e > 0` au sens d'A3) ;
* **contact-topologique** : le palier devient la meilleure limite de son côté.

La littérature du premier passage et des files (first passage, queue position)
utilise les deux selon la question ; la nôtre — « le mur tient-il ? » — se
déclenche au moment où tenir **coûte** quelque chose, ce qui plaide pour
contact-exécution. Le jour de banc dira si les deux divergent assez pour que le
choix importe ; s'ils coïncident à > 95 %, le débat est clos par la mesure.

### « bande d'étude » — PROPOSÉ

**Une définition par procédure, pas un nombre** : la bande est la distance au
mid qui contient **une fraction déclarée du flux exécuté** (proposé : 99,9 %),
mesurée sur le jour de banc, par symbole.

Fondement dans nos propres données : la mesure C8.2 montre `e = 0` au-delà des
premiers déciles de distance des deux côtés — l'attente pré-enregistrée « les
exécutions n'ont lieu qu'au contact » est confirmée. Une bande définie par le
flux exécuté est donc **stable et opposable**, là où la bande héritée (`±0,3 %`
de l'ancien ADR sans autorité) était une hypothèse. La nappe `deep` à ±10 %
garantit qu'on peut la calculer **après coup** quelle que soit la valeur — on
rétrécit toujours à la lecture.

## 5. Ce que C0 doit encore lire — la file, par priorité

1. **Icebergs/recharge** : Esser & Mönch ; Frey & Sandås ; De Winne & D'Hondt —
   parce que B3 est au rang 1 de l'ordre de passage de `03` ;
2. **Impact et absorption** : Farmer, Gillemot, Lillo, Mike & Sen (virtual vs
   actual impact) ; Bouchaud, Farmer & Lillo (Trades, Quotes and Prices) ;
   Large (résilience) — pour B2/B4 et la lecture d'A3 ;
3. **Spoofing empirique** : Lee, Eom & Park (KRX) ; Cartea, Jaimungal & Wang
   (modèle) ; les ordonnances CFTC/FCA des cas Coscia et Sarao (les faits y
   sont décrits en langage opérationnel, colonnes et délais) — pour D4/C9 et le
   typage ;
4. **OFI** : Cont, Kukanov & Stoikov — la fiche A1 en descend directement ;
5. **Files et position** : Moallemi & Yuan ; Huang, Lehalle & Rosenbaum
   (modèle queue-réactif — c'est l'option de montée en gamme de D3/C9).

**Règle de sortie du chantier** : une définition de B7 ne se ferme que quand sa
forme est adossée à une source **relue**, sa constante à une mesure du jour de
banc, et sa ligne écrite dans le document qui la porte (`03` ou C3) — dans cet
ordre, daté, commité.
