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
                     classification, contributor_id)
"""




import re
import sqlite3
import pandas as pd

def main():

    df = pd.read_csv("csv/institutional_crackdown.csv")
    #print(df.columns)
    #print(df["Citation (MLA)"])


    con = sqlite3.connect("articles.db")
    cur = con.cursor()

    for index, row in df.iterrows():
        if row.isna().all():
            continue

        violation_category = "institutional_crackdown"
        contributor_raw = row["Name of Contributor and date of Contribution"]
        date_raw = row["Date"]
        source = row["Source"]
        citation = row["Citation (MLA)"]
        violation = row["Violation"]
        summary = row["Summary"]
        notes = row["Notes"]
        classification = row["Classification"]

        

        contributor_name = get_contributor_name(str(contributor_raw)) if pd.notna(contributor_raw) else None
        publication_date = convert_date(date_raw) if pd.notna(date_raw) else None
        source_name = get_source_from_url(citation) if pd.notna(citation) else None
        article_name = get_article_name(source) if pd.notna(source) else None
        source_url = get_url_from_citation(citation)
        classification_formatted = format_classification(classification)
        #conntributor_id = get_or_create_contributor(cur, contributor_name)

        print("article name:", article_name)
        print("publication_date:", publication_date)
        print("source_name:", source_name)
        print("source_url:", source_url)
        print("citation:", citation)
        print("violation category:", violation_category)
        print("violation:", violation)
        print("summary:", summary)
        print("classification:", classification_formatted)
        print("\n\n")




#res = cur.execute("PRAGMA table_info(articles)")
#print(res.fetchall())d

#res = cur.execute("PRAGMA table_info(contributors)")
# print(res.fetchall())



#We must keep the source names uniform throughout all the entries I feel like this is relatively important
#dictionary that maps the url names to source titles we have in our DB
#No reason to create this now we can do this all late

def get_or_create_contributor(cur, name):
    if name == "NULL":
        return "NULL"

    cur.execute("SELECT id FROM contributors WHERE name = ?", (name,))
    row = cur.fetchone()
    if row is not None:
        return row[0]

    cur.execute("INSERT INTO contributors (name) VALUES (?)", (name,))
    return cur.lastrowid


def get_contributor_name(text):
    text = re.sub(r'\([^)]*\)', '', text)
    match = re.search(r'[,.]|\s+(?=\d)', text)
    if match:
        text = text[:match.start()]
    return text.strip()

def get_article_name(source_text):
    """
    Write a function that gets all text before a dash.

    example input: "Trump's federal workforce cuts: A timeline of firings and court reversals - USATODAY"
    example output: "Trump's federal workforce cuts: A timeline of firings and court reversals"
    """
    parts = re.split(r'[-]', source_text.strip())

    return parts[0].strip()

def convert_date(text):
    #There was some weird formatting going on with the dating I'm not sure if 
    #this works for all the cases but I j manually changed one thing
    try:
        parts = re.split(r'[/-]', text.strip())
        if len(parts) == 2:
            month, day = parts
            year = 2026
        else:
            month, day, year = parts

        year = int(year)
        if year < 100:
            year += 2000

        return f"{year:04d}-{int(month):02d}-{int(day):02d}"
    except ValueError:
        print(text)

def get_source_from_url(citation):
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

def format_classification(classification):
    """
    make the string all lowercase and replace spaces with underscores. if Nan return string NULL


    example input: "Norm Violation"
    output: "norm_violation"
    
    example input: float('nan')
    output: "NULL"
    
    example input: "Unlawful"
    output: "unlawful"

    """
    if pd.isna(classification):
        return "NULL"

    return classification.strip().lower().replace(" ", "_")

def get_url_from_citation(citation):
    """
    Given an mla citation, identify the url of the article and return the website name. Do not expect there to always be a www. or http

    example input: "Bender, Michael C., et al. “Trump Administration Highlights: President Signs Order Aimed at Closing Education Dept. - The New York Times.” Trump Administration Highlights: President Signs Order Aimed at Closing Education Dept., The New York Times, 20 Mar. 2025, www.nytimes.com/live/2025/03/20/us/trump-education-news."
    output: "www.nytimes.com/live/2025/03/20/us/trump-education-news."

    example input: Offenhartz, Jake, et al. “Top Justice Department Official Orders Prosecutors to Drop Charges against New York Mayor Eric Adams.” AP News, AP News, 11 Feb. 2025, apnews.com/article/eric-adams-indictment-109ef48bd49bc8adc1850709c99bf666?utm_source=copy&utm_medium=share.
    output: "apnews.com/article/eric-adams-indictment-109ef48bd49bc8adc1850709c99bf666?utm_source=copy&utm_medium=share."

    example input: Casey, Michael. “Trump administration freezes $2.2 billion in grants to Harvard over campus activism.” AP News, 15 April 2025, https://apnews.com/article/harvard-trump-administration-federal-cuts-antisemitism-0a1fb70a2c1055bda7c4c5a5c476e18d.
    output: "https://apnews.com/article/harvard-trump-administration-federal-cuts-antisemitism-0a1fb70a2c1055bda7c4c5a5c476e18d."
    """
    url_pattern = re.compile(
        r'(?:https?://)?(?:www\.)?[a-zA-Z0-9-]+\.'
        r'(?:com|org|net|gov|edu|mil|int|io|co|us|uk|info|biz|news|tv)'
        r'\S*'
    )

    match = None
    for match in url_pattern.finditer(citation):
        pass  # keep the last match, since the URL is typically at the end of the citation

    if match is None:
        return None

    url = match.group(0)

    if url[-1] == ".":
        url = url[:-1]

    return url


if __name__ == "__main__":
    main()

