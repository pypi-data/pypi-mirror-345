# Localizations
- [ru Русский](README.ru.md)
- [en English](README.md) <-- Current

# GNR Parser
A lightweight library for parsing `.gnr` (Game Notation Record) files and operating on structured game data.

## Features
- `gnrparser.read(data: str)`: Parses raw GNR text and returns structured tag and move data.
- `gnrparser.analyze(data: dict)`: Takes parsed data and returns normalized output with default fields and autocompletions.

## GNR Format Specification (Version 1)
Each GNR file may include the following fields:
- `[Version: INTEGER]` — Format version.
- `[Game: STRING]` — Name of the game.
- `[P<INT>: STRING]` — Player index and name. The format supports any number of players (e.g. `[P1: Alice]`, `[P2: Bob]`).
- `[Variation: STRING]` — Name of the game variation.
- `[Termination: STRING]` — How the game ended. Use `"null"` if the game is still in progress.
- `[Date: STRING]` — Date of the game (format: `DD.MM.YYYY`).
- `[Field Size: INT, INT]` — Width and height of the game field.
- `[Time Limit: STRING]` — Time control format. Examples: `10+5`, `15`, or `null` (no time limit).
- `[Organization: STRING]` — Where or by whom the game was held.
- `[Start Position: STRING]` — Encoded initial field position (custom format, game-specific).
- `1. MOVES 2. MOVES 3. ...` — Turn-based move list (space-separated per turn).

## Installation
```pip install gnrparser```

## Usage
``` python
import gnrparser

raw_data = "...your GNR content..."
parsed = gnrparser.read(raw_data)
analyzed = gnrparser.analyze(parsed)
```

## Author
BesBobowyy — 2025
