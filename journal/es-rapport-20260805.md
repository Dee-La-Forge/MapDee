# ÉS — rapport de la campagne du banc synthétique

> 05/08/2026. Protocoles pré-enregistrés avant chaque mesure :
> `harnais/es_campagne.py` (v1, hash `4800507`) → `_v2.py` (`6996bf6`) →
> `_v3.py` (`ef2aab9`) → `_v4.py` (`b4b72e7`, la composition finale).
> Chiffres bruts : `journal/es-campagne*-20260805.json`, logs à côté.
> Barre d'admission : **amplitude plausible = 2,0 × la masse médiane du
> voisinage** (`ADR-004`, déclarée avant toute mesure de plancher valide).

## 1. Les verdicts, d'abord

| détecteur | bras nul (graines neuves) | plancher | admission |
|---|---|---|---|
| **absorption** | propre (moy −0,002, FP 1,3 %) | **0,5×** | **ADMIS** à consommer des jours de marché |
| **recharge** | propre (moy −0,000, FP 1,9 %) | **1,0×** | **ADMIS** |
| **leurre** | propre (moy −0,14, FP 0 %) | **8,0×** | **ÉCARTÉ** — plancher > 2,0 (`ADR-004`) |

**La conséquence qui compte pour le produit** : sur données réelles, un
« aucun leurre trouvé » produit par cette méthode **ne voudra rien dire** —
elle est aveugle sous 8× la masse locale. Les négatifs d'absorption et de
recharge, eux, seront interprétables jusqu'à 0,5× et 1,0×. C'est exactement
la distinction qu'`05` §8 exige de pouvoir faire, et elle a coûté zéro jour
de marché.

## 2. Quatre itérations, chacune tranchée par son bras nul

| | statistique | bras nul | sort |
|---|---|---|---|
| **v1** | masse au palier visé / médiane de toute la bande | ρ⁰ jusqu'à 0,57, **FP 100 %** | disqualifiée — artefact d'**ancrage** (le lieu choisi à T0 est mécaniquement gonflé pendant la fenêtre) |
| **v2** | normalisée par les voisins à **même distance du mid courant** | leurre/recharge propres ; absorption ρ⁰ = **−0,38** | disqualifiée — artefact du **contact** (le palier au contact est appauvri par les exécutions relativement à ses voisins) |
| **v3** | v2 + centrage sur nul appris (coupe 16/16) | absorption réparée (FP 0,4 %) ; leurre/recharge **cassés** (FP 27 %/13 % — soustraire un μ⁰ bruité à qui n'a pas de biais ajoute de la variance) | disqualifiée comme méthode uniforme |
| **v4** | **composition par mécanisme** — v2 nue pour leurre/recharge, centrée pour absorption — validée sur **32 graines jamais vues par v1-v3** | **3/3 propres** | **retenue** — les planchers du §1 sont les siens |

Une campagne annulée en amont pour **vice d'instrument** (générateur : injection
dimensionnée sur la mauvaise médiane + carnet hors régime — corrigé, testé,
`journal/es-campagne-20260805-ANNULEE-vice-instrument.log`).

## 3. Les deux résultats transverses (campagne 2, volets valides)

**La stabilité du Spearman partiel — l'incertitude n° 1 d'`ADR-001` est
réelle.** À 300 observations/jour, l'estimateur dérive vers le haut quand le
bloc de contrôle grandit : +0,15 de biais à 20 contrôles (0,25 → 0,40,
monotone). L'ordre de grandeur est ~k/n : négligeable sur un vrai jour à 10⁵
observations, disqualifiant à 300. **Règle à porter dans É4 avant le premier
calcul réel** (par mise à jour d'`05`, mécanisme du gel) : *n observations
par jour ≥ 100 × la taille du bloc de contrôle*, vérifié par le préflight.

**La puissance en jours de la règle d'É4** (Student bilatéral 5 %) :

| effet d | jours pour 80 % de puissance |
|---|---|
| 2,0 | 5 |
| 1,5 | 6 |
| 1,0 | 10 |
| 0,5 | **34** |

Avec les **8 jours** d'exploration de la tranche 1, seuls les effets d ≳ 1,2
sont détectables. Les effets mesurés à ÉS près des planchers sont dans la
zone d ≈ 0,9-1,3 : **le banc réel sur 8 jours ne verra que le net.** La
tranche 2 (8 jours de plus) descend la barre vers d ≈ 0,75. À arbitrer quand
elle s'ouvrira ; aucun changement de seuil n'est proposé ici.

## 4. Limites, écrites avant et pendant — aucune découverte après

* **méthode informée du lieu** : les planchers sont des bornes **optimistes**.
  Un détecteur aveugle au lieu fera moins bien ; l'écart se mesurera sur les
  vrais candidats ;
* **quatre itérations de méthode ont précédé le verdict** : risque de
  sur-ajustement méthodologique, borné par des verdicts de nul rendus à
  chaque fois sur graines non réutilisées, et un verdict final sur graines
  neuves — mais pas nul ;
* **le générateur est pauvre par construction** (D3, zero-intelligence) : un
  bras nul propre ici ne garantit pas un bras nul propre sur la dépendance
  réelle du marché. C'est l'étage suivant du banc qui le dira, pas celui-ci ;
* **le leurre écarté n'est pas le leurre indétectable** : la méthode juge la
  *masse localisée* ; la signature d'un leurre est probablement dans sa
  **dynamique** (retrait corrélé à l'approche du prix), pas dans son niveau.
  Un détecteur dédié est une piste ouverte — non lancée, non promise.

## 5. Traces

Planchers inscrits au **registre** (`05` §8 — y compris pour les admis), par
`harnais/registre.py`. Les quatre JSON et cinq logs sont commités. Le
générateur, la statistique et les protocoles sont versionnés dans `harnais/`.
