# Multi-category migration — test run notes

Notes from testing `migrate_add_multiple_article_categories.sql` against a copy of
`articles.db` before running it for real. Dated 2026-09-25.

## What changed

- New `article_categories` junction table (`article_id`, `violation_category`) so an
  article can have multiple categories instead of one.
- `articles.violation_category` column removed (data moved into `article_categories`).
- `articles.classification` CHECK widened to add `'temporary_ruling'`.
- Both changes required a full table rebuild for `articles` (not just `ALTER TABLE
  ... DROP COLUMN`), because SQLite can't modify an existing CHECK constraint
  in-place — widening `classification`'s allowed values forces a rebuild.
- `spreadsheet_to_db.py`'s `add_articles()` and `preview_articles()` updated to read/write
  categories via the junction table instead of a column, fixing a real bug: previously,
  if the same `source_url` appeared in more than one category's CSV, `ON CONFLICT
  (source_url) DO NOTHING` silently dropped every category after the first.

## Test procedure

1. **Copied the live DB, never touched the original:**
   ```bash
   cp articles.db articles_test.db
   ```

2. **Ran the migration against the copy:**
   ```bash
   sqlite3 articles_test.db < migrate_add_multiple_article_categories.sql
   ```
   No errors.

3. **Ran verification queries** (`verify_migration.sql`):
   ```bash
   sqlite3 articles_test.db < verify_migration.sql
   ```
   Results:
   - `articles` count: 176 (unchanged)
   - `article_categories` count: 176 (1:1, as expected pre-reimport)
   - 0 articles missing a category, 0 orphaned junction rows
   - Category distribution matched exactly what `articles.db` had before migrating:
     `institutional_crackdowns=90, erasure_and_censorship=36,
     immigration_and_deportations=29, individual_rights_and_freedoms=21`
   - `.schema` confirmed `violation_category` is gone from `articles`, `classification`
     now includes `temporary_ruling`, and `article_categories` has the correct
     composite PK + `ON DELETE CASCADE` FK.
   - `PRAGMA foreign_key_check` returned nothing (no violations).

4. **Confirmed the bug fix with a real example** — row 3 of
   `csv/individual_rights_and_freedoms.csv` (the Mahmoud Khalil / Columbia student
   article, `source_url` ending `fbbd8196`). Before reimporting, this article
   (`id = 128`) was tagged only `immigration_and_deportations` in the DB, even
   though it also appears in `individual_rights_and_freedoms.csv`.

   Ran `add_articles('individual_rights_and_freedoms')` against `articles_test.db`
   only (connection temporarily monkey-patched in a throwaway script so the real
   `articles.db` was never touched):
   ```
   Inserted 0 new article(s); added 8 category link(s); skipped 24 row(s).
   ```
   Article 128 now has **two** rows in `article_categories`:
   `immigration_and_deportations` and `individual_rights_and_freedoms` — the
   second category is no longer silently dropped. 8 category links were
   recovered from this one CSV alone (not just the row-3 example), confirming
   the bug was real and non-trivial (a repo-wide scan earlier found 31 URLs
   shared across multiple category CSVs).

5. **Idempotency check** — reran the same `add_articles('individual_rights_and_freedoms')`
   call a second time:
   ```
   Inserted 0 new article(s); added 0 category link(s); skipped 32 row(s).
   ```
   Article/category counts stayed unchanged (176 / 184) — re-running a CSV import
   is a safe no-op.

6. **Preview check** — `preview_articles()` (updated to open a read-only connection
   and annotate each row as `NEW ARTICLE` / `EXISTING ARTICLE ... would ADD
   category` / `... already recorded`) verified correct against
   `csv/erasure_and_censorship.csv`.

7. **Existing test suite** (`test_spreadsheet_to_db.py`) — untouched by this
   refactor, since it only covers pure helper functions
   (date/URL/name parsing) that don't reference categories.

## Pre-existing issues found (not caused by this migration, not fixed)

- `preview_articles()` crashes with a `KeyError` on `individual_rights_and_freedoms.csv`
  (and likely `judicial_crackdown.csv`) because those CSVs have a blank header for
  the first column (pandas names it `Unnamed: 0`). `add_articles()` already works
  around this using `row.iloc[0]` (positional); `preview_articles()` still uses the
  named lookup `row["Name of contributor and date uploaded"]` and was never updated
  to match. Works fine on CSVs with a proper header.
- `csv/institutional_crackdown.csv` is named singular, but the DB enum value is
  `institutional_crackdowns` (plural) — re-importing that category would currently
  fail with `FileNotFoundError`.

## Status

- `articles.db` (the real database) was **never modified** during this test — only
  `articles_test.db` (a throwaway copy) was migrated and written to.
- Migration script, verification script, and code changes are considered validated
  and ready to run for real, pending a decision on when to do so.

## To run for real

```bash
cd /Users/nicholasgreene/Documents/democracy_backsliding_DB
cp articles.db "articles.db.bak.$(date +%Y%m%d%H%M%S)"   # backup first
sqlite3 articles.db < migrate_add_multiple_article_categories.sql
sqlite3 articles.db < verify_migration.sql
```
If anything in the verification output looks wrong, restore from the `.bak` copy
before investigating further.
