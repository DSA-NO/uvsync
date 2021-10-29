
=================================================
INSTALL

Installer Anaconda3

Legg til Anaconda3 installasjonskatalog til PATH

Opprett registry key "HKEY_LOCAL_MACHINE\SOFTWARE\uvsync"
Opprett string registry key "HKEY_LOCAL_MACHINE\SOFTWARE\uvsync\bindir" og sett verdi til katalogen med uvsync.py
Opprett string registry key "HKEY_LOCAL_MACHINE\SOFTWARE\uvsync\connection_string" og sett verdi til connection string for uvsync2 databasen
Opprett string registry key "HKEY_LOCAL_MACHINE\SOFTWARE\uvsync\uvsync_directory" og sett verdi til en katalog for mottak av filer fra stasjoner
Opprett string registry key "HKEY_LOCAL_MACHINE\SOFTWARE\uvsync\uvsync_archive" og sett verdi til en katalog for arkivering av behandlede filer
Opprett dword registry key "HKEY_LOCAL_MACHINE\SOFTWARE\uvsync\sync_frequency" og sett verdi til hvor hyppig det skal synkroniseres i antall sekunder (Oppgis i hex)

Åpne cmd som administrator og bruk følgende kommandoer for installasjon/oppdatering av windows service:

Install service: python uvsync_winsrv.py install
Update service: python uvsync_winsrv.py update
Remove service: python uvsync_winsrv.py remove

Kjør "eventvwr" for å åpne systemets event log

=================================================
CONFIG

Sett opp en 64-bit ODBC Data kilde med navn "uvnet2" med tilgang til uvnet2 databasen

=================================================
UVSYNC.PY

uvsync.py henter datafiler for hver stasjon og setter nye data inn i databasen.

Følgende kommandolinje parametere kan benyttes:

--config_dir ...

Dette er navn på katalogen som inneholder uvsync.ini filen. Bruker "working directory" som standard hvis ingenting er angitt.

--sync_date ...

Dette er hvilken dato som skal synkroniseres. Bruker dagens dato som standard hvis ingenting er angitt. 
Formatet er ISO 8601. Eksempel: 2019-03-23

--station ...

Dette er navn på stasjon som skal synkroniseres. Synkroniserer alle stasjoner hvis ingenting er angitt.

=================================================
UVSYNC.INI

uvsync.ini filen må være lagret med encoding ISO 8859-15 (ANSI)

Følgende parametere er påkrevet for hver stasjon:

    - instrument_id

        Heltall som angir stasjonens instrument ID

    - fetch_module
        
        Python modul som skal benyttes for henting av datafil

    - store_module    

        Python modul som skal benyttes for lesing av datafil og lagring i databasen


    Python modulen som er angitt i parameteret fetch_module har en funksjon (required_parameters) 
    som returnerer en liste med ytteligere påkrevde parametere, i tillegg til en funksjon for henting av datafil (fetch)

    Python modulen som er angitt i parameteret store_module har en funksjon (required_parameters) 
    som returnerer en liste med ytteligere påkrevde parametere, i tillegg til en funksjon for lagring av data (store)

=================================================

Tillat kjøring a powershell script, kjør som lokal administrator:
set-executionpolicy remotesigned