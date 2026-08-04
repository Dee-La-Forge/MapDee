# Data Contract — v1 (P0)

Spec typée de ce qui entre et sort du pipeline. Toute rupture ici invalide les
runs antérieurs : on incrémente la version et on le dit dans le rapport.

## 1. Source — archive de PROD, lecture seule

`%LOCALAPPDATA%\gon-sec-recorder\depth\<SYM>\book-<jour>.jsonl[.gz]`
écrit par `tools/sec-recorder.js:344` (`archLine`). **La sandbox n'écrit jamais ici.**

| champ | type | sens |
|---|---|---|
| `t` | int64 ms | horodatage de la rangée |
| `mid` | float | prix moyen du carnet |
| `bs` | float | taille de palier ; palier `k = floor(prix/bs)`, prix du palier = `(k+0.5)·bs` |
| `b` | `[k0,mag0,k1,mag1,…]` | magnitude par palier = `0.5·peak + 0.5·mean` sur la fenêtre (`sec-recorder.js:457`) |
| `med` | float | médiane des magnitudes de la rangée |
| `h` | `[occ×100,…]` | occupancy lissée (EMA de présence), 1 par palier |
| `f` | `[trd0,peak0,trd1,peak1,…]` | flux de la fenêtre : volume exécuté, pic de profondeur |
| `c` | `[conv×100,…]` | conviction `exp(−1.6·CV)`, 1 par palier |

Cadence **10 s** (`SAMPLE_MS=2500 × ARCH_EVERY=4`). On lit le RAW, **jamais**
`/bookarch` (qui sous-échantillonne à 2000 rangées et détruit la cadence).

## 2. Limites CONNUES de la source — à ne jamais oublier

1. **L'archive ne garde que `v > med`** (`sec-recorder.js:470`), puis cappe à
   **top-700 par valeur ∪ 450 plus proches du mid** (`:487-494`). Conséquence :
   la présence d'un palier est **discontinue par artefact de seuil**.
   → **Interdit** : tout label ou feature de la forme « le palier a disparu ».
   → **Mitigation** (commit 5274677) : ne raisonner que sur `peak / traded`.
2. **`peak − v − traded` n'est pas un retrait NET.** Comme `v = 0.5·peak + 0.5·mean`,
   on a `peak − v = 0.5·(peak − mean)` : la quantité mesure la **chute de profondeur
   sous son pic non expliquée par l'exécution**, pas le solde de fin de fenêtre.
   C'est un proxy honnête de « ça s'est retiré », pas une mesure comptable.
   **C'est exactement ce que le L4 de P2 viendra trancher.**
3. **`c` (conviction) n'existe que depuis le 2026-07-28**, `f` (flux) depuis le
   2026-07-26. Sur un split temporel, `f_conv` tombe **entièrement côté test** →
   non entraînable, donc écartée explicitement par le pipeline (jamais imputée
   en douce).
4. **Un palier n'est pas un ordre.** `k` est un bin de prix : sa « persistance »
   agrège des ordres distincts. L'âge médian d'un épisode mesuré en P0 est de
   ~1 h, ce qui est une durée de *zone de liquidité*, pas de *l'ordre*.
   Le passage à l'ordre individuel est précisément l'objet de P2 (L4).
5. **`bs` peut changer en cours de journée** (rebase de grille,
   `sec-recorder.js:447`) : les `k` deviennent incomparables. Le loader ne garde
   que le segment `bs` majoritaire.

## 3. Observation (unité de ligne du dataset P0)

Un **événement** = un mur touché.

| champ | type | sens |
|---|---|---|
| `sym`,`day`,`k`,`side` | str/int | identité du niveau |
| `t_obs` | int64 ms | rangée `i` où les features sont lues — **rien après n'y entre** |
| `t_contact` | int64 ms | rangée `j > i` du premier contact (prix à ±`TOL`) |
| `t_end` | int64 ms | fin de la fenêtre d'issue (`j + W_OUT`) |
| `episode` | str | `sym\|k\|jour\|début-de-présence-continue` — **unité de clustering** |
| `f_*` | float | cf. Feature Registry (`01-feature-registry.md`) |

## 4. Labels

| label | définition | forme |
|---|---|---|
| `y_reject` | sur `[j, j+W_OUT]`, le prix s'éloigne du niveau du côté du rebond plutôt que de le traverser | PRIX — n'utilise que `mid`, donc immunisé au churn par construction |
| `y_flee` | sur `[j, j+FLEE_WIN]`, `Σ retiré > Σ tradé` avec `retiré = max(0, peak − v − traded)` | PROFONDEUR — cible du programme, sous la limite §2.2 |

`y_flee` est **indéfini** (NaN) quand `Σ retiré + Σ tradé = 0` : le mur n'a été ni
mangé ni retiré, l'événement n'est pas informatif. Couverture mesurée : 68 % (BTC), 83 % (ETH).

## 5. Règles anti-fuite — non négociables

- **Aucune feature `t_ref=obs` ne lit une rangée > `i`.**
- Les features `t_ref=contact` sont déclarées comme telles et **interdites sur
  `y_flee`** : `f_absorb_contact = traded(j)/mag` partage le terme `traded` avec
  le label → corrélation **mécanique**, pas prédictive (registry `FORBIDDEN`).
- **Split temporel + embargo 60 min** : train = `t_end < coupure`, test =
  `t_obs > coupure + embargo`. Un `episode` ne peut pas être des deux côtés
  (garde-fou explicite dans `dataset.time_split`).
- **Réplication BTC / ETH indépendante.** Un edge sur un seul symbole est traité
  comme du sur-ajustement jusqu'à preuve du contraire.
- Le **confondeur géométrique** (`f_dist`, `f_side`) est isolé dans son propre
  bloc d'ablation : le chiffre publié est celui **sans GEO**.

## 6. Versionning

`dataset v1 · features v1 · labels v1`. Chaque run écrit son hash de config dans
`lab/02-experiments/p0-<stamp>-<hash>.md` et son dataset dans
`data/cache/p0-events-<SYM>-<hash>.parquet`.
