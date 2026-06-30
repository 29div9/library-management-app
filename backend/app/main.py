import uvicorn
from fastapi import FastAPI
from api.books import router as books_router
from api.members import router as members_router

app = FastAPI(title="Local Neighbourhood Library API", version="1.0.0")


app.include_router(books_router)
app.include_router(members_router)


@app.get("/")
def root():
    return {"msg": "Library API is running"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8001)
