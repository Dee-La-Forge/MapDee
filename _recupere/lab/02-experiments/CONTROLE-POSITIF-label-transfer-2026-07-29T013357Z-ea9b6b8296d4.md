# Transfert de labels — le label faible dit-il ce qu'on croit ? · run `2026-07-29T013357Z` · config `ea9b6b8296d4`

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
  "code_sha": "4752322f84de"
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

**Appariement** : 3691 couples (faible 3872 → 95 % apparié · fort 3993 → 92 %) · clusters effectifs **120** → 30.8 événement(s)/cluster.

Covariables partagées : `c_dist_rel`, `c_delay_s`, `c_age_s`, `c_calm`, `c_notional`, `c_occupancy`

### 1. Accord brut

| | fort : **a fui** | fort : **a tenu** |
|---|---|---|
| faible : **a fui** | 1886 | **280** (faux « a fui ») |
| faible : **a tenu** | **141** (fausse « a tenu ») | 1384 |

- taux d'accord : **88.6 %** · IC95 clusterisé [87.2 ; 89.8] % (bootstrap par cluster)
- **κ de Cohen : 0.768** · IC95 [0.739 ; 0.795] — l'accord au-delà du hasard ; c'est κ qui compte, pas le taux brut (deux labels à 70 % de « a fui » s'accordent à 58 % en tirant à pile ou face)
- prévalence « a fui » : faible **58.7 %** vs fort **54.9 %**
- **effet de grappe : ×1.36** — l'IC correct est 1.36 fois plus large que l'IC naïf

### 2. Où le faible se trompe-t-il ?

Taux de désaccord par quartile (± 1 ET **clusterisée**) — c'est ce tableau qui dit *quoi corriger* dans le proxy. `α` = fuites manquées, `β` = fausses alertes : le désaccord brut seul monte mécaniquement là où le taux de base approche 50 %, sans erreur supplémentaire.

| covariable | quartile | n | désaccord | ± ET | α | β | base |
|---|---|---|---|---|---|---|---|
| `c_dist_rel` | Q1 | 923 | **10.9 %** | 1.2 | 8.0 % | 14.5 % | 54.5 % |
| `c_dist_rel` | Q2 | 923 | **11.6 %** | 1.2 | 7.0 % | 17.0 % | 54.2 % |
| `c_dist_rel` | Q3 | 922 | **10.6 %** | 1.0 | 5.7 % | 16.6 % | 55.0 % |
| `c_dist_rel` | Q4 | 923 | **12.5 %** | 1.2 | 7.2 % | 19.2 % | 56.0 % |
| `c_delay_s` | Q1 | 923 | **9.9 %** | 1.0 | 5.8 % | 14.6 % | 54.0 % |
| `c_delay_s` | Q2 | 923 | **11.2 %** | 1.1 | 7.0 % | 16.0 % | 54.0 % |
| `c_delay_s` | Q3 | 922 | **11.5 %** | 1.2 | 6.5 % | 18.1 % | 56.9 % |
| `c_delay_s` | Q4 | 923 | **13.1 %** | 1.3 | 8.5 % | 18.7 % | 54.8 % |
| `c_age_s` | Q1 | 923 | **16.6 %** | 1.4 | 6.2 % | 20.2 % | 26.0 % |
| `c_age_s` | Q2 | 925 | **12.1 %** | 1.4 | 7.7 % | 16.3 % | 49.0 % |
| `c_age_s` | Q3 | 921 | **9.3 %** | 1.0 | 7.0 % | 13.3 % | 63.3 % |
| `c_age_s` | Q4 | 922 | **7.6 %** | 1.0 | 6.7 % | 11.7 % | 81.5 % |
| `c_calm` | Q1 | 923 | **15.1 %** | 1.4 | 5.7 % | 22.9 % | 45.5 % |
| `c_calm` | Q2 | 923 | **11.3 %** | 1.3 | 6.0 % | 16.7 % | 50.6 % |
| `c_calm` | Q3 | 922 | **10.0 %** | 1.1 | 7.1 % | 13.5 % | 55.0 % |
| `c_calm` | Q4 | 923 | **9.3 %** | 1.0 | 8.4 % | 11.4 % | 68.6 % |
| `c_notional` | Q1 | 925 | **13.8 %** | 1.3 | 5.5 % | 51.8 % | 82.1 % |
| `c_notional` | Q2 | 921 | **14.4 %** | 1.4 | 7.5 % | 26.3 % | 63.3 % |
| `c_notional` | Q3 | 924 | **9.0 %** | 1.1 | 7.4 % | 10.5 % | 48.5 % |
| `c_notional` | Q4 | 921 | **8.4 %** | 0.9 | 9.3 % | 8.0 % | 25.7 % |
| `c_occupancy` | Q1 | 923 | **13.7 %** | 1.5 | 8.5 % | 17.5 % | 43.1 % |
| `c_occupancy` | Q2 | 923 | **13.3 %** | 1.2 | 6.7 % | 20.4 % | 51.6 % |
| `c_occupancy` | Q3 | 923 | **10.7 %** | 1.1 | 7.0 % | 15.8 % | 57.4 % |
| `c_occupancy` | Q4 | 922 | **7.9 %** | 0.9 | 6.1 % | 11.7 % | 67.6 % |

→ Désaccord maximal sur `c_age_s` Q1 (**16.6 %**), minimal sur `c_age_s` Q4 (7.6 %). Écart **9.0 pts**.

### 3. BIAISÉ ou BRUITÉ ? (la question décisive)

**(a) Asymétrie des taux d'erreur CONDITIONNELS** — α = P(faible « a tenu » | vérité « a fui ») = **7.0 %** ; β = P(faible « a fui » | vérité « a tenu ») = **16.8 %**. α − β = **-9.9 pts**, IC95 par bootstrap *par cluster* [-11.7 ; -8.0] pts → p = **< 0.0025**.

  *(Le décalage de prévalence brut — +3.77 pts, p clusterisé 1.182e-11 vs p naïf 9.359e-12 — est DESCRIPTIF et pas diagnostique : un bruit parfaitement symétrique décale déjà la prévalence vers 50 %.)*

**(b) Différentialité** — pente clusterisée du taux d'erreur **à vérité fixée**, sur chaque covariable standardisée. Une pente ≠ 0 = le proxy se trompe *plus ici que là* = **biais non corrigible**.

> Conditionner sur la vérité n'est pas un détail : régresser l'erreur signée `faible − fort` sur X déclare « biaisé » un bruit parfaitement symétrique, parce que E[faible − fort | X] = p·(1 − 2·P(fort=1|X)) dépend de X dès que le taux de base dépend de X. Le selftest a attrapé cette erreur dans la première version de ce harnais.

| taux | covariable | n | pente | ET clust. | p (Holm, **clusterisé**) | p (Holm, naïf) | inflation ET |
|---|---|---|---|---|---|---|---|
| β (a tenu) | `c_calm` | 1664 | -0.0430 ★ | 0.0088 | **1.117e-05** | 2.608e-05 | ×0.96 |
| β (a tenu) | `c_notional` | 1664 | -0.0450 ★ | 0.0095 | **2.244e-05** | 9.493e-06 | ×1.04 |
| β (a tenu) | `c_age_s` | 1664 | -0.0288 ★ | 0.0085 | **0.007364** | 0.01652 | ×0.93 |
| β (a tenu) | `c_occupancy` | 1664 | -0.0224 | 0.0107 | **0.3318** | 0.13 | ×1.17 |
| β (a tenu) | `c_dist_rel` | 1664 | +0.0166 | 0.0091 | **0.5468** | 0.4935 | ×0.99 |
| β (a tenu) | `c_delay_s` | 1664 | +0.0174 | 0.0100 | **0.577** | 0.4657 | ×1.09 |
| α (a fui) | `c_dist_rel` | 2027 | -0.0051 | 0.0057 | **1** | 1 | ×1.01 |
| α (a fui) | `c_delay_s` | 2027 | +0.0057 | 0.0055 | **1** | 1 | ×0.97 |
| α (a fui) | `c_notional` | 2027 | -0.0002 | 0.0039 | **1** | 1 | ×0.68 |
| α (a fui) | `c_occupancy` | 2027 | -0.0078 | 0.0065 | **1** | 1 | ×1.15 |
| α (a fui) | `c_age_s` | 2027 | +0.0003 | 0.0052 | **1** | 1 | ×0.93 |
| α (a fui) | `c_calm` | 2027 | +0.0068 | 0.0060 | **1** | 1 | ×1.06 |

★ = significatif après correction de Holm. La colonne « inflation ET » est le prix du clustering : c'est le facteur dont on aurait sur-vendu chaque significativité en l'ignorant.

**(c) Compression de l'échelle** — `ratio_faible = 0.228(±0.004) + 0.578(±0.008)·ratio_fort`. Une erreur purement aléatoire laisse la pente ≈ 1 ; une pente << 1 avec ordonnée > 0 écrase l'échelle vers « a fui ».

**(d) Contrôle par dégradation simulée** — on retourne les labels FORTS aux taux observés (α=0.059, β=0.166) mais **indépendamment des covariables**, en tirage apparié par cluster. Prédictibilité du faible RÉEL : AUC **0.811** ; des contrefaçons « pur bruit » : 0.798 [0.768 ; 0.826] · écart apparié **+0.012** → p bilatéral **0.43**.

> **Verdict : BIAIS DIFFÉRENTIEL** — le taux d'erreur du label faible dépend des covariables, À VÉRITÉ FIXÉE. Non corrigible par plus de données : un modèle entraîné dessus apprend la MESURE, pas le phénomène.

### 4. Métrique de transfert (porte P4)

Split temporel + embargo 60 min — train **2569** → test **1025** (⚠ purge des 69 clusters à cheval abandonnée (elle ne laissait que 14 lignes de test sur 1025) : les acteurs sont persistants → **fuite d'identité possible**, pas de fuite temporelle). Features = celles de la source FAIBLE (seul scénario déployable : en production, pas de L4).

| entraîné sur | évalué contre | AUC hors-échantillon |
|---|---|---|
| FORT | fort *(plafond)* | **0.877** |
| FORT | faible | 0.811 |
| FAIBLE | faible *(le chiffre de P0)* | 0.811 |
| FAIBLE | fort *(**le chiffre qui décide**)* | **0.850** |

- **écart de transfert** (plafond − faible→fort) : **+0.027** · IC95 par bootstrap **par cluster** [0.009 ; 0.048] (400 tirages)
- concordance des classements produits par les deux entraînements : ρ de Spearman **+0.874** — à l'usage (dimensionner un ordre traversant) c'est le classement qui compte, pas la valeur de l'AUC

> **PORTE P4 : transfert PARTIEL** — il reste du signal réel, mais le proxy en coûte une part mesurable. Chiffrer ce coût avant de dimensionner quoi que ce soit dessus.

---

## ETHUSDT

**Appariement** : 3646 couples (faible 3845 → 95 % apparié · fort 3974 → 92 %) · clusters effectifs **120** → 30.4 événement(s)/cluster.

Covariables partagées : `c_dist_rel`, `c_delay_s`, `c_age_s`, `c_calm`, `c_notional`, `c_occupancy`

### 1. Accord brut

| | fort : **a fui** | fort : **a tenu** |
|---|---|---|
| faible : **a fui** | 1862 | **236** (faux « a fui ») |
| faible : **a tenu** | **114** (fausse « a tenu ») | 1434 |

- taux d'accord : **90.4 %** · IC95 clusterisé [89.2 ; 91.7] % (bootstrap par cluster)
- **κ de Cohen : 0.806** · IC95 [0.783 ; 0.830] — l'accord au-delà du hasard ; c'est κ qui compte, pas le taux brut (deux labels à 70 % de « a fui » s'accordent à 58 % en tirant à pile ou face)
- prévalence « a fui » : faible **57.5 %** vs fort **54.2 %**
- **effet de grappe : ×1.23** — l'IC correct est 1.23 fois plus large que l'IC naïf

### 2. Où le faible se trompe-t-il ?

Taux de désaccord par quartile (± 1 ET **clusterisée**) — c'est ce tableau qui dit *quoi corriger* dans le proxy. `α` = fuites manquées, `β` = fausses alertes : le désaccord brut seul monte mécaniquement là où le taux de base approche 50 %, sans erreur supplémentaire.

| covariable | quartile | n | désaccord | ± ET | α | β | base |
|---|---|---|---|---|---|---|---|
| `c_dist_rel` | Q1 | 912 | **9.1 %** | 1.0 | 5.5 % | 13.6 % | 55.8 % |
| `c_dist_rel` | Q2 | 911 | **11.3 %** | 1.1 | 6.7 % | 16.6 % | 53.8 % |
| `c_dist_rel` | Q3 | 911 | **9.0 %** | 0.9 | 6.6 % | 11.7 % | 52.9 % |
| `c_dist_rel` | Q4 | 912 | **9.0 %** | 1.0 | 4.2 % | 14.6 % | 54.3 % |
| `c_delay_s` | Q1 | 912 | **9.4 %** | 1.0 | 5.6 % | 13.7 % | 52.7 % |
| `c_delay_s` | Q2 | 911 | **10.2 %** | 1.1 | 6.2 % | 14.6 % | 52.7 % |
| `c_delay_s` | Q3 | 911 | **9.5 %** | 1.1 | 5.4 % | 14.5 % | 54.7 % |
| `c_delay_s` | Q4 | 912 | **9.2 %** | 1.0 | 5.8 % | 13.7 % | 56.7 % |
| `c_age_s` | Q1 | 912 | **13.3 %** | 1.2 | 5.2 % | 16.0 % | 25.1 % |
| `c_age_s` | Q2 | 912 | **11.1 %** | 1.2 | 7.2 % | 14.9 % | 50.0 % |
| `c_age_s` | Q3 | 912 | **7.8 %** | 1.0 | 5.8 % | 11.2 % | 62.7 % |
| `c_age_s` | Q4 | 910 | **6.3 %** | 0.8 | 5.0 % | 11.0 % | 79.0 % |
| `c_calm` | Q1 | 912 | **13.5 %** | 1.3 | 7.3 % | 18.6 % | 45.1 % |
| `c_calm` | Q2 | 911 | **9.7 %** | 1.1 | 5.3 % | 14.4 % | 51.9 % |
| `c_calm` | Q3 | 911 | **7.7 %** | 0.9 | 5.2 % | 10.6 % | 53.2 % |
| `c_calm` | Q4 | 912 | **7.6 %** | 0.9 | 5.6 % | 11.5 % | 66.6 % |
| `c_notional` | Q1 | 913 | **13.1 %** | 1.3 | 6.2 % | 40.5 % | 79.7 % |
| `c_notional` | Q2 | 912 | **11.3 %** | 1.2 | 6.8 % | 18.4 % | 61.3 % |
| `c_notional` | Q3 | 911 | **8.1 %** | 1.0 | 5.1 % | 10.9 % | 47.5 % |
| `c_notional` | Q4 | 910 | **5.8 %** | 0.8 | 3.5 % | 6.7 % | 28.1 % |
| `c_occupancy` | Q1 | 912 | **10.7 %** | 1.2 | 7.6 % | 13.2 % | 44.5 % |
| `c_occupancy` | Q2 | 913 | **10.6 %** | 1.1 | 5.8 % | 15.7 % | 51.0 % |
| `c_occupancy` | Q3 | 909 | **9.6 %** | 1.0 | 6.6 % | 13.9 % | 58.7 % |
| `c_occupancy` | Q4 | 912 | **7.5 %** | 0.9 | 3.7 % | 13.7 % | 62.5 % |

→ Désaccord maximal sur `c_calm` Q1 (**13.5 %**), minimal sur `c_notional` Q4 (5.8 %). Écart **7.7 pts**.

### 3. BIAISÉ ou BRUITÉ ? (la question décisive)

**(a) Asymétrie des taux d'erreur CONDITIONNELS** — α = P(faible « a tenu » | vérité « a fui ») = **5.8 %** ; β = P(faible « a fui » | vérité « a tenu ») = **14.1 %**. α − β = **-8.4 pts**, IC95 par bootstrap *par cluster* [-10.3 ; -6.4] pts → p = **< 0.0025**.

  *(Le décalage de prévalence brut — +3.35 pts, p clusterisé 4.28e-10 vs p naïf 5.43e-11 — est DESCRIPTIF et pas diagnostique : un bruit parfaitement symétrique décale déjà la prévalence vers 50 %.)*

**(b) Différentialité** — pente clusterisée du taux d'erreur **à vérité fixée**, sur chaque covariable standardisée. Une pente ≠ 0 = le proxy se trompe *plus ici que là* = **biais non corrigible**.

> Conditionner sur la vérité n'est pas un détail : régresser l'erreur signée `faible − fort` sur X déclare « biaisé » un bruit parfaitement symétrique, parce que E[faible − fort | X] = p·(1 − 2·P(fort=1|X)) dépend de X dès que le taux de base dépend de X. Le selftest a attrapé cette erreur dans la première version de ce harnais.

| taux | covariable | n | pente | ET clust. | p (Holm, **clusterisé**) | p (Holm, naïf) | inflation ET |
|---|---|---|---|---|---|---|---|
| β (a tenu) | `c_notional` | 1670 | -0.0439 ★ | 0.0090 | **1.14e-05** | 2.553e-06 | ×1.06 |
| β (a tenu) | `c_calm` | 1670 | -0.0276 ★ | 0.0087 | **0.01651** | 0.01302 | ×1.02 |
| β (a tenu) | `c_age_s` | 1670 | -0.0218 | 0.0079 | **0.05837** | 0.1034 | ×0.93 |
| α (a fui) | `c_occupancy` | 1976 | -0.0097 | 0.0050 | **0.482** | 0.5876 | ×0.95 |
| α (a fui) | `c_notional` | 1976 | -0.0072 | 0.0047 | **0.9993** | 1 | ×0.89 |
| α (a fui) | `c_calm` | 1976 | -0.0029 | 0.0053 | **1** | 1 | ×1.01 |
| α (a fui) | `c_dist_rel` | 1976 | -0.0048 | 0.0051 | **1** | 1 | ×0.96 |
| α (a fui) | `c_delay_s` | 1976 | -0.0003 | 0.0050 | **1** | 1 | ×0.95 |
| β (a tenu) | `c_delay_s` | 1670 | -0.0016 | 0.0093 | **1** | 1 | ×1.09 |
| β (a tenu) | `c_dist_rel` | 1670 | -0.0010 | 0.0090 | **1** | 1 | ×1.05 |
| α (a fui) | `c_age_s` | 1976 | -0.0034 | 0.0052 | **1** | 1 | ×1.00 |
| β (a tenu) | `c_occupancy` | 1670 | -0.0069 | 0.0096 | **1** | 1 | ×1.13 |

★ = significatif après correction de Holm. La colonne « inflation ET » est le prix du clustering : c'est le facteur dont on aurait sur-vendu chaque significativité en l'ignorant.

**(c) Compression de l'échelle** — `ratio_faible = 0.223(±0.005) + 0.586(±0.008)·ratio_fort`. Une erreur purement aléatoire laisse la pente ≈ 1 ; une pente << 1 avec ordonnée > 0 écrase l'échelle vers « a fui ».

**(d) Contrôle par dégradation simulée** — on retourne les labels FORTS aux taux observés (α=0.057, β=0.148) mais **indépendamment des covariables**, en tirage apparié par cluster. Prédictibilité du faible RÉEL : AUC **0.816** ; des contrefaçons « pur bruit » : 0.803 [0.774 ; 0.825] · écart apparié **+0.012** → p bilatéral **0.43**.

> **Verdict : BIAIS DIFFÉRENTIEL** — le taux d'erreur du label faible dépend des covariables, À VÉRITÉ FIXÉE. Non corrigible par plus de données : un modèle entraîné dessus apprend la MESURE, pas le phénomène.

### 4. Métrique de transfert (porte P4)

Split temporel + embargo 60 min — train **2540** → test **1000** (⚠ purge des 68 clusters à cheval abandonnée (elle ne laissait que 0 lignes de test sur 1000) : les acteurs sont persistants → **fuite d'identité possible**, pas de fuite temporelle). Features = celles de la source FAIBLE (seul scénario déployable : en production, pas de L4).

| entraîné sur | évalué contre | AUC hors-échantillon |
|---|---|---|
| FORT | fort *(plafond)* | **0.876** |
| FORT | faible | 0.816 |
| FAIBLE | faible *(le chiffre de P0)* | 0.802 |
| FAIBLE | fort *(**le chiffre qui décide**)* | **0.855** |

- **écart de transfert** (plafond − faible→fort) : **+0.021** · IC95 par bootstrap **par cluster** [0.010 ; 0.034] (400 tirages)
- concordance des classements produits par les deux entraînements : ρ de Spearman **+0.915** — à l'usage (dimensionner un ordre traversant) c'est le classement qui compte, pas la valeur de l'AUC

> **PORTE P4 : transfert PARTIEL** — il reste du signal réel, mais le proxy en coûte une part mesurable. Chiffrer ce coût avant de dimensionner quoi que ce soit dessus.

---

## Réplication entre symboles (le juge de paix)

| symbole | κ | accord | α | β | différentiel ? | AUC faible→fort | écart transfert |
|---|---|---|---|---|---|---|---|
| BTCUSDT | 0.768 | 88.6 % | 7.0 % | 16.8 % | **OUI** | 0.850 | +0.027 |
| ETHUSDT | 0.806 | 90.4 % | 5.8 % | 14.1 % | **OUI** | 0.855 | +0.021 |

→ Verdicts biais/bruit : BTCUSDT = *BIAIS DIFFÉRENTIEL* · ETHUSDT = *BIAIS DIFFÉRENTIEL*.

> ⚠ **CE VERDICT EST UN CONTRÔLE POSITIF, PAS UN RÉSULTAT** (relecture Meddy 30/07). Le biais a
> été PLANTÉ dans la fixture `synth-weak-biased` ; le harnais l'a retrouvé — c'est tout ce que ce
> chiffre prouve. Et le mot « répliqué » n'a pas sa place ici : les deux « symboles » sont deux
> tirages du MÊME générateur — répliquer un générateur sur deux fixtures ne teste rien.
> **Aucune de ces lignes ne dit quoi que ce soit du vrai label HL ni du vrai label Binance.**
> Le run RÉEL exige la GLU : source faible/moyenne produite depuis le carnet reconstruit
> (désormais réparé — `recon-repair-20260730.md`), même jour que les labels forts.

## Réserves explicites

1. **L'appariement est une hypothèse, pas une donnée.** Deux sources n'observent jamais le même instant. Tout désaccord mesuré ici mélange *désaccord de mesure* et *désaccord d'appariement* ; la seule protection est que la tolérance temporelle (5 s) reste très inférieure à la fenêtre d'issue du label. **À re-tester** : `--match-tol-ms 2000` puis `10000` doivent rendre le MÊME verdict ; sinon le verdict porte sur l'appariement et pas sur le label.
2. **Les non-appariés ne sont pas aléatoires.** Un événement faible sans homologue fort est probablement un événement d'un type particulier (palier hors de la profondeur publiée, épisode tronqué…). L'analyse ne porte donc que sur l'intersection, qui peut être plus « facile » que la population entière.
3. **Un palier n'est pas un ordre.** Le label faible agrège des ordres de plusieurs acteurs sur un même palier ; le fort suit un ordre. Une part irréductible du désaccord est *définitionnelle* et ne se corrigera par aucun raffinement du proxy.
4. **Les covariables viennent de `provenance`**, donc de ce que les sources ont bien voulu exposer. Une covariable manquante peut cacher un différentiel : « pas de biais détecté » signifie *pas sur les axes regardés*, jamais *pas de biais*.
5. **Le contrôle (d) reste le témoin le plus fragile.** Son tirage est apparié par cluster, ce qui absorbe la corrélation intra-wallet, mais son hypothèse nulle est *l'erreur iid conditionnellement à X* : il ne voit un biais que s'il déforme la PRÉDICTIBILITÉ. Le témoin principal reste (b), qui teste la chose directement.
6. **Aucune conclusion économique.** Ce rapport porte sur la signification du label, pas sur sa valeur. Le backtest reste négatif en directionnel (cf. `backtest_eco.py`).

_run en 13 s · code `4752322f84de`_
