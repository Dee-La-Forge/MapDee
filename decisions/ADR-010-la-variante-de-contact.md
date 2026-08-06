# ADR-010 — La variante de « contact » : exécution ou meilleure limite

**Statut : EN RÉDACTION** — la décision appartient à Meddy.
Écrite le 06/08/2026, à la lecture de la 3ᵉ passe C2 (S3″).

## Le fait mesuré

Les deux définitions candidates de C0 §4 ne coïncident PAS (23,9 %/26,7 %
à 1 s, délai médian −18 s/−8 s) : la première exécution sur un mur précède
généralement son passage en meilleure limite — les balayages mangent la
profondeur avant que le front n'arrive. Ce sont deux physiques.

## La recommandation (une, assumée)

**Variante EXÉCUTION** : contact = première transaction dont le prix
touche le palier du mur. Trois raisons : (1) c'est l'événement PRÉCOCE —
pour le produit (« mon mur va-t-il être mangé ? »), le premier dollar
exécuté compte plus que la topologie du front ; (2) c'est la moins chère
(une jointure aux trades, pas de reconstruction de front) ; (3) elle est
désormais mesurable proprement (ADR-009 : prix touchés, 0 perte de
jointure). La variante topologique reste publiée dans les JSON de la 3ᵉ
passe — rien n'est perdu si un chantier futur en a besoin.

## Ce que l'acceptation déclenche

La fermeture de B7 EN BLOC — les trois lignes s'écrivent ensemble dans
`03` avec leurs sources :
* **mur** : `mag ≥ M′ × médiane(voisinage ±0,05 % du mid)`, persistance
  ≥ P′ — M′ = 423,5 (BTC) / 175,4 (ETH), P′ = 6/4 photos (C2 2ᵉ passe) ;
* **contact** : première transaction au palier du mur (C2 3ᵉ passe, S3″) ;
* **bande d'étude** : ±0,0925 % (BTC) / ±0,1451 % (ETH) du mid (S4″,
  quantile 0,999 du flux exécuté).
Puis : les extracteurs A2 (OFI au mur) et B4 (absorption au contact)
deviennent écrivables — leurs définitions existent enfin.
