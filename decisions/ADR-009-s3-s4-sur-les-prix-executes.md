# ADR-009 — S3 et S4 se mesurent sur les PRIX EXÉCUTÉS, pas sur `limitPx`

**Statut : EN RÉDACTION** — la décision appartient à Meddy.
Écrite le 06/08/2026, à la lecture de la 2ᵉ passe C2.

## Le constat qui l'impose

`limitPx` d'un statut FILLED est le **plafond** d'un marketable-limit, pas
le prix touché : queues en nombres ronds (10/20/50/100 %), délais S3
négatifs de minutes, hypothèse « limitPx=0 » réfutée (0/748 640). Deux
passes l'ont payé ; la variable est fausse pour S3/S4, point.

## La règle proposée (3ᵉ passe, protocole à pré-enregistrer)

1. **Source** : le flux de transactions (`trades_2025_12.tar`, jour 08),
   lu directement comme `fills.py` (`read_trades`) — les DEUX contreparties
   portent le prix réellement touché. Pas de dépendance aux `hl_fills`
   non certifiés (la dette reste ce qu'elle est).
2. **S4″** : distance relative du prix de CHAQUE transaction au mid deep
   asof (mêmes tolérances que §5) ; bande = quantile 0,999 — règle de
   lecture inchangée depuis §2.
3. **S3″** : palier d'exécution = prix de transaction // bs ; le reste de
   §5 inchangé (t_bl du deep, fenêtre 1 000 ms, barre 95 %).
4. Compteur publié : part des transactions non jointes et pourquoi.

## Ce que ça ne change pas

M′/P′ (fermées en 2ᵉ passe), les règles de lecture (quantiles, barres),
et la fermeture de B7 en bloc — les trois définitions ensemble, après S3″/S4″.
