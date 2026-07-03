"""
DB schema:

Fields per entry:
id, article_name, publication_date, source_name, source_url, citation, violation_category, violation_description, summary, classification
name_of_contributor, id_of_contributor, date_added,


set_of_tag_values

violation_categories: Immigration and deportations, Erasure and Censorship, Institutional Crackdowns, Individual rights and freedoms,
Judicial Agency, Judicial Crackdown, Targeting/Civil Society Attacks, Civil society resistance, Violence, Foreign Policy

classification: Social Contradiction, Norm Violation, Unlawful, Unconstitutional

Creating DB schema: 

Dates stores as 'YYYY-MM-DD'.

I think only question at this point is how flexible do I want categories to be.

CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    article_name TEXT NOT NULL,
    publication_date TEXT NOT NULL,
    source_name TEXT, 
    source_url TEXT NOT NULL UNIQUE,
    citation TEXT NOT NULL,
    violation_category TEXT NOT NULL CHECK (violation_category IN CHECK (violation_category IN (
        'Immigration and Deportations',
        'Erasure and Censorship',
        'Institutional Crackdowns',
        'Individual Rights and Freedoms',
        'Judicial Agency',
        'Judicial Crackdown',
        'Targeting/Civil Society Attacks',
        'Civil Society Resistance',
        'Violence',
        'Foreign Policy'
    )),
    summary TEXT NOT NULL,
    classification TEXT CHECK (classification IN (
        'Social Contradiction',
        'Norm Violation',
        'Unlawful',
        'Unconstitutional'
    )),
    contributor_id INTEGER REFERNCES contributors(id)
    date_added TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE contributors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

"""