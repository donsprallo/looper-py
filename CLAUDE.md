# CLAUDE.md - looper-py: Python-Client einer looper-Simulation

## 0. Was dieses Repository ist
`looper-py` ist die Python-Bibliothek, mit der Tests und Skripte eine
looper-Simulation starten oder sich an eine laufende hängen, sie bedienen und
Erwartungen an sie prüfen. Das Repository heißt `looper-py`, importiert wird
es als `looper`:

```python
import looper

with looper.run("looper.toml", virtual=True) as simulation:
    ...
```

Die Grenze ist ein Prozess: `looper-core` bedient den Inspector-Vertrag
(`looper-cli run`), dieses Projekt ist einer seiner Clients, so wie
`looper-rs`. Der Vertrag ist
`src/looper/infrastructure/contract/looper_inspector.proto`, eine geprüfte
Kopie des Schemas aus `looper-core` (`tests/test_contract_in_step.py`).

**Absolute Regel:** Nichts hier importiert `looper_core`. Die Abhängigkeit
läuft über den Vertrag, nicht über Python-Pakete.

## 1. Architektur (Clean Architecture / Hexagonal)
Die Abhängigkeiten zeigen *nur* nach innen. `tests/test_architecture.py`
prüft das.

1. **Domain** (`looper.domain`): Was gemessen wurde (`Observation`), die
   einzelnen Prüfungen (`checks`) und ihr Ergebnis (`Outcome`,
   `ExpectationReport`). Nur die Standardbibliothek.
2. **Application** (`looper.application`): Der Port `Inspector` (ABC), die
   Use Cases `Expectations` und `Simulation`. Kennt die Domain, nicht gRPC.
3. **Infrastructure** (`looper.infrastructure`): `GrpcInspector` mit den
   generierten Bindings, `LooperCliRun`, der `looper-cli run` als
   Kindprozess startet.
4. **Composition Root** (`looper.starting`): `run()` und `connect()` – die
   einzige Stelle, die einen konkreten Adapter benennt.

## 2. Keine Geschäftslogik, die looper-core gehört
- Was die Simulation selbst betrifft (Anzeigetexte, Wertebereiche, Regeln
  über Pins und Busse), kommt als Feld im Vertrag. Fehlt eines, wird es im
  Schema von `looper-core` ergänzt, nicht hier nachgebaut.
- Hier zu Hause sind die Erwartungen eines Tests: was ein Kanal erreichen,
  was ein Bus tragen, wie tief der Stack werden darf. Sie lebten früher als
  `looper.testing` in `looper-core` und sind mit dem Wechsel auf gRPC
  hierher umgezogen.

## 3. Code-Qualität & Clean Code
- **Single Responsibility** für jede Funktion, Klasse und jedes Modul.
- **Maximale Länge:** Funktion höchstens 20 Zeilen (Docstrings zählen nicht),
  Datei höchstens 250 Zeilen ohne Kommentare.
- **Guard Clauses** statt verschachtelter `if`/`else`.
- **Vollständige Typisierung**, `mypy --strict`, `from __future__ import annotations`.
- **Namen sind Dokumentation.** Keine Einbuchstabenvariablen außer in kurzen Schleifen.
- **Keine Cleverness:** expliziter, lesbarer Code, keine versteckten Seiteneffekte.
- **Domain-Objekte** sind `dataclasses.dataclass(frozen=True)`.

## 4. Verzeichnisstruktur
src/looper/
├── __init__.py           # öffentliche API: run, connect, Simulation, Expectations
├── starting.py           # Composition Root
├── domain/
│   ├── model/            # Observation, Lesungen, Outcome, ExpectationReport
│   └── checks/           # eine Datei pro Gegenstand: Kanal, Bus, Aufruf, Speicher
├── application/
│   ├── ports.py          # Inspector (ABC) und seine zwei Fehlerarten
│   ├── expectations.py   # deklarieren, Zeit vergehen lassen, prüfen
│   ├── subjects.py       # check.channel(...).reaches(...)
│   └── simulation.py     # was ein Test mit einer Simulation tut
└── infrastructure/
    ├── contract/         # Kopie des Vertrags und die generierten Bindings
    ├── grpc_inspector.py
    ├── translation.py    # Nachrichten -> Domain
    └── looper_cli.py     # `looper-cli run` als Kindprozess

## 5. Regeln für Claude bei der Code-Generierung
- **Vertrag nur gemeinsam ändern:** Erst das Schema in `looper-core`, dann
  die Kopie hier, dann `uv run python scripts/generate_contract.py`.
- **Kein `looper_core`-Import**, auch nicht in Tests. Ein Integrationstest
  startet `looper-cli` als Prozess.
- **Inkrementelles Arbeiten:** Bei größeren Features erst die Domain, dann
  Rückfrage, dann Use Cases und Infrastruktur.
