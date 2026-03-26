# Open Science Policy Monitor

An automated tool that tracks open science policies across 19 Information Systems journals and conferences.

The monitor runs monthly, checking each venue's author guidelines for changes to eight open science practices: Open Access, Preprint, Open Data, Open Materials, Open Artefact, Registered Reports, Open Peer Review, and Replication.

Results are displayed in an interactive matrix at [cathaldoyle.com/how-open/](https://cathaldoyle.com/how-open/).

## How it works

1. A GitHub Action runs on the 1st of each month
2. For each venue, Claude (via the Anthropic API) searches the web for the current author guidelines and codes them against eight open science practices
3. New codings are compared against the current dataset
4. If any changes are detected, a Pull Request is created with the proposed updates and supporting evidence from the venue's published policies
5. Changes are reviewed and merged manually — the agent proposes, a human approves

## Venues monitored

**Senior Scholars' List of Premier Journals:** DSS, EJIS, I&M, I&O, ISJ, ISR, JAIS, JIT, JMIS, JSIS, MISQ

**AIS Journals:** CAIS, BISE, AJIS

**Major Conferences:** ICIS, ECIS, AMCIS, HICSS, DESRIST

## Coding scale

| Code | Meaning |
|------|---------|
| ✓ | Required or actively offered |
| ~ | Permitted or available |
| _(empty)_ | Not addressed |

## Repository structure

```
├── index.html          # Interactive matrix (loads venues-data.js)
├── venues-data.js      # Venue codings as JS (auto-updated by monitor)
├── venues.json         # Master data file with venue metadata
├── monitor.py          # Monitoring script
├── prompt.txt          # System prompt for policy analysis
└── SETUP.md            # Technical setup and deployment guide
```

## Author

Cathal Doyle
