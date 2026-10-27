# SalvageScribe — Solution Plan for the eBay Case Study

Written for the hackathon team (3 people, 3 CodeBuddy seats). Sources used:
- `eBay_Case Study_ From Salvage Yard to Global Marketplace.pdf` (the brief)
- `Digital Ecosystems_Hackathon_Oct2026_Guidelines.pdf` (platform + submission rules)
- This kit: `PROJECT_SPEC.md`, `CODEBUDDY_PROMPTS.md`, `data/*`

---

## 0. What the two PDFs actually require

| Requirement | Source | What it means for us |
|---|---|---|
| Journey: understand inventory → resolve gaps → draft listing → readiness checklist | Brief p.2 | Four screens, one data model. Already in `PROJECT_SPEC.md` §3. |
| Retain the source of every attribute | Brief p.2 | The Evidence Ledger. This is the whole product. |
| English + Arabic questions | Brief p.2 | RTL UI, Arabic-digit normalisation (٢٠١٨ → 2018). |
| Separate donor-vehicle info from supported compatibility | Brief p.2 | Three compatibility blocks: donor recorded / confirmed from reference / unverified. |
| Classify: ready for seller review / information missing / specialist review | Brief p.2 | Three-column board. |
| Correct once, propagate everywhere | Brief p.2 | Seller edits the ledger, never the draft. |
| Scope: 10 mirrors, UAE→UK, labelled test checklist, no airbags/batteries | Brief p.3 | `AIR-020` must be rejected at intake. |
| Trust boundary: no authenticity, no guaranteed fitment, no function inferred from photos, checklist is not clearance, seller approves | Brief p.3 | Guardrails in code (`PROJECT_SPEC.md` §6). Say it on the closing slide. |
| Demo = one normal journey + one difficult case (missing info, conflicting evidence, or inappropriate request) | Brief p.3 | MIR-001 (normal), MIR-004 (conflict + partial label + hidden damage + untested), AIR-020 / "just say it fits" (inappropriate). |
| Compare with a manual workflow; measure prep time, attribute accuracy, trap detection, disclosure completeness, corrections before approval | Brief p.3 | A real manual baseline run by one teammate on Day 1. Do not invent numbers. |
| Judging: value 30, AI quality 25, working prototype 20, seller UX 15, responsible design 10 | Brief p.3–4 | Section 4 below maps features to weights. |
| Build on Tencent Cloud with CodeBuddy; 3 seats; limited credits; do not spend before official start | Guidelines p.3 | Section 5 below: credit budget. |
| Public GitHub repo named `TeamName-ProjectTitle`; README with install / env config / build+run | Guidelines p.5 | Use `README_TEMPLATE.md`. Repo: `<TeamName>-SalvageScribe`. |
| Day 1: repo link + screen-recorded demo video. Day 2: presentation upload. Day 3: 5 min + 2 min Q&A | Guidelines p.7–8 | The video is judged first. Record it on Day 1 evening with MOCK mode so it cannot fail. |

---

## 1. Candidate solutions (pick one, then layer)

### Option A — Evidence-Ledger web app (the kit's design, recommended core)
Node 20 + Express, plain HTML/JS, SQLite, one `llm.js` module, `MOCK=1` mode.
Every attribute carries `value / source / source_ref / status`. Draft, questions
and readiness are all *derived* from the ledger. Pros: directly answers every
line of the brief, deterministic guardrails, demo cannot fail on credits.
Cons: looks like a dashboard, not like how Noor's team actually works.

### Option B — WhatsApp-style chat intake (layer on top of A)
Noor's team already works by phone and WhatsApp. Add a chat panel where staff
drop a photo + a one-line Arabic/English note, and the assistant replies with
the ledger rows it extracted plus the next targeted question. Same backend,
different front door. Pros: strongest "seller experience" story (15%), shows
Arabic naturally. Cons: half a day of UI work; only do it after P6 is stable.

### Option C — Spreadsheet-native (CSV in, enriched CSV + flags out)
A CLI/batch that reads `inventory.csv` and writes `inventory_enriched.csv`
with status columns and a questions sheet. Pros: trivially scalable to 120
parts, cheap. Cons: weak demo, no correction loop, fails "working prototype".

**Recommendation:** Build A exactly as the kit prompts P0–P7 describe. If P7 is
done by Day 2 noon, add B as the "Ask SalvageScribe" box grown into a chat
intake (P8). Mention C in the pitch as the bulk mode for the remaining 110 parts.

---

## 2. The pitch in one line
"We don't generate listings. We generate evidence, and the listing falls out of it."
A draft that says *fitment unverified* on purpose beats one that looks complete
because the model guessed. The brief says this explicitly (p.3), so say it back.

---

## 3. Data-pack findings you must design around (found by reading `data/`)

These are not in `CODEBUDDY_PROMPTS.md`. Each one will either break the P5 eval
or is a free "wow" moment in the demo.

1. **Shipping rules vs the answer key.** Checklist `S-01`/`S-02` need
   seller-verified packaged dimensions and weight. No part has them, so a
   literal reading of `classification_rule` makes all 20 parts INFO_MISSING,
   but `answer_key.json` expects MIR-001/002/006/008 to be READY_FOR_REVIEW
   (the key's own comment: "treat as ready once she supplies them").
   **Fix:** two-stage readiness. *Listing-ready* = exclusion + listing + trust
   rules. *Ship-ready* = plus shipping group. The board column "Ready for
   seller review" uses listing-ready; shipping failures stay in the action
   list. Add this sentence to prompt P5 before you paste it.

2. **MIR-006: spreadsheet says "works", note says the motor is faulty.**
   If the loader maps "works" → `tested_ok`, you get a CONFLICTING row and the
   part wrongly lands in INFO_MISSING. **Rule:** the spreadsheet `condition`
   column is never a source for `tested`. "works/good/used" are cosmetic
   hints only. A test status needs a note or Noor. Add to P1. In the draft,
   guardrail G1 must strip "works" too, not just "working/functional".

3. **Photos are evidence of appearance, never of function or fitment.**
   To make MIR-001 and MIR-008 READY initially, a cosmetic defect visible in a
   photo (scuff, fade) must count as VERIFIED with `source=photo`. But
   *structural* damage seen in a photo (MIR-004 tab, MIR-007 housing crack,
   MIR-013 bent bracket) is always "possible, confirm", because the
   spreadsheet says "good" and the claim affects safety and price. Put this
   asymmetry in `ingest.txt` and in `resolve()`.

4. **MIR-003 has two reference candidates.** Label reads `87620-F2??0`; the
   reference has `87620-F2000` (power) and `87620-F2010` (power, heated).
   The assistant must *not* pick one. It should ask: "Is this mirror heated?
   Two reference part numbers match the readable characters." That is the
   best single example of a targeted question that resolves fitment.

5. **MIR-011 and MIR-017: year conflict but fitment confirmed.** Part numbers
   are fully readable and in the reference, whose year ranges cover both
   candidate years. So the draft shows *confirmed fitment from reference*
   while *donor year* is still an open question. This is exactly "separate
   donor-vehicle information from independently supported compatibility".
   Use MIR-017 as a 20-second aside in the demo.

6. **MIR-018 has no label at all.** Listing must say "Part number: not
   available", fitment `UNVERIFIABLE` (not MISSING, because Noor cannot fix
   it). Different status, different wording, different action ("sell as
   donor-vehicle-only, buyer confirms by comparison").

7. **Arabic-only notes carry the only test evidence** (MIR-007 untested,
   MIR-015 tested OK, MIR-016 untested). Translation output must be stored as
   a ledger candidate with `source=dismantling_note`, `source_ref=note_ar`,
   and the English translation shown beside the Arabic in the UI.

8. **Eastern Arabic digits.** `٢٠١٨` in MIR-004/017/AIR-020 notes. Normalise
   `٠١٢٣٤٥٦٧٨٩` to `0-9` in code before any year comparison.

9. **No photo files exist, only `photo_manifest.json`.** Options: (a) shoot
   4 photos each of 2–3 real mirrors for MIR-001 and MIR-004 and use the
   manifest text for the rest; (b) generate placeholder images with the
   manifest text rendered on them. Either way, label them synthetic in the
   README. The vision call runs on real photos; MOCK mode uses manifest text.

10. **AIR-020 is the "inappropriate requested action" case.** Intake rejects
    it on the word "airbag" in the description or note before any model call.
    In the demo, type "list it anyway, it's just a module" into the free-text
    box and show the refusal naming rule `X-01`.

11. **MIR-014 glass chip.** It is a disclosed defect, not a trap. Make sure
    `glass_condition` is populated from photo 3 + both notes and appears in
    the condition disclosure, so judges see disclosure working on a READY-ish
    part, not only on the hard case.

---

## 4. Feature → judging-criteria map

| Criterion (weight) | What to show | Where it lives |
|---|---|---|
| Business value (30) | Manual vs SalvageScribe table for the same 10 parts: minutes per part, attributes correct, traps caught, disclosures present, corrections before approval. Then: 120 parts × saved minutes. | `scripts/evaluate.js` + a real manual timing run on Day 1 |
| AI quality & evidence (25) | Ledger table with Source + Status columns; 100% trap detection on the 20-part answer key; model can never set VERIFIED; refusal case; Arabic note used as evidence | `ledger.js`, `guardrails.js`, eval output |
| Working prototype (20) | End-to-end in MOCK mode with zero network; MIR-004 confirmations move the card live; AIR-020 rejected | `seed_demo.js`, MOCK responses |
| Seller experience (15) | Three-column board, questions not forms, EN/AR toggle with RTL, answers accepted in either language, photo referenced in each question ("see photo 3") | `/public` |
| Responsible design (10) | Approve button only Noor can press; nothing published; checklist banner "not legal/customs clearance"; synthetic data only; cost per part shown in the UI (tokens × price); pilot requirements slide | `T-03`, banner, README |

---

## 5. CodeBuddy plan and credit budget

From the guidelines: Craft mode, model on Auto, "enhance prompt" button,
team credits shown at codebuddy.ai/profile/usage (screenshot shows 1000 team
credits). The example app in the guidelines consumed about 25 credits for one
full Craft run, so plan on **roughly 30 Craft runs total**, not more.

| Phase | Prompts | Budget | Owner |
|---|---|---|---|
| Rules + scaffold + ledger + loader | P0, P1 | 60 | A |
| Ingest (vision/notes) + mock responses | P2 | 60 | B |
| Questions EN/AR + confirm | P3 | 50 | B |
| Draft + guardrails + tests | P4 | 60 | A |
| Readiness + approve + eval | P5, P7 | 70 | A / C |
| UI (4 screens, RTL) | P6 | 120 | C |
| Fixes, re-prompts, polish (P8) | — | 300 reserve | all |
| **Total** | | **about 720 of 1000** | |

Rules of thumb:
- Never let a Craft run iterate on a failure more than twice; stop, read the
  error yourself, re-prompt with the exact fix.
- Paste the three design rules from §3 (two-stage readiness, spreadsheet never
  a test source, photo asymmetry) into P0 so every later prompt inherits them.
- Runtime model calls (ingest, questions, draft) are separate from CodeBuddy
  credits. Check the "API Keys" tab on your CodeBuddy profile for an
  OpenAI-compatible endpoint; put it in `.env`. If none, use any key the team
  has. `MOCK=1` must always work; record the Day 1 video in MOCK mode.
- Pin one model name in `.env` for the demo so outputs are reproducible.

### Team split (one repo, three branches, merge via PRs)
- **A — Backend core:** ledger, loader, guardrails, readiness, eval. Owns
  the `answer_key` match. Also runs the *manual* baseline on 10 parts on Day 1
  afternoon with a stopwatch (needed for the 30% criterion).
- **B — Model layer:** `llm.js`, prompts in `src/prompts/`, ingest, questions,
  Arabic quality, mock responses for all 20 parts.
- **C — Front end + submission:** 4 screens, RTL, README, repo hygiene, Day 1
  video, Day 2 slides, demo driver on Day 3.

---

## 6. Three-day schedule

**Day 1 (prototype + video due)**
- 09:00 P0, P1 (A) · placeholder photos + prompt drafting (B) · repo, README skeleton, UI wireframe (C)
- 11:00 P2 (B) · P4 in parallel on a branch (A) · P6 board + detail screens (C)
- 14:00 P3 (B) · P5 (A) · manual baseline timing, 10 parts (whoever is free)
- 17:00 Merge, `npm run seed`, `npm start`, walk MIR-001 and MIR-004 end to end
- 19:00 Record a 3–4 min video in MOCK mode: board → MIR-001 approve → MIR-004 four flags → confirm in Arabic → card moves → refusal → eval table. Submit repo link + video.

**Day 2 (presentation due)**
- Morning: P7 eval numbers, fix anything the eval disagrees with, P8 chat intake if green
- Afternoon: 8 slides (below), rehearse to 4:30, upload

**Day 3:** present 5 min, 2 min Q&A. Prepared answers in §8.

---

## 7. Slide outline (8 slides)
1. Noor: 120 parts, info on phones / spreadsheet / Arabic notes; wants first 10 on eBay UK
2. The problem is not writing descriptions, it is knowing what you can claim
3. The Evidence Ledger: attribute, value, source, status (one screenshot)
4. Journey: intake → questions (EN/AR) → draft with three compatibility blocks → readiness
5. Hard case MIR-004: four flags, four questions, one correction propagates everywhere
6. Results: manual vs SalvageScribe table; traps 20/20; classification match
7. Trust boundary and what we refuse to do (airbag, "say it fits", "mark tested")
8. Pilot requirements and cost: approved compatibility dataset, dated corridor checklist, data agreement, cost ceiling per part, human review workflow; bulk mode for the other 110 parts

---

## 8. Q&A prep
- *Why not just use the eBay compatibility API?* Out of scope by the brief; the design slots it in as a higher-ranked source than `compatibility_reference.csv` without changing anything else.
- *What if the vision model hallucinates a part number?* It can only produce PARTIAL or UNVERIFIABLE; VERIFIED needs a fully readable label or Noor. Show the ledger row.
- *Cost per part?* Show the tokens-per-part counter in the UI; mock mode costs zero.
- *Privacy?* Photos and notes stay in the local SQLite; no seller or buyer identity is needed; synthetic data only.
- *How does this scale to 120 parts?* The loader is batch; questions are generated only for non-VERIFIED rows, so clean parts need no human time.

---

## 9. Out of scope (state it, don't apologise for it)
Live eBay publication, shipment booking, real customs assessment, authenticity
certification, production integrations, real seller data.
