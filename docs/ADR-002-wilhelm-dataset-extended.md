# ADR-002: Extend with adamblvck/iching-wilhelm-dataset (Option B)

**Status:** Implemented  
**Context:** Integrate [adamblvck/iching-wilhelm-dataset](https://github.com/adamblvck/iching-wilhelm-dataset) to expose judgment/image/line **text vs comments** and extra metadata (pinyin, hex symbol, trigram keywords) while keeping existing behaviour.

**Summary for maintainers:** The codebase has a single path to full Wilhelm–Baynes (all 64 hexagrams): load adamblvck from submodule (`.js`) or from `data/`/root JSON. If that dataset is absent, the engine uses built-in text only (short judgment/image/lines for hexagrams 1, 2, 11, 63; generic for the rest). There is no other external WB file or parser. Add the submodule (see README) to get full WB; omit it for a smaller install with built-ins only.

---

## 1. Mapping: adamblvck JSON → our model

### 1.1 Source shape (adamblvck)

Each hexagram in `data/iching_wilhelm_translation.json`:

```json
{
  "1": {
    "hex": 1,
    "hex_font": "䷀",
    "trad_chinese": "乾",
    "pinyin": "qián",
    "english": "Initiating",
    "binary": 111111,
    "od": "02",
    "wilhelm_above": { "chinese": "CH'IEN", "symbolic": "THE CREATIVE,", "alchemical": "HEAVEN" },
    "wilhelm_below":  { "chinese": "CH'IEN", "symbolic": "THE CREATIVE,", "alchemical": "HEAVEN" },
    "wilhelm_symbolic": "...",
    "wilhelm_judgment": { "text": "...", "comments": "..." },
    "wilhelm_image":   { "text": "...", "comments": "..." },
    "wilhelm_lines": {
      "1": { "text": "Hidden dragon. Do not act.", "comments": "..." },
      "2": { "text": "...", "comments": "..." },
      ...
      "6": { "text": "...", "comments": "..." }
    }
  }
}
```

### 1.2 Current shape (ours)

- **EnhancedHexagram:** `number`, `chinese_name`, `english_name`, `unicode_symbol`, `binary`, `upper_trigram`, `lower_trigram`, `judgment` (str), `image` (str), `general_meaning`, `interpretations`, `changing_lines: Dict[int, str]`, `commentary: Dict[str, str]`.
- **Full Wilhelm–Baynes:** Only via adamblvck (submodule `.js` or `data/iching_wilhelm_translation.json`). No separate flat JSON; fallback is built-ins only.

### 1.3 Mapping table

| adamblvck key | Current use | New extended field(s) | Notes |
|---------------|-------------|----------------------|--------|
| `hex` | — | (already have `number`) | Optional sanity check. |
| `hex_font` | — | **`hex_unicode`** `str` | e.g. ䷀. |
| `trad_chinese` | `chinese_name` | Keep; can **override** from dataset when present. | |
| `pinyin` | — | **`pinyin`** `str` | e.g. "qián". |
| `english` | — | **`english_short`** `str` (optional) | e.g. "Initiating"; we keep `english_name` like "The Creative" from our names. |
| `binary` | we derive | Can override from dataset (string "111111" or int). | |
| `wilhelm_above` / `wilhelm_below` | — | **`wilhelm_above`** / **`wilhelm_below`** `Dict[str, str]` | `chinese`, `symbolic`, `alchemical`. |
| `wilhelm_symbolic` | — | **`wilhelm_symbolic`** `str` | Paragraph on the hexagram. |
| `wilhelm_judgment.text` | — | **`judgment_text`** `str` | Short oracle. |
| `wilhelm_judgment.comments` | — | **`judgment_comments`** `str` | Wilhelm commentary. |
| (combined) | `judgment` | Keep **`judgment`** = `text + " " + comments` when both present. | Backward compatible. |
| `wilhelm_image.text` | — | **`image_text`** `str` | |
| `wilhelm_image.comments` | — | **`image_comments`** `str` | |
| (combined) | `image` | Keep **`image`** = `text + " " + comments`. | Backward compatible. |
| `wilhelm_lines["n"].text` | — | **`changing_line_texts`** `Dict[int, str]` | Line number → short oracle. |
| `wilhelm_lines["n"].comments` | — | **`changing_line_comments`** `Dict[int, str]` | Line number → commentary. |
| (combined) | `changing_lines[n]` | Keep **`changing_lines[n]`** = `text + " " + comments`. | Backward compatible. |

### 1.4 Backward compatibility

- **Existing fields** `judgment`, `image`, `changing_lines`, `commentary` remain and are still populated (combined text when we have split source).
- **New fields** are optional: only set when loading from adamblvck (or from a converted JSON that includes them). Code that only reads `judgment` / `image` / `changing_lines` continues to work.

---

## 2. Code outline

### 2.1 Data layer (`enhanced_iching_core.py`)

1. **Extend `EnhancedHexagram`**  
   Add optional fields (default `None` or empty dict/string so existing callers don’t break):
   - `pinyin: Optional[str] = None`
   - `hex_unicode: Optional[str] = None`  (e.g. ䷀)
   - `english_short: Optional[str] = None`  (e.g. "Initiating")
   - `wilhelm_symbolic: Optional[str] = None`
   - `wilhelm_above: Optional[Dict[str, str]] = None`
   - `wilhelm_below: Optional[Dict[str, str]] = None`
   - `judgment_text: Optional[str] = None`
   - `judgment_comments: Optional[str] = None`
   - `image_text: Optional[str] = None`
   - `image_comments: Optional[str] = None`
   - `changing_line_texts: Optional[Dict[int, str]] = None`  # line num → short text
   - `changing_line_comments: Optional[Dict[int, str]] = None`

2. **Loader strategy**  
   - **`_load_wilhelm_dataset_adamblvck()`** is the only external Wilhelm–Baynes source: submodule `vendor/iching-wilhelm-dataset/data/iching_wilhelm_translation.js` first, then `data/iching_wilhelm_translation.json` or project-root JSON.
   - **Resolution order:** If adamblvck data exists for a hexagram, use it and fill both existing and new fields (including combined `judgment`, `image`, `changing_lines`). Else use built-in defaults only (no separate flat JSON).

3. **Where hexagrams are built**  
   In `_load_hexagrams()`:
   - For each hexagram number, try adamblvck first:
     - Map `wilhelm_judgment.text` / `.comments` → `judgment_text`, `judgment_comments`; set `judgment = (text + " " + comments).strip()`.
     - Same for image and each line.
     - Map `hex_font` → `hex_unicode`, `pinyin` → `pinyin`, `english` → `english_short`, `wilhelm_above`/`wilhelm_below` → same, `wilhelm_symbolic` → same.
   - If no adamblvck entry, use built-ins only and leave new fields as `None`.

4. **`get_changing_line_guidance()`**  
   No signature change. Internally, if `changing_line_texts` / `changing_line_comments` exist, form per-line strings as e.g. `"Line N: {text}\n{comments}"` for display; otherwise keep current `changing_lines[n]` behaviour.

### 2.2 Divination formatting (`enhanced_divination.py`)

5. **`format_enhanced_consultation()` (or equivalent)**  
   - **Judgment:** If `hexagram.judgment_text` is set, output something like:  
     `**Judgment:** *{judgment_text}*` then on next line `{judgment_comments}`.  
     Else keep current single `**Judgment:** {hexagram.judgment}`.
   - **Image:** Same pattern with `image_text` / `image_comments` vs `image`.
   - **Changing lines:** If `changing_line_texts` / `changing_line_comments` exist for that line, show e.g.  
     `• Line N: *{text}*` then `  {comments}`.  
     Else keep current `• Line N: {hexagram.changing_lines[n]}`.

### 2.3 MCP / server responses (`enhanced_bibliomantic_server.py`)

6. **Hexagram detail response**  
   When building the long hexagram reply:
   - If `hex_unicode` is set, use it in the header (e.g. `*{chinese_name} {hex_unicode}*` or keep existing `unicode_symbol` for trigrams).
   - If `pinyin` is set, add a line like `Pinyin: {pinyin}`.
   - Judgment/Image: same split as in 2.2 (short text first, then commentary) when `judgment_text` / `image_text` exist.
   - Optionally add a short **Symbolic** section from `wilhelm_symbolic` when present.
   - Trigram block: if `wilhelm_above` / `wilhelm_below` exist, optionally append their `symbolic` or `alchemical` to the trigram line.

7. **Tool/response schema**  
   If the MCP exposes structured hexagram objects (e.g. JSON in a response), add optional keys for the new fields so clients can render oracle vs commentary and metadata themselves. Existing keys (`judgment`, `image`, `changing_lines`) remain unchanged.

### 2.4 Data source and dependency

8. **Obtaining adamblvck data**  
   - **Option (a):** Add repo as git submodule under e.g. `vendor/iching-wilhelm-dataset` and load `vendor/iching-wilhelm-dataset/data/iching_wilhelm_translation.json`.
   - **Option (b):** Copy `iching_wilhelm_translation.json` into the project (`data/` or project root) and load from there; document source in README.
   - **Option (c):** (Superseded.) Single source is adamblvck (submodule or JSON); no separate flat file.

9. **Path config**  
   In `enhanced_iching_core`, resolve path to adamblvck JSON from `Path(__file__).resolve().parent` (or from an env var if you want override). If file missing, skip adamblvck and use current JSON / built-in only.

### 2.5 Tests

10. **Tests**  
    - **Unit:** For a hexagram loaded from adamblvck (e.g. 1), assert presence of `judgment_text`, `judgment_comments`, `changing_line_texts[1]`, `changing_line_comments[1]`, and that `judgment` equals combined text+comments.
    - **Regression:** Assert existing tests still pass (they only touch `judgment`, `image`, `changing_lines`).
    - **Formatting:** Optional test that `format_enhanced_consultation` output contains the short oracle line for a changing line when extended data is present.

### 2.6 Summary checklist

- [ ] Extend `EnhancedHexagram` with optional new fields.
- [ ] Add `_load_wilhelm_dataset_adamblvck()` and wire resolution order in `_load_hexagrams()`.
- [ ] Map adamblvck keys to existing + new fields; keep combined strings for `judgment`, `image`, `changing_lines`.
- [ ] Update `format_enhanced_consultation()` to use text/comments split when present.
- [ ] Update enhanced server hexagram response (header, pinyin, judgment/image split, optional symbolic, optional trigram labels).
- [ ] Choose data source (submodule / copied file / converted file) and document.
- [ ] Add/update tests for extended data and backward compatibility.

---

## 3. Reference

- Dataset: [adamblvck/iching-wilhelm-dataset](https://github.com/adamblvck/iching-wilhelm-dataset)  
- Data structure: see repo README and `data/iching_wilhelm_translation.json`.
