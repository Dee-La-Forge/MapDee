# ADR-008 — Le 13 décembre revient dans J8, en jour dégradé reconstruit sans veille

**Statut : ACCEPTÉE** — décision de Meddy, 06/08/2026 (« ADR validée,
rebâtis le 13 sans veille »).

## Le constat qui rouvre la décision

L'amendement de J8 (06/08, `journal/2026-08-06_eth-20251213-*.md` puis
`couverture-j8-*.md`) reposait sur une **impossibilité matérielle** :
20251213 sortait à 0 photo (ETH) et 172 photos (BTC). Le diagnostic
pré-enregistré `diag_croisement` a réfuté l'impossibilité : **le flux du
13 est propre** (rejoué à froid, zéro croisement, les deux symboles) — la
corruption venait de la CHAUFFE, héritée du soir empoisonné du 12
(`journal/2026-08-06_anatomie-incident-12-15.md`).

## La décision

1. **20251213 (BTC et ETH) est reconstruit SANS VEILLE** — le mode
   « premier jour d'archive » de `construit/jour.py`, forcé par
   `GON_SANS_VEILLE=1` : 8 h de chauffe sur son propre matin, émission
   h08-h23, ~66 % de journée attendue. Il entre dans J8 comme **jour
   DÉGRADÉ documenté**, au même titre que les 12 et 15.
2. **Le périmètre J8 est ré-déclaré : « 09-16, 16 jour-symboles », dont
   SIX dégradés** (12×2 à ~70 %, 13×2 à ~66 %, 15×2 à ~50 %) — couverture
   publiée, jamais maquillée.
3. **`05` §7 s'applique : D1 — seul candidat jugé sur J8 — REPASSE**
   (ré-dépôt daté au registre citant cette ADR, puis nouveau tour sur le
   périmètre ré-déclaré). Les candidats J3 ne sont pas touchés.
4. **Interaction ADR-007 assumée** : les six jours dégradés vivront sous
   le plancher qui y sera arbitré — si le plancher les exclut des épreuves
   à l'unité JOUR, ils y seront exclus par déclaration, pas par oubli. La
   pré-déclaration C6 (σ sur jours pleins) n'est pas modifiée.
5. La vérification d'acceptation du rebâti : `book_croise == 0` attendu
   sur les deux manifestes — un rebâti qui croise encore réfuterait
   l'anatomie et rouvrirait cette ADR.
