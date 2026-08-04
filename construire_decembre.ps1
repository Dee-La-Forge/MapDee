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

param(
    [string]$DeepMs   = "250",
    [string]$DeepBand = "0.02",
    [string[]]$Coins  = @("BTC", "ETH")
)

$DEPOT = "C:\Users\DyBoo\Desktop\-MapDee-"
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

Note "=== reconstruction decembre 2025 ==="
Note "reglage deep : DEEP_MS=$DeepMs  DEEP_BAND=$DeepBand"
Note "symboles     : $($Coins -join ', ')"
Note "git          : $(git -C $DEPOT rev-parse --short HEAD)  sale=$([bool](git -C $DEPOT status --porcelain))"

Set-Location "$DEPOT\_recupere"

foreach ($coin in $Coins) {
    # 01-07 : `hl_*` figes (controles croises rendus dessus), seul `deep`
    # se fabrique. `lot.py` refuserait `--phase all` sur ces jours.
    Note "--- $coin  01-07  phase=deep ---"
    & python construit/lot.py --coin $coin --jours 20251201..20251207 --phase deep 2>&1 |
        Out-File $log -Append -Encoding utf8
    if ($LASTEXITCODE -ne 0) { Note "ECHEC sur 01-07 $coin (code $LASTEXITCODE) — arret"; exit 1 }

    Note "--- $coin  08-16 et 24-31  phase=all ---"
    & python construit/lot.py --coin $coin --jours 20251208..20251216 20251224..20251231 2>&1 |
        Out-File $log -Append -Encoding utf8
    if ($LASTEXITCODE -ne 0) { Note "ECHEC sur 08-31 $coin (code $LASTEXITCODE) — arret"; exit 1 }
}

Note "=== termine ==="
