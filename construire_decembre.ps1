# Reconstruction de decembre 2025 — 24 jours x 2 symboles.
#
# POURQUOI CE FICHIER EST DANS LE DEPOT. Le lot precedent a ete lance par un
# script qui n'existe plus, et dont le log est dans `.gitignore`. Il est mort
# le 04/08 a 20 h 52 sur `20251224`, et il ne reste RIEN pour dire pourquoi :
# ni recette, ni code de sortie, ni trace. Une fabrication dont la recette
# n'est pas versionnee n'est pas reproductible, quel que soit le soin mis
# ailleurs.
#
# CE QU'IL FAIT DIFFEREMMENT :
#   * il appelle `construit/lot.py`, qui EST dans le depot et qui refuse de
#     demarrer si un seul jour demande est gele (controle avant la premiere
#     seconde de calcul), s'arrete au premier echec, et ne compte pas un jour
#     sorti sans `deep` ;
#   * il ecrit son journal dans `journal/construction/`, VERSIONNE ;
#   * il inscrit le reglage `deep` dans l'environnement, et chaque artefact
#     produit porte desormais son manifeste (`empreinte.py`).
#
# PERIMETRE — `decisions/ADR-000`, acceptee le 04/08/2026 avant ce lancement.
# (La numerotation des ADR de MapDee repart de zero : les ADR-001 a 021 sont
# ceux des depots morts, archives dans `_recupere/lab/04-decisions/`.)
#   01-07  certification consommee -> `--phase deep` seulement
#   08     banc d'instrument
#   09-16  exploration
#   17-23  RESERVE — absente de la liste, et `lot.py` la refuserait
#   24-31  exploration
#
# REGLAGE `deep` : passe en parametre, mesure sur le banc (jour 08) le
# 04/08/2026. Voir `journal/` pour le verdict et son critere pre-enregistre.

# REGLAGE ARRETE LE 04/08/2026.
#
# DeepMs = 250 — MESURE. L'emission de `deep` est imbriquee sous la porte de
#   `hl_book` : a 250 ms elle sort a CHAQUE photo du carnet (verifie,
#   deep_snaps == book_snaps a l'unite). Descendre plus bas ne donne rien de
#   plus sans toucher `SNAP_MIN_MS`, qui porte sa propre justification.
#
# DeepBand = 0.10 — DECISION, pas mesure. C'est le SEUL choix irreversible de
#   la construction : on retrecit toujours a la lecture, on n'elargit jamais
#   sans refaire les 48 constructions. Et la bande d'etude autour de laquelle
#   on serait tente de retrecir est une HYPOTHESE heritee d'un ADR sans
#   autorite — la graver serait graver l'hypothese.
#   Cout assume : ~2x le temps de rejeu et ~42 Go, contre ~15 Go en etroit.
#   Contrepartie : une vue etroite se derive de la large en quelques minutes,
#   l'inverse est impossible.
param(
    [string]$DeepMs   = "250",
    [string]$DeepBand = "0.10",
    [string[]]$Coins  = @("BTC", "ETH")
)

# INTERPRETEUR EXPLICITE, jamais `python` du PATH. Le journal du 04/08 (§4.9)
# rapporte qu'une iteration precedente a du tourner sous Anaconda 3.12
# (pyarrow 16.1 / pandas 2.1.1 / numpy 1.26.2) faute de pyarrow sous 3.10 —
# et c'est cet environnement-la que decrivait le premier `requirements.txt`.
# Aujourd'hui `python` resout bien vers 3.10.7 et aucun Anaconda n'est
# installe (verifie le 04/08/2026), mais un PATH est une variable de session :
# une construction de 32 h ne doit pas dependre de son ordre.
$PY = "C:\Python\Python310\python.exe"

# ⚠️ DEFAUT CORRIGE LE 05/08/2026, demontre par execution lors de l'audit.
# Si `$PY` n'existe pas, `&` leve une CommandNotFoundException : le programme
# n'est JAMAIS lance, donc `$LASTEXITCODE` n'est pas mis a jour — il vaut encore
# 0, herite de la commande precedente. Les deux blocs passaient, le script
# imprimait « termine », code de sortie 0, ET RIEN N'ETAIT CONSTRUIT. Pire, le
# message d'erreur ne partait pas dans le journal.
# Un controle qui ne peut pas echouer ne protege pas.
if (-not (Test-Path $PY)) {
    Write-Error "REFUS : interpreteur introuvable a '$PY'. Rien n'est lance."
    exit 1
}

$DEPOT = "C:\Users\DyBoo\Desktop\-MapDee-"
if (-not (Test-Path "$DEPOT\data\l4\openbook-202512\book_diffs_202512.tar")) {
    Write-Error "REFUS : archive source introuvable. Rien n'est lance."
    exit 1
}
$env:GON_OPENBOOK_SRC = "$DEPOT\data\l4\openbook-202512"
$env:GON_OPENBOOK_OUT = "$DEPOT\data\openbook"
$env:GON_DEEP_MS      = $DeepMs
$env:GON_DEEP_BAND    = $DeepBand

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$jdir  = "$DEPOT\journal\construction"
New-Item -ItemType Directory -Force $jdir | Out-Null
$log = "$jdir\$stamp-decembre.log"

function Note($m) {
    $l = "$(Get-Date -Format 'HH:mm:ss')  $m"
    $l | Out-File $log -Append -Encoding utf8
    Write-Host $l
}

# PRIORITE BASSE, HERITEE PAR LES ENFANTS (C8.4, 05/08/2026). La construction
# partage la machine avec l'enregistreur de production, et la fenetre de
# capture simultanee HL/Binance ne se rattrape jamais — une construction, si.
# Le diagnostic du 05/08 a montre Binance en resync 5 fois en 40 min pendant
# que la construction tournait : le recorder etait affame de CPU. Les processus
# python lances par `&` heritent de la classe de priorite de ce shell.
(Get-Process -Id $PID).PriorityClass = 'BelowNormal'

Note "=== reconstruction decembre 2025 ==="
Note "reglage deep : DEEP_MS=$DeepMs  DEEP_BAND=$DeepBand"
Note "symboles     : $($Coins -join ', ')"
Note "git          : $(git -C $DEPOT rev-parse --short HEAD)  sale=$([bool](git -C $DEPOT status --porcelain))"

Set-Location "$DEPOT\_recupere"

foreach ($coin in $Coins) {
    # 01-07 : `hl_*` figes (controles croises rendus dessus), seul `deep`
    # se fabrique. `lot.py` refuserait `--phase all` sur ces jours.
    Note "--- $coin  01-07  phase=deep ---"
    & $PY construit/lot.py --coin $coin --jours 20251201..20251207 --phase deep 2>&1 |
        Out-File $log -Append -Encoding utf8
    if ($LASTEXITCODE -ne 0) { Note "ECHEC sur 01-07 $coin (code $LASTEXITCODE) — arret"; exit 1 }

    Note "--- $coin  08-16  phase=all  (TRANCHE 1 SEULE) ---"
    & $PY construit/lot.py --coin $coin --jours 20251208..20251216 2>&1 |
        Out-File $log -Append -Encoding utf8
    if ($LASTEXITCODE -ne 0) { Note "ECHEC sur 08-31 $coin (code $LASTEXITCODE) — arret"; exit 1 }
}

Note "=== termine ==="
