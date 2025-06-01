from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import sqlite3
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI()

# Secret key for JWT
SECRET_KEY = "dsnfb767hcbsfdbashf29e78y834823u9qdiasuhdb "
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30


def init_db():
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS my_books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        pages INTEGER,
        author TEXT,
        publisher TEXT
    )""")
    conn.commit()
    conn.close()

init_db()


def create_token():
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    data = {"exp": expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)



def verify_token(authorization: Optional[str] = Header(None, alias="Authorization")):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("exp") < int(datetime.utcnow().timestamp()):
            raise HTTPException(status_code=401, detail="Token expired")
    except (JWTError, ValueError, IndexError):
        raise HTTPException(status_code=401, detail="Invalid token")

class Book(BaseModel):
    name: str
    description: str
    pages: int
    author: str
    publisher: str


@app.post("/token")
def get_token():
    return {"token": create_token()}


@app.post("/books", dependencies=[Depends(verify_token)])
def create_book(book: Book):
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (name, description, pages, author, publisher) VALUES (?, ?, ?, ?, ?)",
                   (book.name, book.description, book.pages, book.author, book.publisher))
    conn.commit()
    conn.close()
    return {"message": "Book created"}


@app.get("/books", dependencies=[Depends(verify_token)])
def get_books(
    author: str = None,
    publisher: str = None,
    page_no: int = 1
):
    if page_no < 1:
        raise HTTPException(status_code=400, detail="page_no must be >= 1")

    page_size = 2
    offset = (page_no - 1) * page_size

    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()

    query = "SELECT * FROM books WHERE 1=1"
    params = []

    if author:
        query += " AND author=?"
        params.append(author)
    if publisher:
        query += " AND publisher=?"
        params.append(publisher)

    query += " LIMIT ? OFFSET ?"
    params.extend([page_size, offset])

    cursor.execute(query, params)
    books = cursor.fetchall()
    conn.close()

    return [
        {
            "id": b[0],
            "name": b[1],
            "description": b[2],
            "pages": b[3],
            "author": b[4],
            "publisher": b[5]
        }
        for b in books
    ]


@app.delete("/books/{book_id}", dependencies=[Depends(verify_token)])
def delete_book(book_id: int):
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()
    return {"message": "Book deleted"}
