# Registre des grandeurs

> **C'est la mémoire de la boucle d'exploration, et sa machine à états.**
> Une session l'ouvre, voit où en est chaque candidat, et prend le suivant.
> Sans lui, « quoi ensuite » redevient un jugement — et une session retestera ce
> qu'une autre a déjà éliminé.
>
> **C'est un rapport de mesure, pas un cadrage : il ne se réécrit jamais.**
> Une élimination se corrige **par un ajout**, jamais par un effacement. Si on
> s'est trompé, on sait exactement pourquoi on avait sorti un candidat, et on
> peut rouvrir — par ADR, jamais en silence.
>
> Exigé par `05_Protocole_de_selection.md` §5. **Aucun calcul de banc ne se fait
> avant qu'un candidat n'y ait sa ligne.**

---

## Le nombre de candidats, déclaré AVANT le premier calcul

C'est la **première protection contre la multiplicité** (`05` §4). On ne
découvre pas à la fin combien de tests ont été faits : à seuil nominal, une
fraction ressort « significative » sans aucun phénomène, mécaniquement.

| | |
|---|---|
| **candidats déclarés** | **16** — A1-A6, B1-B5, C1-C3, D1-D2. Le **témoin trivial est hors compte** : il n'est pas un test, il ne peut pas être retenu (`05` §4, décision D10 de `chantiers/C9-harnais.md`) |
| **date de la déclaration** | **05/08/2026** — validée par Meddy, avant tout calcul de banc |
| **source** | `03_EconoPhysique.md`, partie I |
| **procédure de contrôle** | taux de fausses découvertes à 10 %, Benjamini-Hochberg, sur l'ensemble des **candidats** jugés à É4 — **et eux seuls** : résolutions et symboles sont des conjonctions internes, pas des tests (`decisions/ADR-001`, II.3). *Corrigé le 05/08/2026 : une version antérieure de cette ligne écrivait « résolutions et symboles compris », à rebours de l'ADR qu'elle citait — aucune ligne de mesure n'existait encore.* |

**Tout candidat ajouté après cette déclaration rouvre le compte, et le dit.**

*Précision du 06/08/2026 (audit externe, critique 1 — le compte n'avait pas
de date de gel)* : **le compte est PAR VAGUE.** La vague 1 = les 16
ci-dessus, **gelée le 05/08** — rien ne s'y ajoute, jamais ; son BH se calcule
sur 16. Les familles instruites dans C0 forment la **vague 2**, dont le
compte gèlera **avant son premier calcul**, à la clôture de C0 par
tarissement (règle dans `chantiers/C0-litterature.md` §5 pré) — jamais au
jour du dernier É4. Le nombre de vagues est publié avec tout résultat.

---

## Les états

Un candidat occupe **un seul** état à la fois. Le passage d'un état au suivant
écrit une ligne — jamais une modification de la précédente.

| état | ce qu'il veut dire |
|---|---|
| `déposée` | la fiche existe, au format d'`05` §1. Rien n'a été calculé. |
| `ÉS` · `É0` · `É1` · `É2` · `É3` · `É4` | l'épreuve en cours |
| `sous surveillance` | a passé É2 entre les deux bornes de redite — É4 devra montrer un apport net |
| `doublon présumé` | a passé É2 au-dessus de la borne haute — ne survit qu'en passant É4 avec un apport significatif |
| `réorientée` | ne se calcule que côté L4 → **fabrique la vérité, ne s'affiche pas**. Pas éliminée : sortie du chemin produit. |
| `éliminée` | une épreuve échouée. **La ligne porte le chiffre qui l'a fait tomber.** |
| `retenue` | a passé les cinq épreuves. Entre dans le bloc de référence d'É2 pour les suivantes. |
| `témoin trivial` | déclaré d'avance, sert de plancher au premier candidat. **Ne peut jamais être retenu.** |

---

## Le format d'une ligne

```
date · nom · état · épreuve · LE CHIFFRE · périmètre · qui l'a proposée
```

* **le chiffre** est obligatoire sur toute élimination et sur tout passage
  d'épreuve. **Aucune décision sur une opinion.**
* **le périmètre** est celui déclaré dans la fiche avant le calcul — il ne
  s'étend pas après avoir vu un résultat.
* le **plancher de détection** mesuré à ÉS s'inscrit ici **même quand la méthode
  passe** : c'est lui qui rendra un futur négatif interprétable.

---

## Le registre

| date | nom | état | épreuve | chiffre | périmètre | proposée par |
|---|---|---|---|---|---|---|
| 2026-08-05 | T0 · masse brute au palier | témoin trivial | — | — | J3 | le protocole (`05` §4), déclaré avant tout calcul |
| 2026-08-05 | méthode banc-v4 · détecteur absorption | ÉS | ÉS | plancher 0,5× — ADMIS (barre 2,0, ADR-004) | synthétique, 8 graines-jours | C9 harnais |
| 2026-08-05 | méthode banc-v4 · détecteur recharge | ÉS | ÉS | plancher 1,0× — ADMIS (barre 2,0, ADR-004) | synthétique, 8 graines-jours | C9 harnais |
| 2026-08-05 | méthode banc-v4 · détecteur leurre | ÉS | ÉS | plancher 8,0× — ÉCARTÉ (barre 2,0, ADR-004) : aucun négatif leurre interprétable | synthétique, 8 graines-jours | C9 harnais |
| 2026-08-05 | A1 · OFI | déposée | — | — | J3 | 03 partie I (dépôt par la boucle) |
| 2026-08-05 | A2 · OFI localisé au mur | déposée | — | — | J3 | 03 partie I (dépôt par la boucle) |
| 2026-08-05 | A3 · flux signé e/r/a | déposée | — | — | J3 | 03 partie I (dépôt par la boucle) |
| 2026-08-05 | A4 · microprice | déposée | — | — | J3 | 03 partie I (dépôt par la boucle) |
| 2026-08-05 | A5 · propagateur | déposée | — | — | J3 | 03 partie I (dépôt par la boucle) |
| 2026-08-05 | A6 · auto-excitation (Hawkes) | déposée | — | — | J3 | 03 partie I (dépôt par la boucle) |
| 2026-08-05 | B1 · hazard rate (version palier) | déposée | — | — | J3 | 03 partie I (dépôt par la boucle) |
| 2026-08-05 | B2 · résilience | déposée | — | — | J3 | 03 partie I (dépôt par la boucle) |
| 2026-08-05 | B3 · réapprovisionnement (iceberg) | déposée | — | — | J3 | 03 partie I (dépôt par la boucle) |
| 2026-08-05 | B4 · absorption au contact | déposée | — | — | J8 | 03 partie I (dépôt par la boucle) |
| 2026-08-05 | B5 · premier passage | déposée | — | — | J3 | 03 partie I (dépôt par la boucle) |
| 2026-08-05 | C1 · concentration | déposée | — | — | J3 | 03 partie I (dépôt par la boucle) |
| 2026-08-05 | C2 · forme et courbure | déposée | — | — | J3 | 03 partie I (dépôt par la boucle) |
| 2026-08-05 | C3 · diffusion anormale | déposée | — | — | J3 | 03 partie I (dépôt par la boucle) |
| 2026-08-05 | D1 · ralentissement critique | déposée | — | — | J8 | 03 partie I (dépôt par la boucle) |
| 2026-08-05 | D2 · cascades | déposée | — | — | J8 | 03 partie I (dépôt par la boucle) |
| 2026-08-05 | méthode banc-v5 · détecteur leurre | ÉS | ÉS | plancher <= 61x (bas de gamme) — ADMIS (barre 485, ADR-005, unité réelle) | synthétique, 8 graines-jours | C9 harnais @cec7fc0 |
| 2026-08-05 | méthode banc-v5 · détecteur recharge | ÉS | ÉS | plancher <= 61x (bas de gamme) — ADMIS (barre 485, ADR-005) | synthétique, 8 graines-jours | C9 harnais @cec7fc0 |
| 2026-08-05 | méthode banc-v5 · détecteur absorption | ÉS | ÉS | REJETÉ au bras nul v5 : centrage instable (μ0 −0,40 vs −0,04 entre lots de graines), FP 64 % | synthétique, 32 nuls neufs | C9 harnais @cec7fc0 |
| 2026-08-06 | A1 · OFI | É1 | É0 | aucun doublon parmi les vivants | J3 | la boucle @fadde96 |
| 2026-08-06 | A1 · OFI | É2 | É1 | admissible — mesure de dégradation due avant É4 | J3 | la boucle @fadde96 |
| 2026-08-06 | A1 · OFI | É3 | É2 | ρmax=0.025 | J3 | la boucle @fadde96 |
| 2026-08-06 | A4 · microprice | É1 | É0 | aucun doublon parmi les vivants | J3 | la boucle @fadde96 |
| 2026-08-06 | A4 · microprice | É2 | É1 | admissible — mesure de dégradation due avant É4 | J3 | la boucle @fadde96 |
| 2026-08-06 | A4 · microprice | É3 | É2 | ρmax=0.094 | J3 | la boucle @fadde96 |
| 2026-08-06 | B1 · hazard rate (version palier) | É1 | É0 | aucun doublon parmi les vivants | J3 | la boucle @fadde96 |
| 2026-08-06 | B1 · hazard rate (version palier) | É2 | É1 | admissible — mesure de dégradation due avant É4 | J3 | la boucle @fadde96 |
| 2026-08-06 | B1 · hazard rate (version palier) | É3 | É2 | ρmax=0.071 | J3 | la boucle @fadde96 |
| 2026-08-06 | B2 · résilience | É1 | É0 | aucun doublon parmi les vivants | J3 | la boucle @fadde96 |
| 2026-08-06 | B2 · résilience | É2 | É1 | admissible — mesure de dégradation due avant É4 | J3 | la boucle @fadde96 |
| 2026-08-06 | B2 · résilience | É3 | É2 | ρmax=0.083 | J3 | la boucle @fadde96 |
| 2026-08-06 | B5 · premier passage | É1 | É0 | aucun doublon parmi les vivants | J3 | la boucle @fadde96 |
| 2026-08-06 | B5 · premier passage | É2 | É1 | admissible — mesure de dégradation due avant É4 | J3 | la boucle @fadde96 |
| 2026-08-06 | B5 · premier passage | É3 | É2 | ρmax=0.179 | J3 | la boucle @fadde96 |
| 2026-08-06 | C1 · concentration | É1 | É0 | aucun doublon parmi les vivants | J3 | la boucle @fadde96 |
| 2026-08-06 | C1 · concentration | É2 | É1 | admissible — mesure de dégradation due avant É4 | J3 | la boucle @fadde96 |
| 2026-08-06 | C1 · concentration | É3 | É2 | ρmax=0.416 | J3 | la boucle @fadde96 |
| 2026-08-06 | C2 · forme et courbure | É1 | É0 | aucun doublon parmi les vivants | J3 | la boucle @fadde96 |
| 2026-08-06 | C2 · forme et courbure | É2 | É1 | admissible — mesure de dégradation due avant É4 | J3 | la boucle @fadde96 |
| 2026-08-06 | C2 · forme et courbure | É3 | É2 | ρmax=0.152 | J3 | la boucle @fadde96 |
| 2026-08-06 | C3 · diffusion anormale | É1 | É0 | aucun doublon parmi les vivants | J3 | la boucle @fadde96 |
| 2026-08-06 | C3 · diffusion anormale | É2 | É1 | admissible — mesure de dégradation due avant É4 | J3 | la boucle @fadde96 |
| 2026-08-06 | C3 · diffusion anormale | É3 | É2 | ρmax=0.088 | J3 | la boucle @fadde96 |
| 2026-08-06 | D1 · ralentissement critique | É1 | É0 | seul dans son périmètre | J8 | la boucle @02866ab |
| 2026-08-06 | D1 · ralentissement critique | É2 | É1 | admissible — mesure de dégradation due avant É4 | J8 | la boucle @02866ab |
| 2026-08-06 | D1 · ralentissement critique | É3 | É2 | ρmax=0.007 | J8 | la boucle @02866ab |
| 2026-08-06 | D1 · ralentissement critique | déposée | — | repasse — ADR-008, périmètre J8 ré-déclaré à 15 jour-symboles (05 §7) | J8 | ADR-008 |

---

## Ce qui est interdit ici

* retirer une ligne ;
* modifier une ligne existante — on en ajoute une nouvelle ;
* inscrire une élimination sans son chiffre ;
* déposer une fiche après avoir calculé la grandeur.
