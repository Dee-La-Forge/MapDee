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
académie : le Dodd-Frank Act (§747, 7 U.S.C. §6c(a)(5)(C) — **réf. de mémoire, à
vérifier** ; un texte de loi se contrôle en une minute) définit le spoofing
comme *« bidding or offering with the intent to cancel the bid or offer before
execution »* — l'**intention d'annuler avant exécution**, pas l'annulation
elle-même. Le règlement européen MAR (596/2014, annexe II et règlement délégué
2016/522 — **réf. de mémoire, à vérifier**) liste les indicateurs du layering : ordres **sans intention
d'exécution**, à des prix étagés, **du côté opposé** à l'ordre qu'on veut faire
exécuter, annulés après l'exécution de celui-ci.

**Ce que dit la recherche empirique** — les traits mesurables récurrents des
cas documentés (Coscia 2015, Sarao ; études sur données coréennes et
taïwanaises, p. ex. Lee, Eom & Park sur le KRX — **réf. non relues**) :

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
Bessembinder, Panayides & Venkataraman (coût/bénéfice de cacher) — **réf.
non relues, toutes**. Constats robustes à travers les places :

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
an electronic limit order book » — **réf. non relues**) et d'**impact** (Bouchaud, Farmer & Lillo ;
Obizhaeva & Wang pour la dynamique offre/demande — **réf. non relues**). Deux
quantités voisines et distinctes :

* **absorption au contact** (notre B4) : la masse d'un palier est consommée par
  exécutions **sans que le prix ne le traverse** — flux exécuté élevé, déplacement
  faible. Le pendant littérature est l'écart entre **impact virtuel et impact
  réel** (Farmer et al., « What really causes large price changes » — **réf.
non relue**) : le carnet
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

## 5 pré. LES RÈGLES DU CHANTIER — écrites le 06/08 AVANT tout balayage supplémentaire
(audit externe du 06/08, critiques 1-3 — toutes fondées)

* **Tarissement** : le chantier se clôt après **DEUX balayages consécutifs**
  ne produisant **aucune famille dont la ligne « à l'exécution » peut être
  ÉCRITE** (un balayage sec peut avoir mal cherché — audit du 06/08) — le critère qui
  a écarté des disciplines entières dans `03`. « J'ai fait N balayages »
  n'est pas un critère (`06` §7).
* **Compte par vagues** : la **vague 1 = 16 candidats, gelée le 05/08** —
  aucune famille de C0 n'y entre, jamais. Les familles instruites ici
  forment la **vague 2**, dont le compte gèlera **avant son premier calcul**,
  à la clôture de C0 par tarissement — pas au jour du dernier É4.
  **Le FDR est contrôlé PAR VAGUE (q = 10 % chacune), PAS globalement** :
  avec W vagues, le taux global attendu dérive vers ~W × 10 % — ce nombre
  et W sont publiés avec tout résultat (audit du 06/08, reste n° 1 :
  déclarer vaut mieux que diluer).
* **Pas de ligne, pas de compte** : une famille sans ligne « à l'exécution »
  écrite **ici** n'entre dans aucun compte et ne coûte de puissance à
  personne. « É0 tranchera » n'est pas une ligne — c'est un report qui
  inverse l'échelle des coûts (`05` §4).

## 5 bis. Familles signalées par Meddy (06/08/2026) — pointage contre le catalogue

Passage en revue d'une liste de ~25 familles : la majorité est déjà au
catalogue sous son représentant fondu (files d'attente → B1/B5/E1 ·
percolation → D2 · phénomènes critiques/susceptibilité → D1/A5/F5 ·
information/spectral → C1 · Mori-Zwanzig → A5 · Lévy/fBm → C3 ·
Ising/SOC → D1/D2 — voir Annexe B de `03`). **Trois absences réelles, à
instruire ici avant toute fiche** :

1. **science des réseaux sur les wallets** (centralité, communautés, motifs)
   — côté vérité, prolongement du bloc E, nourri par C5 ;
2. **information mutuelle / transfert d'entropie comme features** (la
   métrique du banc reste celle d'`ADR-001`) ;
3. **écart à un carnet de référence** (maximum d'entropie, distance de
   Wasserstein) — risque de redite élevé avec C1/C2, É0 tranchera.

**Second balayage (même jour) — les angles morts d'un catalogue venu de la
physique**, absents de la liste de Meddy comme du catalogue :

4. **le canon de la microstructure financière** : PIN/VPIN, lambda de Kyle,
   spreads effectifs/réalisés, sélection adverse — la famille « qui sait
   quelque chose ? » ;
5. **la mécanique des perpétuels** : funding, open interest, **liquidations
   forcées** — le carburant des cascades sur ce marché précis, publié par
   Binance, porté par Hyperliquid, et invisible depuis la physique ;
6. **le lead-lag inter-venues et inter-symboles** — la capture simultanée
   existe déjà. **Ligne à l'exécution (écrite)** : si une place mène
   l'autre de Δt, poster/retirer sur la retardataire AVANT la
   propagation — le retard est le rabais ;
7. **l'horloge volume** (temps-transaction) — transversal, aussi un axe de
   robustesse pour É3 ;
8. **DMD/Koopman** — **SANS LIGNE « à l'exécution » écrite → hors compte** ;
   et c'est nommément la famille déjà payée une fois (sonologie). Elle
   n'entrera qu'avec une ligne, pas avec une promesse ;
9. côté vérité : **inventaire des teneurs** (E7 naturel) et **métaordres /
   loi en racine carrée** — exigent l'identité, notre avantage comparatif.

**Troisième balayage (06/08, sur consigne « ne rien laisser au hasard ») —
par les données possédées et par la surveillance de marché, pas par les
théories** :

10. **le flux REJETÉ** — 70 Go d'ordres rejetés déjà sur disque
    (`*_rejected_202512.tar.xz`), l'ombre des intentions qui n'atteignent
    pas le carnet — exploité nulle part, possédé ici. **Instruit le 06/08
    contre le SCHEMA.md** : chaque enregistrement porte wallet, prix,
    taille, côté ET le motif — cinq capteurs s'y accrochent :
    `badAloPxRejected` = courses perdues des makers (intention + vitesse
    par wallet) · `iocCancelRejected` = agression insatisfaite (invisible
    de la bande des transactions) · `perpMarginRejected`/`perpMaxPosition`
    = stress de marge, capteur AMONT des liquidations (famille n° 5/11) ·
    et dans le flux ACCEPTÉ déjà scanné : `selfTradeCanceled` = marqueur
    moteur du wash-adjacent (n° 13 trouve son code), `scheduledCancel`/
    `triggered` = empreintes d'outillage des algos. Aucune littérature
    établie — les bourses ne publient jamais ce flux ;
11. **divergence oracle/mark ↔ carnet** — le déclencheur mécanique des
    liquidations (complète la famille perpétuels n° 5) ;
12. **taille moyenne d'ordre au palier** (`mag/n` — la colonne `n` de `deep`
    est déjà extraite) : l'ombre publique de la fragmentation E3, promue
    candidate ;
13. vérité : **wash-trading/self-fills** (même wallet des deux côtés — une
    jointure) et **signatures de cadence par wallet** (empreintes d'algos,
    C5 étape 2) ;
14. **intensité de messages par palier** (quote stuffing — le voisin public
    d'A6, sans estimation Hawkes) ;
15. **détection séquentielle de ruptures** (CUSUM/SPRT — la surveillance
    industrielle, distincte de D1) ;
16. **dépendance de queue entre côtés** (copules) — **SANS LIGNE
    écrite → hors compte en l'état** (le risque de redite s'ajoute) ;
17. **contrôle F manquant : saisonnalité intrajournalière** — pas une
    feature, une désaisonnalisation due à toute grandeur à ligne de base.

**Quatrième balayage (06/08, ~02 h) — par l'adversaire et par le contexte** :

18. **stop-hunting avec vérité** — le code `triggered` (9) donne la carte
    des stops réellement déclenchés ; croisée avec l'agression qui pousse le
    prix vers eux : le mécanisme le plus raconté du crypto, jamais mesuré
    proprement faute de déclenchements — possédés ici ;
19. **le consensus des 7 places** — OKX, Bybit, Coinbase dorment dans le
    store du recorder : mid consensus, écart idiosyncratique par venue,
    **migration de profondeur** entre carnets ;
20. **allumage de momentum** — rafale → déclenchements → retournement : les
    trois maillons sont dans nos données (agression, `triggered`, marge) ;
21. **prix ronds** — l'agglutination comportementale aux nombres ronds,
    documentée depuis des décennies, invisible depuis la physique, triviale
    (`k` modulo la grille) ;
22. **asymétrie du temps / effet Zumbach** — la vol grossière passée prédit
    la fine future, pas l'inverse ; l'intention est irréversible, le bruit
    non : retourner le film du carnet et mesurer ce qui change ;
23. **mémoire longue des signes d'échange** — le fait le plus robuste de
    l'économophysique (l'ombre des métaordres), sans identité requise, et
    ses ruptures comme régime ;
24. **le contexte en cadre G** — proximité du funding, régime de vol,
    distance aux grappes de liquidation : des CONDITIONNEURS déclarables
    par les fiches, pas des candidats ;
25. **la part sombre locale** (question de Meddy, 06/08) — la fraction du
    flux exécuté non expliquée par la masse affichée, par palier et par
    fenêtre : la trace mesurable des icebergs, dérivable des termes d'A3,
    et **déjà entr'aperçue par C8.2** (fenêtres à `e > masse affichée`).
    À porter aussi au cadre : l'asymétrie de transparence entre le côté
    vérité (Hyperliquid, 100 % lit) et le côté produit (Binance, icebergs
    + OTC autour) est une facette de H2 à écrire ; et le carnet n'est pas
    tout le marché (limite de périmètre, cadre G). Précision du 06/08 :
    l'OTC crypto est PLUS sombre que les dark pools actions (aucune
    impression post-trade), mais son hedging traverse nos carnets — pour
    A1/A3 il apparaîtra comme choc de flux sans cause visible.
    **Corrigé le 06/08 (audit, critique 5)** : la case « résidu » du
    typage type des MURS irrésolus, pas des événements exogènes — y
    verser l'OTC la rendrait illisible. L'OTC est donc **déclaré hors
    périmètre au cadre G**, avec son propre marqueur d'événement
    exogène si un jour on veut le compter. **Sur la « détection » (06/08)** : le hors-carnet ne
    se détecte pas, il s'infère — par COMPOSITION de familles déjà
    instruites (n° 9 métaordres, n° 20 allumage, résidus d'A5) et du
    marqueur exogène du cadre G — PAS de la case résidu du typage,
    corrigé deux fois le 06/08 — un « détecteur de dark » séparé serait une redite qu'É0
    fondrait. Le seul levier matériel neuf : **capturer les bandes de
    blocs drapeautés** (Deribit/Paradigm, OKX) — un flux de plus au
    recorder, décision de production **chez Meddy**.

## 5 quater. L'ÉTAT DU COMPTE DE LA VAGUE 2 — la population entière, marquée
(audit du 06/08, reste n° 2 : « par marque, pas par déduction du lecteur »)

**Cette table fait foi.** Le compte de la vague 2 = les familles [LIGNE
ÉCRITE] au moment du gel — les autres n'y entrent pas, quel que soit leur
intérêt, tant que leur ligne n'est pas écrite ici.

| n° | famille | statut | ligne « à l'exécution » |
|---|---|---|---|
| 1 | réseaux de wallets | **VÉRITÉ — hors compte** | fabrique la vérité, ne s'affiche pas |
| 2 | information mutuelle en feature | **SANS LIGNE — hors compte** | — |
| 3 | écart à un carnet de référence | **SANS LIGNE — hors compte** | — |
| 4 | PIN/VPIN, Kyle, spreads | **LIGNE ÉCRITE** | un flux informé élevé annonce le déplacement — ne pas poster contre lui, traverser avant |
| 5 | perpétuels (funding, OI, liquidations) | **LIGNE ÉCRITE** | une grappe de liquidations devant soi = coût de traversée explosif et accélération mécanique — réduire, ou traverser avant la grappe |
| 6 | lead-lag inter-venues/symboles | **LIGNE ÉCRITE** | poster/retirer sur la place retardataire avant la propagation — le retard est le rabais |
| 7 | horloge volume | **MÉTHODE/ROBUSTESSE — hors compte** | axe d'É3, pas une grandeur |
| 8 | DMD/Koopman | **SANS LIGNE — hors compte** | — (sonologie déjà payée) |
| 9 | inventaire des teneurs · métaordres | **VÉRITÉ — hors compte** | fabrique la vérité |
| 10 | flux rejeté (5 capteurs) | **VÉRITÉ — hors compte** (reclassé à É1, audit du 06/08 : « les bourses ne publient jamais ce flux » — donc Binance non plus ; c'est la meilleure trouvaille du chantier, ET une trouvaille de fabrique de vérité) | — |
| 11 | divergence oracle/carnet | **LIGNE ÉCRITE** | l'écart oracle-carnet précède les liquidations mécaniques — ne pas poster sur leur chemin |
| 12 | taille moyenne d'ordre au palier | **VÉRITÉ — hors compte** (reclassé à É1 : `FAITS` §9 porte déjà le verdict — « utilisable pour fabriquer la vérité, non affichable », `n` absent de la profondeur Binance. Réouverture possible par le test d'équivalence de `FAITS` §9.2 — une heure, zéro donnée de marché) | — |
| 13 | wash/self-fills · cadences | **VÉRITÉ — hors compte** | fabrique la vérité |
| 14 | intensité de messages (stuffing) | **SANS LIGNE — hors compte** | — |
| 15 | CUSUM/SPRT | **MÉTHODE — hors compte** | outillage de détection, pas une grandeur |
| 16 | copules de queue | **SANS LIGNE — hors compte** | — |
| 17 | saisonnalité intrajournalière | **CONTRÔLE F — hors compte par nature** | — |
| 18 | stop-hunting (via `triggered`) | **SOUS CONDITION — hors compte** (É1 : `triggered` est un code Hyperliquid, Binance ne publie pas ses déclenchements — « une approximation non démontrée compte comme ne traverse pas », C8 §3) | (ligne écrite, en attente de la démonstration Binance) |
| 19 | consensus des 7 places | **LIGNE ÉCRITE** | une venue décrochée du consensus se recale — le sens du recalage est connu d'avance |
| 20 | allumage de momentum | **SOUS CONDITION — hors compte** (même dépendance à `triggered` que la n° 18 — la « carte des grappes » n'existe pas côté Binance sans démonstration) | (ligne écrite, même condition) |
| 21 | prix ronds | **LIGNE ÉCRITE** | les murs aux prix ronds attirent et tiennent autrement — le coût de poster derrière change avec le palier |
| 22 | asymétrie du temps / Zumbach | **SANS LIGNE — hors compte** | — |
| 23 | mémoire longue des signes | **LIGNE ÉCRITE** | une persistance de signes élevée signale un métaordre en cours — l'impact continue, traverser tôt coûte moins |
| 24 | contexte (cadre G) | **CADRE — hors compte par nature** | conditionneurs, pas candidats |
| 25 | part sombre locale | **LIGNE ÉCRITE** | là où la part sombre est haute, la taille traversable dépasse l'affiché — le carnet ment par défaut, en mieux |

**Compte FERME de la vague 2 : 8 familles** (4, 5, 6, 11, 19, 21, 23, 25) —
É1 passé sur la population le 06/08 (audit) : les n° 10 et 12 sont de la
fabrique de vérité, les n° 18 et 20 attendent leur démonstration de
traversée (« une approximation non démontrée compte comme ne traverse
pas »). Douze au lieu de huit aurait resserré le seuil BH de chaque
candidat d'un tiers, pour des familles qui ne traverseront jamais. Gel au
tarissement de C0, avant tout calcul de vague 2 — et É0 en fondra
peut-être encore.

Entrée au banc uniquement par fiche complète (ligne « à l'exécution »
obligatoire), et tout ajout **rouvre le compte D10 et le dit**. La TDA reste
écartée, porte ouverte au premier énoncé actionnable.

**Règle de sortie du chantier** : une définition de B7 ne se ferme que quand sa
forme est adossée à une source **relue**, sa constante à une mesure du jour de
banc, et sa ligne écrite dans le document qui la porte (`03` ou C3) — dans cet
ordre, daté, commité.
