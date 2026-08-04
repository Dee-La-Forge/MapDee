# ADR-005 — Label immunisé au churn du seuil d'archive

**Statut** : acceptée (2026-07-28)

## Contexte
L'archive ne conserve que les paliers `v > med` (`sec-recorder.js:470`) puis
cappe à top-700 ∪ 450-plus-proches (`:487-494`). La **disparition** d'un palier
de l'archive est donc majoritairement un artefact de seuil. Un ancien chantier
en avait tiré ~77 000 faux spoofs.

## Décision
**Interdiction absolue** de tout label ou feature de la forme « le palier a
disparu ». On ne raisonne que sur `peak` et `traded` :
`retiré = max(0, peak − v − traded)`.

## Conséquence
- `y_flee` = `Σ retiré > Σ tradé` sur la fenêtre de contact.
- `y_reject` (forme prix) n'utilise que `mid` : immunisé par construction, il
  sert de contrôle croisé.
- **Limite assumée et documentée** (Data Contract §2.2) : comme
  `v = 0.5·peak + 0.5·mean`, `peak − v − traded` mesure la chute sous le pic non
  expliquée par l'exécution — un proxy honnête, pas une mesure comptable nette.
  C'est le L4 de P2 qui tranchera.
