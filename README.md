
=================================================
INSTALL


Installer Anaconda3


Legg til Anaconda3 installasjonskatalog til PATH


Opprett registry key "HKEY_LOCAL_MACHINE\SOFTWARE\uvsync"

Opprett string registry key "HKEY_LOCAL_MACHINE\SOFTWARE\uvsync\bindir" og sett verdi til katalogen med uvsync.py

Opprett string registry key "HKEY_LOCAL_MACHINE\SOFTWARE\uvsync\connection_string" og sett verdi til connection string for uvsync2 databasen

Opprett string registry key "HKEY_LOCAL_MACHINE\SOFTWARE\uvsync\uvsync_directory" og sett verdi til en katalog for mottak av filer fra stasjoner

Opprett dword registry key "HKEY_LOCAL_MACHINE\SOFTWARE\uvsync\sync_frequency" og sett verdi til hvor hyppig det skal synkroniseres i antall sekunder

Åpne Anaconda cmd som administrator og bruk følgende kommandoer for installasjon, oppdatering eller avinstallasjon av windows service:


Install service: python .\uvsync_winsrv.py install

Update service: python .\uvsync_winsrv.py update

Remove service: python .\uvsync_winsrv.py remove


Kjør "eventvwr.msc" for å åpne systemets event log

Kjør "services.msc" for å åpne systemes tjenester

=================================================

På hver logge stasjon:


Tillat kjøring a powershell script, kjør som lokal administrator:

set-executionpolicy remotesigned