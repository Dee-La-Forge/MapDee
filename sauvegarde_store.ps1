# Sauvegarde quotidienne du store de capture — LA donnee irremplacable :
# la fenetre simultanee HL/Binance ne se rattrape jamais (C8).
#
# Incrementale : robocopy ne copie que les fichiers nouveaux ou modifies
# (les jours clos ne bougent plus — ~1,2 Go/jour). Le L4 de decembre (188 Go)
# est VOLONTAIREMENT exclu — decision de Meddy du 05/08/2026.
#
# Si le volume de destination est absent (disque USB debranche), le script
# echoue proprement et la tache reessaie le lendemain — le log le dira.
param(
    [string]$Source      = "C:\Users\DyBoo\Desktop\LaForge\GON-TV\sandbox\detect\recorder\store",
    [string]$Destination = "H:\Sauvegardes\GON-store"
)

if (-not (Test-Path (Split-Path $Destination -Qualifier))) {
    Write-Error "volume de destination absent : $Destination — rien n'est copie"
    exit 1
}
New-Item -ItemType Directory -Force $Destination | Out-Null
$log = Join-Path $Destination "sauvegarde.log"

"=== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File $log -Append -Encoding utf8
robocopy $Source $Destination /E /XO /R:2 /W:5 /NP /NDL /NFL /LOG+:$log
# robocopy : 0-7 = succes (0 rien a faire, 1 copie faite) ; >= 8 = echec
if ($LASTEXITCODE -ge 8) {
    "ECHEC robocopy code $LASTEXITCODE" | Out-File $log -Append -Encoding utf8
    exit 1
}
exit 0
