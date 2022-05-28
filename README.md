# Install

Installer Python 3.x

Installer python moduler: pyodbc, python-pidfile, pywin32

Opprett config.ini

```
[General]
uvsync_directory = <Directory>
connection_string = <Connection string to database>
```

# På hver logge stasjon:

Tillat kjøring a powershell script, kjør som lokal administrator:

```$ set-executionpolicy remotesigned```

Sett opp oppgave i Oppgaveplanlegger som kjører "uvnetcopy.ps1" hver time