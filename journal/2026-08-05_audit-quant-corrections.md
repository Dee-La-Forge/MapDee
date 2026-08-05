# Audit quant du harnais — constats croisés et corrections, 05-06/08/2026

> Deux audits indépendants la même nuit : le mien (relecture adversariale de
> chaque formule contre sa définition, test de précision à la main) et
> l'audit de conception externe (`journal/2026-08-06_audit-conception.md`,
> constats F1-F10, vérifiés par exécution). Recouvrement fort ; l'externe a
> trouvé trois choses que j'avais ratées. Tout est corrigé, testé (**76/76**,
> dont 6 tests de régression nommés par constat), commité.

## Les défauts corrigés, du plus grave au moindre

| constat | défaut | correction | test |
|---|---|---|---|
| **B5 regarde le futur** (moi) | l'extracteur mesurait le délai JUSQU'AU prochain déplacement — fuite de cible garantie à É4 | version causale : l'ÂGE du niveau (photos depuis le dernier déplacement ≥ 1 palier) | bornes + causalité |
| **F1 crash inter-périmètres** (externe) | É0 comparait J3 à J8 → `ValueError` non attrapée, tour mort — déclenché pile à la livraison des jours 12-16 | É0 **intra-périmètre** (la déduplication inter-périmètres exigera une ADR d'intersection) ; gardes de longueur en É0 et É2 → `RefusEpreuve` propre | `test_F1_*` ×2 |
| **F2/F3 le NaN décidait** (externe) | `abs(nan) < 0,90` = False → chemin d'élimination → `ρ=nan` écrit au registre en ajout seul ; É2 laissait passer en silence | `rangs()` REFUSE NaN/inf ; validation à l'entrée du tour — le candidat pollué est refusé avec sa raison, les autres tournent, le bloc pollué lève | `test_F2_*` ×2 |
| **F4 C2 télescopait** (les deux) | moyenne des différences secondes d'un cumul ≡ `(dernier bin − premier)/14` — toute la forme jetée (vérifié algébriquement ET numériquement) | convexité vraie : `(2·cum(milieu) − cum(proche) − cum(loin))/total`, signe documenté | signes opposés sur profils opposés |
| **F9 bande glissante** (les deux) | la bande ±0,5 % suit le mid : chaque déplacement comptait les paliers de bord comme flux — `ρ(B1, |Δmid|) = 0,45 sur carnet NUL` | **marge intérieure 0,9 × dist_max** : les flux (ajouts/retraits/disparitions/recouvrement) ne se comptent qu'à l'intérieur ; le résiduel est publié (voir mesures pré-É0) | précision à la main |
| **F10 k0 à trois traitements** (les deux) | le palier du mid : exclu des stocks, compté côté ask dans les flux, inclus au profil | UNE règle : exclu des stocks ET des flux, inclus au profil (forme de masse), documenté ; sa masse capturée en diagnostic `m_k0` | précision à la main |
| **F5 hash jeté** (externe) | le préflight promettait le hash du protocole « dans chaque ligne de registre » — aucun appelant ne l'écrivait | `boucle.tour(hash_protocole=…)` signe chaque ligne (`la boucle @<hash>`) ; `e0_reel` le transmet | `test_F5_*` |
| divers (moi) | BH sur collection vide → division par zéro ; doc de signe de C2 inversée ; test qui trouvait « nan » dans « bi**nan**ce » | corrigés | inclus |

## Le test de précision à la main

`harnais/tests/test_charge_precis.py` : un parquet fabriqué ligne à ligne,
trois photos, chaque agrégat attendu calculé sur papier — stocks, Herfindahl,
meilleurs, ajouts, retraits, disparitions, recouvrement, conservation de la
masse du profil, exclusion de k0, marge intérieure. **C'est ce fichier qui
définit la sémantique de `charge()`** ; toute évolution devra le repasser.

## La lecture d'ÉS, resserrée (F6/F7)

Portée par addendum au rapport ÉS : les planchers sont des propriétés du
détecteur d'ÉS, pas du chemin É0→É4 ; ce qui transfère est le code partagé
(Student, puissance, k/n) ; le biais −0,14 du leurre est conservateur mais
gonfle probablement son plancher ; le générateur n'a jamais exercé k0.

## Les deux mesures pré-É0 (demandées par l'audit externe, câblées)

`e0_reel` publie désormais, AVANT tout verdict : **la part de masse au palier
du mid** par jour-symbole, et **ρ(série, |Δmid|)** pour chaque série — le
degré d'intrication mécanique avec le prix, à garder sous les yeux quand É4
jugera contre le déplacement du prix.

## Ce que l'audit n'invalide pas

Aucune mesure publiée ne tombe : C8.2/C8.3/C8.4 et C5 n'utilisent pas les
extracteurs ; les campagnes ÉS utilisaient leur propre statistique, et leurs
verdicts étaient déjà bornés — l'addendum les borne mieux. Les extracteurs
n'avaient jamais touché une donnée réelle : **les défauts sont morts avant
d'avoir menti.**
