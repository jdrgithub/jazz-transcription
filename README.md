# Jazz Solo Transcription & Analysis

Analyze jazz solos from symbolic notation (and eventually audio) and get plain-English insights about scales, arpeggios, and approach tones.

## What it does

- Download and browse the [Weimar Jazz Database](https://jazzomat.hfm-weimar.de/) (456 solo transcriptions)
- Import solos from MusicXML or standard notation
- Detect jazz scales, arpeggios, and approach tones
- Generate high-level summaries and formatted text reports
- Store analyzed solos in a local library
- Search and cache public-domain transcriptions

Audio transcription scaffolding lives under `jazz_analysis/core/`; the active workflow today is notation-based analysis via the CLI.

## Requirements

- Python 3.9+
- Dependencies listed in `requirements.txt` (notably `music21`, `librosa`, `numpy`)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Run the interactive CLI from the `jazz_analysis` package directory:

```bash
cd jazz_analysis
python jazz_analysis.py
```

### Main menu

| # | Action |
|---|--------|
| 1 | Download Weimar Jazz Database |
| 2 | Browse available solos |
| 3 | Select solo for analysis |
| 4 | Extract solo data |
| 5 | Import MusicXML file |
| 6 | Import standard notation |
| 7 | Analyze jazz scales |
| 8 | Analyze jazz arpeggios |
| 9 | Analyze approach tones |
| 10 | Generate analysis summary |
| 11 | Generate formatted report |
| 12 | Manage local solo library |
| 13 | Public domain transcriptions |
| 14 | Exit |

Typical flow: download the Weimar DB → browse/select a solo → run scale/arpeggio/approach analysis → generate a summary or formatted report → optionally save to the local library.

## Project structure

```
jazz-transcription/
├── jazz_analysis/
│   ├── jazz_analysis.py          # CLI entry point
│   ├── core/                     # Audio transcription (early / planned)
│   └── notation/
│       ├── analysis/             # Scales, arpeggios, approaches, summaries
│       ├── data_access/          # Weimar + public-domain clients
│       ├── database/             # Local solo library (SQLite)
│       └── importers/            # MusicXML + notation parsers
├── data/                         # Downloaded DBs (gitignored)
├── audio/                        # Sample audio files
├── requirements.txt
├── ROADMAP.md                    # Overall product roadmap
├── ROADMAP.notation.md           # Notation-track implementation plan
└── BUILD.log.md                  # Build / phase history
```

## Data notes

- Weimar Jazz Database downloads to `data/weimar_jazz_database.db` (SQLite; ODbL).
- The `data/` directory and `*.db` files are gitignored.
- Local solo library and public-domain cache are created on first use.

## Roadmaps

- **[ROADMAP.md](ROADMAP.md)** — product goals (audio + notation + archives)
- **[ROADMAP.notation.md](ROADMAP.notation.md)** — notation pipeline phases
- **[BUILD.log.md](BUILD.log.md)** — completed work and decisions

Notation Phases 1–4 (Weimar access, importers, analysis engine, archive integration) are largely in place. Audio transcription and end-to-end correction UI remain future work.

## License / attribution

Weimar Jazz Database data is released under the Open Database License (ODbL). Respect source licenses when using public-domain or third-party transcriptions.
