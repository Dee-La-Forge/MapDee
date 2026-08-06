# ADR-006 — Sortir un candidat d'une vague gelée : par re-déclaration, jamais par élimination discrète

**Statut : EN RÉDACTION** — la décision appartient à Meddy. Écrite le
06/08/2026, au moment où la conséquence est apparue comme un CHOIX, pour ne
pas la rencontrer plus tard comme un blocage.

## Le couplage dur, nommé

La barrière de vague (posée le 06/08, `boucle.py`) exige que **chaque**
candidat de la vague 1 soit terminal ou à É4 avant que BH ne tourne. Or
`extracteurs.ABSENTS` recense **7 fiches sur 16 sans extracteur** :

| fiches | ce qui manque |
|---|---|
| A2, B4 | les définitions de B7 (« contact », « mur ») |
| A3, B3, D2 | le flux exécuté (jointure non construite) |
| A5 | sa calibration (noyau, dizaines de minutes/jour-symbole) |
| A6 | son coût — la fiche elle-même hésite (heures/jour-symbole, É1 ❌) |

**Conséquence : un extracteur jamais construit gèle l'É4 de toute la
vague, définitivement.** C'est le comportement voulu — « le compte est
déclaré AVANT » n'a pas d'autre sens — mais il faut que la sortie soit
écrite d'avance.

## La règle proposée

1. La **seule** sortie légitime d'un candidat d'une vague gelée est une
   **ADR qui re-déclare la vague** : le candidat passe `réorientée` au
   registre avec la raison (« extracteur non construit, décision ADR-00x »),
   et le nouveau compte de la vague est déclaré dans l'ADR même.
2. **Jamais** d'élimination discrète : un candidat qui disparaît sans ADR
   fausserait le dénominateur déclaré — ce serait la fuite de multiplicité
   par la porte de service.
3. La re-déclaration est **irréversible dans la vague** : un candidat sorti
   ne réintègre pas la vague 1 ; s'il devient constructible plus tard, il
   entre en vague 2+ avec son compte.
4. Tant qu'aucune ADR de re-déclaration n'est acceptée, le blocage est le
   comportement **correct** : il force à trancher (construire A6 ou le
   sortir) au lieu de laisser filer.

## Ce que ça ne décide pas

Quels candidats sortir, et quand. C'est l'objet d'ADR futures, une par
re-déclaration, chacune avec son compte. Celle-ci ne fixe que le MÉCANISME.
