Claude reccomendation for how to balance learning and creating with this app.

1. **Set up git and a project skeleton.** Learn basic commits and branches now. It’s the habit that pays off most.
2. **Build a read-only API.** FastAPI with SQLAlchemy (or SQLModel) on your existing database. Add endpoints like `GET /articles` and `GET /articles/{id}`, with pagination. Test them in the auto-generated docs page.
3. **Build a minimal React frontend.** Use Vite to scaffold it. Make a list page and an article page that fetch from your API. This is where you learn components, state, and `fetch`.
4. **Add search.** Use SQLite FTS5 plus a search box in React. It’s a small feature with a big payoff.
5. **Add admin features.** Create and edit endpoints, and an admin form. This forces you to learn authentication, which is an important topic to understand rather than copy. Session cookies are simpler and safer to start with than JWTs.
6. **Deploy it.** Use something like Render, Railway, or Fly.io. You’ll learn about environment variables, builds, and production vs. development.

Intro to full stack development - mongo DB

Front end -- user side interface, this code all runs in the browser or the client as referred to.

	-HMTL,CSS, React, Javascript/Typescript?

Connect thes two through API's. Backends can also be prebuilt and accessible through public API's.

Backend -- business logic, applicaitons and processes. Code that runs not in the browser or client side.

	-Python, Flask/FastAPI?, SQLITE3

	-I will have to create API's to access articles DB. Look into RESTFUL API's

HTTP Network request: Running code from browser to request a server to compute or retrieve some information. Fetch and promises in javascript.

DOM manipulation -- how Javascript changes the html page

Note about react and other frameworks. Frameworks are abstractions that hide complexity. Using this early might not give me a real understanding of how development works. I think the question then becomes how important really is this understanding?

	-reccomendation might be javascript -> react -> typescript because of this

Next learn HTTP next, how does networking work generally?

Next hosting through cloud compute

Next is web security, SQL injection

What is server side rendering?
