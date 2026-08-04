# Transfert de labels — le label faible dit-il ce qu'on croit ? · run `2026-07-30T022425Z` · config `1ad50e04edfc`

Source **faible** : `synth-weak-biased` (weak) · source **forte** : `synth-strong` (strong).

> ⚠ **RUN SUR FIXTURES SYNTHÉTIQUES.** Les vraies sources L4 n'étaient pas importables au moment du run. Les chiffres ci-dessous valident le HARNAIS, pas le label. Aucun d'eux ne doit être cité comme un résultat de marché.

```json
{
  "weak": "synth:weak-biased",
  "strong": "synth:strong",
  "symbols": [
    "BTCUSDT",
    "ETHUSDT"
  ],
  "days": [
    "2026-07-26",
    "2026-07-27"
  ],
  "match_tol_ms": 5000,
  "match_tol_rel": 5e-05,
  "n_boot": 400,
  "train_frac": 0.7,
  "embargo_s": 3600.0,
  "seed": 12345,
  "synthetic": true,
  "code_sha": "eea6b346638a"
}
```

Appariement : même symbole, |Δt| ≤ **5 s**, |Δprix|/prix ≤ **0.5 bp**, **injectif** (un événement fort ne sert qu'une fois — sinon un mur touché trois fois se verrait recopier la même vérité et l'accord serait fabriqué).

**Clés de `provenance` refusées comme covariables** (le harnais ne laisse pas n'importe quoi devenir une feature) :

- `oid` — identifiant de venue (ADR-009)
- `size_canceled` — grandeur d'issue (circularité avec le label)
- `t_place_ms` — horodatage (fuite temporelle possible)

Toute statistique ci-dessous est **clusterisée** sur la partition commune (wallet ∪ épisode, composantes connexes). L'« effet de grappe » est le rapport ET clusterisée / ET naïve : c'est ce qu'on aurait sur-vendu en traitant chaque contact comme indépendant.

---

## BTCUSDT

**Appariement** : 3691 couples (faible 3872 → 95 % apparié · fort 3993 → 92 %) · clusters effectifs **238** → 15.5 événement(s)/cluster.

Covariables partagées : `c_dist_rel`, `c_delay_s`, `c_age_s`, `c_calm`, `c_notional`, `c_occupancy`

### 1. Accord brut

| | fort : **a fui** | fort : **a tenu** |
|---|---|---|
| faible : **a fui** | 1886 | **280** (faux « a fui ») |
| faible : **a tenu** | **141** (fausse « a tenu ») | 1384 |

- taux d'accord : **88.6 %** · IC95 clusterisé [87.1 ; 89.8] % (bootstrap par cluster)
- **κ de Cohen : 0.768** · IC95 [0.742 ; 0.794] — l'accord au-delà du hasard ; c'est κ qui compte, pas le taux brut (deux labels à 70 % de « a fui » s'accordent à 58 % en tirant à pile ou face)
- prévalence « a fui » : faible **58.7 %** vs fort **54.9 %**
- **effet de grappe : ×1.38** — l'IC correct est 1.38 fois plus large que l'IC naïf

### 2. Où le faible se trompe-t-il ?

Taux de désaccord par quartile (± 1 ET **clusterisée**) — c'est ce tableau qui dit *quoi corriger* dans le proxy. `α` = fuites manquées, `β` = fausses alertes : le désaccord brut seul monte mécaniquement là où le taux de base approche 50 %, sans erreur supplémentaire.

| covariable | quartile | n | désaccord | ± ET | α | β | base |
|---|---|---|---|---|---|---|---|
| `c_dist_rel` | Q1 | 923 | **10.9 %** | 1.2 | 8.0 % | 14.5 % | 54.5 % |
| `c_dist_rel` | Q2 | 923 | **11.6 %** | 1.1 | 7.0 % | 17.0 % | 54.2 % |
| `c_dist_rel` | Q3 | 922 | **10.6 %** | 1.0 | 5.7 % | 16.6 % | 55.0 % |
| `c_dist_rel` | Q4 | 923 | **12.5 %** | 1.2 | 7.2 % | 19.2 % | 56.0 % |
| `c_delay_s` | Q1 | 923 | **9.9 %** | 1.0 | 5.8 % | 14.6 % | 54.0 % |
| `c_delay_s` | Q2 | 923 | **11.2 %** | 1.1 | 7.0 % | 16.0 % | 54.0 % |
| `c_delay_s` | Q3 | 922 | **11.5 %** | 1.3 | 6.5 % | 18.1 % | 56.9 % |
| `c_delay_s` | Q4 | 923 | **13.1 %** | 1.2 | 8.5 % | 18.7 % | 54.8 % |
| `c_age_s` | Q1 | 923 | **16.6 %** | 1.4 | 6.2 % | 20.2 % | 26.0 % |
| `c_age_s` | Q2 | 925 | **12.1 %** | 1.4 | 7.7 % | 16.3 % | 49.0 % |
| `c_age_s` | Q3 | 921 | **9.3 %** | 1.1 | 7.0 % | 13.3 % | 63.3 % |
| `c_age_s` | Q4 | 922 | **7.6 %** | 1.0 | 6.7 % | 11.7 % | 81.5 % |
| `c_calm` | Q1 | 923 | **15.1 %** | 1.3 | 5.7 % | 22.9 % | 45.5 % |
| `c_calm` | Q2 | 923 | **11.3 %** | 1.2 | 6.0 % | 16.7 % | 50.6 % |
| `c_calm` | Q3 | 922 | **10.0 %** | 1.1 | 7.1 % | 13.5 % | 55.0 % |
| `c_calm` | Q4 | 923 | **9.3 %** | 1.0 | 8.4 % | 11.4 % | 68.6 % |
| `c_notional` | Q1 | 925 | **13.8 %** | 1.4 | 5.5 % | 51.8 % | 82.1 % |
| `c_notional` | Q2 | 921 | **14.4 %** | 1.4 | 7.5 % | 26.3 % | 63.3 % |
| `c_notional` | Q3 | 924 | **9.0 %** | 1.1 | 7.4 % | 10.5 % | 48.5 % |
| `c_notional` | Q4 | 921 | **8.4 %** | 0.9 | 9.3 % | 8.0 % | 25.7 % |
| `c_occupancy` | Q1 | 923 | **13.7 %** | 1.4 | 8.5 % | 17.5 % | 43.1 % |
| `c_occupancy` | Q2 | 923 | **13.3 %** | 1.3 | 6.7 % | 20.4 % | 51.6 % |
| `c_occupancy` | Q3 | 923 | **10.7 %** | 1.2 | 7.0 % | 15.8 % | 57.4 % |
| `c_occupancy` | Q4 | 922 | **7.9 %** | 0.9 | 6.1 % | 11.7 % | 67.6 % |

→ Désaccord maximal sur `c_age_s` Q1 (**16.6 %**), minimal sur `c_age_s` Q4 (7.6 %). Écart **9.0 pts**.

### 3. BIAISÉ ou BRUITÉ ? (la question décisive)

**(a) Asymétrie des taux d'erreur CONDITIONNELS** — α = P(faible « a tenu » | vérité « a fui ») = **7.0 %** ; β = P(faible « a fui » | vérité « a tenu ») = **16.8 %**. α − β = **-9.9 pts**, IC95 par bootstrap *par cluster* [-12.1 ; -7.7] pts → p = **< 0.0025**.

  *(Le décalage de prévalence brut — +3.77 pts, p clusterisé 2.51e-10 vs p naïf 9.359e-12 — est DESCRIPTIF et pas diagnostique : un bruit parfaitement symétrique décale déjà la prévalence vers 50 %.)*

**(b) Différentialité** — pente clusterisée du taux d'erreur **à vérité fixée**, sur chaque covariable standardisée. Une pente ≠ 0 = le proxy se trompe *plus ici que là* = **biais non corrigible**.

> Conditionner sur la vérité n'est pas un détail : régresser l'erreur signée `faible − fort` sur X déclare « biaisé » un bruit parfaitement symétrique, parce que E[faible − fort | X] = p·(1 − 2·P(fort=1|X)) dépend de X dès que le taux de base dépend de X. Le selftest a attrapé cette erreur dans la première version de ce harnais.

| taux | covariable | n | pente | ET clust. | p (Holm, **clusterisé**) | p (Holm, naïf) | inflation ET |
|---|---|---|---|---|---|---|---|
| β (a tenu) | `c_calm` | 1664 | -0.0430 ★ | 0.0085 | **4.543e-06** | 2.608e-05 | ×0.93 |
| β (a tenu) | `c_notional` | 1664 | -0.0450 ★ | 0.0094 | **1.85e-05** | 9.493e-06 | ×1.03 |
| β (a tenu) | `c_age_s` | 1664 | -0.0288 ★ | 0.0086 | **0.007891** | 0.01652 | ×0.94 |
| β (a tenu) | `c_occupancy` | 1664 | -0.0224 | 0.0100 | **0.2288** | 0.13 | ×1.09 |
| β (a tenu) | `c_dist_rel` | 1664 | +0.0166 | 0.0085 | **0.4062** | 0.4935 | ×0.93 |
| β (a tenu) | `c_delay_s` | 1664 | +0.0174 | 0.0091 | **0.4062** | 0.4657 | ×1.00 |
| α (a fui) | `c_dist_rel` | 2027 | -0.0051 | 0.0059 | **1** | 1 | ×1.05 |
| α (a fui) | `c_delay_s` | 2027 | +0.0057 | 0.0058 | **1** | 1 | ×1.02 |
| α (a fui) | `c_notional` | 2027 | -0.0002 | 0.0039 | **1** | 1 | ×0.69 |
| α (a fui) | `c_occupancy` | 2027 | -0.0078 | 0.0065 | **1** | 1 | ×1.15 |
| α (a fui) | `c_age_s` | 2027 | +0.0003 | 0.0056 | **1** | 1 | ×0.99 |
| α (a fui) | `c_calm` | 2027 | +0.0068 | 0.0058 | **1** | 1 | ×1.02 |

★ = significatif après correction de Holm. La colonne « inflation ET » est le prix du clustering : c'est le facteur dont on aurait sur-vendu chaque significativité en l'ignorant.

**(c) Compression de l'échelle** — `ratio_faible = 0.228(±0.004) + 0.578(±0.008)·ratio_fort`. Une erreur purement aléatoire laisse la pente ≈ 1 ; une pente << 1 avec ordonnée > 0 écrase l'échelle vers « a fui ».

**(d) Contrôle par dégradation simulée** — ⚠ Témoin NON DÉCISIF — mesuré aveugle à un biais différentiel planté (contrôle positif du 29/07, p=0,43). Son silence ne dit rien ; seul un POSITIF de sa part serait informatif. Il est calculé et rapporté, mais **exclu du verdict**.

  On retourne les labels FORTS aux taux observés (α=0.062, β=0.161) mais **indépendamment des covariables**, en tirage apparié par cluster. Prédictibilité du faible RÉEL : AUC **0.812** ; des contrefaçons « pur bruit » : 0.797 [0.767 ; 0.828] · écart apparié **+0.015** → p bilatéral **0.36**.

> **Verdict : BIAIS DIFFÉRENTIEL** — le taux d'erreur du label faible dépend des covariables, À VÉRITÉ FIXÉE. Non corrigible par plus de données : un modèle entraîné dessus apprend la MESURE, pas le phénomène. *(verdict assemblé sur (a) et (b) seuls ; (c) et (d) sont descriptifs.)*

### 4. Métrique de transfert (porte P4)

Deux splits, une hiérarchie (correctif 30/07) :

- **split GROUPÉ par cluster** (embargo 60 min) — **c'est lui qui fait foi** : aucun cluster des deux côtés, par construction. Train **2519** → test **964** lignes / **63** clusters de test (split GROUPÉ par cluster : 162 clusters train / 63 test, 13 écartés (chevauchent [t_cut ; t_cut + embargo]) — aucun cluster des deux côtés, par construction).
- split temporel classique — rapporté pour CHIFFRER la fuite d'identité, pas pour décider. Train 2569 → test 1023 lignes / 69 clusters (clusters à cheval purgés (1 sur 70)).

Features = celles de la source FAIBLE (seul scénario déployable : en production, pas de L4). Chaque AUC est donnée avec son IC95 bootstrap **par cluster** [q2,5 ; q97,5] — jamais en point seul.

| entraîné sur | évalué contre | AUC — split GROUPÉ (**fait foi**, 63 clusters) | AUC — split temporel (69 clusters) |
|---|---|---|---|
| FORT | fort *(plafond)* | **0.876 [0.847 ; 0.901]** | 0.877 [0.853 ; 0.901] |
| FORT | faible | 0.812 [0.778 ; 0.842] | 0.810 [0.781 ; 0.839] |
| FAIBLE | faible *(le chiffre de P0)* | 0.813 [0.777 ; 0.840] | 0.811 [0.779 ; 0.837] |
| FAIBLE | fort *(**le chiffre qui décide**)* | **0.853 [0.821 ; 0.881]** | 0.850 [0.821 ; 0.879] |

- **prime d'identité** = A_ws(temporel) − A_ws(groupé) = **-0.003 [-0.040 ; 0.035]** — c'est la part d'AUC due à la RECONNAISSANCE des acteurs présents des deux côtés du split temporel, pas au phénomène (IC par différence tirage à tirage de deux bootstraps indépendants : approximation, les deux tests se recouvrent partiellement).
- **La colonne « split GROUPÉ » fait foi** ; la colonne « split temporel » n'est là que pour rendre la fuite d'identité visible et chiffrée.
- ⚠ garde de lecture : avec **63 clusters de test**, l'IC de A_ws a une largeur de **0.060** — un premier chiffre réel PEU CONCLUANT est le résultat ATTENDU de ce design (le split groupé paie la propreté en clusters), pas un échec du transfert.
- **écart de transfert** (plafond − faible→fort, split groupé) : **+0.022** · IC95 par bootstrap **par cluster** [0.008 ; 0.036] (400 tirages)
- concordance des classements produits par les deux entraînements : ρ de Spearman **+0.885** — à l'usage (dimensionner un ordre traversant) c'est le classement qui compte, pas la valeur de l'AUC

> **PORTE P4 : transfert PARTIEL** — il reste du signal réel, mais le proxy en coûte une part mesurable. Chiffrer ce coût avant de dimensionner quoi que ce soit dessus.

---

## ETHUSDT

**Appariement** : 3646 couples (faible 3845 → 95 % apparié · fort 3974 → 92 %) · clusters effectifs **240** → 15.2 événement(s)/cluster.

Covariables partagées : `c_dist_rel`, `c_delay_s`, `c_age_s`, `c_calm`, `c_notional`, `c_occupancy`

### 1. Accord brut

| | fort : **a fui** | fort : **a tenu** |
|---|---|---|
| faible : **a fui** | 1862 | **236** (faux « a fui ») |
| faible : **a tenu** | **114** (fausse « a tenu ») | 1434 |

- taux d'accord : **90.4 %** · IC95 clusterisé [89.2 ; 91.6] % (bootstrap par cluster)
- **κ de Cohen : 0.806** · IC95 [0.783 ; 0.830] — l'accord au-delà du hasard ; c'est κ qui compte, pas le taux brut (deux labels à 70 % de « a fui » s'accordent à 58 % en tirant à pile ou face)
- prévalence « a fui » : faible **57.5 %** vs fort **54.2 %**
- **effet de grappe : ×1.21** — l'IC correct est 1.21 fois plus large que l'IC naïf

### 2. Où le faible se trompe-t-il ?

Taux de désaccord par quartile (± 1 ET **clusterisée**) — c'est ce tableau qui dit *quoi corriger* dans le proxy. `α` = fuites manquées, `β` = fausses alertes : le désaccord brut seul monte mécaniquement là où le taux de base approche 50 %, sans erreur supplémentaire.

| covariable | quartile | n | désaccord | ± ET | α | β | base |
|---|---|---|---|---|---|---|---|
| `c_dist_rel` | Q1 | 912 | **9.1 %** | 1.0 | 5.5 % | 13.6 % | 55.8 % |
| `c_dist_rel` | Q2 | 911 | **11.3 %** | 1.1 | 6.7 % | 16.6 % | 53.8 % |
| `c_dist_rel` | Q3 | 911 | **9.0 %** | 1.0 | 6.6 % | 11.7 % | 52.9 % |
| `c_dist_rel` | Q4 | 912 | **9.0 %** | 1.0 | 4.2 % | 14.6 % | 54.3 % |
| `c_delay_s` | Q1 | 912 | **9.4 %** | 0.9 | 5.6 % | 13.7 % | 52.7 % |
| `c_delay_s` | Q2 | 911 | **10.2 %** | 1.1 | 6.2 % | 14.6 % | 52.7 % |
| `c_delay_s` | Q3 | 911 | **9.5 %** | 1.1 | 5.4 % | 14.5 % | 54.7 % |
| `c_delay_s` | Q4 | 912 | **9.2 %** | 1.0 | 5.8 % | 13.7 % | 56.7 % |
| `c_age_s` | Q1 | 912 | **13.3 %** | 1.2 | 5.2 % | 16.0 % | 25.1 % |
| `c_age_s` | Q2 | 912 | **11.1 %** | 1.2 | 7.2 % | 14.9 % | 50.0 % |
| `c_age_s` | Q3 | 912 | **7.8 %** | 1.0 | 5.8 % | 11.2 % | 62.7 % |
| `c_age_s` | Q4 | 910 | **6.3 %** | 0.9 | 5.0 % | 11.0 % | 79.0 % |
| `c_calm` | Q1 | 912 | **13.5 %** | 1.3 | 7.3 % | 18.6 % | 45.1 % |
| `c_calm` | Q2 | 911 | **9.7 %** | 1.0 | 5.3 % | 14.4 % | 51.9 % |
| `c_calm` | Q3 | 911 | **7.7 %** | 0.9 | 5.2 % | 10.6 % | 53.2 % |
| `c_calm` | Q4 | 912 | **7.6 %** | 0.9 | 5.6 % | 11.5 % | 66.6 % |
| `c_notional` | Q1 | 913 | **13.1 %** | 1.2 | 6.2 % | 40.5 % | 79.7 % |
| `c_notional` | Q2 | 912 | **11.3 %** | 1.2 | 6.8 % | 18.4 % | 61.3 % |
| `c_notional` | Q3 | 911 | **8.1 %** | 1.0 | 5.1 % | 10.9 % | 47.5 % |
| `c_notional` | Q4 | 910 | **5.8 %** | 0.8 | 3.5 % | 6.7 % | 28.1 % |
| `c_occupancy` | Q1 | 912 | **10.7 %** | 1.1 | 7.6 % | 13.2 % | 44.5 % |
| `c_occupancy` | Q2 | 913 | **10.6 %** | 1.2 | 5.8 % | 15.7 % | 51.0 % |
| `c_occupancy` | Q3 | 909 | **9.6 %** | 0.9 | 6.6 % | 13.9 % | 58.7 % |
| `c_occupancy` | Q4 | 912 | **7.5 %** | 0.8 | 3.7 % | 13.7 % | 62.5 % |

→ Désaccord maximal sur `c_calm` Q1 (**13.5 %**), minimal sur `c_notional` Q4 (5.8 %). Écart **7.7 pts**.

### 3. BIAISÉ ou BRUITÉ ? (la question décisive)

**(a) Asymétrie des taux d'erreur CONDITIONNELS** — α = P(faible « a tenu » | vérité « a fui ») = **5.8 %** ; β = P(faible « a fui » | vérité « a tenu ») = **14.1 %**. α − β = **-8.4 pts**, IC95 par bootstrap *par cluster* [-10.3 ; -6.3] pts → p = **< 0.0025**.

  *(Le décalage de prévalence brut — +3.35 pts, p clusterisé 2.904e-10 vs p naïf 5.43e-11 — est DESCRIPTIF et pas diagnostique : un bruit parfaitement symétrique décale déjà la prévalence vers 50 %.)*

**(b) Différentialité** — pente clusterisée du taux d'erreur **à vérité fixée**, sur chaque covariable standardisée. Une pente ≠ 0 = le proxy se trompe *plus ici que là* = **biais non corrigible**.

> Conditionner sur la vérité n'est pas un détail : régresser l'erreur signée `faible − fort` sur X déclare « biaisé » un bruit parfaitement symétrique, parce que E[faible − fort | X] = p·(1 − 2·P(fort=1|X)) dépend de X dès que le taux de base dépend de X. Le selftest a attrapé cette erreur dans la première version de ce harnais.

| taux | covariable | n | pente | ET clust. | p (Holm, **clusterisé**) | p (Holm, naïf) | inflation ET |
|---|---|---|---|---|---|---|---|
| β (a tenu) | `c_notional` | 1670 | -0.0439 ★ | 0.0088 | **7.83e-06** | 2.553e-06 | ×1.04 |
| β (a tenu) | `c_calm` | 1670 | -0.0276 ★ | 0.0085 | **0.0123** | 0.01302 | ×1.00 |
| β (a tenu) | `c_age_s` | 1670 | -0.0218 | 0.0079 | **0.05744** | 0.1034 | ×0.93 |
| α (a fui) | `c_occupancy` | 1976 | -0.0097 | 0.0050 | **0.4833** | 0.5876 | ×0.96 |
| α (a fui) | `c_notional` | 1976 | -0.0072 | 0.0044 | **0.8365** | 1 | ×0.84 |
| α (a fui) | `c_calm` | 1976 | -0.0029 | 0.0055 | **1** | 1 | ×1.06 |
| α (a fui) | `c_dist_rel` | 1976 | -0.0048 | 0.0049 | **1** | 1 | ×0.93 |
| α (a fui) | `c_delay_s` | 1976 | -0.0003 | 0.0048 | **1** | 1 | ×0.91 |
| β (a tenu) | `c_delay_s` | 1670 | -0.0016 | 0.0085 | **1** | 1 | ×1.00 |
| β (a tenu) | `c_dist_rel` | 1670 | -0.0010 | 0.0089 | **1** | 1 | ×1.04 |
| α (a fui) | `c_age_s` | 1976 | -0.0034 | 0.0052 | **1** | 1 | ×0.98 |
| β (a tenu) | `c_occupancy` | 1670 | -0.0069 | 0.0094 | **1** | 1 | ×1.11 |

★ = significatif après correction de Holm. La colonne « inflation ET » est le prix du clustering : c'est le facteur dont on aurait sur-vendu chaque significativité en l'ignorant.

**(c) Compression de l'échelle** — `ratio_faible = 0.223(±0.005) + 0.586(±0.008)·ratio_fort`. Une erreur purement aléatoire laisse la pente ≈ 1 ; une pente << 1 avec ordonnée > 0 écrase l'échelle vers « a fui ».

**(d) Contrôle par dégradation simulée** — ⚠ Témoin NON DÉCISIF — mesuré aveugle à un biais différentiel planté (contrôle positif du 29/07, p=0,43). Son silence ne dit rien ; seul un POSITIF de sa part serait informatif. Il est calculé et rapporté, mais **exclu du verdict**.

  On retourne les labels FORTS aux taux observés (α=0.060, β=0.150) mais **indépendamment des covariables**, en tirage apparié par cluster. Prédictibilité du faible RÉEL : AUC **0.803** ; des contrefaçons « pur bruit » : 0.795 [0.766 ; 0.821] · écart apparié **+0.008** → p bilatéral **0.63**.

> **Verdict : BIAIS DIFFÉRENTIEL** — le taux d'erreur du label faible dépend des covariables, À VÉRITÉ FIXÉE. Non corrigible par plus de données : un modèle entraîné dessus apprend la MESURE, pas le phénomène. *(verdict assemblé sur (a) et (b) seuls ; (c) et (d) sont descriptifs.)*

### 4. Métrique de transfert (porte P4)

Deux splits, une hiérarchie (correctif 30/07) :

- **split GROUPÉ par cluster** (embargo 60 min) — **c'est lui qui fait foi** : aucun cluster des deux côtés, par construction. Train **2514** → test **914** lignes / **61** clusters de test (split GROUPÉ par cluster : 165 clusters train / 61 test, 14 écartés (chevauchent [t_cut ; t_cut + embargo]) — aucun cluster des deux côtés, par construction).
- split temporel classique — rapporté pour CHIFFRER la fuite d'identité, pas pour décider. Train 2540 → test 1000 lignes / 68 clusters (aucun cluster à cheval).

Features = celles de la source FAIBLE (seul scénario déployable : en production, pas de L4). Chaque AUC est donnée avec son IC95 bootstrap **par cluster** [q2,5 ; q97,5] — jamais en point seul.

| entraîné sur | évalué contre | AUC — split GROUPÉ (**fait foi**, 61 clusters) | AUC — split temporel (68 clusters) |
|---|---|---|---|
| FORT | fort *(plafond)* | **0.870 [0.847 ; 0.891]** | 0.876 [0.855 ; 0.895] |
| FORT | faible | 0.803 [0.774 ; 0.831] | 0.816 [0.789 ; 0.843] |
| FAIBLE | faible *(le chiffre de P0)* | 0.796 [0.770 ; 0.821] | 0.802 [0.773 ; 0.828] |
| FAIBLE | fort *(**le chiffre qui décide**)* | **0.852 [0.829 ; 0.874]** | 0.855 [0.832 ; 0.877] |

- **prime d'identité** = A_ws(temporel) − A_ws(groupé) = **+0.003 [-0.025 ; 0.033]** — c'est la part d'AUC due à la RECONNAISSANCE des acteurs présents des deux côtés du split temporel, pas au phénomène (IC par différence tirage à tirage de deux bootstraps indépendants : approximation, les deux tests se recouvrent partiellement).
- **La colonne « split GROUPÉ » fait foi** ; la colonne « split temporel » n'est là que pour rendre la fuite d'identité visible et chiffrée.
- ⚠ garde de lecture : avec **61 clusters de test**, l'IC de A_ws a une largeur de **0.045** — un premier chiffre réel PEU CONCLUANT est le résultat ATTENDU de ce design (le split groupé paie la propreté en clusters), pas un échec du transfert.
- **écart de transfert** (plafond − faible→fort, split groupé) : **+0.018** · IC95 par bootstrap **par cluster** [0.003 ; 0.033] (400 tirages)
- concordance des classements produits par les deux entraînements : ρ de Spearman **+0.900** — à l'usage (dimensionner un ordre traversant) c'est le classement qui compte, pas la valeur de l'AUC

> **PORTE P4 : transfert PARTIEL** — il reste du signal réel, mais le proxy en coûte une part mesurable. Chiffrer ce coût avant de dimensionner quoi que ce soit dessus.

---

## Réplication entre symboles (le juge de paix)

| symbole | κ | accord | α | β | différentiel ? | AUC faible→fort | écart transfert |
|---|---|---|---|---|---|---|---|
| BTCUSDT | 0.768 | 88.6 % | 7.0 % | 16.8 % | **OUI** | 0.853 | +0.022 |
| ETHUSDT | 0.806 | 90.4 % | 5.8 % | 14.1 % | **OUI** | 0.852 | +0.018 |

→ Verdicts biais/bruit : BTCUSDT = *BIAIS DIFFÉRENTIEL* · ETHUSDT = *BIAIS DIFFÉRENTIEL* → **RÉPLIQUÉ**.

---

## Robustesse à l'appariement (2 s / 5 s / 10 s)

L'appariement (±Δt, ±Δprix) est une hypothèse : le verdict doit y survivre. On re-déroule ici l'appariement ET l'analyse aux trois tolérances (mêmes données, mêmes graines). Le critère n'est **pas** l'égalité des étiquettes de verdict — un verdict catégoriel peut basculer sur un écart minuscule autour d'un seuil — mais le CHEVAUCHEMENT des IC95 des grandeurs CONTINUES : κ, (α − β) et l'écart de transfert. « NON ROBUSTE » exige des IC **disjoints** entre deux tolérances sur au moins une grandeur. Les étiquettes restent affichées à titre indicatif ; elles ne décident plus.

### BTCUSDT

| tolérance | couples | κ · IC95 | α − β (pts) · IC95 | écart transfert · IC95 | verdict *(indicatif)* |
|---|---|---|---|---|---|
| 2 s | 3692 | 0.768 [0.736 ; 0.795] | -9.9 [-12.1 ; -7.4] | +0.023 [0.008 ; 0.038] | *BIAIS DIFFÉRENTIEL* |
| 5 s *(nominale)* | 3691 | 0.768 [0.742 ; 0.794] | -9.9 [-12.1 ; -7.7] | +0.022 [0.008 ; 0.036] | *BIAIS DIFFÉRENTIEL* |
| 10 s | 3691 | 0.768 [0.739 ; 0.797] | -9.9 [-11.8 ; -7.6] | +0.022 [0.007 ; 0.037] | *BIAIS DIFFÉRENTIEL* |

### ETHUSDT

| tolérance | couples | κ · IC95 | α − β (pts) · IC95 | écart transfert · IC95 | verdict *(indicatif)* |
|---|---|---|---|---|---|
| 2 s | 3646 | 0.806 [0.782 ; 0.827] | -8.4 [-10.6 ; -6.2] | +0.018 [0.004 ; 0.031] | *BIAIS DIFFÉRENTIEL* |
| 5 s *(nominale)* | 3646 | 0.806 [0.783 ; 0.830] | -8.4 [-10.3 ; -6.3] | +0.018 [0.003 ; 0.033] | *BIAIS DIFFÉRENTIEL* |
| 10 s | 3646 | 0.806 [0.781 ; 0.826] | -8.4 [-10.5 ; -6.4] | +0.018 [0.002 ; 0.034] | *BIAIS DIFFÉRENTIEL* |

> **Verdict robuste à l'appariement (2 s / 5 s / 10 s)** — les IC des grandeurs continues se chevauchent entre les trois tolérances.

## Réserves explicites

1. **L'appariement est une hypothèse, pas une donnée.** Deux sources n'observent jamais le même instant. Tout désaccord mesuré ici mélange *désaccord de mesure* et *désaccord d'appariement* ; la seule protection est que la tolérance temporelle (5 s) reste très inférieure à la fenêtre d'issue du label. Depuis le 30/07, ce n'est plus une promesse : le balayage 2 s / 5 s / 10 s est EXÉCUTÉ à chaque run (section « Robustesse à l'appariement »), sur les grandeurs continues et leurs IC.
2. **Les non-appariés ne sont pas aléatoires.** Un événement faible sans homologue fort est probablement un événement d'un type particulier (palier hors de la profondeur publiée, épisode tronqué…). L'analyse ne porte donc que sur l'intersection, qui peut être plus « facile » que la population entière.
3. **Un palier n'est pas un ordre.** Le label faible agrège des ordres de plusieurs acteurs sur un même palier ; le fort suit un ordre. Une part irréductible du désaccord est *définitionnelle* et ne se corrigera par aucun raffinement du proxy.
4. **Les covariables viennent de `provenance`**, donc de ce que les sources ont bien voulu exposer. Une covariable manquante peut cacher un différentiel : « pas de biais détecté » signifie *pas sur les axes regardés*, jamais *pas de biais*.
5. **Le contrôle (d) est un témoin NON DÉCISIF, et c'est mesuré.** Son hypothèse nulle est *l'erreur iid conditionnellement à X* : il ne voit un biais que s'il déforme la PRÉDICTIBILITÉ. Contrôle positif du 29/07 : sur une fixture au biais différentiel planté (retrouvé par (b)), il a rendu p = 0,43. Il est depuis EXCLU du verdict ; il reste calculé parce que seul un POSITIF de sa part serait informatif. Le témoin principal reste (b).
6. **Aucune conclusion économique.** Ce rapport porte sur la signification du label, pas sur sa valeur. Le backtest reste négatif en directionnel (cf. `backtest_eco.py`).

_run en 98 s · code `eea6b346638a`_
