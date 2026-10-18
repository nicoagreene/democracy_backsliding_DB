from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/") #this is root directory
def root():
    return {"Hello": "World"}

@app.get("/hiiii") #get is used to receive data from a server
#So this is where the backend is. I can now putting any amount of computation here and return it with this function
#I think it has to be in JSON?
def hi(): 
    return {"Hi": "Nico"}

articles = []

@app.post('/articles') #post is used to send data to a server
#So after I add data to the server I'm assuming it all disappears once the server stops running? Do you have to 
#do periodic backups to save the data?
#Every single reload of the server loses the data upon some experimentation ...
def add_item(article: str):
    articles.append(article)
    return articles

@app.get('/articles/{article_num}')
# so I think the brackets meaning it can be passable as an argument
# it looks like the var below needs to exactly match the argument passed namespace
def get_article(article_num: int): #if you specify type hint in arg, fastapi will change it for u
    if article_num < len(articles):
        return articles[article_num]
    else:
        #So if this doesn't match HTTPExcpetions syntax or validity wont error j basic internal error message
        raise HTTPException(status_code=404)

"""

Use Uvicorn to run server of app,
run 'uvicorn main:app --reload' to run the app's server with auto reload flag

HTTP status codes are something YOU need to return. Follow guidelines for what everyone will understand
"""