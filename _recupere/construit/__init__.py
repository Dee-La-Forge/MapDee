"""Fabrication des parquets dérivés depuis l'archive brute OPEN BOOK.

Ce paquet est **porté** de `sandbox/detect/` le 04/08/2026. C'est la seule
exception à la règle « rien de l'ancien dépôt sauf la donnée » (`QUESTION.md`),
et elle est motivée : sans les constructeurs, `deep` reste figé à 5 jours de BTC,
ce que l'audit du 04/08 a identifié comme le verrou dominant de la recherche —
M1 est aveugle sous |rho| = 0,06 et ne peut pas trancher avec si peu.

    openbook.py   lecture du format binaire brut (statuts, diffs, transactions)
    grille.py     `_nice` et `BIN_REL` — UNE implémentation de la grille
    jour.py       hl_orders + hl_book + deep, pour un (jour, symbole)
    fills.py      hl_fills, pour un (jour, symbole)

Ce qui a changé au portage, et rien d'autre :

  * les chemins (`SANDBOX` -> racine du dépôt, sortie vers `data/openbook`) ;
  * les imports `gondetect.*` remplacés par `construit.*`, sans réécriture ;
  * `_refuse_si_gele` re-documenté pour CE dépôt (voir `jour.py`).

Les commentaires d'origine sont conservés **mot pour mot**. Ils décrivent des
fautes mesurées et leur coût ; les réécrire perdrait la seule chose qui
empêche de les refaire.
"""
