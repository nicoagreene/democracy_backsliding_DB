PRAGMA foreign_keys = OFF;

BEGIN;

CREATE TABLE article_categories (
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    violation_category TEXT NOT NULL CHECK (violation_category IN (
        'immigration_and_deportations',
        'erasure_and_censorship',
        'institutional_crackdowns',
        'individual_rights_and_freedoms',
        'judicial_agency',
        'judicial_crackdown',
        'targeting_civil_society_attacks',
        'civil_society_resistance',
        'violence',
        'foreign_policy'
    )),
    PRIMARY KEY (article_id, violation_category)
) STRICT;

INSERT INTO article_categories (article_id, violation_category)
SELECT id, violation_category FROM articles;

-- Rebuild articles: drop violation_category (now lives in
-- article_categories) AND widen classification's CHECK to add
-- 'temporary_ruling'. SQLite's ALTER TABLE cannot modify an existing CHECK
-- constraint, so a plain DROP COLUMN isn't enough here -- a full table
-- rebuild is required to pick up the new classification value.
CREATE TABLE articles_new (
    id INTEGER PRIMARY KEY,
    article_name TEXT NOT NULL,
    publication_date TEXT NOT NULL,     -- ISO format: 'YYYY-MM-DD'
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL UNIQUE,
    citation TEXT NOT NULL,
    violation_description TEXT NOT NULL,
    summary TEXT NOT NULL,
    classification TEXT CHECK (classification IN (
        'social_contradiction',
        'norm_violation',
        'unlawful',
        'unconstitutional',
        'temporary_ruling'
    )),
    contributor_id INTEGER REFERENCES contributors(id),
    date_added TEXT NOT NULL DEFAULT (datetime('now'))
) STRICT;

INSERT INTO articles_new
SELECT id, article_name, publication_date, source_name, source_url, citation,
       violation_description, summary, classification, contributor_id, date_added
FROM articles;

DROP TABLE articles;
ALTER TABLE articles_new RENAME TO articles;

COMMIT;

PRAGMA foreign_keys = ON;
PRAGMA foreign_key_check;   -- must return zero rows