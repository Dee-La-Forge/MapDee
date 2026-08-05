# C8.4 — Diagnostic de l'enregistreur de production, et sa réparation

> **Tranchée par Meddy le 05/08/2026** (« tranche C8.4 et répare
> l'enregistreur »), rendue le jour même. Outil de mesure versionné :
> `chantiers/c8_capture_sante.py` — relançable à tout moment, lecture seule.
>
> L'enregistreur vit hors dépôt :
> `LaForge/GON-TV/sandbox/detect/recorder/` (code + `store/` + tâche planifiée
> `GON-detect-recorder-P1`). Ce rapport est la trace MapDee de son état.

## 1. Le verdict d'abord : la prémisse de C8.4 était fausse

Le protocole C8 disait « son volume s'est effondré et des jours manquent ».
**Mesuré : ni l'un ni l'autre.** Aucun jour ne manque depuis le début de la
capture (28/07), et les jours sont complets à **≥ 99,8 %** — sauf trois pertes
datées, toutes expliquées au niveau **machine**, aucune au niveau du recorder.
L'impression d'effondrement venait probablement de la comparaison des tailles
de fichiers HL (~20 Mo) contre Binance (~200-390 Mo) : c'est structurel — 40
paliers retenus contre le carnet entier — pas une dégradation.

## 2. La mesure — complétude par jour (jour plein à 100 ms = 864 000 lignes)

Lignes identiques entre les 4 flux (BINANCE, HYPERLIQUID × BTC, ETH) à < 0,01 %
près — l'horloge de ticks est commune ; ce qui suit est le flux le plus bas.
Jours UTC (les fichiers roulent à 02:00 locale).

| jour (UTC) | lignes | complétude | gaps HL | gaps Binance | sessions |
|---|---:|---:|---:|---:|---:|
| 28/07 | 147 982 | 17 % | 10 | 14 | 3-5 — **premier jour, capture démarrée en cours de journée** |
| 29/07 | 863 418 | 99,9 % | 22 | 6 | 3 |
| 30/07 | 862 315 | 99,8 % | 22 | 2 | 1 |
| 31/07 | 863 791 | 100 % | 18 | 2 | 1 |
| 01/08 | 862 866 | 99,9 % | 20 | 0 | 1 |
| **02/08** | **754 378** | **87,3 % — 3,0 h perdues** | 18 | 3 | 3 |
| 03/08 | 863 527 | 99,9 % | 18 | 4 | 3 |
| **04/08** | **805 340** | **93,2 % — 1,6 h perdues** | 26 | 16 | **9** |

**Pour C8.3 (fenêtre simultanée)** : cinq jours pleins déjà en caisse (29/07 →
01/08 et 03/08), deux jours à 88-93 %, exploitables avec leurs trous marqués —
l'enregistreur écrit ses trous honnêtement (`gap` avec durée), rien n'est
maquillé.

## 3. Les causes, par élément de preuve

| perte | cause | preuve |
|---|---|---|
| 04/08, ~1,6 h et 9 sessions | **plantage machine dur** à 17:26 (« redémarré sans s'arrêter correctement » — matériel/alimentation, pas logiciel) + panne **réseau/DNS** de ~2 min à 16:32 (toutes venues en `getaddrinfo failed` simultanément) + plusieurs redémarrages volontaires du recorder en soirée (itérations sur les flux `hyperliquid_fin`/`large`, ~20:36-20:40) | journal Système Event 41 · `recorder.log` 16:32-16:34 · `recorder.log` 20:36/20:40 |
| 05/08 (jour en cours) | **redémarrage machine à 02:19** (RuntimeBroker — redémarrage utilisateur/mise à jour) ; capture de retour à 02:24, au premier déclenchement après ouverture de session | Event 1074 · `recorder.log` 02:24 |
| 02/08 UTC, ~3,0 h | **aucune trace dans le journal Système** (ni reboot, ni veille — vérifiés) : arrêt au niveau du processus, pendant la matinée locale du 03/08 — c'est la « panne du 03/08 » déjà connue du protocole C8. **Cause non établie** ; à ne pas présenter autrement | absence d'événements 41/42/1074/6008 sur la période |

**Et deux dégradations continues, plus petites :**

* **Hyperliquid coupe ses websockets ~toutes les 3 h** (reconnexions serveur,
  visibles dans le log sans erreur préalable) → 18-26 trous courts par jour,
  ~30-60 s cumulées. Binance : 0-6. C'est la différence déjà vue par C8.2
  (9 trous HL contre 2 Binance le 02/08) ;
* **resyncs Binance sous charge CPU** : le chaînage de diffs se rompt quand le
  recorder est affamé — 5 resyncs en 40 min ce matin, **pendant que la
  construction de décembre et C5 tournaient à priorité égale**. Le recorder
  perd alors quelques secondes de diffs par resync (trous marqués).

## 4. Ce qui protège déjà — et qu'il ne faut pas réinventer

Le recorder est bien conçu sur ce plan : verrou d'instance unique + tâche
planifiée qui relance **toutes les 5 minutes** (inoffensive tant qu'il tourne,
auto-réparatrice sinon) + relance à l'ouverture de session + `IgnoreNew` + pas
de limite d'exécution + les trous écrits avec leur durée.

## 5. Réparations appliquées le 05/08

1. **Priorités** : construction et C5 abaissés à `BelowNormal` (processus en
   cours), et **gravé dans `construire_decembre.ps1`** — les enfants héritent
   de la classe de priorité du shell. La fenêtre de traversée ne se rattrape
   jamais ; une construction, si.
2. **Outil de santé** : `chantiers/c8_capture_sante.py` — la complétude se
   mesure en une commande, plus jamais à l'impression.

## 6. La réparation qui t'attend — une commande, bloquée pour moi

**Le talon d'Achille restant** : la tâche tourne en `InteractiveToken` — après
un redémarrage, la capture attend qu'une session s'ouvre. Un reboot nocturne
(mise à jour, plantage) qui reste sur l'écran de verrouillage = capture morte
jusqu'au matin. Le passage à **S4U** (exécution sans session, sans mot de passe
stocké) règle ça ; la modification de tâche planifiée m'est bloquée par les
permissions. À lancer toi-même :

```
! powershell -Command "Set-ScheduledTask -TaskName 'GON-detect-recorder-P1' -Principal (New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Limited)"
```

Test non destructif ensuite (ne touche pas la capture en cours — le verrou
fait sortir la nouvelle instance immédiatement) :

```
! powershell -Command "Start-ScheduledTask -TaskName 'GON-detect-recorder-P1'; Start-Sleep 5; Get-Content 'C:\Users\DyBoo\Desktop\LaForge\GON-TV\sandbox\detect\recorder\recorder.log' -Tail 2"
```

Attendu : `[singleton] un recorder tourne déjà` — preuve que le démarrage S4U
fonctionne, sans avoir tué quoi que ce soit.

## 7. Recommandations restantes — décisions chez toi

* **le plantage dur du 04/08 (Event 41)** : s'il se reproduit, c'est matériel
  (alimentation, RAM, température) — à surveiller ; deux occurrences
  justifieraient un memtest et un œil sur l'alimentation ;
* **Windows Update** : régler les heures actives, ou différer les redémarrages
  automatiques — le reboot de 02:19 en pleine construction en est probablement
  un ;
* **les coupures HL toutes les ~3 h** : corrigeables dans l'adaptateur
  (reconnexion anticipée à chevauchement), mais ~45 s/jour de gain contre le
  risque de toucher du code de production qui marche — je recommande de **ne
  pas** y toucher tant que C8.3 n'exige pas mieux.
