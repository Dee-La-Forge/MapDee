# Installe la tache planifiee de relance de la construction au demarrage.
# A LANCER DANS UNE CONSOLE POWERSHELL ELEVEE (admin) :
#
#     cd C:\Users\DyBoo\Desktop\-MapDee-
#     .\installe_taches.ps1
#
# Optionnel : .\installe_taches.ps1 -AvecSauvegarde installe AUSSI la
# sauvegarde quotidienne du store (decision laissee ouverte le 05/08/2026).
#
# Pourquoi S4U : meme raison que le recorder (C8.4) — la tache tourne apres un
# redemarrage MEME SANS session ouverte, sans mot de passe stocke. Le nom de
# compte doit etre QUALIFIE (machine\utilisateur), le nom nu echoue en
# 0x80070534 — appris le 05/08.
#
# Pourquoi c'est inoffensif : construire_decembre.ps1 porte depuis le
# 05/08/2026 un refus d'instance (deux lot.py concurrents ecriraient les memes
# artefacts). La tache peut donc se declencher a tout moment sans risque —
# y compris pour un test manuel via Start-ScheduledTask.
param([switch]$AvecSauvegarde)

$compte = "$env:COMPUTERNAME\$env:USERNAME"
$p = New-ScheduledTaskPrincipal -UserId $compte -LogonType S4U -RunLevel Limited
$s = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew `
        -ExecutionTimeLimit (New-TimeSpan -Days 4) -StartWhenAvailable `
        -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# --- relance de la construction au demarrage --------------------------------
$a = New-ScheduledTaskAction -Execute 'powershell.exe' `
        -Argument '-NoProfile -ExecutionPolicy Bypass -File "C:\Users\DyBoo\Desktop\-MapDee-\construire_decembre.ps1"' `
        -WorkingDirectory 'C:\Users\DyBoo\Desktop\-MapDee-'
$t = New-ScheduledTaskTrigger -AtStartup
$t.Delay = 'PT2M'   # laisser les disques monter
# -ErrorAction Stop : la premiere version affichait « OK » apres un Acces
# refuse — un installeur qui annonce un succes qu'il n'a pas obtenu est pire
# que pas d'installeur (demontre le 05/08, en session non elevee).
try {
    Register-ScheduledTask -TaskName 'GON-MapDee-construction-reprise' `
        -Action $a -Trigger $t -Principal $p -Settings $s -Force -ErrorAction Stop | Out-Null
} catch {
    Write-Error ("ECHEC : $($_.Exception.Message) — l'enregistrement S4U exige " +
                 "une console ELEVEE (clic droit PowerShell > executer en tant " +
                 "qu'administrateur). Rien n'est installe.")
    exit 1
}
Write-Host "OK : GON-MapDee-construction-reprise (au demarrage + 2 min, S4U $compte)"
Write-Host "     test sans risque : Start-ScheduledTask 'GON-MapDee-construction-reprise'"
Write-Host "     -> si une construction tourne deja, le script refuse et sort."

# --- sauvegarde du store (optionnelle) --------------------------------------
if ($AvecSauvegarde) {
    $a2 = New-ScheduledTaskAction -Execute 'powershell.exe' `
            -Argument '-NoProfile -ExecutionPolicy Bypass -File "C:\Users\DyBoo\Desktop\-MapDee-\sauvegarde_store.ps1"'
    $t2 = New-ScheduledTaskTrigger -Daily -At '02:20'
    Register-ScheduledTask -TaskName 'GON-store-sauvegarde' `
        -Action $a2 -Trigger $t2 -Principal $p -Settings $s -Force | Out-Null
    Write-Host "OK : GON-store-sauvegarde (quotidienne 02:20 -> H:\Sauvegardes\GON-store)"
}

Get-ScheduledTask -TaskName 'GON-*' | Select-Object TaskName, State |
    Format-Table -AutoSize
