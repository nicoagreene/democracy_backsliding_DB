from fastapi import FastAPI, HTTPException
import sqlite3
import random

api = FastAPI()

#this line below is the app is called a decorator
@api.get("/") #this is root directory
def root():
    return {"Hello": "World"}

@api.get("/hiiii") #get is used to receive data from a server
#So this is where the backend is. I can now putting any amount of computation here and return it with this function
#I think it has to be in JSON?
def hi(): 
    return {"Hi": "Nico"}

articles = []

@api.post('/articles') #post is used to send data to a server
#So after I add data to the server I'm assuming it all disappears once the server stops running? Do you have to 
#do periodic backups to save the data?
#Every single reload of the server loses the data upon some experimentation ...
def add_item(article: str):
    articles.append(article)
    return articles

@api.get('/articles/{cat}')
def get_article(cat : str):
    con = sqlite3.connect("articles.db")
    con.row_factory = sqlite3.Row  # lets you access columns by name: row["article_name"]
    cur = con.cursor()

    cur.execute(
        """
        SELECT a.*
        FROM articles a
        JOIN article_categories ac ON ac.article_id = a.id
        WHERE ac.violation_category = ?
        ORDER BY a.publication_date
        """,
        (cat,),
    )
    rows = cur.fetchall()
    ri = random.randint(0, len(rows) - 1)
    con.close()
    if not rows:
        raise HTTPException(status_code=404)
    
    return [rows[ri]["article_name"], rows[ri]["summary"]]

@api.get('/articles/browse')
def get_20(page: int = 0, limit: int = 20):
    con = sqlite3.connect("articles.db")
    cur = con.cursor()
    # Execute command to get the coresponding article
    # cur.execute()

    


@api.get('/articles_list/{article_num}')
# so I think the brackets meaning it can be passable as an argument
# it looks like the var below needs to exactly match the argument passed namespace
def get_article_list(article_num: int): #if you specify type hint in arg, fastapi will change it for u
    if article_num < len(articles):
        return articles[article_num]
    else:
        #So if this doesn't match HTTPExcpetions syntax or validity wont error j basic internal error message
        raise HTTPException(status_code=404)



#Define a get request that gets a random article in the DB from the 
#passd in category






"""

Use Uvicorn to run server of app,
run 'uvicorn main:api --reload' to run the app's server with auto reload flag

HTTP status codes are something YOU need to return. Follow guidelines for what everyone will understand

What makes fastapi fast is that it uses asynchronous programming, can execute computation during
i/o downtime (while request is getting processed on backed)

When fastapi:
    -Django if comprehensive framework for not coding from scratch, batteries included
    -Flask for maximum simplicity and simplicity, you get nothing and can do everything
    -FastAPI, high performance api, simple api

Front end sends requests to API, gets responses, and does displays this to user

aynchronous and synchronous functions:
    -async keyword added to to funciton below decorator to make a request asynchronous
    -I don't think I need to use any async?
    -Fastapi will still be asynchronous even if you define no endpoints as 
    async because of how it is built

path parameter: specified in path with /'param' and in fastapi ast /{param_name}
query parameter: specified in path with ?var_name=arg and in fastapi with simply var_name in fun below decorator (w default)
    -You need to specify correct type hint in function argument.

To get to UI to mess around with getting and posting j add /docs to localhost URL

Can't have two methods with the same url


"""