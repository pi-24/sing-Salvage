# Singularity-SalvageScribe

AI assistant that turns a salvage yard's fragmented inventory information
(photos, spreadsheet rows, Arabic/English notes, donor-vehicle records) into
evidence-tracked used-parts listing drafts and a UAE→UK readiness checklist,
without inventing part numbers, fitment or condition.

Built for the FutureMindz Fest Hackathon (Dubai CommerCity, October 2026),
eBay case study "From Salvage Yard to Global Marketplace". Developed with
Tencent CodeBuddy on Tencent Cloud.

## The problem

Noor runs a Dubai salvage business with 120 used parts. Her inventory lives in
phone photos, a basic spreadsheet, handwritten labels and Arabic WhatsApp
notes. Part numbers are sometimes unreadable, donor-vehicle details conflict
between sources, and testing status is rarely recorded. She wants to list her
first ten side-view mirrors on eBay UK without guessing compatibility or hiding
damage.

## What it does

- **Evidence ledger** per part: every attribute carries a value, a source
  (seller confirmed, label photo, dismantling note, spreadsheet, model
  inference) and a status (VERIFIED / PARTIAL / CONFLICTING / MISSING /
  UNVERIFIABLE). The model can never set VERIFIED.
- **Targeted questions** in English and Arabic (RTL), generated only for what
  the evidence cannot settle, in a fixed priority order: safety → identifiers
  → side → damage → test status → components → packaged size and weight.
- **Listing drafts** with a mandatory condition-disclosure block and a
  compatibility block split into *donor vehicle recorded* / *confirmed fitment
  from reference* / *unverified*.
- **Readiness checklist** against a versioned, dated test checklist
  (`data/checklist_UAE_UK_v1.json`), classifying each part as *Ready for
  seller review*, *Information missing* or *Specialist review required*, with a
  prioritised action list.
- **Correct once, propagate everywhere.** The seller corrects a ledger row;
  the draft and the checklist are recomputed from it.
- **Hard guardrails in code, not prompts** (see `PROJECT_SPEC.md` §6): no
  "working" wording unless tested OK, no fitment list unless the part number is
  verified and found in the approved reference, no draft for excluded parts
  (airbags, batteries, etc.), seller approval is the only way to "approve".

## Repository layout

| Path | Purpose |
|---|---|
| `PROJECT_SPEC.md` | Design spec: ledger model, screens, API, guardrails, readiness rules |
| `CODEBUDDY_PROMPTS.md` | Ordered CodeBuddy Craft prompts (P0–P8) used to build the app |
| `SOLUTIONS.md` | Solution plan, data-pack findings, judging map, credit budget, demo runbook |
| `data/inventory.csv` | Noor's spreadsheet (messy, as she keeps it) |
| `data/donor_vehicles.csv` | Dismantling / donor-vehicle records |
| `data/inventory_notes.json` | Team notes in English and Arabic |
| `data/photo_manifest.json` | What each photo shows (drives MOCK mode and the placeholder images) |
| `data/photos/` | Synthetic placeholder images, one per manifest entry |
| `data/compatibility_reference.csv` | Small approved compatibility reference (deliberately incomplete) |
| `data/checklist_UAE_UK_v1.json` | Versioned, dated UAE→UK test checklist with rule IDs |
| `data/answer_key.json` | Judges' answer key: traps, expected flags, expected classification |
| `build_pack.py` | Regenerates the synthetic data pack |
| `src/`, `public/`, `scripts/`, `tests/` | Application code (created by the CodeBuddy prompts) |

## Prerequisites

- Node.js 20 or newer
- npm 10 or newer
- Optional: an OpenAI-compatible LLM endpoint and key. The app runs fully in
  `MOCK=1` mode without one.
- Optional: Python 3.10+ to regenerate the data pack or placeholder photos.

## Install

```bash
git clone https://github.com/pi-24/Singularity-SalvageScribe.git
cd Singularity-SalvageScribe
npm install
```

## Configure

```bash
cp .env.example .env
```

| Variable | Purpose | Example |
|---|---|---|
| `LLM_BASE_URL` | OpenAI-compatible chat-completions endpoint | `https://api.example.com/v1` |
| `LLM_API_KEY` | API key for that endpoint | `sk-...` |
| `LLM_MODEL` | Model name pinned for the demo (reproducible output) | `your-model-name` |
| `LLM_VISION_MODEL` | Model used for the photo ingest step (defaults to `LLM_MODEL`) | `your-vision-model` |
| `MOCK` | `1` = canned responses from `data/mock_responses/`, no credits used | `1` |
| `PORT` | HTTP port | `3000` |
| `DB_PATH` | SQLite file location | `./salvagescribe.sqlite` |

Leave `MOCK=1` for the demo. Set `MOCK=0` and fill in the three `LLM_*`
variables to run real model calls.

## Build and run

There is no build step. The frontend is plain HTML/JS served from `/public`.

```bash
npm run seed      # load the 10-part demo inventory into SQLite
npm start         # http://localhost:3000
```

Checks:

```bash
npm test          # guardrail unit tests (one per guardrail in PROJECT_SPEC.md §6)
npm run eval      # run all 20 test-pack parts and compare with data/answer_key.json
```

`npm run eval` prints traps detected / traps present, attributes correct /
total, condition disclosures present / required and classification accuracy,
and saves the run to `results/`.

## Regenerate the data pack

```bash
python build_pack.py                 # rewrites data/*.csv and data/*.json
python scripts/make_placeholder_photos.py   # rewrites data/photos/*.jpg from the manifest
```

## Demo

- Video: _link added on submission_
- **Normal journey:** `MIR-001`. Everything verified, fitment confirmed from
  the reference, seller approves.
- **Hard case:** `MIR-004`. Spreadsheet says 2017, dismantling record says
  2018; part-number label half readable; photo 3 shows a possible crack in the
  mounting tab; no electrical test recorded. Four flags, four questions.
  Seller answers in Arabic, the card moves, the draft updates, fitment stays
  unverified.
- **Inappropriate request:** `AIR-020` (airbag) is rejected at intake; typing
  "just say it fits all Corollas 2014–2020" or "mark it as tested" in the
  free-text box is refused with an explanation of which ledger row needs a
  source.

## Test data

All data in `data/` is synthetic and was generated by `build_pack.py`. Part
numbers are invented and do not correspond to real OEM parts. Photos are
placeholder images rendered from `photo_manifest.json`. No real seller, buyer
or production credentials are used. `data/answer_key.json` is for judges.

## Trust boundary and limitations

The prototype does not certify authenticity, guarantee vehicle compatibility,
infer functionality from photographs, or provide customs, tax or legal
clearance. The checklist is a labelled **test checklist** with fictional
sources. Listing approval stays with the seller. There is no live eBay
publication, shipment booking or production integration.

## Requirements for a real pilot

- An approved compatibility dataset (or eBay's compatibility service) slotted
  in as a higher-ranked source than `compatibility_reference.csv`
- A dated, reviewed corridor checklist replacing `checklist_UAE_UK_v1.json`
- A seller data-handling agreement; photos and notes stay in the seller's
  own storage
- A model cost ceiling per part and a pinned model version
- A human review workflow for the *Specialist review* column

## Team Singularity

| Name | Role |
|---|---|
| Piyush Goel ([pi-24](https://github.com/pi-24)) | _role_ |
| _name_ | _role_ |
| _name_ | _role_ |

## License

MIT, see `LICENSE`.
