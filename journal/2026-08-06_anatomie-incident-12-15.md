# Anatomie de l'incident d'archive 12→15 — et le 13 est récupérable aux deux tiers

> 06/08/2026. Verdicts du diagnostic pré-enregistré `diag_croisement`
> (critère écrit avant de regarder), quatre jour-symboles rejoués.

## Les verdicts

| jour | symbole | premier croisement | union oids | Jaccard | verdict pré-enregistré |
|---|---|---|---|---|---|
| 20251212 | BTC | **h18** | 152 219 | 0,77 | IRRÉCUPÉRABLE (union ≫ 1000) |
| 20251212 | ETH | **h18** | 137 865 | 0,70 | IRRÉCUPÉRABLE |
| 20251213 | BTC | **AUCUN** (rejeu à froid) | 0 | — | voir ci-dessous |
| 20251213 | ETH | **AUCUN** (rejeu à froid) | 0 | — | voir ci-dessous |
| 20251215 | ETH | h12 (partiel, h00-12) | 5 857 | 0,14 | IRRÉCUPÉRABLE |

## L'anatomie — deux fenêtres, une contagion par la chauffe

1. **Fenêtre 1 : le 12 à 18 h**, les deux symboles en même temps — des
   `remove` perdus à la capture, ~140-150 k ordres fantômes accumulés qui
   épinglent le carnet jusqu'à la fin du jour. Les 18 premières heures
   sont saines (les 69-75 % déjà comptés).
2. **Le 13 n'est PAS corrompu** : rejoué à froid (carnet vide), son flux
   propre ne croise JAMAIS, sur les deux symboles. Le croisement de bout
   en bout vu par la production venait de la **CHAUFFE** — les 8 dernières
   heures du 12 (16 h-23 h) contiennent la fenêtre d'incident, et le
   carnet hérité était empoisonné avant la première photo.
3. **Pourquoi les 14 et 16 sont sains** : la chauffe rejoue la veille
   depuis un carnet VIDE — les fantômes postés AVANT la fenêtre de chauffe
   n'y figurent pas. La chauffe du 14 (13 : 16-23 h, flux propre) et celle
   du 16 (15 : 16-23 h — les fantômes du 15 datent de ~12 h, hors fenêtre)
   filtrent l'incident par construction.
4. **Fenêtre 2 : le 15 à 12 h** (pas 13 h — le gel du compteur de photos
   était le symptôme retardé), même signature, churn massif.

## La conséquence — une décision qui appartient à Meddy

**20251213 est reconstructible aux deux tiers** : rebâti SANS veille
(comportement « premier jour d'archive », déjà écrit dans `jour.py` —
8 h de chauffe sur son propre matin, émission h08-h23), il sortirait
~66 % de journée, saine — un jour DÉGRADÉ comme les 12 et 15, plus un
trou. Ce qui le demande : un moyen de forcer le mode sans-veille
(`GON_SANS_VEILLE`, correction en file, fenêtre des corrections) et une
**ré-déclaration du périmètre J8 par ADR** — J8 a été amendé sur une
impossibilité matérielle qui vient de tomber ; y revenir n'est pas
automatique, c'est une décision de périmètre (`05` §7 : les candidats J8
déjà jugés — D1 — repassent). Elle interagit avec ADR-007 : un jour à
66 % vivra sous le plancher qui y sera arbitré.

Rien n'est rebâti sans cette décision. Le constat, lui, est mesuré.
