# Wiederanlauf nach einem Nutzungslimit

## Tatsächlicher Vorfall und Korrektur, 2026-11-10

Der erste Nachtlauf startete03:38MEZ, scheiterte aber sofort an `already has an active writer`. Die geöffnete Oberfläche hielt die ursprüngliche Sitzung zum Schreiben reserviert, obwohl der letzte Turn abgeschlossen war. Es fand **keine nächtliche Produktentwicklung** statt. Der zuvor bestandene Dry-Run prüfte nur Argumente und konnte diesen Fehler nicht erkennen.

Korrigiert auf `codex exec fork AUSGANGS_UUID`: separate Fortsetzung mit kopierter Gesprächshistorie, kein zweiter Writer derselben Sitzung. Ein tatsächlicher minimaler Modellaufruf in read-only/ephemeral-Modus lief am10.11. erfolgreich durch (Exit0, exakte Antwort OPEN_LOUD_FORK_OK). Testbefehl `python -B tools/check_codex_fork.py`, lokaler Nachweis `.tools/overnight/fork-smoke-validation.json`. Das ist ein Starttest, noch kein Beweis eines vollständigen Engineeringlaufs. Argument- und Zeittests bleiben zusätzlich bestehen. Offizielle OpenAI-Dokumentation: [Developer commands / exec fork](https://learn.chatgpt.com/docs/developer-commands).

Protokolle neuer Versuche tragen eindeutige Zeitstempel, damit der erste Fehler nicht überschrieben wird. Writer-Konflikte erhalten einen expliziten Blockierungsstatus. Der Supervisor wartet weiterhin auf das Ende des aktiven Ausgangs-Turns; keine parallelen Änderungen durch Oberfläche und Fortsetzung. Im folgenden Text bezeichnet die feste UUID die Ausgangssitzung; die fortgesetzte Arbeit erhält eine eigene Sitzungs-ID.

Der Nutzer hat automatisches Fortsetzen nach Ablauf des5h-Fensters ausdrücklich beauftragt. `tools/resume_after_reset.py` verwendet die installierte Codex-CLI0.167.0 und eine feste Sitzungs-UUID. Keine API-Schlüssel, kein Kontowechsel, kein Zurücksetzen von Limits. Grundlage: [offizielle OpenAI-Dokumentation zum nichtinteraktiven Betrieb](https://learn.chatgpt.com/docs/non-interactive-mode), [CLI-Referenz](https://learn.chatgpt.com/docs/cli/reference) und tatsächlich ausgeführtes `codex exec resume --help`.

Der lokale Startzeitpunkt ist eine Wartezeit, kein garantierter Kontingent-Reset. Ein erneutes Quotalimit führt zu weiterem Warten; sonstige Fehler beenden den Supervisor mit Protokoll. Maximal zwei Versuche und ein festes nächtliches Start-Endfenster. Ein erfolgreicher Codex-Lauf beendet den Supervisor. Windows muss eingeschaltet/angemeldet sein, die Authentifizierung gültig und Fusion für CAD erreichbar bleiben. Kein automatisches Windows-Wakeup eingerichtet.

Vor einem Lauf:

```powershell
python -B tools/resume_after_reset.py --session SESSION_UUID --session-log ABSOLUTE_ROLLOUT_PATH --not-before 2026-11-10T03:00:00+01:00 --stop-at 2026-11-10T08:00:00+01:00 --dry-run
```

Erst nach Prüfung ohne `--dry-run` ausführen; die Zeitangaben sind Beispiele. Der Supervisor wartet zusätzlich auf einen beendeten/abgebrochenen bzw. ausdrücklich limitbeendeten Turn und `.tools/overnight/ready.json` mit `ready:true`. Er startet nicht blind eine zweite aktive Ausführung. Ein Prozess-Lock verhindert doppelte Supervisoren desselben Projekts. Start als verdeckter Windows-Prozess mit `Start-Process -WindowStyle Hidden`; lokale PID/Zeiten in `.tools/overnight/status.json`, Ablaufprotokoll in `supervisor.jsonl`, Codex-Ausgabe in `exec-*.jsonl`. Diese Dateien bleiben git-ignoriert.

Stoppen: leere Datei `.tools/overnight/STOP` anlegen. Sie stoppt das Warten/weitere Starts; ein schon laufender Codex-Prozess wird nicht während eines Dateischreibens abgewürgt. Der Wiederanlaufauftrag liegt versioniert in `continue_prompt.md`. Er verbietet rekursive Supervisorstarts und erhält sämtliche Nutzerkorrekturen. Die für dieses Projekt bereits autorisierten vollen Rechte werden im Kindprozess explizit verwendet; es werden keine fremden Regeldateien oder Authentifizierungen geändert.

Testumfang: Unit-Tests prüfen Zeitberechnung und CLI-Argumentaufbau ohne einen kostenpflichtigen Codex-Lauf zu starten. Dry-Run prüft tatsächlichen CLI-Pfad, Rollout-/UUID-Zuordnung und Zeiten. Ein erfolgreicher nächtlicher Wiederanlauf kann erst nach dem tatsächlichen Lauf bestätigt werden.
