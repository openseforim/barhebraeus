# barhebraeus-chronography

Pilot (20-Nov-2026): OCR of Barhebraeus' *Chronography* (the first, secular part of his history, the *Chronicon
Syriacum*) in the edition of Paul Bedjan, *Gregorii Barhebraei Chronicon Syriacum e codd. mss. emendatum ac punctis
vocalibus adnotationibusque locupletatum* (Paris: Maisonneuve, 1890; printed by Drugulin, Leipzig). As far as we found,
no Unicode text of this edition is online: the archive.org OCR of the BYU scan is not in Syriac letters.

The method comes from the Bochart project ([bochart-hierozoicon](https://github.com/openseforim/bochart),
`SYRIAC.md`): vision LLMs cannot read a long Syriac text, but Kraken with Beth Mardutho's Qoruyo models can.

**Read it:** https://openseforim.org/barhebraeus/ (each page line by line: the Syriac as Kraken
read it, and the same words in Hebrew letters; `uv run build_site.py` writes `docs/`). The Hebrew letters come from a
fixed table (the one of the Bochart project: one letter per consonant, final forms at word end, vowels left out; ܤ = ס).

## Source

- Scan: University of Toronto (Robarts), archive.org item
  [`ketabademadatbez00barhuoft`](https://archive.org/details/ketabademadatbez00barhuoft), 400 ppi, 620 leaves, no
  licence restriction. Bedjan's pages run from the back of the scan: **printed page = 605 − leaf**.
  A second scan (BYU, 600 ppi, item `Bedjan1890GregoriiBarhebraeiChroniconSyriacum`) carries a CC BY-NC-ND licence
  for the scan; not used.
- Type: **East Syriac**, fully vocalised (not Serto, as in the 1789 Bruns-Kirsch edition).
- The page images are not stored in this repository (`data/raw/` is gitignored). They were fetched through the browser
  (`b64save.py`): the leaf's JPEG is
  `https://archive.org/download/ketabademadatbez00barhuoft/ketabademadatbez00barhuoft_jp2.zip/ketabademadatbez00barhuoft_jp2%2Fketabademadatbez00barhuoft_LLLL.jp2&ext=jpg&reduce=0&quality=95`
  (2098 × 3308 px).

## OCR

`uv run ocr_kraken.py 120 121 ...` runs Kraken 7.1.1 from a separate Python 3.12 environment
(`../syriac-ocr/.venv`) with two Qoruyo models (CC-BY 4.0, Zenodo):

| step | model | Zenodo record |
|---|---|---|
| segmentation (baselines) | `syr_print_seg03_91.mlmodel` | 17406626 |
| recognition, East Syriac print | `SyrEastSyr_01_18.mlmodel` | 17406690 |

Kraken's raw output is in visual order (`data/kraken/pNNN.raw.txt`); `ocr_kraken.logical()` turns each line into
logical order (one reversal of the line, then digits and Latin turned back and brackets swapped) and writes
`data/text/pNNN.txt`. About 35-90 seconds a page on the laptop's CPU, free.

## Pilot result: pp. 120-129

The 10 pages give 2,365 words. The check (`uv run check_pilot.py`) is the year AG 1095 (AD 784, the plague of locusts,
Bedjan p. 128), which was transcribed earlier the same day from two other prints in another script (Rosenmüller's
Bochart, vol. 3 p. 283, and Bruns-Kirsch 1789, p. 134, both Serto, read with Kraken's Serto model and reconciled by
hand). Compared on consonants (vowel points and seyame removed; ܤ counted as ܣ):

- 58 words; **55 the same (95%)** before the comparison was used to correct the reference;
- of the 3 differences, 2 were errors in the reference, not in Bedjan's OCR: Bedjan's vowels show ܘܲܡܤܲܒܸܟ݂ (read ܘܡܫܬܟܚ
  by hand from the Serto prints, where Kraken had read ܘܡܣܒܟ in both) and ܘܠܲܓܹ̈ܐ (read ܘܠܓ̈ܢܐ); both were corrected in
  the Bochart project;
- 1 is a Kraken error in Bedjan: ܓܪܒܚܐ for ܓܪܒܝܐ (north).

Other errors seen on a read-through of p. 128: the year digits (Bedjan's "1095" read as 1025), a final punctuation
mark read as ؟. The vowel points have not been checked yet.

## Reader layout (20-Nov-2026)

Each page is split at its punctuation (`.` and `:`; `segments.py`), not by printed line: one row per phrase, Hebrew letters on
the left, the Syriac on the right (on a phone: Syriac first). Bedjan's notes (lines that begin with a note number) come
at the end. P. 1 also has an English translation per segment (`data/translation/p001.json`, by Claude from the OCR
text, God addressed with modern You/Your, not checked by a Syriacist): `build_site.py` adds an English column to any page
that has such a file.

## Translation model test (20-Nov-2026)

`translate_test.py`: pp. 1 (the preface; reference: the pilot translation), 128 (the locusts; reference: Rosenmüller's
Latin) and 250 (narrative: Romanus Diogenes after Manzikert), 132 segments, one call per page, through OpenRouter.
Accuracy judged by reading the outputs against the Syriac and the references. Total cost of the test: $0.26.

| model | $ per 1,000 segments | s per page | accuracy |
|---|---|---|---|
| Gemini 3.8 Flash | 0.10 | 6 | as good as Opus; marks OCR doubts usefully ("[1095 {OCR: 1025}]", "laid eggs {lit. cast seed}") |
| Claude Haiku 5.5 | 0.12 | 45 | **not usable**: invents ("a fierce frost" for the locusts, "Baghdad", "the Manichaeans") |
| Gemini 4 Argon | 0.25 | 12 | good; more {OCR?} flags |
| GPT-6.1 Sol | 0.37 | 14 | good; some free renderings ("the virtues it enumerates") |
| Claude Sonnet 5.5 | 0.37 | 8 | weak on the preface; lost the segment alignment on p. 250 |
| Claude Opus 5.5 | 0.76 | 10 | good; one wrong word on p. 250 (ܢܦܪܣܝܘܗܝ "separate" for "expose") where Flash and Argon were right |

**Choice: Gemini 3.8 Flash**, about $3 for the whole book (about 30,000 segments), about an hour. A second reading by
Argon or Opus only for pages with many {OCR?} marks.

## To do (later, not now)

- **English translation**: done in a first machine version on 20-Nov-2026 (`translate_book.py`: Gemini 3.8 Flash, $2.78 for
  589 pages; pp. 59, 583 and 593-599 by Gemini 4 Argon, $0.10, because Flash returned nothing for p. 59 and its safety filter
  refused p. 583). To do: check a sample against Budge's translation (1932); translate again after the OCR fixes (delete
  the page's `data/translation/pNNN.json`; a page whose segments no longer match is shown without English).
- **The first letter of a line**: Kraken often drops the rightmost letter of a printed line (p. 1: ܕ for ܚܕ, ܒ̈ܢܐ for ܙܒ̈ܢܐ,
  ܕܝܢܬܐ for ܡܕܝܢܬܐ). Measured with `qa_words.py` on 460 pages: 1.2% of line-initial words look like a frequent word without
  its first letter, against 0.28% in mid-line (a lower bound: only words whose full form is frequent are found;
  `data/qa/line_start.tsv`). The letter is clear in the print, and more padding (`ocr --pad 48`) does not help: the letter
  is then read, but wrongly (ܝܕ for ܚܕ). The Serto model did the same on Bochart p. 283 (ܟܫܢܬ for ܒܫܢܬ). Likely fix:
  fine-tune the Qoruyo model (`ketos train`) on a few hundred corrected lines; a first set of corrections can come from
  `line_start.tsv`, where the full word is unique.
- **Fine-tune, first attempt (20-Nov-2026): worse, not used.** `ft_alto.py` (ALTO with line polygons for the flagged
  pages; 129 of 165 done, the rest failed silently), `ft_build_alto.py` (corrected ALTO copies: 131 corrected words on 104
  training pages, 29 on 25 held-out pages), then `ketos -d cpu --workers 2 train -f alto -i SyrEastSyr_01_18.mlmodel
  --resize union --no-reorder -r 0.0001 -N 4 -q fixed -B 4` (2,967 lines, about 3 hours on the CPU). On the held-out pages
  (`ketos test -f alto --no-reorder`): base model 67 errors (99.86% characters), fine-tuned 1,004 errors (97.94%); the
  drop is there from the first epoch, so the training convention probably does not match the base model's (text order
  with --no-reorder on ALTO, or the codec resize). Rectangular line crops (`ft_build.py`, `-f path`) are worse still: the
  base model reads them at 17%. Before another attempt, find the base model's training settings (model metadata,
  `ketos show`, Beth Mardutho's guide) and check that one epoch at learning rate 0 keeps 99.86%.
- **Suspect words**: `data/qa/suspects.tsv` lists 3,457 words seen once with a frequent form one letter away; 1,685 of them
  differ by one changed letter (the rest are mostly prefixes and endings, i.e. grammar). A random sample of 12 looked
  about half real errors (ܘܬܪܝܨ for ܘܬܪܝܢ, ܐܩܝܗ for ܐܩܝܡ, ܩܟܒ for ܩܪܒ) and half valid forms (ܕܬܒܥ, ܠܚܡܝ). To read them on the
  scan, run Kraken with ALTO output (`-a`), which keeps the line boxes; cutting lines by projection did not match Kraken's
  line order (the counts differ by up to 6 lines a page).
- **A second edition as a check** (sample run 20-Nov-2026, `bk_ocr.py`, `cross_check.py`): 10 pages of Bruns-Kirsch 1789
  (vol. 2, pp. 30-530, Serto; printed page = 637 − leaf) read with Kraken's Serto model and aligned to Bedjan (found by
  shared word triples: BK 30 ≈ Bedjan 28, BK 530 ≈ Bedjan 491). Only 61% of the 2,188 words agree, and most
  disagreements are errors of the 1789 reading: the Serto model confuses ܒ and ܟ on this scan (ܟܬܪ for ܒܬܪ, ܟܪ for ܒܪ).
  So the 1789 text is not a word-by-word reference as it stands. It does confirm Bedjan errors where the two differ by
  one letter and the 1789 form is the frequent word: 16 such corrections (`data/qa/confirmed.tsv`), all of them real
  on a read-through (ܙܟܕ → ܘܟܕ, ܫܠܟܐ → ܡܠܟܐ, ܗܪ → ܗܘ, and lost first letters: ܣܐ → ܐܣܐ, ܡܪܘ → ܐܡܪܘ). Rare words are not
  always errors: Bedjan p. 491 (the Mongols) is full of names. The whole 1789 volume is downloaded by
  `download_bruns_kirsch.ps1`; a full run needs a better Serto reading first (fine-tune, or fold ܒ/ܟ in the comparison).
- **Page header and page number**: on the uncropped JPEG 2000 images the facing page shows through above the header
  (p. 30: the header read as the book title, the page number as "86"). Drop the first line (or two) of each page before
  the split, after a check on a sample.
- **Year digits** (p. 128: "1095" read as "1025") and the vowel points: not checked yet.

## Next steps

1. **Scale.** 600 pages at about one minute a page is about 10 hours of CPU: run in the background, 2-3 processes,
   resumable (skip pages whose `data/text/pNNN.txt` exists). The download of 600 leaves (about 1.4 GB) through the
   browser is slow in batches of 5: better a download command run by the owner (the archive.org jp2 zip, 416 MB).
2. **A second check page**: another passage that has an independent text (Bruns-Kirsch 1789 has the whole chronicle in
   Serto: the two editions can be compared page by page, which also measures Kraken's Serto reading).
3. **Layout**: the page header, Bedjan's notes at the foot and his marginal numbers come out as text lines; mark them
   (line position) before the text is joined.
4. **Translation**: Budge's English translation (1932) exists; an English side-by-side is not needed for every page,
   but a site like Bochart's (Syriac with a parallel English) would make the text searchable.
