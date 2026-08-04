# P0-FRAG — Porte pré-enregistrée : fragilité × flux → amplitude

**Date** : 2026-07-30 · **Statut** : ACCEPTÉ dans son principe (Meddy, 31/07) — trous de l'annexe tranchés ci-dessous
· **Rang dans la file** : APRÈS le jalon 1. Ce document existe pour être écrit
AVANT d'avoir vu le moindre chiffre — il ne déclenche rien.

> **ANNEXE DE RELECTURE (Claude, 30/07) — deux trous à trancher À LA VALIDATION,
> avant toute ligne de code :**
>
> 1. **Percolation des clusters — tel qu'écrit, G = 1 par jour.** « Fenêtres se
>    chevauchant sur [t, t+H] fusionnées en composantes connexes » avec un pas de
>    30 s et H = 120 s : chaque point chevauche le suivant (30 < 120), la clôture
>    transitive avale la journée entière → un seul cluster par jour et par
>    symbole, IC incalculables (exactement la composante géante mesurée le 30/07
>    sur l'union-find du jalon, en pire). Correctif à arbitrer : coupure par
>    SEUIL, pas par chevauchement — un épisode se ferme quand l'amplitude
>    réalisée repasse sous son quantile q50 glissant pendant ≥ H, ou coupure
>    fixe type EPISODE_MS. À écrire dans la porte avant validation.
> 2. **Instrument et cadence de la CIBLE non fixés.** La mèche max sur [t, t+30 s]
>    exige un mid plus fin que l'archive 10 s (3 points par fenêtre = quantisation
>    massive). Options réelles : (a) banc gelé HL 5 jours → mid dense reconstruit
>    (500 ms) mais il n'existe QUE pour 05-08 (~12 h CPU/jour-coin à étendre) ;
>    (b) archive Binance du recorder sandbox (100 ms, book+trades) mais ~3 jours
>    et instrument DIFFÉRENT du banc (règle « instrument égal ») ; (c) H = 120 s
>    seul sur l'archive 10 s, en renonçant à H = 30 s. La porte doit nommer son
>    choix — et si (b), dire que les features de fragilité y sont les proxys
>    faibles, pas les grandeurs validées L4.
>
> **RÉSOLUTION (31/07, sous validation globale de Meddy ; amendable jusqu'au
> lancement, qui reste post-jalon-1)** : (1) percolation -> coupure par SEUIL :
> un épisode de volatilité se ferme quand l'amplitude réalisée repasse sous son
> quantile q50 glissant pendant >= H — jamais de fusion par simple chevauchement ;
> (2) instrument -> H = 120 s SEUL sur l'archive 10 s du banc gelé (coût zéro,
> instrument égal) ; H = 30 s abandonné sauf si le mid dense reconstruit est
> étendu aux 5 jours d'ici là (~12 h CPU/jour-coin, non planifié).
>
> Le reste est conforme aux doctrines en vigueur (coupure causale d'hl_features,
> bootstrap corrigé, LODO+purge, rang intra-jour, M vs B2, règle BTC-ETH,
> relance unique). Rien d'autre à redire.

## La question (une seule)

> L'état du carnet à l'instant t — sa FRAGILITÉ — prédit-il l'AMPLITUDE du
> déplacement de prix à horizon court, au-delà de ce que la volatilité passée
> prédit déjà ?

Explicitement EXCLU du périmètre : la direction. La composante directionnelle
est celle que p2a5 a montrée instable (le pré-contact respire avec le régime,
26→48 %) et que P0 a montrée non rentable (fade naïf, brut négatif). Cette
porte teste l'amplitude, pas le signe. Toute lecture directionnelle d'un
résultat de P0-frag est une violation du périmètre.

## Pourquoi cette porte a une chance

1. La volatilité s'agglutine — prédire l'amplitude est le morceau FAISABLE du
   problème (fait stylisé robuste, quarante ans de littérature GARCH/HAR).
   La baseline sera donc forte, et c'est voulu : battre une baseline faible
   ne vaut rien.
2. L'hypothèse mécanique est falsifiable : un carnet CREUX (profondeur faible,
   niveaux au profil « bluff ») offre moins de résistance → le même flux
   traverse plus loin → mèches plus amples. Un carnet DENSE amortit.
3. Personne n'a testé cette hypothèse avec un relief VALIDÉ (features issues
   d'un banc supervisé par la vérité L4). C'est le seul ingrédient nouveau ;
   sans lui, ce test est la littérature existante.

## Entrées (X), figées avant tout run

Calculées à l'instant t, STRICTEMENT causales (mêmes règles de coupure que
`hl_features` — la rangée qui contient t est exclue) :

- **Fragilité du relief** : agrégats sur la nappe des niveaux actifs —
  profondeur totale par côté, part de la profondeur portée par des niveaux
  jeunes (< 60 s), distance au premier niveau « épais », et — dès que le
  jalon 1 a livré — le score de crédibilité moyen pondéré par la taille.
  Version pré-jalon : les trois features validées individuellement
  (placed, age, dist) en agrégats, sans score composite.
- **Flux** : OFI sur la fenêtre [t−60 s, t], volume taker net, nombre de
  trades agressifs. Depuis les archives existantes (traded/peak).
- **Interaction** : flux × fragilité — LE terme de l'hypothèse. Sans lui on
  teste deux effets marginaux, pas le rapport de forces.

## Cible (y), figée

**Amplitude de la mèche à horizon H** : max(|haut−t.mid|, |t.mid−bas|) sur
[t, t+H], en bp du mid, H ∈ {30 s, 120 s} (deux horizons, pré-déclarés, pas
de balayage). Cible en RANG intra-jour (leçon ADR-010 : le niveau appartient
au régime, le modèle n'apprend que le rang).

## Baselines (l'ordre est le test)

- **B0 — climatologie GLISSANTE** : quantiles d'amplitude des jours
  ANTÉRIEURS uniquement (jamais le jour évalué — contrat `climatology_crps`).
- **B1 — volatilité passée seule** : amplitude réalisée sur [t−300 s, t] +
  heure du jour. C'est la baseline À BATTRE : elle capture l'agglutination.
- **B2 — B1 + flux** : ce que le flux ajoute sans le relief.
- **M — B2 + fragilité + interaction** : le modèle de l'hypothèse.

La porte ne compare jamais M à B0. Le verdict est M contre B2 : le RELIEF
ajoute-t-il quelque chose que flux et volatilité passée n'ont pas ?

## Protocole (hérité, non renégociable)

- Échantillonnage : un point toutes les 30 s, par symbole, sur les jours du
  banc gelé. Clusters = épisodes de volatilité (fenêtres se chevauchant sur
  [t, t+H] fusionnées en composantes connexes) — les mèches d'une même
  cascade ne sont PAS indépendantes.
- Splits : LODO par jour + purge des clusters à cheval. IC par
  `cluster_bootstrap` (version corrigée du bootstrap, celle du jalon).
- Métriques : Spearman prédit/réalisé par jour (rang) et CRPS en skill
  contre B1 (pas B0). IC partout, points nulle part.
- Hold-out : le dernier jour d'archive n'est JAMAIS touché avant le verdict.

## Seuils de GO/NO-GO (gravés ici, avant tout chiffre)

- **GO** : ΔSpearman(M − B2) > 0 avec IC95 excluant 0 sur les DEUX symboles
  au même horizon, OU skill CRPS(M vs B1) − skill(B2 vs B1) > 0, IC95
  excluant 0, deux symboles.
- **NO-GO** : tout le reste. Un gain sur un seul symbole = artefact présumé
  (règle BTC-ETH). Un gain sur un seul horizon parmi deux = à déclarer, pas
  à célébrer.
- **Cas dégradé** : si les clusters de test < 60 par fold, verdict
  « PUISSANCE INSUFFISANTE » — plus de jours, UN re-run, comme la grille du
  jalon. Pas de troisième passage.

## Ce qu'un GO déclenche (et rien d'autre)

Un indicateur de RÉGIME sur la map (terrain fragile / dense) — couche 3 de
l'application. PAS un signal d'entrée, PAS une taille de position, PAS une
direction. Toute exploitation au-delà exige sa propre porte.

## Ce qu'un NO-GO clôt

L'hypothèse « le relief visible module l'amplitude au-delà du flux » — sur
ces features, ces horizons, cet instrument. Elle rejoint le fade naïf au
registre des choses testées et mortes. La question d'origine du projet
(sonologie → wicks) aura alors reçu sa réponse, mesurée.

## Coût et calendrier

Aucune donnée nouvelle, aucun L4, aucune infra : archives existantes + code
du banc. Estimation : 2-3 jours de calcul/analyse. Démarrage : après le
verdict du jalon 1, jamais avant (règle : un programme à la fois).
