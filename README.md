# 📚 Book Management API with FastAPI + SQLite + JWT

This is a simple Book Management REST API built using [FastAPI](https://fastapi.tiangolo.com/), SQLite for database, and JSON Web Tokens (JWT) for authentication.

## 🚀 Features

- ✅ Add a new book
- 📖 Retrieve all books (with optional filtering by author or publisher)
- ❌ Delete a book by ID
- 🔐 JWT-based authentication for all routes

---

## 🧾 Requirements

- Python 3.10+
- FastAPI
- Uvicorn
- python-jose
- sqlite3 (bundled with Python)

### Install dependencies

```bash```
pip install fastapi uvicorn python-jose

## Run the Server
uvicorn main:app --reload --port 8001

## API Usage / Endpoints

### Doc endpoint
http://127.0.0.1:8001/docs

### Generate Token 
 curl -X POST http://127.0.0.1:8001/token

###  Create Book
curl -X POST http://127.0.0.1:8001/books \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "Atomic Habits",
        "description": "Self-help book",
        "pages": 320,
        "author": "James Clear",
        "publisher": "Penguin"
      }'


### Get all books
curl -X GET http://127.0.0.1:8001/books \
  -H "Authorization: Bearer <your-token>"

### Filter by author
curl -X GET "http://127.0.0.1:8001/books?author=James%20Clear" \
  -H "Authorization: Bearer <your-token>"

### Filter by publisher
curl -X GET "http://127.0.0.1:8001/books?publisher=Penguin" \
  -H "Authorization: Bearer <your-token>"

### Delete Book
curl -X DELETE http://127.0.0.1:8001/books/1 \
  -H "Authorization: Bearer <your-token>"

