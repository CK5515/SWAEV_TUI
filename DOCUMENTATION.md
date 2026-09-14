# SWAEV GoldBEAM TUI -> Documentation

Reference for every tool in the SWAEV Genomics terminal client, plus recipes for driving
it from a regular shell with `curl`, `jq` and Python.

<- Back to the [README](./README.md)

> **About the outputs.** GoldBEAM is still in training. Every contact matrix in this build
> comes from a deterministic *simulated* surrogate, not from trained model weights. The 40×40
> matrix is the same whatever sequence you load, so anything derived from it (TADs, A/B
> compartments, insulation, loops, ΔContact / SDI, saliency) is illustrative only. Tracks
> computed directly from your DNA (GC, skew, entropy, twist, bendability, CpG O/E, repeats,
> CTCF motif hits) are real. Every exported file starts with a
> `# WARNING: Simulated data. Not real model output.` header.

---

## Contents

1. [Getting started](#1-getting-started)
2. [Screen layout](#2-screen-layout)
3. [Keyboard reference](#3-keyboard-reference)
4. [Loading sequences](#4-loading-sequences)
5. [Tool index -> Flight Simulator (tools 1–9)](#5-tool-index--flight-simulator-tools-19)
6. [Simulation mode -> variant commands](#6-simulation-mode--variant-commands)
7. [Overlays -> CTCF scanner, history, cell lines](#7-overlays--ctcf-scanner-history-cell-lines)
8. [Interpretability Suite (tabs 1–7)](#8-interpretability-suite-tabs-17)
9. [Exports and file formats](#9-exports-and-file-formats)
10. [Settings, themes and languages](#10-settings-themes-and-languages)
11. [Files on disk](#11-files-on-disk)
12. [Power users -> scripting from the terminal](#12-power-users--scripting-from-the-terminal)
13. [Updating and uninstalling](#13-updating-and-uninstalling)

---

## 1. Getting started

```bash
curl -fsSL https://raw.githubusercontent.com/CK5515/SWAEV_TUI/main/install.sh | bash
swaev
```

The installer needs **Python 3.9+** and `pip`. It:

- downloads `client.py` to `~/.swaev/client.py`
- installs `rich` and `requests`
- writes a `swaev` launcher to `~/.local/bin/swaev`
- adds `~/.local/bin` to your `PATH` (bash, zsh or fish)

The TUI uses `termios` for raw key input, so it runs on **Linux and macOS**. On Windows, use WSL.

### First launch

The first run opens an onboarding wizard that asks for:

| Step | What it sets |
|---|---|
| Name | The display name shown in the header |
| Theme | One of 5 colour themes ([§10](#10-settings-themes-and-languages)) |
| Language | English, Español, Français, Deutsch |
| API key | Your `X-API-Key` from <https://swaev.com/portal>. Optional. |
| FASTA folder | The folder the file browser (`L`) scans |

On every launch after that, the client:

1. Checks GitHub for a newer `client.py` and updates itself if one exists ([§13](#13-updating-and-uninstalling)).
2. Checks your API key against `https://gateway.swaev.com/v1/user/usage`.
   - **Valid:** you see your subscription tier and megabase quota.
   - **Invalid (401/403/404):** the key is removed from your config.
   - **Gateway unreachable:** the client continues in offline mode.
   - **No key:** you get an offline **Sandbox** profile. Every local tool still works.
3. Opens the **Genomic Flight Simulator**. Press `L` to load a sequence, or `G` to fetch one from UCSC.

---

## 2. Screen layout

The Flight Simulator has three panels:

```
┌──────────────── FLIGHT HEADER (locus · cell line · mode · quota) ────────────────┐
│                                    │                    │                        │
│   HUD WORKSPACE                    │  TOOLKIT REGISTRY  │   SEQUENCE RADAR       │
│   output of the active tool (1–9)  │  list of tools 1–9 │   rotating DNA helix,  │
│                                    │                    │   coloured by GC/AT,   │
│                                    │                    │   CTCF links marked    │
├──────────────────────────────────────────────────────────────────────────────────┤
│  key bar -> shows only the keys that work in the current context                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

- **Mode** is either `OBSERVATION` (browse and analyse) or `SIMULATION` (type variant
  commands). Press `M` to switch.
- The minimum usable terminal size is **40 × 16**. Below that, the client shows a
  "terminal too small" panel.
- When tool `9` is active, the Sequence Radar turns amber/gold.

---

## 3. Keyboard reference

### Global keys (Flight Simulator)

| Key | Action |
|---|---|
| `1` – `9` | Switch the active tool (this also closes any open overlay) |
| `L` | Open or close the FASTA file browser |
| `G` | Enter a UCSC coordinate to fetch (hg38) |
| `C` | Open or close the CTCF Motif Scanner overlay |
| `⇥ Tab` | Cycle the cell-line context: GM12878 → H1-hESC → IMR90 |
| `M` | Switch between OBSERVATION and SIMULATION mode |
| `I` | Launch the Interpretability Suite (needs a loaded sequence) |
| `H` | Open or close session history |
| `E` | Export the active tool's output ([§9](#9-exports-and-file-formats)) |
| `S` | Settings. **Observation mode only**: in Simulation mode, `s` starts an `snp` command. |
| `?` | Full-screen help for the active tool |
| `Q` | Quit |
| `Ctrl-C` / `Ctrl-D` | Quit immediately |

### Context keys

| Context | Keys |
|---|---|
| File browser | `↑↓` select · `⏎` load · `/` or `:` type a path · `G` UCSC fetch · `L`/`Esc` close |
| Typing a path | `⏎` load · `⌫` edit · `Esc` cancel |
| History overlay | `↑↓` select · `⏎` reload · `x`/`Del` remove entry · `H`/`Esc` close |
| CTCF overlay | `↑↓` select · `⏎` send the anchor to the deletion sandbox · `C`/`Esc` close |
| GOTO (UCSC) input | `⏎` fetch · `⌫` edit · `Esc` cancel |
| Simulation command line | type `s`/`d`/`r` to start `snp`/`del`/`reset` · `⏎` run · `⌫` edit · `Esc` clear |
| Help screens | `↑↓`/`j`/`k` scroll · `PgUp`/`PgDn` · `Home`/`End` · `Space` page down · `q`/`Esc`/`⏎` back |

---

## 4. Loading sequences

### From a FASTA file -> `L`

The browser lists every `.fa`, `.fasta` and `.fna` file in your configured FASTA folder.
To load a file somewhere else, press `/` and type its full path.

- Header lines (`>`) and blank lines are skipped.
- `A C G T` become tokens 0–3. `U` is read as `T`. Any other character becomes `N` (token 4).
- A file load has no genomic coordinates. Exports use `chrUnknown` starting at 0.

### From UCSC -> `G`

Type a coordinate and press `⏎`. The fetch runs in the background, so you can keep working.

```
chr7:114200000-115240000
7:114,200,000-115,240,000     (commas and a missing "chr" are both accepted)
```

- Sequences come from the UCSC REST API, assembly **hg38**.
- Chromosomes `1–22`, `X`, `Y` and `M`/`MT` are accepted.
- Flight Simulator exports use the **real chromosome and start coordinate**.
- If UCSC can't be reached, the client loads a random *synthetic* sequence of the same
  length (capped at 1 Mb) and warns you.

### From history -> `H`

Every loaded file or UCSC region is saved to session history, most recent first. Select an
entry and press `⏎` to load it again ([§7](#7-overlays--ctcf-scanner-history-cell-lines)).

---

## 5. Tool index -> Flight Simulator (tools 1–9)

Press the number key to open a tool, and `?` for its in-app help.

| # | Tool | Summary | Input | `E` exports |
|---|---|---|---|---|
| 1 | ◐ Sequence Analytics | GC skew · Shannon entropy · composition | your DNA | saliency `.bedGraph` |
| 2 | ⌦ Virtual Deletion Probe | In-silico mutagenesis · SDI · ΔContact map | simulated matrix | -> |
| 3 | ⬡ Biophysical Profiler | Helical twist · bendability · CpG island track | your DNA | saliency `.bedGraph` |
| 4 | ≋ Insulation Scoring | TAD barrier profile and boundary table | simulated matrix | TAD boundaries `.bed` |
| 5 | ⊞ Multi-Scale Dilation Check | d1/d2/d4/d8 contact-head diagnostics | simulated matrix | -> |
| 6 | ◍ Species-Embedding Bias | CpG depletion · repeat density · GC bias | your DNA | saliency `.bedGraph` |
| 7 | ⊡ Boundary Anchor Scan | CTCF density + predicted loop anchors | DNA + matrix | TAD `.bed` + loops `.tsv` |
| 8 | ⬛ Structural Disruption Map | 24-bit colour contact matrix + Δ overlay | simulated matrix | -> |
| 9 | ⬡ GoldBEAM Prediction | Model status · benchmark · mission control | -> | -> |

### 1 · Sequence Analytics

- **GC skew** `(G−C)/(G+C)` per bin shows strand asymmetry. Points where the skew flips
  sign often mark replication origins and transcription start sites.
- **Shannon entropy** `H = −Σ p·log₂p` per bin. Low values mean repeats or low-complexity
  sequence; high values mean complex DNA.
- **Composition stats:**
  - GC% -> fraction of G and C bases
  - Tm -> Wallace rule: 2 °C per A/T, 4 °C per G/C
  - CpG O/E -> observed/expected CpG; the mammalian norm is 0.60–0.80
  - Complexity -> 3-mer entropy (Wootton–Federhen)

**Use it for:** checking a region's composition before you model it.

### 2 · Virtual Deletion Probe

Apply an SNP or a deletion and see how the predicted structure changes.

1. Press `M` to switch to SIMULATION mode.
2. Type `snp 500000 G>A` or `del 450000 520000` and press `⏎`. See [§6](#6-simulation-mode--variant-commands) for the full syntax.
3. Read the result:
   - **SDI** (Structural Disruption Index) is the mean |ΔContact| across the matrix.
     ≥ 0.15 is structurally significant; ≥ 0.30 is severe. A red ⚠ appears above the threshold.
   - **Δ map:** red cells are contact gains, blue cells are contact losses. Red/blue striping
     along the diagonal means a TAD boundary moved. An off-diagonal red dot means a neo-loop.

**Shortcut:** press `C`, pick a CTCF anchor and press `⏎`. The client switches to this tool
in SIMULATION mode with a deletion of that anchor already applied.

### 3 · Biophysical Profiler

- **Helical twist** (Calladine & Drew dinucleotide table, about 33–35.5° per step). Low
  twist means a wider minor groove that proteins can reach more easily.
- **Bendability** (Brukner 1995). High values mean flexible DNA that wraps nucleosomes easily.
- **CpG O/E track.** Bins with O/E above 0.6 are flagged ▲ as CpG-island candidates
  (promoters, CTCF sites).

**Use it for:** reading nucleosome-positioning and protein-accessibility signals across a locus.

### 4 · Insulation Scoring

- **Diamond insulation score** (Crawford 2016). For each bin, contacts are summed inside a
  diamond-shaped window on the diagonal. Local minima mark TAD boundaries.
- **Chart:** the x-axis is genomic bins. The y-axis is insulation, where 0 is the strongest
  barrier. Red ▲ marks a called boundary.
- **Boundary table:** boundaries ranked by valley depth, showing the raw insulation score and
  the strength normalised to [0, 1]. Only valleys at least 0.12 deep are called.
- `E` writes a TAD boundary `.bed` file you can open in IGV or the UCSC browser.

### 5 · Multi-Scale Dilation Check

Diagnostics for GoldBEAM's four dilated convolutional heads:

| Head | Range | Captures |
|---|---|---|
| d1 | 0–100 kb | loops, CTCF point contacts |
| d2 | 100–500 kb | sub-domain interactions |
| d4 | 500 kb–2 Mb | TAD-scale architecture |
| d8 | 2 Mb+ | macro-domains, compartments |

- A healthy head has a mean contact between 0.05 and 0.35. Simulated values may fall outside
  that range and be flagged; this is expected until the real weights are loaded.
- The **P(s) decay curve** plots contact probability against genomic distance. It should
  fall steadily; a flat curve points to a matrix artefact.

### 6 · Species-Embedding Bias

Checks whether the sequence looks like the mammalian DNA GoldBEAM is trained on:

| Signal | Interpretation |
|---|---|
| CpG O/E < 0.45 and GC% > 35% | methylated mammalian DNA ✓ |
| CpG O/E > 1.0 | invertebrate or prokaryote |
| GC% > 55% | GC-rich organism (plant or bacterium) |

It also plots the **CpG depletion profile** and **repeat density**: the fraction of each bin
in runs of 4 or more identical bases.

**Use it for:** checking that a sequence is in-distribution before you trust any prediction.

### 7 · Boundary Anchor Scan

- **CTCF density:** hits of the core motif per bin. The top 5 peaks are flagged ▲.
- **Loop anchor pairs:** the top off-diagonal contact scores, at least 6 bins apart.
- `E` writes both a TAD `.bed` and a loop-anchor `.tsv`. You can check the anchors against
  CTCF ChIP-seq peaks with `bedtools intersect` ([§12.5](#125-post-process-exports)).
- Press `C` to open the full six-motif scanner.

### 8 · Structural Disruption Map

- The full **40 × 40 contact matrix** in 24-bit colour, drawn at 2× vertical resolution with
  half-block characters. Colours run purple → yellow → white for low → high contact.
- Bright triangles along the diagonal are TADs; off-diagonal bright spots are loops.
- In SIMULATION mode, after a variant is applied, this panel shows the Δ map and the border
  turns red.
- `Tab` cycles the cell-line context ([§7](#7-overlays--ctcf-scanner-history-cell-lines)).

### 9 · GoldBEAM Prediction

- Mission-control view of the model: O(N) encoder → multi-scale heads (d1/d2/d4/d8).
- The target benchmark is **Akita's 0.832 Pearson correlation** on held-out sequences.
- Current status: pre-training. Every output is simulated.
- Opening this tool starts a short countdown animation and turns the Sequence Radar gold.

---

## 6. Simulation mode -> variant commands

Press `M`, type a command and press `⏎`. `Esc` clears the command line; `M` returns to OBSERVATION mode.

| Command | Effect | Example |
|---|---|---|
| `snp <pos> <REF>><ALT>` | Point mutation at a position in the loaded sequence | `snp 500000 G>A` |
| `del <start> <end>` | Deletion from `start` to `end` (start must be less than end) | `del 450000 520000` |
| `reset` | Restore the wild-type baseline | `reset` |

- Positions count bases from the **start of the loaded sequence**, not genomic coordinates.
  To target `chr7:114,650,000` in a region fetched from `chr7:114200000-…`, use `snp 450000 …`.
- A SNP perturbs the matrix around one bin (strength 0.30). A deletion perturbs it around the
  middle bin of the range (strength 0.50).
- Each applied variant is saved to the session's history entry.
- The same commands work at the Interpretability Suite prompt ([§8](#8-interpretability-suite-tabs-17)).

---

## 7. Overlays -> CTCF scanner, history, cell lines

### CTCF Motif Scanner -> `C`

Searches the loaded sequence for exact matches to six structural motifs. The scan runs in the
background and returns up to 200 hits, sorted by position.

| Motif | Pattern |
|---|---|
| `CTCF_core` | `CCCTCCTGG` |
| `CTCF_core_rc` | `CCAGGAGGG` |
| `CTCF_alt` | `GGGTGGCAG` |
| `CTCF_alt_rc` | `CTGCCACCC` |
| `SP1_GC_box` | `GGGCGG` |
| `CpG_cluster` | `CCGCGCGG` |

Hits show genomic coordinates when the sequence came from UCSC. `⏎` on a hit sends it to
the deletion sandbox (tool 2).

### Session history -> `H`

Each entry records:

- source (`FILE` or `UCSC`) and locator
- length and GC%
- cell line
- last-opened time
- up to 20 variants and 20 exports

`⏎` reloads the entry and `x` removes it. The file keeps the 50 most recent sessions
([§12.4](#124-query-session-history)).

### Cell-line shifter -> `Tab`

| Context | Tissue | Effect on the matrix |
|---|---|---|
| GM12878 | Lymphoblastoid B-cell | sharp TADs: boosts short-range, damps long-range contacts |
| H1-hESC | Embryonic stem cell | diffuse, open chromatin: the opposite bias |
| IMR90 | Lung fibroblast | intermediate compaction |

Switching cell line clears any applied variant and the cached insulation and boundary results.

---

## 8. Interpretability Suite (tabs 1–7)

Press `I` with a sequence loaded. The suite computes every analysis once when it opens, then
waits for commands at its own `» interpret>` prompt. Type a command and press `⏎`.

| Command | Action |
|---|---|
| `1` – `7` | Switch tab |
| `snp <pos> <REF>><ALT>` / `del <start> <end>` / `reset` | Variant modeller (jumps to tab 6) |
| `e1` `e2` `e3` `e4` / `ea` | Export (jumps to tab 7) |
| `?` / `help` / `h` | Help for the current tab |
| `q` / `quit` / `exit` / `back` / empty line | Return to the Flight Simulator |

| Tab | Name | What it shows | Exported by |
|---|---|---|---|
| 1 | **TAD Architecture** | Contact map with TAD triangles and the boundary table (insulation score, strength) | `e1` |
| 2 | **A/B Compartments** | O/E matrix → Pearson correlation → first eigenvector. Green = A (active), blue = B (inactive). The higher-GC side is labelled A. | `e2` |
| 3 | **Insulation Profile** | 1D diamond insulation chart; ▲ marks boundaries | `e1` |
| 4 | **Loop Anchor Registry** | Ranked off-diagonal contacts: rank, bin 1/bin 2, distance in bins, score | `e3` |
| 5 | **Sequence Saliency** | Per-bin attribution; ◆ marks the top 5 bins. Currently a GC-based proxy, later gradient attribution. | `e4` |
| 6 | **Variant Modeller** | ΔContact heatmap, mean \|Δ\|, max gain and max loss. \|Δ\| > 0.15 is significant. | -> |
| 7 | **Export Centre** | Lists the export codes and confirms what was written | `ea` |

> Suite exports always use `chrUnknown` starting at 0, even for UCSC regions. For real
> coordinates, export with `E` in the Flight Simulator, or shift the coordinates with `awk`
> ([§12.5](#125-post-process-exports)).

---

## 9. Exports and file formats

All exports go to **`~/goldbeam_exports/`** with timestamped names:

| File | Written by | Columns |
|---|---|---|
| `goldbeam_tad_boundaries_YYYYMMDD_HHMMSS.bed` | FS `E` on tools 4 and 7 · suite `e1` | `chrom start end TAD_boundary_<bin> score(0–1000) .` |
| `goldbeam_ab_compartments_….bed` | suite `e2` | `chrom start end {A\|B}_compartment_<bin> score(\|eigvec\|×1000) .` |
| `goldbeam_loop_anchors_….tsv` | FS `E` on tool 7 · suite `e3` | `chrom anchor1_start anchor1_end anchor2_start anchor2_end contact_score` |
| `goldbeam_saliency_….bedGraph` | FS `E` on tools 1, 3, 6 · suite `e4` | `chrom start end value` |

In the Flight Simulator, `E` on tools 2, 5, 8 and 9 shows *"Nothing to export for this tool"*.

Every file starts with a provenance header. BED and bedGraph files also have a `track` line:

```
# provenance: SIMULATED -> GoldBEAM model in training. Illustrative only.
# tool: GoldBEAM TAD Boundary Caller
# generated: 2026-09-14 21:24:52
# WARNING: Simulated data. Not real model output.
track name="GoldBEAM_TAD" description="Predicted TAD boundaries (…)"
chr7	114200000	114226000	TAD_boundary_1	412	.
```

- **Bin size** is the sequence length divided by the number of matrix bins (40).
- IGV and the UCSC browser read these files as they are. For `bedtools`, strip the `#` and
  `track` lines first.

---

## 10. Settings, themes and languages

Press `S` in OBSERVATION mode:

| Option | Setting |
|---|---|
| `1` | Display name |
| `2` | Theme. For SWAEV Blue, you also choose a dark or light terminal background. |
| `3` | Language |
| `4` | API key. The new key is verified against the gateway right away. |
| `5` | FASTA folder. The path is validated, the number of FASTA files is shown, and the folder is created if needed. |
| `6` / `⏎` | Back |

**Themes:**

- Retro Multi Colour (`multi_colour`)
- SWAEV Blue (`swaev_blue`)
- SWAEV Lime (`swaev_lime`, the default)
- Cyberpunk Neon (`cyberpunk_neon`)
- Retro Amber (`retro_amber`)

**Languages:** English (`en`) · Español (`es`) · Français (`fr`) · Deutsch (`de`)

---

## 11. Files on disk

| Path | Contents |
|---|---|
| `~/.swaev/client.py` | The application; it replaces itself when updating |
| `~/.local/bin/swaev` | Launcher: `exec python3 ~/.swaev/client.py` |
| `~/.goldbeam.json` | Configuration |
| `~/.goldbeam_history.json` | Session history (last 50 sessions) |
| `~/goldbeam_exports/` | Exported BED, TSV and bedGraph files |

`~/.goldbeam.json`:

```json
{
  "api_url": "https://gateway.swaev.com",
  "api_key": "YOUR_X_API_KEY",
  "username": "Ada",
  "theme": "swaev_lime",
  "language": "en",
  "onboarded": true,
  "fasta_dir": "/home/ada/genomes",
  "terminal_background": "dark"
}
```

- If `api_url` is empty or points at `localhost`, `127.0.0.1` or `*.a.run.app`, it is reset
  to `https://gateway.swaev.com` on launch.
- `fasta_dir` defaults to `.`, which means the folder you launched `swaev` from. Set an
  absolute path to get the same list every time.
- `~/.goldbeam.json` holds your API key in plain text. Keep it private (`chmod 600 ~/.goldbeam.json`).

---

## 12. Power users -> scripting from the terminal

The TUI has **no command-line flags or subcommands**: `swaev` always opens the interactive
interface. For automation, use the same building blocks the client uses:

- the SWAEV gateway
- the UCSC REST API
- the JSON config and history files
- the analysis functions inside `client.py`

The gateway currently exposes one endpoint, **`GET /v1/user/usage`**. Contact-map
prediction runs locally, so there is no prediction endpoint to call yet.

The examples below need `curl`, `jq` and `python3`.

### 12.1 Check your account and quota

```bash
# Reuse the key the TUI already stores, or export SWAEV_API_KEY yourself
export SWAEV_API_KEY="$(jq -r .api_key ~/.goldbeam.json)"

curl -fsS https://gateway.swaev.com/v1/user/usage \
  -H "X-API-Key: ${SWAEV_API_KEY}" | jq
```

Response fields read by the client:

| Field | Type | Meaning |
|---|---|---|
| `name` | string | Account name |
| `email` | string | Account email |
| `subscription_tier` | string | e.g. `sandbox` |
| `megabase_limit` | number | Megabase quota |
| `megabases_used` | number | Megabases used |
| `concurrent_limit` | int | Maximum concurrent jobs |
| `active_jobs` | int | Jobs running now |

HTTP `200` means the key is valid. `401`, `403` or `404` means the key is invalid.

```bash
# Remaining megabases, for use in a script
curl -fsS https://gateway.swaev.com/v1/user/usage -H "X-API-Key: ${SWAEV_API_KEY}" \
  | jq -r '"\(.subscription_tier): \(.megabase_limit - .megabases_used) Mb remaining"'

# Validate a key: print only the HTTP status
curl -s -o /dev/null -w '%{http_code}\n' https://gateway.swaev.com/v1/user/usage \
  -H "X-API-Key: ${SWAEV_API_KEY}"
```

### 12.2 Fetch genomic regions as FASTA

This makes the same UCSC request as `G`, but saves a FASTA file into your FASTA folder so it
shows up in the file browser (`L`):

```bash
fetch_region() {   # usage: fetch_region chr7 114200000 115240000 [hg38]
  local chrom=$1 start=$2 end=$3 genome=${4:-hg38}
  local dir; dir="$(jq -r '.fasta_dir // "."' ~/.goldbeam.json)"
  local out="${dir}/${chrom}_${start}_${end}.fa"
  curl -fsS "https://api.genome.ucsc.edu/getData/sequence?genome=${genome};chrom=${chrom};start=${start};end=${end}" \
    | jq -r --arg hdr ">${chrom}:${start}-${end} ${genome}" '$hdr, (.dna | ascii_upcase | scan(".{1,60}"))' \
    > "$out" && echo "wrote $out"
}

fetch_region chr7 114200000 115240000
```

The header `>chr7:114200000-115240000` records the region's coordinates. The script in
[§12.6](#126-headless-analysis-with-clientpy) reads them back from it.

To fetch many regions, list them in a BED file:

```bash
# regions.bed:  chrom<TAB>start<TAB>end
while IFS=$'\t' read -r chrom start end _; do
  fetch_region "$chrom" "$start" "$end"
  sleep 1                     # be polite to the UCSC API
done < regions.bed
```

### 12.3 Change the configuration

The TUI reads `~/.goldbeam.json` when it starts, so edit it while `swaev` is closed:

```bash
cfg=~/.goldbeam.json
jq '.theme = "retro_amber" | .language = "de"' "$cfg" > "$cfg.tmp" && mv "$cfg.tmp" "$cfg"
jq --arg d "$HOME/genomes" '.fasta_dir = $d'    "$cfg" > "$cfg.tmp" && mv "$cfg.tmp" "$cfg"
jq --arg k "$NEW_KEY"      '.api_key = $k'      "$cfg" > "$cfg.tmp" && mv "$cfg.tmp" "$cfg"
jq '.onboarded = false'                         "$cfg" > "$cfg.tmp" && mv "$cfg.tmp" "$cfg"   # rerun the wizard
```

### 12.4 Query session history

```bash
# One line per session: opened, source, locator, length, GC%, cell line, #variants, #exports
jq -r '.[] | [.last_opened, .source, .locator, .length, .gc_pct, .cell_line,
              (.variants|length), (.exports|length)] | @tsv' ~/.goldbeam_history.json

# Every UCSC region you have explored (handy input for fetch_region)
jq -r '.[] | select(.source == "ucsc") | .locator' ~/.goldbeam_history.json

# Export files created for a given locus
jq -r --arg loc "chr7:114200000-115240000" \
  '.[] | select(.locator == $loc) | .exports[]' ~/.goldbeam_history.json
```

### 12.5 Post-process exports

```bash
cd ~/goldbeam_exports

# Newest file of each type
ls -t goldbeam_tad_boundaries_*.bed | head -1
ls -t goldbeam_loop_anchors_*.tsv   | head -1

# Strip the provenance and track lines into a clean BED file for bedtools
grep -v -e '^#' -e '^track' goldbeam_tad_boundaries_20260914_212452.bed > tads.clean.bed

# Suite exports use chrUnknown:0. Move them onto the real locus:
awk -v c=chr7 -v s=114200000 'BEGIN{OFS="\t"} /^#|^track/ {next} {$1=c; $2+=s; $3+=s; print}' \
  goldbeam_ab_compartments_20260914_212452.bed > ab.chr7.bed

# Which predicted loop anchors overlap CTCF ChIP-seq peaks?
tail -n +6 goldbeam_loop_anchors_20260914_212452.tsv | cut -f1-3 > anchors1.bed
bedtools intersect -u -a anchors1.bed -b ctcf_peaks.bed

# Refuse to use simulated output in a pipeline
grep -q 'Simulated data' goldbeam_saliency_*.bedGraph && echo "simulated -> skipping"
```

### 12.6 Headless analysis with `client.py`

`client.py` only starts the TUI when it is run directly, so Python can import it and call its
analysis and export functions without opening the interface. `goldbeam_batch.py`:

```python
#!/usr/bin/env python3
"""Batch-analyse every FASTA in a folder with the GoldBEAM client's own functions."""
import importlib.util, os, sys

CLIENT = os.environ.get("GOLDBEAM_CLIENT", os.path.expanduser("~/.swaev/client.py"))
spec = importlib.util.spec_from_file_location("goldbeam", CLIENT)
gb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gb)          # safe: the TUI only starts under __main__

fasta_dir = sys.argv[1] if len(sys.argv) > 1 else "."
out_dir = sys.argv[2] if len(sys.argv) > 2 else "goldbeam_batch"
os.makedirs(out_dir, exist_ok=True)

print("file\tlength\tgc_pct\tcpg_oe\tctcf_hits")
for name in gb.scan_fasta_files(fasta_dir):
    tokens = gb.parse_fasta(os.path.join(fasta_dir, name))
    if not tokens:
        continue
    # Use real coordinates when the header looks like ">chr7:114200000-114201000"
    with open(os.path.join(fasta_dir, name)) as fh:
        header = fh.readline().lstrip(">").split()
    coords = gb._parse_genomic_coord(header[0]) if header else None
    chrom, start = (coords[0], coords[1]) if coords else ("chrUnknown", 0)

    stats = gb.compute_sequence_stats(tokens)
    hits = gb.scan_ctcf_motifs(tokens)
    print(f"{name}\t{stats['length']}\t{stats['gc_pct']:.2f}\t{stats['cpg_oe']:.3f}\t{len(hits)}")

    matrix, provenance = gb.get_contact_matrix(tokens)
    bin_bp = max(1, len(tokens) // len(matrix))
    stem = os.path.join(out_dir, os.path.splitext(name)[0])
    boundaries = gb.call_tad_boundaries(gb.compute_insulation_score(matrix))
    gb.export_tad_bed(boundaries, chrom, start, bin_bp, provenance, output_path=stem + ".tad.bed")
    assignments, eigvec = gb.compute_ab_compartments(matrix)
    gb.export_compartment_bed(assignments, eigvec, chrom, start, bin_bp, provenance, output_path=stem + ".ab.bed")
    gb.export_loop_tsv(gb.find_loop_anchors(matrix), chrom, start, bin_bp, provenance, output_path=stem + ".loops.tsv")
    gb.export_saliency_bedgraph(gb.generate_simulated_saliency(tokens, n_bins=len(matrix)), chrom, start, bin_bp, provenance, output_path=stem + ".saliency.bedGraph")
```

```bash
python3 goldbeam_batch.py ~/genomes ./results > summary.tsv
column -t summary.tsv
```

Together with `fetch_region`, this runs a whole pipeline without opening the TUI:

```bash
while IFS=$'\t' read -r c s e _; do fetch_region "$c" "$s" "$e"; done < regions.bed
python3 goldbeam_batch.py "$(jq -r .fasta_dir ~/.goldbeam.json)" ./results
```

**Useful functions** (tokens are `0=A 1=C 2=G 3=T 4=N`):

| Function | Returns |
|---|---|
| `parse_fasta(path)` | token list |
| `scan_fasta_files(dir)` | `.fa` / `.fasta` / `.fna` file names |
| `fetch_ucsc_sequence(chrom, start, end, assembly="hg38")` | token list, or `None` on failure |
| `compute_sequence_stats(tokens)` | dict: `length a c g t n_count gc_pct at_skew gc_skew tm cpg_count cpg_oe` |
| `scan_ctcf_motifs(tokens, coord_offset=0, max_results=200)` | list of `{name, start, end, local_start, local_end, seq}` |
| `get_contact_matrix(tokens)` | `(40×40 matrix, provenance)` -> simulated for now |
| `compute_insulation_score(matrix, diamond_size=5)` | per-bin scores |
| `call_tad_boundaries(scores, min_valley_depth=0.12)` | list of `{bin, insulation_score, boundary_strength}` |
| `compute_ab_compartments(matrix)` | `(["A"/"B", …], eigenvector)` |
| `find_loop_anchors(matrix, min_dist=6, top_n=25)` | list of `(bin1, bin2, score)` |
| `compute_delta_matrix(wt, vt)` / `compute_delta_stats(delta)` | Δ matrix / `{mean_abs_delta, max_gain, max_loss}` |
| `generate_simulated_saliency(tokens, n_bins=40)` | per-bin attribution (GC proxy) |
| `export_tad_bed` · `export_compartment_bed` · `export_loop_tsv` · `export_saliency_bedgraph` | path of the written file (pass `output_path=` to choose it) |

These functions are internal to the client, so their names and signatures can change
between versions. If you depend on them, pin a copy of `client.py`.

---

## 13. Updating and uninstalling

On every launch, the client compares `version.txt` on GitHub with its own `__version__`
(a date such as `2026-09-14`). If GitHub has a newer version, it downloads the new
`client.py` over itself and restarts.

```bash
# Installed vs latest version
grep -m1 '^__version__' ~/.swaev/client.py
curl -fsS https://raw.githubusercontent.com/CK5515/SWAEV_TUI/main/version.txt

# Force a reinstall
curl -fsSL https://raw.githubusercontent.com/CK5515/SWAEV_TUI/main/install.sh | bash
```

To uninstall:

```bash
rm -rf ~/.swaev ~/.local/bin/swaev
rm -f  ~/.goldbeam.json ~/.goldbeam_history.json   # optional: settings and history
rm -rf ~/goldbeam_exports                          # optional: your exported files
```

The installer also added a `PATH` line marked `# Added by SWAEV installer` to your shell rc
file. Remove it by hand if you no longer need it.
