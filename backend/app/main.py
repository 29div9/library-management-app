import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.books import router as books_router
from backend.app.api.members import router as members_router
from backend.app.api.borrowings import router as borrowings_router

app = FastAPI(title="Local Neighbourhood Library API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(books_router)
app.include_router(members_router)
app.include_router(borrowings_router)


@app.get("/")
def root():
    return {"msg": "Library API is running"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8001)
