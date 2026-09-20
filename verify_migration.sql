-- Run after migrate_add_multiple_article_categories.sql, e.g.:
--   sqlite3 articles.db < verify_migration.sql

-- Row counts: articles count must be unchanged; junction row count should
-- equal the articles count today (1:1), since no article has 2+ categories
-- until add_articles() is re-run against overlapping CSVs.
SELECT
    (SELECT COUNT(*) FROM articles)                           AS articles_count,
    (SELECT COUNT(*) FROM article_categories)                 AS junction_count,
    (SELECT COUNT(*) FROM articles a
       LEFT JOIN article_categories ac ON ac.article_id = a.id
      WHERE ac.article_id IS NULL)                            AS articles_missing_category,
    (SELECT COUNT(*) FROM article_categories ac
       LEFT JOIN articles a ON a.id = ac.article_id
      WHERE a.id IS NULL)                                     AS orphaned_junction_rows;

-- Distribution should match the known pre-migration breakdown:
-- institutional_crackdowns=90, erasure_and_censorship=36,
-- immigration_and_deportations=29, individual_rights_and_freedoms=21,
-- all other categories = 0, total = 176.
SELECT violation_category, COUNT(*) FROM article_categories
GROUP BY violation_category ORDER BY COUNT(*) DESC;

-- violation_category must be gone from articles; classification's CHECK
-- must now include 'temporary_ruling'; article_categories must exist with
-- the composite PK and CASCADE delete.
.schema articles
.schema article_categories

PRAGMA foreign_key_check;   -- must return zero rows
