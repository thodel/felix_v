# ATR batch — felix-v-sample-gemini-v1

- pages: **100**
- started: 2026-11-17T12:03:47+00:00
- wall time: 1.5 min

| model | read | skipped | failed | empty | looped | arguing | cut off | chars/page | s/page | wall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemini-3.8-flash` | 9 | 91 | 0 | 4 | 0 | 0 | 0 | 1210 | 10.1 | 1.5 min |

**These columns are not quality.** There is no ground truth in this run, and characters per page measures how much a model wrote, not how much of it is right — a model that hallucinates fluently leads this table. Comparing the readings is the point; the numbers only say what each run cost and whether it completed. Measuring accuracy needs transcribed lines and `eval/linebench.py`.

## Pages that came back empty

- `gemini-3.8-flash`: 4 of 9 page(s) (44%)
  - vol2_0237_L
  - vol7_0005_R
  - vol7_0310_R
  - vol8_0174_L

These are successes by every signal this runner has: a 200, no error, both files on disk, and `is_complete` will skip them on every later run. **Look at the images before reading anything into the number.** A blank verso or an envelope flap is genuinely empty, and knowing how many the corpus holds is worth having before extrapolating a cost per page. A *written* page that comes back empty is a defect no other column here would ever show — the segmenter found no lines on it (gateway), or the model answered the page with nothing at all (external reader). The second is a reading the prompt refused, not a page the model could not fetch: compare the same pages under another prompt before concluding anything about the corpus.

## Readings

100 page(s) per model — too many to put in one file. The transcriptions are in `/home/dh/agentic_historian/agentic_historian/data/vlm_test/felix-v-sample-gemini-v1`, one `.txt` per page per model.
