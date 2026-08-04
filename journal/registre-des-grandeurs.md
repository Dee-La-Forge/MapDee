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
| **candidats déclarés** | *à remplir avant le premier calcul* |
| **date de la déclaration** | — |
| **source** | `03_EconoPhysique.md`, partie I |
| **procédure de contrôle** | taux de fausses découvertes à 10 %, Benjamini-Hochberg, sur l'ensemble des candidats jugés à É4 — résolutions et symboles compris (`decisions/ADR-001`) |

**Tout candidat ajouté après cette déclaration rouvre le compte, et le dit.**

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
| — | *(vide — aucun candidat déposé)* | — | — | — | — | — |

---

## Ce qui est interdit ici

* retirer une ligne ;
* modifier une ligne existante — on en ajoute une nouvelle ;
* inscrire une élimination sans son chiffre ;
* déposer une fiche après avoir calculé la grandeur.
