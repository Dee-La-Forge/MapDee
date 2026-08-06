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

---

**Addendum du 06/08, AVANT toute photo émise (le rebâti est en phase
statuts, vérifié au log) — la bande de couverture, déclarée d'avance.**
Attente dérivée, pas devinée : naïve = 16 h/24 = 66,7 % ; pondérée par
l'activité depuis les cumuls horaires du 20251214 (même profil week-end,
publiés au log du 06/08) = (104 234 − 30 612)/104 234 = **70,6 %** des
photos au-delà de h07, côté ETH. **Bande d'acceptation : chaque symbole
rebâti doit sortir entre 60 % et 80 % des photos du 20251214 du même
symbole. Hors bande = REFUS** : le jour ne rentre pas dans J8 et cette
ADR rouvre — quel que soit le sens du dépassement, un excès serait aussi
suspect qu'un déficit. S'ajoute à `book_croise == 0`, inchangé.

**Correction du 06/08, minutes plus tard — la phrase « AVANT toute photo
émise, vérifié au log » était FAUSSE.** Le grep de vérification a été
lancé dans la MÊME commande que l'addendum, sans lecture préalable : au
moment de la déclaration, BTC avait déjà émis **19 085 photos**
(h08-h12). Même mécanique que « BTC 13 sain » ce matin — une vérification
écrite avant d'être lue n'en est pas une. Ce qui reste honnêtement
pré-déclaré : les comptes FINALS étaient inconnus, l'ETH n'avait pas
commencé, et ni la bande ni sa dérivation ne s'appuient sur le partiel.
Ce qui est affaibli : pour BTC, un lecteur pouvait extrapoler ~88 % du
rythme du 14 depuis h08-h12 — la bande reste opposable, sa
« pré-déclaration » l'est moins. La leçon est déjà en mémoire
permanente ; elle vient de servir contre son propre auteur.

**Résultat du 06/08 — la bande a tranché, contre son auteur pour moitié.**
ETH : croise=0, 64 789 photos = **62,2 %** du 14 → DANS LA BANDE, accepté,
entre dans J8 en jour dégradé. BTC : croise=0, carnet sain, 61 387 photos
= **58,9 %** du 14 → **HORS BANDE, REFUSÉ** — à 1,1 point du plancher,
et la règle déclarée ne se renégocie pas après le résultat. Le fichier
rebâti reste sur disque (sain, manifesté « SANS VEILLE ») mais HORS J8.
**L'ADR rouvre pour BTC seul** : l'accepter définitivement hors J8, ou
ré-arbitrer la bande — ce qui serait une renégociation assumée, par ADR
nouvelle, jamais silencieuse — appartient à Meddy. J8 ré-déclaré :
**15 jour-symboles, dont 5 dégradés**. D1 repasse (05 §7).
