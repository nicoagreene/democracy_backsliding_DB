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
    publication_date TEXT NOT NULL,     -- ISO format: 'YYYY-MM-DD'
    source_name TEXT NOT NULL, 
    source_url TEXT NOT NULL UNIQUE,
    citation TEXT NOT NULL,
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
    violation_description TEXT NOT NULL,
    summary TEXT NOT NULL,
    classification TEXT CHECK (classification IN (
        'social_contradiction',
        'norm_violation',
        'unlawful',
        'unconstitutional'
    )),
    contributor_id INTEGER REFERENCES contributors(id),
    date_added TEXT NOT NULL DEFAULT (datetime('now'))      -- ISO format: 'YYYY-MM-DD'
) STRICT;

CREATE TABLE contributors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
) STRICT;

"""
#prompt to insert a value:
"""
INSERT INTO articles (article_name, publication_date, source_name, source_url,
                     citation, violation_category, violation_description, summary, 
                     classification, contributo_id)
"""




import re
import sqlite3
import pandas as pd

institutional_crackdown_df = pd.read_csv("csv/institutional_crackdown.csv")
print(institutional_crackdown_df.columns)
print(institutional_crackdown_df["Citation (MLA)"])

con = sqlite3.connect("articles.db")
cur = con.cursor()


#res = cur.execute("PRAGMA table_info(articles)")
#print(res.fetchall())

#res = cur.execute("PRAGMA table_info(contributors)")
# print(res.fetchall())



#We must keep the source names uniform throughout all the entries I feel like this is relatively important
#dictionary that maps the url names to source titles we have in our DB
#No reason to create this now we can do this all later
source_names = {
}

def get_contributor_name(text):
    text = re.sub(r'\([^)]*\)', '', text)
    text = text.split(',')[0]
    return text.strip()

def convert_date(text):
    month, day, year = text.strip().split('/')
    return f"20{int(year):02d}-{int(month):02d}-{int(day):02d}"

def get_source_date(citation):
    """
    Given an mla citation, identify the url of the article and return the website name. Do not expect there to always be a www. or http

    example input: "Bender, Michael C., et al. “Trump Administration Highlights: President Signs Order Aimed at Closing Education Dept. - The New York Times.” Trump Administration Highlights: President Signs Order Aimed at Closing Education Dept., The New York Times, 20 Mar. 2025, www.nytimes.com/live/2025/03/20/us/trump-education-news."
    output: "nytimes"

    example input: Offenhartz, Jake, et al. “Top Justice Department Official Orders Prosecutors to Drop Charges against New York Mayor Eric Adams.” AP News, AP News, 11 Feb. 2025, apnews.com/article/eric-adams-indictment-109ef48bd49bc8adc1850709c99bf666?utm_source=copy&utm_medium=share.
    output: "apnews"

    example input: Casey, Michael. “Trump administration freezes $2.2 billion in grants to Harvard over campus activism.” AP News, 15 April 2025, https://apnews.com/article/harvard-trump-administration-federal-cuts-antisemitism-0a1fb70a2c1055bda7c4c5a5c476e18d.
    output: "apnews"
    """
    url_pattern = re.compile(
        r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+)\.'
        r'(?:com|org|net|gov|edu|mil|int|io|co|us|uk|info|biz|news|tv)'
        r'(?=[/\s".,)]|$)'
    )

    match = None
    for match in url_pattern.finditer(citation):
        pass  # keep the last match, since the URL is typically at the end of the citation

    if match is None:
        return None

    return match.group(1).lower()

