# Feature Registry — v1 (P0)

> **GÉNÉRÉ** depuis `gondetect/features.py` (`REGISTRY`). Ne pas éditer à la main :
> le code est la source de vérité, le pipeline refuse toute feature hors registry
> (`extract_obs`/`extract_contact` ne produisent que ces colonnes).

`t_ref` = quand la feature est lisible. `obs` = à la rangée d'observation, avant
le contact → **prédictive**. `contact` = à la rangée de contact → contemporaine
de la décision, **pas** prédictive, et **interdite** sur les labels avec lesquels
elle partage un terme (cf. `FORBIDDEN`).

| feature | t_ref | origine | coût | hypothèse | statut |
|---|---|---|---|---|---|
| `f_mult` | obs | mag/med (sec-recorder row[2],row[3]) | O(1) | la TAILLE du mur prédit sa survie | baseline — déjà réfutée en JS (edge ≈ 0) |
| `f_logmag` | obs | heatmap-offline.js:80 logN(mag) | O(1) | idem en échelle log (la maquette y lit la salience) | baseline |
| `f_dist` | obs | |lvl−mid|/mid | O(1) | un niveau proche est touché plus vite / plus fragile | contrôle (confondeur : à neutraliser, pas à célébrer) |
| `f_side` | obs | lvl<mid → support (1) sinon résistance (0) | O(1) | asymétrie bid/ask | contrôle |
| `f_occ` | obs | heatmap-offline.js:81 occupancy (EMA présence) | O(1) | un mur PRÉSENT en continu est réel | candidate |
| `f_conv` | obs | heatmap-offline.js:81 conviction exp(−k·CV) | O(1) | un mur FERME (taille stable) tient au contact | candidate — +11,7 pts mesurés en JS (à répliquer) |
| `f_peak_ratio` | obs | peak/mag (row[5] impair) | O(1) | un mur déjà bien plus gros que son résidu s'érode | candidate |
| `f_persist` | obs | présence sur LOOKBACK rangées | O(L) | PERSISTANCE : le spoofer impatient ne tient pas 300 s | candidate — 1er des 2 discriminants orthogonaux |
| `f_age` | obs | rangées de présence continue avant i | O(L) | âge du mur = engagement de capital | candidate |
| `f_turnover` | obs | Σ|Δmag| / mag moyen sur LOOKBACK | O(L) | le churn trahit un ordre qui se repositionne (pas engagé) | candidate |
| `f_absorb_hist` | obs | Σ traded sur LOOKBACK / mag | O(L) | un mur déjà mangé et rechargé = vraie absorption | candidate |
| `f_withdraw_hist` | obs | Σ max(0,peak−v−traded) sur LOOKBACK / mag | O(L) | un mur qui a DÉJÀ fui par le passé refuira — sans jamais dire « le palier a disparu » (immunisé au churn du seuil) | candidate — cœur du P0 |
| `f_wd_ratio_hist` | obs | retiré/(retiré+tradé) sur LOOKBACK | O(L) | la NATURE du départ (retrait vs exécution) discrimine | candidate — cœur du P0 |
| `f_spec_flatness` | obs | entropie de Wiener du spectre de |mag| | O(N log N) | un palier ENTRETENU par un algo a un spectre TONAL (recharge périodique) ; une liquidité posée et laissée est plate. Flatness basse = machine. | TESTÉE 29/07 — univariée 0,547/0,583 (au niveau de f_persist) mais ΔAUC multivariée ≈ 0 → REDONDANTE avec PRÉSENCE, écartée |
| `f_spec_tonality` | obs | pic/moyenne du spectre | O(N log N) | force de la périodicité dominante — même idée, lue par le sommet plutôt que par l'entropie | TESTÉE 29/07 — signal INVERSÉ faible mais répliqué (0,473/0,420) ; ΔAUC ≈ 0 → écartée |
| `f_spec_centroid` | obs | centroïde spectral normalisé | O(N log N) | où siège l'énergie : dérive lente (réel) vs agitation rapide (repositionnement) | TESTÉE 29/07 — la MEILLEURE des cinq (0,566/0,592, au-dessus de f_persist) mais ΔAUC ≈ 0 → redondante, écartée |
| `f_spec_flux` | obs | flux spectral entre deux demi-fenêtres | O(N log N) | le RÉGIME du palier change-t-il ? un ordre qui va fuir se met à bouger autrement avant de partir | TESTÉE 29/07 — nulle (0,512/0,521), écartée |
| `f_coh_neighbours` | obs | corrélation |mag| du palier vs somme des voisins ±5 paliers | O(N·k) | COHÉRENCE LOCALE : la vraie profondeur respire avec son voisinage ; un mur isolé qui vit sa vie est un artefact | TESTÉE 29/07 — NULLE (0,498/0,511) : aucune cohérence locale intra-venue. N'infirme pas la cohérence MULTI-VENUE (objet distinct), mais le proxy gratuit ne marche pas |
| `f_absorb_contact` | contact | backtest-heatmap.js:44 tradedAt(j) | O(1) | le flux exécuté AU contact discrimine | référence JS (−27,5 pts) — contemporaine, PAS prédictive |

## Blocs d ablation

- **GEO (confondeur)** : `f_dist`, `f_side`
- **TAILLE** : `f_mult`, `f_logmag`
- **PRÉSENCE** : `f_occ`, `f_persist`, `f_age`
- **FORME** : `f_peak_ratio`, `f_turnover`
- **FLUX (historique)** : `f_absorb_hist`, `f_withdraw_hist`, `f_wd_ratio_hist`
- **SONOLOGIE** : `f_spec_flatness`, `f_spec_tonality`, `f_spec_centroid`, `f_spec_flux`, `f_coh_neighbours`

## Interdits par circularité

- sur `y_flee` : `f_absorb_contact`

## Verdict SONOLOGIE (29/07)

ΔAUC du cran SONOLOGIE dans l ablation, sur les 4 cellules :
**+0,007 · +0,007 · +0,002 · +0,000**. Cinq descripteurs DSP pour rien.

Prises isolément, deux d entre elles portent pourtant un vrai signal
(`f_spec_centroid` 0,566/0,592 et `f_spec_flatness` 0,547/0,583 — au-dessus de
`f_persist`). Elles n ajoutent rien parce qu elles **ré-encodent la même chose** :
combien la profondeur du palier bouge. La sonologie ne dit pas autre chose que la
persistance, elle le dit dans une autre langue.

Signature d un léger sur-ajustement : les ajouter fait monter BTC (0,712 -> 0,720)
et laisse ETH inchangé (0,667), ce qui creuse l ecart de réplication de 0,045 a
0,052. **Elles ne sont pas retenues dans le jeu de production.**
