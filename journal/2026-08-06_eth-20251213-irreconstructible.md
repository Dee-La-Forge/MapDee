# ETH 20251213 est irreconstructible — le trou d'archive que la note du 04/08 n'avait pas fini de cerner

> 06/08/2026, 04 h 55. Découvert par l'ARRÊT PROPRE du lot ETH 08-16 :
> `20251213 ETH` sort avec 0 photo, lot.py refuse de le compter et s'arrête
> (« un jour sorti sans deep complet ne se compte pas »). L'instrument a
> fonctionné exactement comme conçu.

## La preuve, dans les manifestes

| jour ETH | carnets croisés | photos valides |
|---|---|---|
| 20251212 | **8 476 949** | 86 339 (journée à 75 %, incident du soir) |
| **20251213** | **15 191 426** | **0** — la journée entière est incohérente |
| 20251214 | (vérifié sain le 04/08 : 8 307 instants, reconstruction parfaite) | |

Le chiffre du 12 est **exactement celui de la vieille affirmation** (« 8 476 949
carnets croisés sur ETH » — journal du 04/08 §1) : la note d'origine mesurait
l'incident du 12 au soir. La vérification du 04/08 a réfuté « l'archive
s'arrête le 12 » en blanchissant le 14 — mais **sa table n'a jamais
reconstruit le 13**, implicitement couvert par l'argument « week-end léger ».
Le 13 est en réalité la convalescence de l'incident : le flux de carnet ETH y
est croisé de bout en bout. (BTC 20251213 se reconstruit normalement — le
défaut est côté ETH seulement.)

## Les décisions

1. **`20251213 ETH` est un TROU D'ARCHIVE DOCUMENTÉ** — au même titre que les
   `gap` du recorder : compté, nommé, jamais maquillé. Il ne se
   reconstruira pas depuis cette archive.
2. **Le périmètre J8 est amendé** : « 09-16, moins 20251213 ETH (trou
   d'archive) » — 15 jour-symboles au lieu de 16. Ce n'est pas un périmètre
   ajusté après un résultat : c'est une impossibilité matérielle, documentée
   avant tout calcul de J8. `03` (définition de J8) et `harnais/e0_reel`
   portent l'amendement.
3. **La construction reprend sur 20251214-16 ETH** (le 14 est vérifié sain ;
   les 15-16, jamais vérifiés, diront ce qu'ils sont au rejeu — s'ils
   tombent aussi, même traitement : trou documenté, pas maquillage).
4. La vérification finale de `construire_decembre.ps1` attendra **31/32**
   avec le trou nommé — correction en file (jamais sous un run).

## La leçon — la même qu'au 04/08, un cran plus loin

« Avant de renoncer à une donnée sur la foi d'une note, ouvrir la donnée » —
et son complément d'aujourd'hui : **une réfutation partielle ne blanchit que
ce qu'elle a ouvert.** Le 04/08 a ouvert le 14 et réfuté la fin du monde ;
le 13, jamais ouvert, portait le vrai trou. Les compteurs du constructeur
(`book_croise` par jour, dans chaque manifeste) font désormais ce travail
jour par jour, mécaniquement.

---

**Addendum du 06/08, plus tard le même jour — la phrase « BTC 20251213 se
reconstruit normalement » est FAUSSE.** Le manifeste dit 172 photos
(≈0,14 % d'une journée) pour 28 056 154 carnets croisés : le 13 BTC est un
trou de facto que la garde binaire de `construit/` (0 photo = refus,
>0 = compté) a laissé passer. L'affirmation venait du non-échec du lot de
décembre — un constat documentaire, pas une mesure : le péché exact que la
note d'à côté reprochait à la vérification du 04/08. J8 est ré-amendé à
**14 jour-symboles** (« 09-16 moins 20251213 BTC et ETH ») — table
complète et décisions :
`journal/2026-08-06_couverture-j8-la-garde-binaire-a-laisse-passer-un-trou.md`.
