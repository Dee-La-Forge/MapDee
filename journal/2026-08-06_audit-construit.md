# Audit de `construit/` — avant la promotion C10, pendant que le 16 ETH tourne

> 06/08/2026. Read-only, aucune édition sous le run (règle payée 10 h).
> Périmètre : `openbook.py`, `grille.py`, `jour.py` (811 lignes, lu en
> entier), `lot.py`. `00` §7 corrigé autorise l'audit — c'est le programme
> dont sort chaque chiffre du projet, et C10 s'apprête à le promouvoir.

## Ce qui est sain, vérifié ligne à ligne

* `grille.py` : implémentation unique, selftest anti-2,5 (le coefficient
  fautif des 9 divergences), bornes exactes, cas ETH 7,5-pile → 10.
* `openbook.py` : décodage testé contre le SCHEMA (pas une intuition),
  float64 justifié, jointure oid = verrou déclaré et mesuré.
* `jour.py` : `_refuse_si_gele` normalise ses entrées (la garde ne dépend
  pas de la discipline des appelants) ; manifestes de provenance corrects
  (`produits` = ce que LA passe a écrit) ; `fusionne` atomique
  (`.encours` + replace) ; `_parquet_complet` à double `PAR1` ; paliers
  fantômes évincés (le fix mesuré du 03/08) ; horloge monotone à sources
  crédibles ; chauffe sur la veille avec l'absence DITE.

## Les quatre défauts trouvés (corrections EN FILE, jamais sous un run)

1. **`n_temps_approx` est saturé par construction.** Chaque `update`
   (~12 M/jour, sans instant propre PAR DESIGN) incrémente le compteur
   censé surveiller la qualité de la jointure oid — « le verrou du
   module ». Une vraie dégradation de jointure y serait invisible.
   → séparer `n_updates` (normal) de `n_sans_temps` (new/remove non
   appariés, le vrai signal).
2. **Le `.gz` tronqué passe encore « déjà extrait ».** `_extract_day`
   compte les fichiers EXISTANTS ; un kill en cours d'extraction laisse un
   tronqué qui passe — c'est l'EOFError qui a coûté des heures le 05/08,
   purgé à la main (`gzip -t`) mais jamais corrigé dans le code.
   → extraction atomique : nom temporaire + rename.
3. **`read_diffs` avale les lignes illisibles en silence** — `except:
   continue`, aucun compteur. Pendant un incident, des millions de lignes
   pourraient disparaître sans trace. → compteur `n_illisibles` dans les
   stats du manifeste. (C'est ce compteur, s'il avait existé, qui aurait
   répondu mécaniquement à la question d'aujourd'hui.)
4. **La garde de couverture binaire** — déjà actée (table du 06/08,
   ADR-007) : plancher dans `lot.py` + `heures_a_zero_photo` au manifeste.

## Le mécanisme de l'incident 12→15, avancé d'un cran

Mesure du jour (work/20251215, heures 10/13/16 ETH) : **0 ligne
illisible**, new ≈ remove équilibrés (h16 : 2 164 046 / 2 163 367),
updates ~0,5 %. Le flux est **bien formé** — l'incident n'est PAS de la
corruption d'octets. Un carnet qui reste croisé 10 h avec un flux propre
et équilibré pointe vers une **fenêtre de `remove` perdue à la capture**
(des ordres fantômes épinglent le meilleur bid au-dessus du meilleur ask),
ou un défaut amont de la bourse. Les deux symboles croisant en même temps
(12 au soir, 15 dès 13 h) désignent la capture/venue, pas un symbole.

**Piste de récupération, en file (post-tranche)** : un rejeu diagnostic
qui, à l'entrée en croisement, logge les oids du haut de carnet — si un
PETIT ensemble d'ordres fantômes épingle le carnet, une règle d'éviction
(documentée par ADR) pourrait récupérer une partie des journées 12/13/15.
Espérance modérée (la simultanéité des symboles évoque un défaut amont),
mais le coût est un script et l'enjeu est 2 à 4 jour-symboles.

## Verdict d'ensemble

L'instrument est bien plus sain que sa réputation d'« archive » : les
fautes passées sont documentées dans le code avec leurs mesures, les
gardes actives normalisent leurs entrées. Les quatre défauts sont des
défauts d'OBSERVABILITÉ (compteurs, garde binaire), pas de calcul — la
promotion C10 peut se faire après la fenêtre de corrections.
