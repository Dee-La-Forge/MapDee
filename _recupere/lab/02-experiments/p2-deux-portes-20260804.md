# P2 — deux portes, une s'ouvre : le prix ne choisit pas franchement

**04/08/2026, 01 h 20** · BTC · jours 20251209 à 12 · **RÉPOND À : ADR-001**

La question d'origine de Meddy, dans sa forme la plus propre : le prix encadré
par deux portes, **une seule s'ouvre — part-il de ce côté ?**

Le contrôle est **interne** : les deux portes subissent le même instant, la même
volatilité, la même tendance. C'est ce que P1 n'avait pas.

---

## Le résultat

| jour | une seule ouverte | P(prix vers la porte ouverte) | rendement vers elle |
|---|---|---|---|
| 09/12 | 1 220 | 0,551 | **+2,14 bp** |
| 10/12 | 1 221 | 0,516 | +1,23 bp |
| 11/12 | 1 309 | 0,529 | +0,94 bp |
| 12/12 | 639 | **0,479** | **−1,07 bp** |

**Unité = le jour**, comme la nuit l'a imposé (les fenêtres se recouvrent, l'écart-type
intra-journalier est faux d'un facteur cinq) :

    rendement moyen        +0,809 bp
    écart-type entre jours  1,354
    IC 95 % de Student     [−1,35 ; +2,96]      t = +1,19
    P moyenne               0,519
    jours du bon signe      3/4

**L'intervalle contient zéro.** Et le quatrième jour a le signe **inverse**, avec
un `t` intra-journalier de −2,29 : ce n'est pas un jour tiède, c'est un jour qui
dit le contraire.

## Ce que ça fait à P1

P1 concluait bien plus fort : porte fermée jamais franchie, ouverture 4 min
avant, 40 bp de distance, quatre jours stables. **P2 est le même phénomène mesuré
avec un contrôle interne, et il ne confirme pas.**

L'explication la plus probable est celle que P1 nommait sans la mesurer : dans
P1, rien ne contrôlait **la direction que le prix avait déjà**. Une porte
s'ouvre parce que son porteur voit le marché venir ; le prix continue ; on
observe « ouverture puis passage » sans qu'aucune porte n'ait rien autorisé.
P2 met les deux portes face au même marché — et l'effet tombe des deux tiers.

Il n'est pas nul pour autant : **+0,81 bp en moyenne, 3 jours sur 4 du bon
signe, P = 0,519**. C'est un effet possible, faible, non établi.

## Le cas dominant, qu'on n'a pas regardé

**83 à 89 % des instants voient les DEUX portes s'ouvrir**, et 2 % aucune. Le cas
discriminant — une seule — ne représente que **10 à 16 %**.

Autrement dit : la plupart du temps, les deux côtés s'écartent ensemble. Ce
n'est pas une porte qui s'ouvre pour laisser passer, c'est **le carnet entier qui
se retire**. Ça déplace encore la question, et ce n'est pas mesuré.

## Ce qu'il faudrait pour trancher

Quatre jours ne suffisent pas : avec un écart-type inter-journalier de 1,35 bp,
il en faudrait **une vingtaine** pour distinguer +0,8 bp de zéro. Les jours
13 à 16 sont disponibles et jamais ouverts ; la réserve 17-23 reste fermée.
