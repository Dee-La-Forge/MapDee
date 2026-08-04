# Lot 2 — les 21 jours restants de decembre, BTC.
#
# Attend la fin du lot 1 (deux rejeux simultanes se disputent le disque et le
# meme dossier d'extraction). Puis construit dans un ordre qui protege :
#
#   1. les 13 jours NEUFS      rien a perdre
#   2. les 8 RECONSTRUCTIONS   ecrasent des fichiers qui marchent -> en dernier
#
# La reserve 20251217-23 n'est pas dans la liste, et le code la refuserait de
# toute facon. Les jours 20251201-07 ont leurs `hl_*` figes : `--phase deep`.
#
# `work/` gonfle d'environ 15 Gio par passage et ne se nettoie pas tout seul :
# on purge le jour ET sa veille apres chaque construction.

$SRC = "C:\Users\DyBoo\Desktop\-MapDee-\data\l4\openbook-202512"
$env:GON_OPENBOOK_SRC = $SRC
$env:GON_OPENBOOK_OUT = "C:\Users\DyBoo\Desktop\-MapDee-\data\openbook"
$log  = "C:\Users\DyBoo\Desktop\-MapDee-\_lot2.log"
$lot1 = "C:\Users\DyBoo\Desktop\-MapDee-\_lot1.log"
Set-Location "C:\Users\DyBoo\Desktop\-MapDee-\_recupere"

function Note($m) { "$(Get-Date -Format 'HH:mm:ss')  $m" | Out-File $log -Append -Encoding utf8 }

"=== lot 2 — 21 jours BTC ===" | Out-File $log -Encoding utf8
Note "en attente de la fin du lot 1..."
while (-not (Select-String -Path $lot1 -Pattern 'lot 1 termine' -Quiet -ErrorAction SilentlyContinue)) {
    Start-Sleep -Seconds 60
}
Note "lot 1 termine — demarrage"

# 13 jours NEUFS, puis 8 RECONSTRUCTIONS
$neufs   = @('20251203','20251204','20251205','20251206','20251207',
             '20251213','20251225','20251226','20251227','20251228',
             '20251229','20251230','20251231')
$refaits = @('20251201','20251202','20251208','20251209','20251210',
             '20251211','20251212','20251214')
$figes   = @('20251201','20251202','20251203','20251204','20251205','20251206','20251207')

$n = 0
foreach ($j in ($neufs + $refaits)) {
    $n++
    $phase = if ($figes -contains $j) { 'deep' } else { 'all' }
    $type  = if ($neufs -contains $j) { 'NEUF' } else { 'REFAIT' }
    $libre = [math]::Round((Get-PSDrive C).Free / 1GB, 1)

    if ($libre -lt 40) { Note "ARRET : plus que $libre Go libres"; break }

    Note "[$n/21] $j BTC  phase=$phase  $type  (libre $libre Go)"
    & python construit/jour.py --day $j --coin BTC --phase $phase 2>&1 |
        Out-File $log -Append -Encoding utf8

    # purge du jour et de sa veille — sinon `work/` sature le disque
    $veille = ([datetime]::ParseExact($j, 'yyyyMMdd', $null)).AddDays(-1).ToString('yyyyMMdd')
    foreach ($d in @($j, $veille)) {
        $w = Join-Path $SRC "work\$d"
        if (Test-Path $w) { Remove-Item $w -Recurse -Force -ErrorAction SilentlyContinue }
    }
}
Note "=== lot 2 termine — $n jours traites ==="
