# La sélection adverse — la question renversée, et la première qui répond

**04/08/2026, 00 h 05** · BTC · jours 20251209, 10, 11 · **EXPLORATOIRE**

Les trois pistes de la soirée ont la même forme d'échec : un signal réel, trop
petit pour franchir **7 bp de frais**. Or ces 7 bp n'existent que parce qu'on
**ouvre une position exprès**.

Un teneur de marché poste déjà. Il paie déjà. La question devient : ce signal
réduit-il une perte qu'il **subit de toute façon** ?

---

## La mesure

Chaque transaction a deux contreparties appariées par `tid` : un **Maker** dont
l'ordre était posé, un **Taker** qui vient le consommer.

    P&L du Maker sur H = signe(son côté) × (mid(t+H) − prix du fill)

On le compare selon que le Taker **croisait** — posait d'un côté du carnet en
agressant de l'autre — au même instant.

## Le résultat

| jour | % des fills | H | servi par un CROISEUR | par un AUTRE | **surcoût** | t |
|---|---|---|---|---|---|---|
| 09/12 | 12,3 % | 30 s | −1,882 bp | −0,883 bp | **+0,999** | +32,4 |
| 10/12 | 11,9 % | 30 s | −1,992 | −0,701 | **+1,291** | +29,8 |
| 11/12 | 13,2 % | 30 s | −1,898 | −0,731 | **+1,167** | +41,0 |
| 09/12 | | 60 s | −1,614 | −0,792 | +0,822 | +18,8 |
| 10/12 | | 60 s | −1,655 | −0,653 | +1,002 | +18,9 |
| 11/12 | | 60 s | −1,634 | −0,678 | +0,956 | +23,9 |

**Surcoût moyen à 30 s : +1,152 bp** (écart-type entre jours 0,147), sur
**183 004 fills** en trois jours, avec des `t` de **30 à 41**.

Le teneur perd dans les deux cas — c'est la sélection adverse normale, que la
fourchette compense. Mais **être servi par un croiseur coûte 2,6 fois plus cher
qu'être servi par quelqu'un d'autre**.

## Pourquoi ce chiffre-ci compte, alors que +0,63 bp ne comptait pas

Parce que le seuil à franchir n'est pas le même.

| | signal directionnel | signal de sélection adverse |
|---|---|---|
| ce qu'on décide | ouvrir une position exprès | poster ou retirer, ce qu'on fait déjà |
| coût à couvrir | **7 bp** (preneur, aller-retour) | **0** — la décision existe déjà |
| valeur mesurée | +0,63 bp → **facteur 11 manquant** | **+1,15 bp par fill évité** |

Un teneur paie ~1 bp de frais et encaisse ~1,1 bp de fourchette sur BTC. Un
surcoût de 1,15 bp sur 12 % de ses fills n'est pas un détail : **c'est l'ordre
de grandeur de sa marge entière**.

## Ce que ça ne dit pas

1. **Ce n'est pas un P&L de teneur.** C'est la marque au marché du fill, qui en
   est la composante dominante — pas la file d'attente, pas l'inventaire, pas
   l'horizon de couverture.
2. **Un surcoût mesuré n'est une économie que si l'on peut retirer à temps.**
   Le signal est calculable en direct (`orderUpdates`, vérifié), mais la latence
   entre détecter et annuler n'est pas mesurée.
3. **Éviter 12 % des fills a un coût d'opportunité** : moins de volume, donc
   moins de fourchette encaissée. Le solde net n'est pas calculé.
4. **BTC seul, trois jours.** Et « croiser » reste une structure, pas une
   intention : un teneur qui gère son inventaire croise aussi.

## Ce qui reste à faire, dans l'ordre

1. **Le solde net** : fourchette perdue en retirant, contre sélection adverse
   évitée. C'est ce calcul-là qui tranche.
2. **La latence** : à quelle vitesse le signal est-il exploitable en direct ?
3. **Les cinq éléments de spoofing jamais utilisés** — apparition du mur,
   disparition à l'approche, rafraîchissement, empilement, réputation. Le
   +1,15 bp sort de **deux éléments sur dix**.
