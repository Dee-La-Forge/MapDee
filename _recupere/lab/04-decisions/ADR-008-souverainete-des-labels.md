# ADR-008 — Souveraineté des labels : le nœud d'abord, l'achat en secours

**Statut** : acceptée (2026-07-29, décision Meddy)

## Contexte
Le plan initial prévoyait d'ACHETER le L4 Hyperliquid (P2) chez un fournisseur
tiers, et de ne monter le nœud qu'après la porte P4. Deux vérifications du 29/07
changent la donne :

1. Le L4 n'est **pas un produit** : c'est une donnée que le nœud Hyperliquid
   produit déjà. Un nœud **non-validateur standard** suffit — `--write-order-statuses`
   (+ `--write-fills`, `--write-raw-book-diffs`), aucune compilation particulière.
2. L'API publique ne peut PAS s'y substituer : `orderUpdates` et `openOrders` sont
   limités à sa propre adresse, et un spoof ne s'exécute jamais — il est donc
   invisible dans le flux `trades`.

## Décision
**Aucune dépendance à un fournisseur externe pour la génération des labels.**
La voie normale est le **nœud auto-hébergé**. L'achat de données devient un
**plan de secours**, à n'activer que si le pipeline nœud se révèle incomplet ou
insuffisant pour reconstruire les labels.

Séquence : **P2a** (faisabilité du nœud) → **P2b** (achat) *seulement en cas d'échec*.

## Conséquences

**Gagné** — coût du projet quasi nul ; aucune dépendance à un tiers qui peut
changer ses prix, ses conditions ou disparaître ; et la donnée est la MÊME que
celle dont les fournisseurs se servent, sans intermédiaire ni retraitement opaque.

**Perdu** — le nœud ne produit **aucun historique** : il démarre le jour où on le
lance. *Atténuation* : le recorder multi-venue tourne depuis le 28/07 ; un nœud
lancé maintenant recouvre la même fenêtre, ce qu'exige justement le test de
transfert. L'historique ne fait que gagner du temps.

**Tension assumée avec le plan initial.** Celui-ci plaçait le nœud après la porte
P4 pour éviter le « piège du nœud » : des semaines d'infra avant le moindre
chiffre. Ce n'est plus le même risque — **P0 est franchi**, le chiffre existe
(AUC 0,712/0,667 répliqué, coût de traversée 5,1×). Monter le nœud n'est plus
prématuré, c'est l'étape suivante d'un résultat déjà mesuré.

**Garde-fou** : P2a est **limité à ~1 jour de travail**. Au-delà, on n'insiste
pas — on bascule sur P2b plutôt que de laisser l'infra manger le projet. C'est
la discipline du plan initial, conservée sous une autre forme.
