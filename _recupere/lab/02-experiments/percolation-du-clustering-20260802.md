# Le clustering a PERCOLÉ — pourquoi la purge « améliore » l'AUC · 2026-08-02

_Diagnostic, aucun verdict. Scripts : `experiments/audit_pipeline.py` et
`experiments/audit_purge_why.py`, rejouables. Rien n'est réentraîné : les
prédictions archivées du jalon sont découpées, à modèle, graine et métrique
STRICTEMENT identiques — seule l'appartenance au groupe change._

## Le fait

À modèle identique, l'AUC est **plus haute** sur le test purgé que sur le test
complet — BTC 0,7032 contre 0,6370, ETH 0,6601 contre 0,6342, sur **14 folds
sur 16**. La purge devait empêcher le modèle d'être récompensé pour mémoriser
une identité. Il fait **mieux** là où il ne connaît personne.

## La cause : une composante géante

| BTC, groupe | lignes | clusters | plus gros cluster | top-10 |
|---|---|---|---|---|
| **VUS au train** | 56 480 | 466 | **54 575** | **97,0 %** |
| INÉDITS (purgés) | 3 346 | 1 468 | 1 443 | 46,9 % |

**Un seul cluster porte 96,6 % du groupe VUS** (ETH : 21 622 sur 22 047, soit
**98,1 %**). Les composantes connexes (wallet ∪ épisode-palier) se sont soudées :
les wallets récurrents relient tout à tout.

**Ce que fait la purge n'est donc pas d'écarter des acteurs connus — c'est de
casser cette masse en singletons.** Cluster médian : 3 lignes côté VUS, **1**
côté inédits.

## Conséquence sur les intervalles — l'anomalie s'explique

| groupe | paires | IC95 |
|---|---|---|
| VUS | **222 131** | [0,531 ; 0,755] |
| INÉDITS | **2 556** | [0,637 ; 0,753] |

**87 fois moins de données donnent un intervalle plus étroit.** Le bootstrap
tire des clusters avec remise : quand un cluster pèse 96 %, chaque tirage
revient à jouer sa présence à pile ou face. La largeur ne mesure plus
l'incertitude d'estimation, elle mesure la présence d'un bloc.

Le plafond de 200 paires par couple de clusters mord **90,1 %** côté VUS contre
**25,3 %** côté inédits ; les paires par cluster passent de **476,7 à 1,7** —
deux ordres de grandeur.

## La population inédite est aussi plus facile (effet second, réel)

| | VUS | INÉDITS |
|---|---|---|
| P(y>0) | 0,093 | **0,121** |
| E[y \| y>0] | 0,469 | **0,774** |
| écart-type de y | 0,197 | **0,283** |
| y au p90 | **0,000** | 0,195 |

Chez les VUS, **90 % des lignes ont une cible exactement nulle**.

## Ce qui ne peut PAS être conclu

L'hypothèse « les acteurs récurrents sont intrinsèquement plus durs à
prédire » (+0,062 d'écart) est **inséparable** des deux effets ci-dessus sur
ces données. Elle n'est ni établie ni écartée.

## Le précédent manqué

Cette percolation avait été repérée le **30/07**. L'annexe de
`P0-FRAG-porte-preenregistree.md` la nomme : « *exactement la composante géante
mesurée le 30/07 sur l'union-find du jalon, en pire* », et pose le correctif —
fermer un épisode par **coupure de seuil**, jamais par simple chevauchement.

**Ce correctif n'a été appliqué qu'à la conception de P0-FRAG.** Le jalon a
continué de tourner avec son clustering percolé, jusqu'au verdict.

## Portée

Le verdict C du jalon **reste rendu**. Mais il est désormais établi que son
unité statistique s'était effondrée en un bloc unique, que la purge fragmentait
accidentellement, et que ses intervalles étaient pilotés par la présence d'un
seul cluster. **Le défaut est en amont de la purge, pas dedans.**

Toute nouvelle certification doit d'abord réparer le clustering. Le faire après
avoir vu ces chiffres serait un ajustement post-hoc : la nouvelle règle doit
être écrite et gelée avant le prochain run.
